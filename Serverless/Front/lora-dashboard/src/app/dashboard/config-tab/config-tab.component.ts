import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { MatSnackBar } from '@angular/material/snack-bar';
import * as yaml from 'js-yaml';
import { ApiService } from '../../core/api.service';
import { AuthService } from '../../auth/auth.service';
import { TrainRequest, TrainingDataUploadRequest } from '../../core/models';
import { FrontendLoggerService } from '../../core/frontend-logger.service';

@Component({
  selector: 'app-config-tab',
  templateUrl: './config-tab.component.html',
  styleUrls: ['./config-tab.component.scss']
})
export class ConfigTabComponent implements OnInit {
  editorContent = '';
  selectedTemplate = 'training';
  isLoading = false;
  isStarting = false;

  templates = [
    { value: 'training', label: 'Conservative Training', file: 'training_conservative.yaml' }
  ];

  // 📁 FILE UPLOAD PROPERTIES
  trainingName = '';
  uploadedFiles: File[] = [];
  isDragOver = false;
  isUploading = false;
  cleanupExisting = true;

  // 📝 LOGS PROPERTIES
  isDownloadingLogs = false;
  isLoadingStats = false;
  logStats: any = null;

  constructor(
    private http: HttpClient,
    private snackBar: MatSnackBar,
    private apiService: ApiService,
    private authService: AuthService,
    public frontendLogger: FrontendLoggerService  // Changed to public for template access
  ) { }

  ngOnInit(): void {
    this.loadTemplate();
  }

  onTemplateChange(): void {
    this.loadTemplate();
  }

  loadTemplate(): void {
    this.isLoading = true;
    const template = this.templates.find(t => t.value === this.selectedTemplate);
    
    if (template) {
      const templateUrl = `assets/templates/${template.file}`;
      console.log('Loading template from:', templateUrl);
      
      this.http.get(templateUrl, { responseType: 'text' })
        .subscribe({
          next: (content) => {
            console.log('Template loaded successfully, content length:', content.length);
            this.editorContent = content;
            this.isLoading = false;
          },
          error: (error) => {
            console.error('Failed to load template:', error);
            console.error('Template URL:', templateUrl);
            this.snackBar.open(`Failed to load template: ${template.label}`, 'Close', { duration: 3000 });
            // Set default content to show something is working
            this.editorContent = `# ${template.label} Template\n# Template file not found or failed to load\n# Please check console for details\n\njob: ${this.selectedTemplate}\nconfig:\n  name: "example_${this.selectedTemplate}"\n  # Add your configuration here`;
            this.isLoading = false;
          }
        });
    } else {
      this.isLoading = false;
      this.snackBar.open('Template not found', 'Close', { duration: 3000 });
    }
  }

  validateYAML(): boolean {
    try {
      yaml.load(this.editorContent);
      return true;
    } catch (error) {
      console.error('YAML validation error:', error);
      return false;
    }
  }

  onContentChange(content: string): void {
    this.editorContent = content;
  }

  formatYAML(): void {
    try {
      const parsed = yaml.load(this.editorContent);
      this.editorContent = yaml.dump(parsed, { 
        indent: 2,
        lineWidth: 120,
        noRefs: true
      });
      this.snackBar.open('YAML formatted successfully', 'Close', { duration: 2000 });
    } catch (error) {
      this.snackBar.open('Invalid YAML: Cannot format', 'Close', { duration: 3000 });
    }
  }

  copyToClipboard(): void {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(this.editorContent).then(() => {
        this.snackBar.open('Configuration copied to clipboard', 'Close', { duration: 2000 });
      }).catch(() => {
        this.snackBar.open('Failed to copy to clipboard', 'Close', { duration: 3000 });
      });
    }
  }

  downloadConfig(): void {
    const blob = new Blob([this.editorContent], { type: 'text/yaml' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${this.selectedTemplate}_config.yaml`;
    link.click();
    window.URL.revokeObjectURL(url);
  }

  getValidationStatus(): { isValid: boolean; message: string } {
    if (!this.editorContent.trim()) {
      return { isValid: false, message: 'Configuration is empty' };
    }
    
    const isValid = this.validateYAML();
    return {
      isValid,
      message: isValid ? 'Valid YAML configuration' : 'Invalid YAML syntax'
    };
  }

  /**
   * Start LoRA training process
   */
  startTraining(): void {
    if (!this.editorContent.trim()) {
      this.snackBar.open('Please provide a valid training configuration', 'Close', {
        duration: 3000,
        panelClass: ['error-snackbar']
      });
      return;
    }

    // Validate YAML before sending
    if (!this.validateYAML()) {
      this.snackBar.open('Invalid YAML configuration. Please fix errors first.', 'Close', {
        duration: 3000,
        panelClass: ['error-snackbar']
      });
      return;
    }

    try {
      const config = yaml.load(this.editorContent) as any;
      const jobType = config?.job;
      
      // Ensure it's a training job
      if (jobType !== 'extension') {
        this.snackBar.open(
          `Invalid job type: ${jobType}. This tab only supports training (job: extension)`, 
          'Close', 
          {
            duration: 5000,
            panelClass: ['error-snackbar']
          }
        );
        return;
      }
      
      this.isStarting = true;
      
      // Start training process
      this.apiService.startTraining({ config: this.editorContent }).subscribe({
        next: (response) => {
          this.snackBar.open(
            `LoRA training started successfully! Process ID: ${response.data?.process_id}`, 
            'Close', 
            {
              duration: 5000,
              panelClass: ['success-snackbar']
            }
          );
          this.isStarting = false;
        },
        error: (error) => {
          console.error('Failed to start training:', error);
          this.snackBar.open('Failed to start LoRA training: ' + (error.message || 'Unknown error'), 'Close', {
            duration: 5000,
            panelClass: ['error-snackbar']
          });
          this.isStarting = false;
        }
      });
      
    } catch (error) {
      this.snackBar.open('Failed to parse YAML configuration', 'Close', {
        duration: 3000,
        panelClass: ['error-snackbar']
      });
      this.isStarting = false;
    }
  }

  // 📁 FILE UPLOAD METHODS

  /**
   * Handle drag over event
   */
  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver = true;
  }

  /**
   * Handle drag leave event
   */
  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver = false;
  }

  /**
   * Handle drop event
   */
  onDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver = false;

    const files = event.dataTransfer?.files;
    if (files) {
      this.handleFileSelection(Array.from(files));
    }
  }

  /**
   * Handle file input change
   */
  onFilesSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files) {
      this.handleFileSelection(Array.from(input.files));
    }
  }

  /**
   * Process selected files
   */
  private handleFileSelection(files: File[]): void {
    const validFiles = files.filter(file => this.isValidFile(file));
    const invalidFiles = files.filter(file => !this.isValidFile(file));

    if (invalidFiles.length > 0) {
      this.snackBar.open(
        `${invalidFiles.length} file(s) skipped: Invalid format or size`,
        'Close',
        { duration: 3000, panelClass: ['error-snackbar'] }
      );
    }

    // Add valid files
    this.uploadedFiles.push(...validFiles);

    if (validFiles.length > 0) {
      this.snackBar.open(
        `Added ${validFiles.length} file(s) for upload`,
        'Close',
        { duration: 2000, panelClass: ['success-snackbar'] }
      );
    }
  }

  /**
   * Validate file
   */
  private isValidFile(file: File): boolean {
    const maxSize = 50 * 1024 * 1024; // 50MB
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'text/plain'];
    const allowedExtensions = ['.jpg', '.jpeg', '.png', '.webp', '.txt'];

    if (file.size > maxSize) return false;
    
    const hasValidType = allowedTypes.includes(file.type);
    const hasValidExtension = allowedExtensions.some(ext => 
      file.name.toLowerCase().endsWith(ext)
    );

    return hasValidType || hasValidExtension;
  }

  /**
   * Remove file from upload list
   */
  removeFile(index: number): void {
    this.uploadedFiles.splice(index, 1);
  }

  /**
   * Clear all files
   */
  clearFiles(): void {
    this.uploadedFiles = [];
  }

  /**
   * Get file type icon class
   */
  getFileTypeIcon(file: File): string {
    return file.type.startsWith('image/') ? 'text-blue-600' : 'text-green-600';
  }

  /**
   * Format file size
   */
  formatFileSize(bytes: number): string {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  }

  /**
   * Get image count
   */
  getImageCount(): number {
    return this.uploadedFiles.filter(file => file.type.startsWith('image/')).length;
  }

  /**
   * Get caption count
   */
  getCaptionCount(): number {
    return this.uploadedFiles.filter(file => 
      file.name.toLowerCase().endsWith('.txt')
    ).length;
  }

  /**
   * Get total file size
   */
  getTotalSize(): number {
    return this.uploadedFiles.reduce((sum, file) => sum + file.size, 0);
  }

  /**
   * Check if can upload
   */
  canUpload(): boolean {
    return this.uploadedFiles.length > 0 && 
           this.getImageCount() > 0;
  }

  /**
   * Upload files to server
   */
  uploadFiles(): void {
    if (!this.canUpload()) {
      this.snackBar.open('Please fill in training name and add images', 'Close', {
        duration: 3000,
        panelClass: ['error-snackbar']
      });
      return;
    }

    this.isUploading = true;

    const uploadRequest: TrainingDataUploadRequest = {
      files: this.uploadedFiles,
      training_name: this.trainingName.trim() || `training_${Date.now()}`,  // Auto-generate if empty
      trigger_word: '',  // Empty - user manages their own captions
      cleanup_existing: this.cleanupExisting
    };

    // 📝 LOG TO FILE - Upload request
    const requestId = this.frontendLogger.logRequest(
      'upload_training_data',
      'POST',
      {
        ...uploadRequest,
        files_count: uploadRequest.files.length,
        files_sizes: uploadRequest.files.map(f => ({ name: f.name, size: f.size }))
      }
    );

    this.frontendLogger.logFileOperation('upload_start', uploadRequest.files, requestId);

    this.apiService.uploadTrainingData(uploadRequest).subscribe({
      next: (response) => {
        console.log('📥 [UPLOAD] Full Backend Response:', response);
        console.log('📁 [UPLOAD] Training Folder:', response.training_folder);
        console.log('📊 [UPLOAD] Response Type:', typeof response);
        console.log('📋 [UPLOAD] Response Keys:', Object.keys(response || {}));
        
        // Log detailed uploaded files information with enhanced details
        if (response.uploaded_files && response.uploaded_files.length > 0) {
          console.log(`📂 [UPLOAD] Uploaded Files Details (${response.uploaded_files.length} files, ${response.total_size_formatted || 'N/A'} total):`);
          response.uploaded_files.forEach((file, index) => {
            const sizeInfo = file.size_formatted || `${(file.size / 1024).toFixed(1)}KB`;
            const typeInfo = file.file_type ? ` [${file.file_type}]` : '';
            console.log(`   ${index + 1}. ${file.filename} (${sizeInfo})${typeInfo}`);
            console.log(`      📁 Folder: ${file.folder || 'training_data'}`);
            console.log(`      📁 Local path: ${file.path}`);
            if (file.runpod_workspace_path) {
              console.log(`      🚀 RunPod path: ${file.runpod_workspace_path}`);
            }
            if (file.runpod_relative_path) {
              console.log(`      📁 Relative path: ${file.runpod_relative_path}`);
            }
          });
          
          // Log file types summary if available
          if (response.file_types_summary) {
            console.log(`📊 [UPLOAD] File Types Summary:`);
            console.log(`   📷 Images: ${response.file_types_summary.images?.length || 0}`);
            console.log(`   📝 Captions: ${response.file_types_summary.captions?.length || 0}`);
            if (response.file_types_summary.other?.length > 0) {
              console.log(`   📄 Other: ${response.file_types_summary.other.length}`);
            }
          }
        }
        
        // Log RunPod environment information
        if (response.runpod_info) {
          console.log('⚡ [UPLOAD] RunPod Environment Info:');
          console.log(`   Worker ID: ${response.runpod_info.worker_id}`);
          console.log(`   Pod ID: ${response.runpod_info.pod_id}`);
          console.log(`   Endpoint ID: ${response.runpod_info.endpoint_id || 'N/A'}`);
          console.log(`   Workspace: ${response.runpod_info.workspace_path}`);
          console.log(`   Training folder (relative): ${response.runpod_info.training_folder_relative}`);
        }
        
        // 📝 LOG TO FILE - Upload response
        this.frontendLogger.logResponse(requestId, 'upload_training_data', response, 200);
        
        // Create enhanced upload summary message using backend detailed_message
        // FIXED: Handle undefined/null values gracefully to prevent "undefined" from showing
        const totalImages = response.total_images ?? 0;
        const totalCaptions = response.total_captions ?? 0;
        
        let detailedMessage = response.detailed_message || 
          `✅ Successfully uploaded ${totalImages} images and ${totalCaptions} captions!`;
        
        // Add debug info if available
        if (response.debug_info) {
          const debug = response.debug_info;
          if (debug.all_files_failed) {
            detailedMessage += '\n⚠️ Warning: All files failed to upload. Check file format and content.';
          } else if (debug.total_files_failed && debug.total_files_failed > 0) {
            detailedMessage += `\n⚠️ Note: ${debug.total_files_failed} files failed to upload.`;
          }
        }
        
        // Add files list if available
        if (response.uploaded_files && response.uploaded_files.length > 0) {
          const filesList = response.uploaded_files.slice(0, 3).map((f: any) => 
            `${f.filename} (${f.size_formatted || (f.size ? (f.size / 1024).toFixed(1) + 'KB' : 'N/A')})`
          ).join(', ');
          const moreFiles = response.uploaded_files.length > 3 ? 
            ` and ${response.uploaded_files.length - 3} more files` : '';
          
          detailedMessage += `\n📄 Files: ${filesList}${moreFiles}`;
        }
        
        // Add RunPod worker info
        if (response.runpod_info) {
          detailedMessage += `\n🗂️ Folder: ${response.runpod_info.training_folder_relative || 'training_data'}`;
          detailedMessage += `\n⚡ Worker: ${response.runpod_info.worker_id || 'local'}`;
        }

        this.snackBar.open(
          detailedMessage,
          'Close',
          { duration: 8000, panelClass: ['success-snackbar'] }
        );
        
        // Update YAML config with training folder
        if (response.training_folder) {
          console.log('✅ [UPLOAD] Updating YAML with folder:', response.training_folder);
          this.updateConfigWithTrainingFolder(response.training_folder);
        } else {
          console.warn('⚠️ [UPLOAD] No training_folder in response!');
          console.log('🔍 [UPLOAD] Available fields:', Object.keys(response || {}));
        }
        
        // Reset upload form
        this.clearFiles();
        this.isUploading = false;
      },
      error: (error) => {
        console.error('Upload failed:', error);
        
        // 📝 LOG TO FILE - Upload error
        this.frontendLogger.logError(requestId, 'upload_training_data', error, { uploadRequest });
        
        this.snackBar.open(
          'Failed to upload training data: ' + (error.message || 'Unknown error'),
          'Close',
          { duration: 5000, panelClass: ['error-snackbar'] }
        );
        this.isUploading = false;
      }
    });
  }

  // 📝 DOWNLOAD LOGS METHODS

  /**
   * Download frontend logs as JSON file
   */
  downloadFrontendLogs(): void {
    const logStats = this.frontendLogger.getLogStats();
    if (logStats.total === 0) {
      this.snackBar.open('No frontend logs to download', 'Close', { duration: 3000 });
      return;
    }

    try {
      console.log('📁 [CONFIG-TAB] Starting frontend logs download...', {
        logsCount: logStats.total,
        browser: navigator.userAgent
      });

      this.frontendLogger.downloadLogs();
      this.snackBar.open('Frontend logs downloaded (JSON)', 'Close', {
        duration: 3000,
        panelClass: ['success-snackbar']
      });
    } catch (error) {
      console.error('📁 [CONFIG-TAB] Frontend download failed:', error);
      const errorMessage = error instanceof Error ? error.message : String(error);
      this.snackBar.open('Download failed: ' + errorMessage, 'Close', { duration: 5000 });
    }
  }

  /**
   * NEW: Download frontend logs as readable text file
   */
  downloadFrontendLogsAsText(): void {
    const logStats = this.frontendLogger.getLogStats();
    if (logStats.total === 0) {
      this.snackBar.open('No frontend logs to download', 'Close', { duration: 3000 });
      return;
    }

    try {
      console.log('📁 [CONFIG-TAB] Starting frontend logs text download...', {
        logsCount: logStats.total,
        browser: navigator.userAgent
      });

      this.frontendLogger.downloadLogsAsText();
      this.snackBar.open('Frontend logs downloaded (TXT)', 'Close', {
        duration: 3000,
        panelClass: ['success-snackbar']
      });
    } catch (error) {
      console.error('📁 [CONFIG-TAB] Frontend text download failed:', error);
      const errorMessage = error instanceof Error ? error.message : String(error);
      this.snackBar.open('Download failed: ' + errorMessage, 'Close', { duration: 5000 });
    }
  }

  /**
   * Get frontend log statistics
   */
  getFrontendLogStats(): any {
    return this.frontendLogger.getLogStats();
  }

  /**
   * NEW: Download current text buffer
   */
  downloadCurrentBuffer(): void {
    const bufferKey = 'lora_dashboard_logs_text_buffer';
    const buffer = localStorage.getItem(bufferKey) || '';
    
    if (!buffer.trim()) {
      this.snackBar.open('No text buffer to download', 'Close', { duration: 3000 });
      return;
    }

    try {
      console.log('📁 [CONFIG-TAB] Downloading text buffer...', {
        bufferSize: buffer.length,
        browser: navigator.userAgent
      });

      this.frontendLogger.downloadCurrentTextBuffer();
      this.snackBar.open('Current log buffer downloaded', 'Close', {
        duration: 3000,
        panelClass: ['success-snackbar']
      });
    } catch (error) {
      console.error('📁 [CONFIG-TAB] Buffer download failed:', error);
      const errorMessage = error instanceof Error ? error.message : String(error);
      this.snackBar.open('Download failed: ' + errorMessage, 'Close', { duration: 5000 });
    }
  }

  /**
   * Update YAML config with training folder path
   */
  private updateConfigWithTrainingFolder(trainingFolder: string): void {
    try {
      console.log('🔄 [CONFIG] Updating YAML with training folder:', trainingFolder);
      
      // Use text replacement instead of YAML parsing to preserve formatting and all fields
      let updatedContent = this.editorContent;
      
      // Update training_folder (if exists)
      const trainingFolderRegex = /(\s*training_folder:\s*)[^\n\r]+/;
      if (trainingFolderRegex.test(updatedContent)) {
        updatedContent = updatedContent.replace(trainingFolderRegex, `$1${trainingFolder}`);
        console.log('✅ [CONFIG] Updated training_folder');
      } else {
        // Add training_folder after device: cuda:0
        const deviceRegex = /(\s*device:\s*cuda:0\s*\n)/;
        if (deviceRegex.test(updatedContent)) {
          updatedContent = updatedContent.replace(deviceRegex, `$1      training_folder: ${trainingFolder}\n`);
          console.log('✅ [CONFIG] Added training_folder');
        }
      }
      
      // Update folder_path (if exists)
      const folderPathRegex = /(\s*folder_path:\s*)[^\n\r]+/;
      if (folderPathRegex.test(updatedContent)) {
        updatedContent = updatedContent.replace(folderPathRegex, `$1${trainingFolder}`);
        console.log('✅ [CONFIG] Updated folder_path');
      } else {
        // Add folder_path to datasets section
        const datasetsRegex = /(\s*datasets:\s*\n\s*-\s*)/;
        if (datasetsRegex.test(updatedContent)) {
          updatedContent = updatedContent.replace(datasetsRegex, `$1folder_path: ${trainingFolder}\n          `);
          console.log('✅ [CONFIG] Added folder_path');
        }
      }
      
      this.editorContent = updatedContent;
      
      this.snackBar.open('Configuration updated with training data path', 'Close', {
        duration: 3000,
        panelClass: ['success-snackbar']
      });
      
    } catch (error) {
      console.error('Failed to update YAML config:', error);
      this.snackBar.open('Warning: Could not update YAML config automatically', 'Close', {
        duration: 3000,
        panelClass: ['warning-snackbar']
      });
    }
  }

  // 📝 BACKEND LOGS METHODS

  /**
   * Download backend logs
   */
  downloadBackendLogs(logType: string): void {
    if (this.isDownloadingLogs) return;
    
    this.isDownloadingLogs = true;
    
    this.apiService.getBackendLogs(logType, 1000).subscribe({
      next: (response) => {
        // Create and download file
        const timestamp = new Date().toISOString().split('T')[0];
        const filename = `backend_${logType}_logs_${timestamp}.json`;
        
        const dataStr = JSON.stringify(response, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.click();
        
        URL.revokeObjectURL(url);
        
        this.snackBar.open(`Downloaded ${logType} logs successfully!`, 'Close', {
          duration: 3000,
          panelClass: ['success-snackbar']
        });
        
        this.isDownloadingLogs = false;
      },
      error: (error) => {
        console.error('Failed to download logs:', error);
        this.snackBar.open(`Failed to download ${logType} logs: ${error.message}`, 'Close', {
          duration: 5000,
          panelClass: ['error-snackbar']
        });
        this.isDownloadingLogs = false;
      }
    });
  }

  /**
   * Refresh log statistics
   */
  refreshLogStats(): void {
    if (this.isLoadingStats) return;
    
    this.isLoadingStats = true;
    
    this.apiService.getLogStats().subscribe({
      next: (stats) => {
        this.logStats = stats;
        this.isLoadingStats = false;
        
        this.snackBar.open('Log statistics refreshed!', 'Close', {
          duration: 2000
        });
      },
      error: (error) => {
        console.error('Failed to load log stats:', error);
        this.snackBar.open('Failed to load log statistics', 'Close', {
          duration: 3000,
          panelClass: ['error-snackbar']
        });
        this.isLoadingStats = false;
      }
    });
  }

  /**
   * Format date for display
   */
  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleString();
  }

  // Removed Monaco Editor - using simple textarea instead
}
