import { Component, OnInit, OnDestroy } from '@angular/core';
import { FormControl } from '@angular/forms';
import { Subject, takeUntil } from 'rxjs';
import { MatSnackBar } from '@angular/material/snack-bar';
import * as yaml from 'js-yaml';
import { ApiService } from '../../core/api.service';
import { LoRAModel } from '../../core/models';

@Component({
  selector: 'app-lora-tab',
  templateUrl: './lora-tab.component.html',
  styleUrls: ['./lora-tab.component.scss']
})
export class LoraTabComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();

  loraModels: LoRAModel[] = [];
  selectedLoRA: LoRAModel | null = null;
  isLoadingModels = false;
  isGenerating = false;

  yamlConfig = '';

  constructor(
    private apiService: ApiService,
    private snackBar: MatSnackBar
  ) { }

  ngOnInit(): void {
    this.loadLoRAModels();
    this.loadDefaultConfig();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Load available LoRA models
   */
  loadLoRAModels(): void {
    this.isLoadingModels = true;
    
    this.apiService.getLoRAModels()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (models) => {
          this.loraModels = models;
          this.isLoadingModels = false;
          
          // Auto-select first model if available
          if (models.length > 0) {
            this.selectedLoRA = models[0];
            this.updateYamlWithLoRA();
          }
        },
        error: (error) => {
          console.error('Failed to load LoRA models:', error);
          this.snackBar.open('Failed to load LoRA models', 'Close', {
            duration: 5000,
            panelClass: ['error-snackbar']
          });
          this.isLoadingModels = false;
        }
      });
  }

  /**
   * Load default generation config
   */
  async loadDefaultConfig(): Promise<void> {
    try {
      const response = await fetch('/assets/templates/generate.yaml');
      if (response.ok) {
        this.yamlConfig = await response.text();
      } else {
        throw new Error('Failed to load default config');
      }
    } catch (error) {
      console.error('Failed to load default config:', error);
      // Fallback to basic config
      this.yamlConfig = `job: generate
config:
  name: flux_generation
  process:
    - type: to_folder
      output_folder: "/workspace/samples_flux"
      device: cuda:0
      generate:
        sampler: flowmatch
        width: 896
        height: 896
        guidance_scale: 2
        sample_steps: 20
        prompts:
          - "Example prompt"
      model:
        name_or_path: "/workspace/models/FLUX.1-dev"
        is_flux: true
        quantize: false
        dtype: fp16
        lora_dtype: fp16
        lora_path: ""
        lora_scale: 1.0`;
    }
  }

  /**
   * Handle LoRA model selection
   */
  onLoRASelected(): void {
    if (this.selectedLoRA) {
      this.updateYamlWithLoRA();
    }
  }

  /**
   * Update YAML config with selected LoRA path
   */
  updateYamlWithLoRA(): void {
    if (!this.selectedLoRA) {
      return;
    }

    try {
      const config = yaml.load(this.yamlConfig) as any;
      
      // Update LoRA path in the model section
      if (config.config?.process?.[0]?.model) {
        config.config.process[0].model.lora_path = this.selectedLoRA.path;
        
        // Note: Prompts are left unchanged - user manages their own captions and prompts
      }
      
      this.yamlConfig = yaml.dump(config, { 
        indent: 2,
        lineWidth: 120,
        noRefs: true 
      });
      
    } catch (error) {
      console.error('Failed to update YAML config:', error);
      this.snackBar.open('Failed to update configuration with LoRA path', 'Close', {
        duration: 3000,
        panelClass: ['error-snackbar']
      });
    }
  }

  /**
   * Start image generation
   */
  startGeneration(): void {
    if (!this.yamlConfig.trim()) {
      this.snackBar.open('Please provide a valid YAML configuration', 'Close', {
        duration: 3000,
        panelClass: ['error-snackbar']
      });
      return;
    }

    // Validate YAML before sending
    try {
      yaml.load(this.yamlConfig);
    } catch (error) {
      this.snackBar.open('Invalid YAML configuration', 'Close', {
        duration: 3000,
        panelClass: ['error-snackbar']
      });
      return;
    }

    this.isGenerating = true;
    
    this.apiService.startGeneration({ config: this.yamlConfig })
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          this.snackBar.open(
            `Generation started! Process ID: ${response.data?.process_id}`, 
            'Close', 
            {
              duration: 5000,
              panelClass: ['success-snackbar']
            }
          );
          this.isGenerating = false;
        },
        error: (error) => {
          console.error('Failed to start generation:', error);
          this.snackBar.open('Failed to start generation', 'Close', {
            duration: 5000,
            panelClass: ['error-snackbar']
          });
          this.isGenerating = false;
        }
      });
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
   * Copy LoRA path to clipboard
   */
  copyLoRAPath(): void {
    if (!this.selectedLoRA) {
      return;
    }
    
    if (navigator.clipboard) {
      navigator.clipboard.writeText(this.selectedLoRA.path).then(() => {
        this.snackBar.open('LoRA path copied to clipboard', 'Close', {
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
   * Get relative time string
   */
  getRelativeTime(date: string): string {
    const now = new Date();
    const past = new Date(date);
    const diffInSeconds = Math.floor((now.getTime() - past.getTime()) / 1000);
    
    const intervals = [
      { label: 'year', seconds: 31536000 },
      { label: 'month', seconds: 2592000 },
      { label: 'day', seconds: 86400 },
      { label: 'hour', seconds: 3600 },
      { label: 'minute', seconds: 60 }
    ];
    
    for (const interval of intervals) {
      const count = Math.floor(diffInSeconds / interval.seconds);
      if (count >= 1) {
        return `${count} ${interval.label}${count > 1 ? 's' : ''} ago`;
      }
    }
    
    return 'Just now';
  }
}
