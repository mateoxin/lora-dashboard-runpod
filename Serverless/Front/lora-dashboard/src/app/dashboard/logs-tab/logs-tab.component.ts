import { Component, OnInit, OnDestroy } from '@angular/core';
import { interval, Subject } from 'rxjs';
import { takeUntil, switchMap } from 'rxjs/operators';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ApiService } from '../../core/api.service';
import { FrontendLoggerService } from '../../core/frontend-logger.service';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-logs-tab',
  templateUrl: './logs-tab.component.html',
  styleUrls: ['./logs-tab.component.scss']
})
export class LogsTabComponent implements OnInit, OnDestroy {
  // Backend logs
  backendLogs: string[] = [];
  logStats: any = null;
  selectedLogType = 'app';
  logTypes = [
    { value: 'app', label: 'Application Logs' },
    { value: 'requests', label: 'Request Logs' },
    { value: 'errors', label: 'Error Logs' },
    { value: 'system', label: 'System Logs' }
  ];

  // Frontend logs
  frontendLogs: any[] = [];
  
  // UI state
  isLoadingBackend = false;
  isLoadingFrontend = false;
  autoRefresh = false;
  maxLines = 100;
  showFullContent = false;
  searchTerm = '';
  filteredBackendLogs: string[] = [];
  filteredFrontendLogs: any[] = [];
  showFrontendAsText = true; // Show frontend logs in readable text format
  
  private destroy$ = new Subject<void>();

  constructor(
    private apiService: ApiService,
    private frontendLogger: FrontendLoggerService,
    private snackBar: MatSnackBar
  ) { }

  ngOnInit(): void {
    this.loadBackendLogs();
    this.loadBackendLogStats();
    this.loadFrontendLogs();
    this.updateFilteredLogs();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Load backend logs
   */
  loadBackendLogs(): void {
    if (this.isLoadingBackend) return;
    
    this.isLoadingBackend = true;
    // Use -1 for unlimited lines when showFullContent is true
    const linesToLoad = this.showFullContent ? -1 : this.maxLines;
    this.apiService.getBackendLogs(this.selectedLogType, linesToLoad)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          if (response.lines) {
            this.backendLogs = response.lines;
          } else if (response.message) {
            // For RunPod endpoints where logs are not directly accessible
            this.backendLogs = [response.message];
          }
          this.updateFilteredLogs();
          this.isLoadingBackend = false;
        },
        error: (error) => {
          console.error('Failed to load backend logs:', error);
          this.snackBar.open('Failed to load backend logs: ' + error.message, 'Close', { duration: 5000 });
          this.isLoadingBackend = false;
        }
      });
  }

  /**
   * Load backend log statistics
   */
  loadBackendLogStats(): void {
    this.apiService.getLogStats()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (stats) => {
          this.logStats = stats;
        },
        error: (error) => {
          console.error('Failed to load log stats:', error);
        }
      });
  }

  /**
   * Load frontend logs from logger service
   */
  loadFrontendLogs(): void {
    this.isLoadingFrontend = true;
    try {
      // Enable full content mode for frontend logs when showFullContent is true
      this.frontendLogger.setDataTruncation(!this.showFullContent);
      if (this.showFullContent) {
        this.frontendLogger.setMaxLogs(10000); // Higher limit for full content
      } else {
        this.frontendLogger.setMaxLogs(1000); // Normal limit
      }
      
      this.frontendLogs = this.frontendLogger.getLogs();
      
      // DEBUG: Log frontend logs loading
      console.log('🔍 [DEBUG] Frontend logs loaded:', {
        count: this.frontendLogs.length,
        logs: this.frontendLogs.slice(0, 3), // Show first 3 logs
        loggerStats: this.frontendLogger.getLogStats(),
        fileLoggingEnabled: this.frontendLogger.isFileLoggingEnabled(),
        automaticLogging: 'HTTP Interceptor active - ALL requests/responses logged automatically'
      });
      
      // If no logs, try to generate a test log
      if (this.frontendLogs.length === 0) {
        console.log('⚠️ [DEBUG] No frontend logs found, generating test log...');
        this.frontendLogger.logRequest('/debug/test', 'GET', { test: true });
        this.frontendLogs = this.frontendLogger.getLogs();
        console.log('🔍 [DEBUG] After test log generation:', this.frontendLogs.length);
      }
      
      this.updateFilteredLogs();
      this.isLoadingFrontend = false;
    } catch (error) {
      console.error('Failed to load frontend logs:', error);
      this.isLoadingFrontend = false;
    }
  }

  /**
   * Change log type and reload
   */
  onLogTypeChange(): void {
    this.loadBackendLogs();
  }

  /**
   * Change max lines and reload
   */
  onMaxLinesChange(): void {
    this.loadBackendLogs();
  }

  /**
   * Toggle show full content
   */
  toggleFullContent(): void {
    this.showFullContent = !this.showFullContent;
    this.loadBackendLogs();
    this.loadFrontendLogs(); // Also reload frontend logs with new settings
  }

  /**
   * Handle search term change
   */
  onSearchChange(): void {
    this.updateFilteredLogs();
  }

  /**
   * Clear search term
   */
  clearSearch(): void {
    this.searchTerm = '';
    this.updateFilteredLogs();
  }

  /**
   * Update filtered logs based on search term
   */
  updateFilteredLogs(): void {
    if (!this.searchTerm) {
      this.filteredBackendLogs = [...this.backendLogs];
      this.filteredFrontendLogs = [...this.frontendLogs];
    } else {
      const searchLower = this.searchTerm.toLowerCase();
      
      // Filter backend logs
      this.filteredBackendLogs = this.backendLogs.filter(log => 
        log.toLowerCase().includes(searchLower)
      );
      
      // Filter frontend logs
      this.filteredFrontendLogs = this.frontendLogs.filter(log => {
        const logStr = JSON.stringify(log).toLowerCase();
        return logStr.includes(searchLower);
      });
    }
  }

  /**
   * Toggle auto refresh
   */
  toggleAutoRefresh(): void {
    this.autoRefresh = !this.autoRefresh;
    if (this.autoRefresh) {
      this.startAutoRefresh();
    }
  }

  /**
   * Start auto refresh for logs
   */
  startAutoRefresh(): void {
    if (this.autoRefresh) {
      interval(environment.autoRefreshInterval)
        .pipe(
          takeUntil(this.destroy$),
          switchMap(() => this.apiService.getBackendLogs(this.selectedLogType, this.maxLines))
        )
        .subscribe({
          next: (response) => {
            if (response.lines) {
              this.backendLogs = response.lines;
            }
            // Also refresh frontend logs
            this.loadFrontendLogs();
          },
          error: (error) => {
            console.error('Auto-refresh failed:', error);
          }
        });
    }
  }

  /**
   * Download backend logs as file
   */
  downloadBackendLogs(): void {
    if (this.backendLogs.length === 0) {
      this.snackBar.open('No backend logs to download', 'Close', { duration: 3000 });
      return;
    }

    const content = this.backendLogs.join('\n');
    const blob = new Blob([content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `backend-logs-${this.selectedLogType}-${new Date().toISOString().slice(0, 19).replace(/[:.]/g, '-')}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

    this.snackBar.open('Backend logs downloaded', 'Close', { duration: 3000 });
  }

  /**
   * Download frontend logs as file
   */
  downloadFrontendLogs(): void {
    if (this.frontendLogs.length === 0) {
      this.snackBar.open('No frontend logs to download', 'Close', { duration: 3000 });
      return;
    }

    try {
      console.log('📁 [LOGS-TAB] Starting frontend logs download...', {
        logsCount: this.frontendLogs.length,
        browser: navigator.userAgent
      });

      // Use the enhanced logger service download method
      this.frontendLogger.downloadLogs();
      this.snackBar.open('Frontend logs downloaded', 'Close', { duration: 3000 });
    } catch (error) {
      console.error('📁 [LOGS-TAB] Frontend download failed:', error);
      const errorMessage = error instanceof Error ? error.message : String(error);
      this.snackBar.open('Download failed: ' + errorMessage, 'Close', { duration: 5000 });
    }
  }

  /**
   * Download all logs as combined file
   */
  downloadAllLogs(): void {
    const backendContent = this.backendLogs.join('\n');
    const frontendContent = JSON.stringify(this.frontendLogs, null, 2);
    
    const combined = `=== BACKEND LOGS (${this.selectedLogType}) ===\n\n${backendContent}\n\n=== FRONTEND LOGS ===\n\n${frontendContent}`;
    
    const blob = new Blob([combined], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `all-logs-${new Date().toISOString().slice(0, 19).replace(/[:.]/g, '-')}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

    this.snackBar.open('All logs downloaded', 'Close', { duration: 3000 });
  }

  /**
   * Clear frontend logs
   */
  clearFrontendLogs(): void {
    try {
      this.frontendLogger.clearLogs();
      this.loadFrontendLogs();
      this.snackBar.open('Frontend logs and text buffer cleared', 'Close', { duration: 3000 });
    } catch (error) {
      this.snackBar.open('Failed to clear frontend logs', 'Close', { duration: 3000 });
    }
  }

  /**
   * Download current text buffer before clearing
   */
  downloadCurrentBuffer(): void {
    try {
      this.frontendLogger.downloadCurrentTextBuffer();
      this.snackBar.open('Text buffer downloaded', 'Close', { duration: 3000 });
    } catch (error) {
      this.snackBar.open('Failed to download text buffer', 'Close', { duration: 3000 });
    }
  }

  /**
   * Clear backend logs
   */
  clearBackendLogs(): void {
    if (this.isLoadingBackend) return;
    
    this.isLoadingBackend = true;
    this.apiService.clearBackendLogs(this.selectedLogType)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          this.backendLogs = []; // Clear the displayed logs immediately
          this.snackBar.open(`${this.selectedLogType} logs cleared successfully`, 'Close', { 
            duration: 3000,
            panelClass: ['success-snackbar']
          });
          this.isLoadingBackend = false;
          // Refresh to confirm clearing
          this.loadBackendLogs();
        },
        error: (error) => {
          console.error('Failed to clear backend logs:', error);
          this.snackBar.open(`Failed to clear ${this.selectedLogType} logs: ${error.message}`, 'Close', { 
            duration: 5000,
            panelClass: ['error-snackbar']
          });
          this.isLoadingBackend = false;
        }
      });
  }

  /**
   * Generate test frontend logs for debugging
   */
  generateTestLogs(): void {
    const testLogs = [
      { method: 'GET', endpoint: '/health', data: { test: 'health check' } },
      { method: 'POST', endpoint: '/api/test', data: { message: 'test log entry' } },
      { method: 'GET', endpoint: '/processes', data: { filter: 'active' } }
    ];

    testLogs.forEach((log, index) => {
      setTimeout(() => {
        this.frontendLogger.logRequest(log.endpoint, log.method, log.data);
        if (index === 0) {
          // Simulate a response for the first log
          setTimeout(() => {
            this.frontendLogger.logResponse('test-id', log.endpoint, { success: true }, 200, 250);
          }, 100);
        }
      }, index * 100);
    });

    // Add a file operation log
    setTimeout(() => {
      this.frontendLogger.logFileOperation('upload', [new File(['test'], 'test.txt')]);
    }, 400);

    setTimeout(() => {
      this.loadFrontendLogs();
      this.snackBar.open('Test logs generated successfully!', 'Close', { 
        duration: 3000,
        panelClass: ['success-snackbar']
      });
    }, 600);
  }

  /**
   * Get log level color class
   */
  getLogLevelColor(logLine: string): string {
    if (logLine.includes('ERROR') || logLine.includes('CRITICAL')) {
      return 'text-red-600';
    } else if (logLine.includes('WARNING') || logLine.includes('WARN')) {
      return 'text-yellow-600';
    } else if (logLine.includes('INFO')) {
      return 'text-blue-600';
    } else if (logLine.includes('DEBUG')) {
      return 'text-gray-600';
    }
    return 'text-gray-800';
  }

  /**
   * Get frontend log level color
   */
  getFrontendLogLevelColor(logEntry: any): string {
    switch (logEntry.level?.toLowerCase()) {
      case 'error':
        return 'text-red-600';
      case 'warn':
      case 'warning':
        return 'text-yellow-600';
      case 'info':
        return 'text-blue-600';
      case 'debug':
        return 'text-gray-600';
      default:
        return 'text-gray-800';
    }
  }

  /**
   * Format timestamp for display
   */
  formatTimestamp(timestamp: string | number): string {
    const date = new Date(timestamp);
    return date.toLocaleString();
  }

  /**
   * Copy log entry to clipboard
   */
  copyToClipboard(text: string): void {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text).then(() => {
        this.snackBar.open('Copied to clipboard', 'Close', {
          duration: 2000,
          panelClass: ['success-snackbar']
        });
      }).catch(() => {
        this.snackBar.open('Failed to copy to clipboard', 'Close', {
          duration: 3000,
          panelClass: ['error-snackbar']
        });
      });
    }
  }

  /**
   * Track by function for backend logs
   */
  trackByIndex(index: number, item: string): number {
    return index;
  }

  /**
   * Track by function for frontend logs
   */
  trackByLogEntry(index: number, item: any): string {
    return item.timestamp + item.requestId;
  }

  /**
   * Format file size for display
   */
  formatFileSize(bytes: number): string {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  }

  /**
   * Convert object to JSON string for template use
   */
  toJsonString(obj: any): string {
    return JSON.stringify(obj, null, 2);
  }

  /**
   * Format frontend log entry as readable text
   */
  formatFrontendLogAsText(logEntry: any): string {
    const timestamp = new Date(logEntry.timestamp).toLocaleString();
    const level = (logEntry.level || 'INFO').padEnd(5);
    const type = logEntry.type?.padEnd(12) || 'LOG'.padEnd(12);
    
    let line = `[${timestamp}] ${level} ${type}`;
    
    if (logEntry.requestId) {
      line += ` ID:${logEntry.requestId}`;
    }
    
    // Add method and endpoint for API calls
    if (logEntry.method && logEntry.endpoint) {
      line += ` ${logEntry.method} ${logEntry.endpoint}`;
    }
    
    // Add duration for responses
    if (logEntry.duration) {
      line += ` (${logEntry.duration}ms)`;
    }
    
    // Add main message or data
    if (logEntry.type === 'REQUEST') {
      line += ` | Request sent`;
      if (logEntry.data && typeof logEntry.data === 'object') {
        const dataKeys = Object.keys(logEntry.data).filter(key => !['endpoint', 'method'].includes(key));
        if (dataKeys.length > 0) {
          line += ` | Params: {${dataKeys.join(', ')}}`;
        }
      }
    } else if (logEntry.type === 'RESPONSE') {
      line += ` | Response received`;
      if (logEntry.data) {
        if (logEntry.data.success !== undefined) {
          line += ` | Success: ${logEntry.data.success}`;
        }
        if (logEntry.data.message) {
          line += ` | ${logEntry.data.message}`;
        }
        if (logEntry.data.processes && Array.isArray(logEntry.data.processes)) {
          line += ` | Processes: ${logEntry.data.processes.length}`;
        }
        if (logEntry.data.models && Array.isArray(logEntry.data.models)) {
          line += ` | Models: ${logEntry.data.models.length}`;
        }
        if (logEntry.data.count !== undefined) {
          line += ` | Count: ${logEntry.data.count}`;
        }
      }
    } else if (logEntry.type === 'ERROR') {
      line += ` | ERROR`;
      if (logEntry.error) {
        const errorMsg = typeof logEntry.error === 'string' ? 
          logEntry.error : 
          logEntry.error.message || JSON.stringify(logEntry.error);
        line += `: ${errorMsg}`;
      }
    } else if (logEntry.type === 'FILE_OPERATION') {
      line += ` | File operation`;
      if (logEntry.data?.operation) {
        line += `: ${logEntry.data.operation}`;
      }
      if (logEntry.data?.files?.length) {
        line += ` | Files: ${logEntry.data.files.length}`;
        const fileNames = logEntry.data.files.map((f: any) => f.name).slice(0, 3);
        if (fileNames.length > 0) {
          line += ` (${fileNames.join(', ')}${logEntry.data.files.length > 3 ? '...' : ''})`;
        }
        // Add total size info
        const totalSize = logEntry.data.files.reduce((sum: number, f: any) => sum + (f.size || 0), 0);
        if (totalSize > 0) {
          line += ` | Size: ${this.formatFileSize(totalSize)}`;
        }
      }
    }
    
    return line;
  }

  /**
   * Toggle frontend logs display format
   */
  toggleFrontendFormat(): void {
    this.showFrontendAsText = !this.showFrontendAsText;
  }
}