import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';

export interface LogEntry {
  timestamp: string;
  type: 'REQUEST' | 'RESPONSE' | 'ERROR' | 'FILE_OPERATION';
  level: 'INFO' | 'WARN' | 'ERROR';
  requestId?: string;
  endpoint?: string;
  method?: string;
  data?: any;
  error?: any;
  duration?: number;
}

@Injectable({
  providedIn: 'root'
})
export class FrontendLoggerService {
  private logs: LogEntry[] = [];
  private maxLogs = 5000; // Increased for full content viewing
  private logToConsole = true;
  private logToStorage = true;
  private logToFile = true; // NEW: Enable file logging
  private storageKey = 'lora_dashboard_logs';
  private logFilePrefix = 'lora_dashboard_log';
  private truncateData = false; // Control data truncation

  constructor() {
    this.loadLogsFromStorage();
  }

  /**
   * Log a request
   */
  logRequest(endpoint: string, method: string, data: any, requestId?: string): string {
    const id = requestId || this.generateRequestId();
    
    const logEntry: LogEntry = {
      timestamp: new Date().toISOString(),
      type: 'REQUEST',
      level: 'INFO',
      requestId: id,
      endpoint,
      method,
      data: this.sanitizeData(data)
    };

    this.addLog(logEntry);
    
    if (this.logToConsole) {
      console.log(`🚀 [FRONTEND] REQUEST | ${method} ${endpoint} | ID: ${id}`, {
        data: this.sanitizeData(data),
        requestId: id,
        timestamp: logEntry.timestamp
      });
    }

    return id;
  }

  /**
   * Log a response
   */
  logResponse(requestId: string, endpoint: string, data: any, status?: number, duration?: number): void {
    const logEntry: LogEntry = {
      timestamp: new Date().toISOString(),
      type: 'RESPONSE',
      level: status && status >= 400 ? 'ERROR' : 'INFO',
      requestId,
      endpoint,
      data: this.sanitizeData(data),
      duration
    };

    this.addLog(logEntry);
    
    if (this.logToConsole) {
      const icon = status && status >= 400 ? '❌' : '✅';
      console.log(`${icon} [FRONTEND] RESPONSE | ${endpoint} | ID: ${requestId} | ${duration}ms`, {
        data: this.sanitizeData(data),
        status,
        duration,
        requestId,
        timestamp: logEntry.timestamp
      });
    }
  }

  /**
   * Log an error
   */
  logError(requestId: string, endpoint: string, error: any, context?: any): void {
    const logEntry: LogEntry = {
      timestamp: new Date().toISOString(),
      type: 'ERROR',
      level: 'ERROR',
      requestId,
      endpoint,
      error: this.serializeError(error),
      data: context ? this.sanitizeData(context) : undefined
    };

    this.addLog(logEntry);
    
    if (this.logToConsole) {
      console.error(`💥 [FRONTEND] ERROR | ${endpoint} | ID: ${requestId}`, {
        error: error,
        context: context,
        requestId,
        timestamp: logEntry.timestamp
      });
    }
  }

  /**
   * Log file operations
   */
  logFileOperation(operation: string, files: File[], requestId?: string): void {
    const logEntry: LogEntry = {
      timestamp: new Date().toISOString(),
      type: 'FILE_OPERATION',
      level: 'INFO',
      requestId,
      data: {
        operation,
        files: files.map(f => ({
          name: f.name,
          size: f.size,
          type: f.type,
          lastModified: f.lastModified
        }))
      }
    };

    this.addLog(logEntry);
    
    if (this.logToConsole) {
      console.log(`📁 [FRONTEND] FILE | ${operation} | ${files.length} files | ID: ${requestId}`, {
        files: logEntry.data.files,
        requestId,
        timestamp: logEntry.timestamp
      });
    }
  }

  /**
   * Get all logs
   */
  getLogs(): LogEntry[] {
    return [...this.logs];
  }

  /**
   * Get logs by request ID
   */
  getLogsByRequestId(requestId: string): LogEntry[] {
    return this.logs.filter(log => log.requestId === requestId);
  }

  /**
   * Clear all logs
   */
  clearLogs(): void {
    this.logs = [];
    this.saveLogsToStorage();
    
    // IMPORTANT: Also clear text file buffer
    this.clearTextBuffer();
    
    console.log('🧹 [FRONTEND] Logs and text buffer cleared');
  }

  /**
   * Clear text file buffer
   */
  clearTextBuffer(): void {
    const bufferKey = this.storageKey + '_text_buffer';
    try {
      // Download current buffer before clearing (optional - user choice)
      const buffer = localStorage.getItem(bufferKey);
      if (buffer && buffer.trim()) {
        console.log('📁 [FRONTEND] Text buffer found with', buffer.split('\n').length, 'lines');
        // Uncomment the line below if you want to auto-download before clearing
        // this.downloadTextBuffer(buffer);
      }
      
      // Clear the buffer
      localStorage.removeItem(bufferKey);
      console.log('🧹 [FRONTEND] Text buffer cleared');
    } catch (e) {
      console.warn('Failed to clear text buffer:', e);
    }
  }

  /**
   * Export logs as JSON
   */
  exportLogs(): string {
    return JSON.stringify(this.logs, null, 2);
  }

  /**
   * Download logs as file
   */
  downloadLogs(): void {
    try {
      const dataStr = this.exportLogs();
      console.log('📁 [FRONTEND] Starting download...', {
        logsCount: this.logs.length,
        dataSize: dataStr.length,
        browser: navigator.userAgent
      });

      // Enhanced download with error handling and fallback
      this.downloadFileWithFallback(
        dataStr, 
        `lora_dashboard_logs_${new Date().toISOString().split('T')[0]}.json`,
        'application/json'
      );
    } catch (error) {
      console.error('📁 [FRONTEND] Download failed:', error);
      const errorMessage = error instanceof Error ? error.message : String(error);
      alert('Download failed: ' + errorMessage);
    }
  }

  /**
   * Get logging statistics
   */
  getLogStats(): any {
    const total = this.logs.length;
    const requests = this.logs.filter(l => l.type === 'REQUEST').length;
    const responses = this.logs.filter(l => l.type === 'RESPONSE').length;
    const errors = this.logs.filter(l => l.type === 'ERROR').length;
    const fileOps = this.logs.filter(l => l.type === 'FILE_OPERATION').length;

    return {
      total,
      requests,
      responses,
      errors,
      fileOperations: fileOps,
      storageSize: this.getStorageSize(),
      oldestLog: total > 0 ? this.logs[0].timestamp : null,
      newestLog: total > 0 ? this.logs[total - 1].timestamp : null
    };
  }

  private addLog(logEntry: LogEntry): void {
    this.logs.push(logEntry);
    
    // Keep only the latest N logs
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(-this.maxLogs);
    }
    
    if (this.logToStorage) {
      this.saveLogsToStorage();
    }
    
    // NEW: Auto-save to text file
    if (this.logToFile) {
      this.appendToTextFile(logEntry);
    }
  }

  private sanitizeData(data: any): any {
    if (!data) return data;
    
    try {
      const sanitized = JSON.parse(JSON.stringify(data, (key, value) => {
        // Hide sensitive data
        if (typeof key === 'string' && 
            (key.toLowerCase().includes('password') || 
             key.toLowerCase().includes('token') || 
             key.toLowerCase().includes('key') ||
             key.toLowerCase().includes('secret'))) {
          return '***HIDDEN***';
        }
        
        // Truncate large content only if truncation is enabled
        if (this.truncateData && typeof value === 'string' && value.length > 500) {
          return `${value.substring(0, 500)}... [TRUNCATED - ${value.length} chars]`;
        }
        
        return value;
      }));
      
      return sanitized;
    } catch (e) {
      return { error: 'Failed to sanitize data', original: String(data) };
    }
  }

  private serializeError(error: any): any {
    if (error instanceof Error) {
      return {
        name: error.name,
        message: error.message,
        stack: error.stack
      };
    }
    return error;
  }

  private generateRequestId(): string {
    return Math.random().toString(36).substr(2, 8);
  }

  private saveLogsToStorage(): void {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(this.logs));
    } catch (e) {
      console.warn('Failed to save logs to localStorage:', e);
    }
  }

  private loadLogsFromStorage(): void {
    try {
      const stored = localStorage.getItem(this.storageKey);
      if (stored) {
        this.logs = JSON.parse(stored);
      }
    } catch (e) {
      console.warn('Failed to load logs from localStorage:', e);
      this.logs = [];
    }
  }

  private getStorageSize(): number {
    try {
      const stored = localStorage.getItem(this.storageKey);
      return stored ? stored.length : 0;
    } catch (e) {
      return 0;
    }
  }

  /**
   * NEW: Append single log entry to text file
   */
  private appendToTextFile(logEntry: LogEntry): void {
    try {
      const logLine = this.formatLogEntryAsText(logEntry);
      
      // Since we can't directly append to files in browser, we'll create periodic downloads
      // Store in localStorage with rotation
      this.appendToFileBuffer(logLine);
      
    } catch (e) {
      console.warn('Failed to append to text file:', e);
    }
  }

  /**
   * NEW: Format log entry as readable text line
   */
  private formatLogEntryAsText(logEntry: LogEntry): string {
    const timestamp = new Date(logEntry.timestamp).toLocaleString();
    const level = logEntry.level.padEnd(5);
    const type = logEntry.type.padEnd(12);
    
    let line = `[${timestamp}] ${level} ${type}`;
    
    if (logEntry.requestId) {
      line += ` ID:${logEntry.requestId}`;
    }
    
    if (logEntry.method && logEntry.endpoint) {
      line += ` ${logEntry.method} ${logEntry.endpoint}`;
    }
    
    if (logEntry.duration) {
      line += ` (${logEntry.duration}ms)`;
    }
    
    if (logEntry.data) {
      const dataStr = typeof logEntry.data === 'string' ? 
        logEntry.data : JSON.stringify(logEntry.data);
      line += ` | Data: ${dataStr.substring(0, 200)}${dataStr.length > 200 ? '...' : ''}`;
    }
    
    if (logEntry.error) {
      const errorStr = typeof logEntry.error === 'string' ? 
        logEntry.error : JSON.stringify(logEntry.error);
      line += ` | ERROR: ${errorStr}`;
    }
    
    return line;
  }

  /**
   * NEW: Manage text file buffer with rotation
   */
  private appendToFileBuffer(logLine: string): void {
    const bufferKey = this.storageKey + '_text_buffer';
    const maxBufferSize = 50000; // ~50KB per buffer
    
    try {
      let buffer = localStorage.getItem(bufferKey) || '';
      buffer += logLine + '\n';
      
      // If buffer is getting too large, auto-download and clear
      if (buffer.length > maxBufferSize) {
        this.downloadTextBuffer(buffer);
        buffer = logLine + '\n'; // Start new buffer with current line
      }
      
      localStorage.setItem(bufferKey, buffer);
    } catch (e) {
      console.warn('Text buffer full, triggering download:', e);
      this.downloadCurrentTextBuffer();
    }
  }

  /**
   * NEW: Download text buffer as file
   */
  private downloadTextBuffer(buffer: string): void {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `${this.logFilePrefix}_${timestamp}.txt`;
    
    const blob = new Blob([buffer], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
    
    console.log(`📁 [FRONTEND] Log file downloaded: ${filename}`);
  }

  /**
   * NEW: Download current text buffer
   */
  downloadCurrentTextBuffer(): void {
    const bufferKey = this.storageKey + '_text_buffer';
    const buffer = localStorage.getItem(bufferKey) || '';
    
    if (buffer.trim()) {
      this.downloadTextBuffer(buffer);
      localStorage.removeItem(bufferKey);
    } else {
      console.log('📁 [FRONTEND] No text buffer to download');
    }
  }

  /**
   * NEW: Download all logs as formatted text file
   */
  downloadLogsAsText(): void {
    try {
      const textContent = this.logs
        .map(log => this.formatLogEntryAsText(log))
        .join('\n');
      
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const filename = `${this.logFilePrefix}_full_${timestamp}.txt`;
      
      console.log('📁 [FRONTEND] Starting text download...', {
        logsCount: this.logs.length,
        contentSize: textContent.length,
        filename: filename
      });

      // Enhanced download with error handling and fallback
      this.downloadFileWithFallback(textContent, filename, 'text/plain');
      
      console.log(`📁 [FRONTEND] Full log file downloaded: ${filename} (${this.logs.length} entries)`);
    } catch (error) {
      console.error('📁 [FRONTEND] Text download failed:', error);
      const errorMessage = error instanceof Error ? error.message : String(error);
      alert('Text download failed: ' + errorMessage);
    }
  }

  /**
   * NEW: Enable/disable file logging
   */
  setFileLogging(enabled: boolean): void {
    this.logToFile = enabled;
    console.log(`📁 [FRONTEND] File logging ${enabled ? 'enabled' : 'disabled'}`);
  }

  /**
   * NEW: Get file logging status
   */
  isFileLoggingEnabled(): boolean {
    return this.logToFile;
  }

  /**
   * NEW: Enable/disable data truncation
   */
  setDataTruncation(enabled: boolean): void {
    this.truncateData = enabled;
    console.log(`📝 [FRONTEND] Data truncation ${enabled ? 'enabled' : 'disabled'}`);
  }

  /**
   * NEW: Get data truncation status
   */
  isDataTruncationEnabled(): boolean {
    return this.truncateData;
  }

  /**
   * NEW: Set maximum logs limit
   */
  setMaxLogs(max: number): void {
    this.maxLogs = max;
    // Trim current logs if needed
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(-this.maxLogs);
      this.saveLogsToStorage();
    }
    console.log(`📊 [FRONTEND] Max logs set to ${max}`);
  }

  /**
   * NEW: Enhanced download method with fallback options
   */
  private downloadFileWithFallback(content: string, filename: string, mimeType: string): void {
    console.log('📁 [FRONTEND] Attempting download...', {
      filename,
      mimeType,
      contentLength: content.length,
      browserSupport: {
        blob: !!window.Blob,
        objectURL: !!URL.createObjectURL,
        download: 'download' in document.createElement('a')
      }
    });

    // Method 1: Standard Blob download (primary method)
    try {
      const blob = new Blob([content], { type: mimeType });
      const url = URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      link.style.display = 'none';
      
      // Add to DOM, click, then remove
      document.body.appendChild(link);
      
      console.log('📁 [FRONTEND] Triggering download click...', {
        href: link.href,
        download: link.download,
        linkInDOM: document.body.contains(link)
      });
      
      link.click();
      
      // Clean up after a short delay
      setTimeout(() => {
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        console.log('📁 [FRONTEND] Download cleanup completed');
      }, 100);
      
      return;
    } catch (error) {
      console.error('📁 [FRONTEND] Standard download failed:', error);
    }

    // Method 2: Data URI fallback
    try {
      console.log('📁 [FRONTEND] Trying data URI fallback...');
      const dataUri = `data:${mimeType};charset=utf-8,${encodeURIComponent(content)}`;
      
      const link = document.createElement('a');
      link.href = dataUri;
      link.download = filename;
      link.style.display = 'none';
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      console.log('📁 [FRONTEND] Data URI download succeeded');
      return;
    } catch (error) {
      console.error('📁 [FRONTEND] Data URI download failed:', error);
    }

    // Method 3: Open in new window fallback
    try {
      console.log('📁 [FRONTEND] Trying new window fallback...');
      const blob = new Blob([content], { type: mimeType });
      const url = URL.createObjectURL(blob);
      
      const newWindow = window.open(url, '_blank');
      if (newWindow) {
        console.log('📁 [FRONTEND] Content opened in new window');
        // Clean up URL after window opens
        setTimeout(() => URL.revokeObjectURL(url), 1000);
      } else {
        throw new Error('Popup blocked');
      }
      return;
    } catch (error) {
      console.error('📁 [FRONTEND] New window fallback failed:', error);
    }

    // Method 4: Last resort - copy to clipboard
    try {
      console.log('📁 [FRONTEND] Using clipboard fallback...');
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(content);
        alert(`Download failed, but content has been copied to clipboard.\nFilename: ${filename}\nPlease paste into a text editor and save manually.`);
        console.log('📁 [FRONTEND] Content copied to clipboard as fallback');
        return;
      }
    } catch (error) {
      console.error('📁 [FRONTEND] Clipboard fallback failed:', error);
    }

    // All methods failed
    console.error('📁 [FRONTEND] All download methods failed!');
    alert(`Download failed! Please check browser settings and allow downloads from this site.\n\nTroubleshooting:\n1. Check if downloads are blocked\n2. Disable popup blocker\n3. Try different browser\n4. Content is available in browser console`);
    
    // Debug info to console
    console.log('📁 [FRONTEND] Content for manual copy:', content);
  }
} 