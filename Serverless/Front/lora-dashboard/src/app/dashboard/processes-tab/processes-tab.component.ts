import { Component, OnInit, OnDestroy } from '@angular/core';
import { interval, Subject } from 'rxjs';
import { takeUntil, switchMap } from 'rxjs/operators';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ApiService } from '../../core/api.service';
import { Process } from '../../core/models';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-processes-tab',
  templateUrl: './processes-tab.component.html',
  styleUrls: ['./processes-tab.component.scss']
})
export class ProcessesTabComponent implements OnInit, OnDestroy {
  processes: Process[] = [];
  isLoading = false;
  autoRefresh = true;
  private destroy$ = new Subject<void>();
  
  // 🚀 SERVERLESS INFO
  isRunPodServerless = environment.apiBaseUrl?.includes('api.runpod.ai') || false;
  showServerlessInfo = false;

  displayedColumns: string[] = [
    'name', 'type', 'status', 'progress', 'lora_info', 'gpu_id', 'elapsed_time', 'eta', 'actions'
  ];

  // 📁 BULK DOWNLOAD PROPERTIES
  selectedProcessIds: string[] = [];
  includeImages = true;
  includeLoras = true;
  isBulkDownloading = false;
  downloadItems: any[] = [];

  constructor(
    private apiService: ApiService,
    private snackBar: MatSnackBar
  ) { }

  ngOnInit(): void {
    this.loadProcesses();
    this.startAutoRefresh();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadProcesses(): void {
    if (this.isLoading) return;
    
    this.isLoading = true;
    this.apiService.getProcesses()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (processes) => {
          this.processes = processes.sort((a, b) => 
            new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
          );
          
          // 🚀 Show serverless info if no processes on RunPod
          this.showServerlessInfo = this.isRunPodServerless && processes.length === 0;
          
          // 🔍 Enhanced debugging for frontend
          if (this.isRunPodServerless) {
            console.log('🔍 [FRONTEND] Processes loaded:', {
              count: processes.length,
              showInfo: this.showServerlessInfo,
              serverless: this.isRunPodServerless,
              environment: environment.apiBaseUrl
            });
          }
          
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Failed to load processes:', error);
          this.snackBar.open('Failed to load processes: ' + error.message, 'Close', { duration: 5000 });
          this.isLoading = false;
        }
      });
  }

  startAutoRefresh(): void {
    if (this.autoRefresh) {
      interval(environment.autoRefreshInterval)
        .pipe(
          takeUntil(this.destroy$),
          switchMap(() => this.apiService.getProcesses())
        )
        .subscribe({
          next: (processes) => {
            this.processes = processes.sort((a, b) => 
              new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
            );
            // Update serverless info for auto-refresh too
            this.showServerlessInfo = this.isRunPodServerless && processes.length === 0;
          },
          error: (error) => {
            console.error('Auto-refresh failed:', error);
            // Don't show snackbar for auto-refresh failures to avoid spam
          }
        });
    }
  }

  toggleAutoRefresh(): void {
    this.autoRefresh = !this.autoRefresh;
    if (this.autoRefresh) {
      this.startAutoRefresh();
    }
  }

  getStatusColor(status: string): string {
    switch (status) {
      case 'running': return 'primary';
      case 'completed': return 'accent';
      case 'failed': return 'warn';
      case 'cancelled': return 'warn';
      default: return '';
    }
  }

  getProcessTypeIcon(type: string): string {
    return type === 'training' ? 'school' : 'image';
  }

  formatElapsedTime(seconds?: number): string {
    if (!seconds) return 'N/A';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${remainingSeconds}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${remainingSeconds}s`;
    } else {
      return `${remainingSeconds}s`;
    }
  }

  formatETA(seconds?: number): string {
    if (!seconds) return 'N/A';
    return this.formatElapsedTime(seconds);
  }

  canCancelProcess(process: Process): boolean {
    return process.status === 'pending' || process.status === 'running';
  }

  cancelProcess(process: Process): void {
    if (!this.canCancelProcess(process)) return;
    
    this.apiService.cancelProcess(process.id).subscribe({
      next: () => {
        this.snackBar.open(`Process "${process.name}" cancelled`, 'Close', { duration: 3000 });
        this.loadProcesses();
      },
      error: (error) => {
        this.snackBar.open('Failed to cancel process: ' + error.message, 'Close', { duration: 5000 });
      }
    });
  }

  downloadResults(process: Process): void {
    if (process.status !== 'completed') return;
    
    this.apiService.getDownloadUrl(process.id).subscribe({
      next: (downloadData) => {
        if (downloadData && downloadData.type === 'file_data') {
          // Handle base64 file download for RunPod Serverless
          this.downloadBase64File(downloadData.data, downloadData.filename, downloadData.content_type);
          this.snackBar.open(`Downloaded: ${downloadData.filename}`, 'Close', { duration: 3000 });
        } else if (typeof downloadData === 'string') {
          // Handle URL-based download for regular API
          window.open(downloadData, '_blank');
        } else {
          this.snackBar.open('No download available for this process', 'Close', { duration: 3000 });
        }
      },
      error: (error) => {
        this.snackBar.open('Failed to get download: ' + error.message, 'Close', { duration: 5000 });
      }
    });
  }

  /**
   * Download file from base64 data
   */
  downloadBase64File(base64Data: string, filename: string, contentType: string = 'application/octet-stream'): void {
    try {
      // Convert base64 to blob
      const byteCharacters = atob(base64Data);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: contentType });

      // Create download link
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.href = url;
      link.download = filename;
      
      // Trigger download
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
    } catch (error) {
      console.error('Error downloading file:', error);
      this.snackBar.open('Error downloading file', 'Close', { duration: 3000 });
    }
  }

  getProcessCountByStatus(status: string): number {
    return this.processes.filter(process => process.status === status).length;
  }

  getGroupedProcesses(): { type: string; processes: Process[] }[] {
    const groups = this.processes.reduce((acc, process) => {
      if (!acc[process.type]) {
        acc[process.type] = [];
      }
      acc[process.type].push(process);
      return acc;
    }, {} as { [key: string]: Process[] });

    return Object.keys(groups).map(type => ({
      type: type.charAt(0).toUpperCase() + type.slice(1),
      processes: groups[type]
    }));
  }

  /**
   * Get LoRA information for a process
   */
  getLoRAInfo(process: Process): { type: string; value: string; copyable?: boolean } | null {
    if (!process.config?.config?.process?.[0]) {
      return null;
    }

    const processConfig = process.config.config.process[0];

    // For generation processes, show LoRA path
    if (process.type === 'generation' && processConfig.model?.lora_path) {
      return {
        type: 'LoRA Path',
        value: processConfig.model.lora_path,
        copyable: true
      };
    }

    // For training processes, show trigger word
    if (process.type === 'training' && processConfig.trigger_word) {
      return {
        type: 'Trigger Word',
        value: processConfig.trigger_word,
        copyable: false
      };
    }

    return null;
  }

  /**
   * Copy text to clipboard
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

  // 📁 BULK DOWNLOAD METHODS

  /**
   * Get completed processes
   */
  getCompletedProcesses(): Process[] {
    return this.processes.filter(p => p.status === 'completed');
  }

  /**
   * Check if process is selected
   */
  isProcessSelected(processId: string): boolean {
    return this.selectedProcessIds.includes(processId);
  }

  /**
   * Toggle process selection
   */
  toggleProcessSelection(processId: string): void {
    const index = this.selectedProcessIds.indexOf(processId);
    if (index > -1) {
      this.selectedProcessIds.splice(index, 1);
    } else {
      this.selectedProcessIds.push(processId);
    }
  }

  /**
   * Select all completed processes
   */
  selectAllCompleted(): void {
    this.selectedProcessIds = this.getCompletedProcesses().map(p => p.id);
  }

  /**
   * Clear selection
   */
  clearSelection(): void {
    this.selectedProcessIds = [];
  }

  /**
   * Check if all completed processes are selected
   */
  allCompletedSelected(): boolean {
    const completed = this.getCompletedProcesses();
    return completed.length > 0 && completed.every(p => this.isProcessSelected(p.id));
  }

  /**
   * Generate bulk download URLs
   */
  generateBulkDownloadUrls(): void {
    if (this.selectedProcessIds.length === 0) {
      this.snackBar.open('Please select at least one process', 'Close', {
        duration: 3000,
        panelClass: ['error-snackbar']
      });
      return;
    }

    if (!this.includeImages && !this.includeLoras) {
      this.snackBar.open('Please select at least one download option', 'Close', {
        duration: 3000,
        panelClass: ['error-snackbar']
      });
      return;
    }

    this.isBulkDownloading = true;

    const request = {
      process_ids: this.selectedProcessIds,
      include_images: this.includeImages,
      include_loras: this.includeLoras
    };

    this.apiService.getBulkDownloadUrls(request).subscribe({
      next: (response) => {
        this.downloadItems = response.download_items;
        this.snackBar.open(
          `Generated ${response.total_files} download links (${this.formatFileSize(response.total_size)})`,
          'Close',
          { duration: 5000, panelClass: ['success-snackbar'] }
        );
        this.isBulkDownloading = false;
      },
      error: (error) => {
        console.error('Failed to generate download URLs:', error);
        this.snackBar.open(
          'Failed to generate download URLs: ' + (error.message || 'Unknown error'),
          'Close',
          { duration: 5000, panelClass: ['error-snackbar'] }
        );
        this.isBulkDownloading = false;
      }
    });
  }

  /**
   * Get download items by type
   */
  getDownloadItemsByType(type: string): any[] {
    return this.downloadItems.filter(item => item.type === type);
  }

  /**
   * Get total download size
   */
  getTotalDownloadSize(): number {
    return this.downloadItems.reduce((sum, item) => sum + (item.size || 0), 0);
  }

  /**
   * Get download item icon class
   */
  getDownloadItemIcon(type: string): string {
    switch (type) {
      case 'image': return 'text-blue-600';
      case 'lora': return 'text-purple-600';
      default: return 'text-gray-600';
    }
  }

  /**
   * Download individual file
   */
  downloadFile(item: any): void {
    if (item.data) {
      // Handle base64 download for RunPod Serverless
      this.downloadBase64File(item.data, item.filename, item.content_type);
    } else if (item.url) {
      // Handle URL-based download for regular API
      window.open(item.url, '_blank');
    }
  }

  /**
   * Copy download URL to clipboard
   */
  copyDownloadUrl(item: any): void {
    if (item.url && navigator.clipboard) {
      navigator.clipboard.writeText(item.url).then(() => {
        this.snackBar.open('Download URL copied to clipboard', 'Close', {
          duration: 2000,
          panelClass: ['success-snackbar']
        });
      }).catch(() => {
        this.snackBar.open('Failed to copy URL', 'Close', {
          duration: 3000,
          panelClass: ['error-snackbar']
        });
      });
    } else if (item.data) {
      // For base64 files, we can't copy a URL but we can notify about the alternative
      this.snackBar.open('File will be downloaded directly (no URL available)', 'Close', {
        duration: 3000,
        panelClass: ['info-snackbar']
      });
    }
  }

  /**
   * Download all files
   */
  downloadAllFiles(): void {
    if (this.downloadItems.length === 0) return;

    // Ask for confirmation for many files
    if (this.downloadItems.length > 10) {
      const confirmed = confirm(`This will download ${this.downloadItems.length} files. Continue?`);
      if (!confirmed) return;
    }

    // Download all files
    this.downloadItems.forEach((item, index) => {
      // Add small delay between downloads to avoid browser blocking
      setTimeout(() => {
        if (item.data) {
          // Handle base64 download for RunPod Serverless
          this.downloadBase64File(item.data, item.filename, item.content_type);
        } else if (item.url) {
          // Handle URL-based download for regular API
          window.open(item.url, '_blank');
        }
      }, index * 200); // Increased delay for base64 processing
    });

    this.snackBar.open(
      `Initiated download for ${this.downloadItems.length} files`,
      'Close',
      { duration: 3000, panelClass: ['success-snackbar'] }
    );
  }

  /**
   * Clear download items
   */
  clearDownloadItems(): void {
    this.downloadItems = [];
  }

  /**
   * Format date for display
   */
  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString();
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
}
