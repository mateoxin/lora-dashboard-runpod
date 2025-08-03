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
  private maxLogs = 1000;
  private logToConsole = true;
  private logToStorage = true;
  private storageKey = 'lora_dashboard_logs';

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
    console.log('🧹 [FRONTEND] Logs cleared');
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
    const dataStr = this.exportLogs();
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `lora_dashboard_logs_${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    
    URL.revokeObjectURL(url);
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
        
        // Truncate large content
        if (typeof value === 'string' && value.length > 500) {
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
} 