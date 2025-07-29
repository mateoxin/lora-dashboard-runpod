import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { MatSnackBar } from '@angular/material/snack-bar';
import * as yaml from 'js-yaml';
import { ApiService } from '../../core/api.service';

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

  constructor(
    private http: HttpClient,
    private snackBar: MatSnackBar,
    private apiService: ApiService
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

  // Removed Monaco Editor - using simple textarea instead
}
