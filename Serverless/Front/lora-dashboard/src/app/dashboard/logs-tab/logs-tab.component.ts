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
    this.apiService.getBackendLogs(this.selectedLogType, this.maxLines)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          if (response.lines) {
            this.backendLogs = response.lines;
          } else if (response.message) {
            // For RunPod endpoints where logs are not directly accessible
            this.backendLogs = [response.message];
          }
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
      this.frontendLogs = this.frontendLogger.getLogs();
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

    const content = JSON.stringify(this.frontendLogs, null, 2);
    const blob = new Blob([content], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `frontend-logs-${new Date().toISOString().slice(0, 19).replace(/[:.]/g, '-')}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

    this.snackBar.open('Frontend logs downloaded', 'Close', { duration: 3000 });
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
      this.snackBar.open('Frontend logs cleared', 'Close', { duration: 3000 });
    } catch (error) {
      this.snackBar.open('Failed to clear frontend logs', 'Close', { duration: 3000 });
    }
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
}