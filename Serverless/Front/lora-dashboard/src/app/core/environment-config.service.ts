import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';

export interface EnvironmentConfig {
  runpodToken: string;
  runpodEndpointUrl: string;
  apiBaseUrl: string;
  encryptionKey: string;
  autoRefreshInterval: number;
  maxFileSize: number;
  mockMode: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class EnvironmentConfigService {
  private config: EnvironmentConfig | null = null;

  constructor(private http: HttpClient) {}

  /**
   * Load configuration from external config file or environment
   * This allows runtime configuration without rebuilding the app
   */
  loadConfig(): Observable<EnvironmentConfig> {
    if (this.config) {
      return of(this.config);
    }

    // Try to load from assets/config.json first
    return this.http.get<EnvironmentConfig>('/assets/config.json').pipe(
      catchError(() => {
        // Fallback to default configuration from environment
        const defaultConfig: EnvironmentConfig = {
          runpodToken: this.getConfigValue('RUNPOD_TOKEN', 'YOUR_RUNPOD_TOKEN_HERE'),
          runpodEndpointUrl: this.getConfigValue('RUNPOD_ENDPOINT_URL', 'https://your-endpoint.runpod.net/api'),
          apiBaseUrl: this.getConfigValue('API_BASE_URL', 'http://localhost:8000/api'),
          encryptionKey: this.getConfigValue('ENCRYPTION_KEY', 'LoRA-Dashboard-Secret-Key-2024'),
          autoRefreshInterval: parseInt(this.getConfigValue('AUTO_REFRESH_INTERVAL', '5000')),
          maxFileSize: parseInt(this.getConfigValue('MAX_FILE_SIZE', '52428800')),
          mockMode: this.getConfigValue('MOCK_MODE', 'false') === 'true'
        };
        
        this.config = defaultConfig;
        return of(defaultConfig);
      }),
      map(config => {
        this.config = config;
        return config;
      })
    );
  }

  /**
   * Get configuration value with fallback
   */
  private getConfigValue(key: string, defaultValue: string): string {
    // In a real environment, this could read from various sources:
    // - Environment variables (if exposed to frontend)
    // - Local storage
    // - URL parameters
    // - Injected configuration
    
    return defaultValue;
  }

  /**
   * Get current configuration
   */
  getConfig(): EnvironmentConfig | null {
    return this.config;
  }

  /**
   * Validate that configuration is properly set
   */
  validateConfig(): boolean {
    if (!this.config) {
      return false;
    }

    const placeholders = [
      'YOUR_RUNPOD_TOKEN_HERE',
      'your_runpod_api_token_here',
      'your-endpoint.runpod.net'
    ];

    // Check if any configuration still contains placeholders
    const hasPlaceholders = 
      placeholders.some(placeholder => 
        this.config!.runpodToken.includes(placeholder) ||
        this.config!.runpodEndpointUrl.includes(placeholder)
      );

    return !hasPlaceholders;
  }

  /**
   * Get validation errors
   */
  getValidationErrors(): string[] {
    const errors: string[] = [];
    
    if (!this.config) {
      errors.push('Configuration not loaded');
      return errors;
    }

    if (this.config.runpodToken === 'YOUR_RUNPOD_TOKEN_HERE' || 
        this.config.runpodToken === 'your_runpod_api_token_here') {
      errors.push('RunPod token is not configured. Please set your actual token.');
    }

    if (this.config.runpodEndpointUrl.includes('your-endpoint')) {
      errors.push('RunPod endpoint URL is not configured. Please set your actual endpoint.');
    }

    return errors;
  }
} 