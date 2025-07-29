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

  displayedColumns: string[] = [
    'name', 'type', 'status', 'progress', 'lora_info', 'gpu_id', 'elapsed_time', 'eta', 'actions'
  ];

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
      next: (url) => {
        if (url) {
          window.open(url, '_blank');
        } else {
          this.snackBar.open('No download available for this process', 'Close', { duration: 3000 });
        }
      },
      error: (error) => {
        this.snackBar.open('Failed to get download URL: ' + error.message, 'Close', { duration: 5000 });
      }
    });
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
}
