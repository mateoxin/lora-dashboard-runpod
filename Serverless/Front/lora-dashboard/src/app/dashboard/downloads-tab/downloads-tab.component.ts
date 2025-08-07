import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subject, takeUntil } from 'rxjs';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ApiService } from '../../core/api.service';
import { LoRAModel, Process, DownloadItem } from '../../core/models';

export interface GeneratedFile {
  id: string;
  filename: string;
  path: string;
  type: 'lora' | 'image' | 'other';
  size: number;
  size_formatted: string;
  created_at: string;
  process_id?: string;
  downloadable: boolean;
}

@Component({
  selector: 'app-downloads-tab',
  templateUrl: './downloads-tab.component.html',
  styleUrls: ['./downloads-tab.component.scss']
})
export class DownloadsTabComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();

  loraFiles: GeneratedFile[] = [];
  imageFiles: GeneratedFile[] = [];
  allFiles: GeneratedFile[] = [];
  
  isLoading = false;
  autoRefresh = false;
  private refreshInterval: any;
  
  selectedFiles: Set<string> = new Set();
  isDownloading = false;
  
  // Filter options
  filterType: 'all' | 'lora' | 'images' = 'all';
  sortBy: 'name' | 'date' | 'size' = 'date';
  sortOrder: 'asc' | 'desc' = 'desc';

  constructor(
    private apiService: ApiService,
    private snackBar: MatSnackBar
  ) { }

  ngOnInit(): void {
    this.loadFiles();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  }

  /**
   * Load all generated files (LoRAs and images)
   */
  loadFiles(): void {
    this.isLoading = true;
    
    // Try the new dedicated files endpoint first, then fallback to individual endpoints
    this.apiService.listGeneratedFiles()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (fileData) => {
          if (fileData.error) {
            // Fallback to legacy method if new endpoint fails
            this.loadFilesLegacy();
            return;
          }
          
          const files: GeneratedFile[] = [];
          
          // Add LoRA files from new endpoint
          if (fileData.lora_files && Array.isArray(fileData.lora_files)) {
            fileData.lora_files.forEach((lora: any) => {
              files.push({
                id: lora.id || lora.filename?.replace('.safetensors', '') || `lora_${Date.now()}`,
                filename: lora.filename || lora.name + '.safetensors',
                path: lora.path,
                type: 'lora',
                size: lora.size || 0,
                size_formatted: lora.size_formatted || this.formatFileSize(lora.size || 0),
                created_at: lora.created_at || new Date().toISOString(),
                downloadable: true
              });
            });
          }
          
          // Add image files from new endpoint
          if (fileData.image_files && Array.isArray(fileData.image_files)) {
            fileData.image_files.forEach((image: any) => {
              files.push({
                id: image.id || `img_${Date.now()}_${Math.random()}`,
                filename: image.filename,
                path: image.path,
                type: 'image',
                size: image.size || 0,
                size_formatted: image.size_formatted || this.formatFileSize(image.size || 0),
                created_at: image.created_at || new Date().toISOString(),
                process_id: image.process_id,
                downloadable: true
              });
            });
          }
          
          this.allFiles = files;
          this.filterAndSortFiles();
          this.isLoading = false;
        },
        error: (error) => {
          console.warn('New files endpoint failed, trying legacy method:', error);
          // Fallback to legacy method
          this.loadFilesLegacy();
        }
      });
  }

  /**
   * Legacy method to load files from individual endpoints
   */
  private loadFilesLegacy(): void {
    // Load LoRA models and processes to get generated files
    Promise.all([
      this.apiService.getLoRAModels().toPromise(),
      this.apiService.getProcesses().toPromise()
    ]).then(([loraModels, processes]) => {
      const files: GeneratedFile[] = [];
      
      // Add LoRA files
      if (loraModels) {
        loraModels.forEach((lora: LoRAModel) => {
          files.push({
            id: lora.id,
            filename: lora.name + '.safetensors',
            path: lora.path,
            type: 'lora',
            size: lora.size || 0,
            size_formatted: this.formatFileSize(lora.size || 0),
            created_at: lora.created_at,
            downloadable: true
          });
        });
      }
      
      // Add generated images from completed processes
      if (processes) {
        processes
          .filter((process: Process) => process.status === 'completed' && process.type === 'generation')
          .forEach((process: Process) => {
            if (process.output_path) {
              // Add images based on process output
              files.push({
                id: `img_${process.id}`,
                filename: `generated_${process.id}.png`,
                path: process.output_path,
                type: 'image',
                size: 0, // Will be updated when we get actual file info
                size_formatted: 'Unknown',
                created_at: process.updated_at,
                process_id: process.id,
                downloadable: true
              });
            }
          });
      }
      
      this.allFiles = files;
      this.filterAndSortFiles();
      this.isLoading = false;
    }).catch((error) => {
      console.error('Error loading files:', error);
      this.snackBar.open('Failed to load files', 'Close', { duration: 3000 });
      this.isLoading = false;
    });
  }

  /**
   * Filter and sort files based on current settings
   */
  filterAndSortFiles(): void {
    let filtered = [...this.allFiles];
    
    // Apply type filter
    if (this.filterType !== 'all') {
      filtered = filtered.filter(file => {
        if (this.filterType === 'lora') return file.type === 'lora';
        if (this.filterType === 'images') return file.type === 'image';
        return true;
      });
    }
    
    // Apply sorting
    filtered.sort((a, b) => {
      let comparison = 0;
      
      switch (this.sortBy) {
        case 'name':
          comparison = a.filename.localeCompare(b.filename);
          break;
        case 'date':
          comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
          break;
        case 'size':
          comparison = a.size - b.size;
          break;
      }
      
      return this.sortOrder === 'desc' ? -comparison : comparison;
    });
    
    // Update filtered arrays
    this.loraFiles = filtered.filter(f => f.type === 'lora');
    this.imageFiles = filtered.filter(f => f.type === 'image');
  }

  /**
   * Toggle auto refresh
   */
  toggleAutoRefresh(): void {
    if (this.autoRefresh) {
      this.refreshInterval = setInterval(() => {
        this.loadFiles();
      }, 10000); // Refresh every 10 seconds
    } else {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval);
      }
    }
  }

  /**
   * Toggle file selection
   */
  toggleFileSelection(fileId: string): void {
    if (this.selectedFiles.has(fileId)) {
      this.selectedFiles.delete(fileId);
    } else {
      this.selectedFiles.add(fileId);
    }
  }

  /**
   * Select all visible files
   */
  selectAllFiles(): void {
    const allVisibleIds = [
      ...this.loraFiles.map(f => f.id),
      ...this.imageFiles.map(f => f.id)
    ];
    allVisibleIds.forEach(id => this.selectedFiles.add(id));
  }

  /**
   * Clear all selections
   */
  clearSelection(): void {
    this.selectedFiles.clear();
  }

  /**
   * Download single file
   */
  downloadFile(file: GeneratedFile): void {
    if (!file.downloadable) {
      this.snackBar.open('File not available for download', 'Close', { duration: 3000 });
      return;
    }

    this.isDownloading = true;
    
    if (file.process_id) {
      // For process-based files, use process download
      this.apiService.getDownloadUrl(file.process_id)
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: (downloadData) => {
            if (downloadData && downloadData.data) {
              this.triggerFileDownload(downloadData.data, file.filename, downloadData.content_type);
              this.snackBar.open(`Downloaded: ${file.filename}`, 'Close', { duration: 3000 });
            } else {
              this.snackBar.open('Download URL not available', 'Close', { duration: 3000 });
            }
            this.isDownloading = false;
          },
          error: (error) => {
            console.error('Download error:', error);
            this.snackBar.open('Download failed', 'Close', { duration: 3000 });
            this.isDownloading = false;
          }
        });
    } else {
      // For direct files (LoRAs), use direct file download
      this.apiService.downloadFileDirect(file.path)
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: (downloadData) => {
            if (downloadData && downloadData.data) {
              this.triggerFileDownload(downloadData.data, file.filename, downloadData.content_type);
              this.snackBar.open(`Downloaded: ${file.filename}`, 'Close', { duration: 3000 });
            } else {
              this.snackBar.open('Download data not available', 'Close', { duration: 3000 });
            }
            this.isDownloading = false;
          },
          error: (error) => {
            console.error('Direct download error:', error);
            this.snackBar.open('Download failed', 'Close', { duration: 3000 });
            this.isDownloading = false;
          }
        });
    }
  }

  /**
   * Download selected files as bulk
   */
  downloadSelectedFiles(): void {
    if (this.selectedFiles.size === 0) {
      this.snackBar.open('No files selected', 'Close', { duration: 3000 });
      return;
    }

    this.isDownloading = true;
    
    const selectedProcessIds = this.allFiles
      .filter(f => this.selectedFiles.has(f.id) && f.process_id)
      .map(f => f.process_id!);
    
    if (selectedProcessIds.length > 0) {
      const bulkRequest = {
        process_ids: selectedProcessIds,
        include_images: true,
        include_loras: true
      };
      
      this.apiService.getBulkDownloadUrls(bulkRequest)
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: (response) => {
            if (response.zip_url) {
              // Download zip file
              window.open(response.zip_url, '_blank');
              this.snackBar.open(`Downloading ${response.total_files} files`, 'Close', { duration: 3000 });
            } else if (response.download_items && response.download_items.length > 0) {
              // Download individual files
              response.download_items.forEach((item: DownloadItem) => {
                window.open(item.url, '_blank');
              });
              this.snackBar.open(`Downloading ${response.download_items.length} files`, 'Close', { duration: 3000 });
            }
            this.isDownloading = false;
            this.clearSelection();
          },
          error: (error) => {
            console.error('Bulk download error:', error);
            this.snackBar.open('Bulk download failed', 'Close', { duration: 3000 });
            this.isDownloading = false;
          }
        });
    } else {
      this.snackBar.open('No downloadable files selected', 'Close', { duration: 3000 });
      this.isDownloading = false;
    }
  }

  /**
   * Trigger file download from base64 data
   */
  private triggerFileDownload(base64Data: string, filename: string, contentType: string = 'application/octet-stream'): void {
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
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading file:', error);
      this.snackBar.open('Download failed', 'Close', { duration: 3000 });
    }
  }

  /**
   * Format file size for display
   */
  private formatFileSize(bytes: number): string {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  }

  /**
   * Get file type icon
   */
  getFileIcon(file: GeneratedFile): string {
    switch (file.type) {
      case 'lora': return 'memory';
      case 'image': return 'image';
      default: return 'insert_drive_file';
    }
  }

  /**
   * Get file type color
   */
  getFileTypeColor(file: GeneratedFile): string {
    switch (file.type) {
      case 'lora': return 'text-purple-600';
      case 'image': return 'text-green-600';
      default: return 'text-gray-600';
    }
  }

  /**
   * Copy file path to clipboard
   */
  copyPath(file: GeneratedFile): void {
    navigator.clipboard.writeText(file.path).then(() => {
      this.snackBar.open('Path copied to clipboard', 'Close', { duration: 2000 });
    }).catch(err => {
      console.error('Failed to copy path:', err);
      this.snackBar.open('Failed to copy path', 'Close', { duration: 3000 });
    });
  }
}
