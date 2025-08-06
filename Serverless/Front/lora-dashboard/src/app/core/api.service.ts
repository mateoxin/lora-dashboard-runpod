import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, throwError, forkJoin, of } from 'rxjs';
import { catchError, map, switchMap } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { 
  ApiResponse, 
  Process, 
  LoRAModel, 
  GenerateRequest, 
  TrainRequest,
  ProcessesResponse,
  LoRAResponse,
  TrainingDataUploadRequest,
  TrainingDataUploadResponse,
  BulkDownloadRequest,
  BulkDownloadResponse
} from './models';
import { AuthService } from '../auth/auth.service';
import { MockApiService } from './mock-api.service';
import { FrontendLoggerService } from './frontend-logger.service';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly baseUrl = environment.apiBaseUrl;

  constructor(
    private http: HttpClient,
    private authService: AuthService,
    private mockApiService: MockApiService,
    private frontendLogger: FrontendLoggerService
  ) { }

  /**
   * Get HTTP headers with authentication token and RunPod token
   */
  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    const headers: any = {
      'Content-Type': 'application/json'
    };
    
    // Add auth token if available
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    // Add RunPod token for serverless communication
    if (environment.runpodToken) {
      headers['X-RunPod-Token'] = environment.runpodToken;
    }
    
    return new HttpHeaders(headers);
  }

  /**
   * Handle HTTP errors
   */
  private handleError(error: any): Observable<never> {
    console.error('API Error:', error);
    let errorMessage = 'An unknown error occurred';
    
    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = error.error.message;
    } else {
      // Server-side error
      errorMessage = error.error?.message || error.message || `Error Code: ${error.status}`;
    }
    
    return throwError(() => new Error(errorMessage));
  }

  /**
   * GET /health - Health check
   */
  getHealth(): Observable<ApiResponse> {
    // NEW: Log request
    const requestId = this.frontendLogger.logRequest(this.baseUrl, 'GET', { endpoint: '/health' });
    const startTime = Date.now();

    if (environment.mockMode) {
      return this.mockApiService.getHealth();
    }
    
    // Check if this is a RunPod endpoint
    const isRunPodEndpoint = this.baseUrl.includes('api.runpod.ai');
    
    if (isRunPodEndpoint) {
      // Use RunPod native health endpoint
      const headers = new HttpHeaders({
        'Authorization': `Bearer ${environment.runpodToken}`
      });
      
      return this.http.get<any>(`${this.baseUrl}/health`, { headers }).pipe(
        map(response => {
          const result = {
            success: true,
            data: response,
            message: 'RunPod endpoint health check'
          };
          this.frontendLogger.logResponse(requestId, this.baseUrl + '/health', result, 200, Date.now() - startTime);
          return result;
        }),
        catchError(error => {
          // If native health fails, try custom health job
          const runpodPayload = {
            input: {
              type: 'health'
            }
          };
          
          return this.http.post<any>(`${this.baseUrl}/runsync`, runpodPayload, { 
            headers: new HttpHeaders({
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${environment.runpodToken}`
            })
          }).pipe(
            map(response => ({
              success: true,
              data: response.output || response,
              message: 'Custom health check via handler'
            })),
            catchError(error => {
              this.frontendLogger.logError(requestId, this.baseUrl + '/health', error);
              return this.handleError(error);
            })
          );
        })
      );
    } else {
      // Regular FastAPI format
      return this.http.get<ApiResponse>(`${this.baseUrl}/health`).pipe(
        map(response => {
          this.frontendLogger.logResponse(requestId, this.baseUrl + '/health', response, 200, Date.now() - startTime);
          return response;
        }),
        catchError(error => {
          this.frontendLogger.logError(requestId, this.baseUrl + '/health', error);
          return this.handleError(error);
        })
      );
    }
  }

  /**
   * GET /status/{job_id} - Check RunPod job status (native RunPod endpoint)
   */
  getRunPodJobStatus(jobId: string): Observable<any> {
    const isRunPodEndpoint = this.baseUrl.includes('api.runpod.ai');
    
    if (!isRunPodEndpoint) {
      return throwError(() => new Error('Job status check only available for RunPod endpoints'));
    }
    
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${environment.runpodToken}`
    });
    
    return this.http.get<any>(`${this.baseUrl}/status/${jobId}`, { headers }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * POST /cancel/{job_id} - Cancel RunPod job (native RunPod endpoint)
   */
  cancelRunPodJob(jobId: string): Observable<any> {
    const isRunPodEndpoint = this.baseUrl.includes('api.runpod.ai');
    
    if (!isRunPodEndpoint) {
      return throwError(() => new Error('Job cancellation only available for RunPod endpoints'));
    }
    
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${environment.runpodToken}`
    });
    
    return this.http.post<any>(`${this.baseUrl}/cancel/${jobId}`, {}, { headers }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * GET /processes - Get all processes
   */
  getProcesses(): Observable<Process[]> {
    // NEW: Log request
    const requestId = this.frontendLogger.logRequest(this.baseUrl, 'GET', { endpoint: '/processes' });
    const startTime = Date.now();

    if (environment.mockMode) {
      return this.mockApiService.getProcesses();
    }
    
    // Check if this is a RunPod endpoint
    const isRunPodEndpoint = this.baseUrl.includes('api.runpod.ai');
    
    if (isRunPodEndpoint) {
      // RunPod format - use /runsync for quick data retrieval
      const runpodPayload = {
        input: {
          type: 'processes'
        }
      };
      
      const headers = new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${environment.runpodToken}`
      });
      
      return this.http.post<any>(`${this.baseUrl}/runsync`, runpodPayload, { headers }).pipe(
        map(response => {
          const data = response.output || response;
          let result;
          if (data.status === 'success' && data.processes) {
            result = data.processes.map((p: any) => ({
              id: p.id,
              status: p.status || 'unknown',
              type: p.type || 'training',
              created_at: p.created_at || new Date().toISOString(),
              updated_at: p.updated_at || new Date().toISOString(),
              progress: p.progress || 0,
              error: p.error || null
            }));
          } else {
            result = data.processes || [];
          }
          this.frontendLogger.logResponse(requestId, this.baseUrl + '/processes', { processes: result, count: result.length }, 200, Date.now() - startTime);
          return result;
        }),
        catchError(error => {
          this.frontendLogger.logError(requestId, this.baseUrl + '/processes', error);
          return this.handleError(error);
        })
      );
    } else {
      // Regular FastAPI format
      return this.http.get<ProcessesResponse>(`${this.baseUrl}/processes`, {
        headers: this.getHeaders()
      }).pipe(
        map(response => {
          this.frontendLogger.logResponse(requestId, this.baseUrl + '/processes', response, 200, Date.now() - startTime);
          return response.processes;
        }),
        catchError(error => {
          this.frontendLogger.logError(requestId, this.baseUrl + '/processes', error);
          return this.handleError(error);
        })
      );
    }
  }

  /**
   * GET /lora - Get available LoRA models (maps to list_models for simple backend)
   */
  getLoRAModels(): Observable<LoRAModel[]> {
    // NEW: Log request
    const requestId = this.frontendLogger.logRequest(this.baseUrl, 'GET', { endpoint: '/lora' });
    const startTime = Date.now();

    if (environment.mockMode) {
      return this.mockApiService.getLoRAModels();
    }
    
    // Check if this is a RunPod endpoint
    const isRunPodEndpoint = this.baseUrl.includes('api.runpod.ai');
    
    if (isRunPodEndpoint) {
      // RunPod format - use /runsync for quick data retrieval
      const runpodPayload = {
        input: {
          type: 'list_models'
        }
      };
      
      const headers = new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${environment.runpodToken}`
      });
      
      return this.http.post<any>(`${this.baseUrl}/runsync`, runpodPayload, { headers }).pipe(
        map(response => {
          const data = response.output || response;
          let result = [];
          if (data.models) {
            // Convert simple backend format to frontend format
            result = data.models.map((model: any) => ({
              id: model.filename || model.id,
              name: model.filename || model.name,
              path: model.path || `/workspace/ai-toolkit/output/${model.filename}`,
              size: model.size_mb ? `${model.size_mb}MB` : 'Unknown',
              created_at: model.modified_date || new Date().toISOString(),
              status: 'ready'
            }));
          }
          this.frontendLogger.logResponse(requestId, this.baseUrl + '/lora', { models: result, count: result.length }, 200, Date.now() - startTime);
          return result;
        }),
        catchError(error => {
          this.frontendLogger.logError(requestId, this.baseUrl + '/lora', error);
          return this.handleError(error);
        })
      );
    } else {
      // Regular FastAPI format
      return this.http.get<LoRAResponse>(`${this.baseUrl}/lora`, {
        headers: this.getHeaders()
      }).pipe(
        map(response => {
          this.frontendLogger.logResponse(requestId, this.baseUrl + '/lora', response, 200, Date.now() - startTime);
          return response.models;
        }),
        catchError(error => {
          this.frontendLogger.logError(requestId, this.baseUrl + '/lora', error);
          return this.handleError(error);
        })
      );
    }
  }

  /**
   * POST /train - Start training process
   */
  startTraining(request: TrainRequest): Observable<ApiResponse> {
    // NEW: Log request with config details
    const requestId = this.frontendLogger.logRequest(this.baseUrl, 'POST', { 
      endpoint: '/train',
      configLength: request.config?.length || 0,
      hasConfig: !!request.config
    });
    const startTime = Date.now();

    if (environment.mockMode) {
      return this.mockApiService.startTraining(request);
    }
    
    // Check if this is a RunPod endpoint
    const isRunPodEndpoint = this.baseUrl.includes('api.runpod.ai');
    
    if (isRunPodEndpoint) {
      // RunPod format - use train_with_yaml for simple backend
      const runpodPayload = {
        input: {
          type: 'train_with_yaml',
          config: request.config
        }
      };
      
      const headers = new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${environment.runpodToken}`
      });
      
      return this.http.post<any>(`${this.baseUrl}/runsync`, runpodPayload, { headers }).pipe(
        map(response => {
          const result = response.output || response;
          this.frontendLogger.logResponse(requestId, this.baseUrl + '/train', result, 200, Date.now() - startTime);
          return result;
        }),
        catchError(error => {
          this.frontendLogger.logError(requestId, this.baseUrl + '/train', error, { request });
          return this.handleError(error);
        })
      );
    } else {
      // Regular FastAPI format
      return this.http.post<ApiResponse>(`${this.baseUrl}/train`, request, {
        headers: this.getHeaders()
      }).pipe(
        map(response => {
          this.frontendLogger.logResponse(requestId, this.baseUrl + '/train', response, 200, Date.now() - startTime);
          return response;
        }),
        catchError(error => {
          this.frontendLogger.logError(requestId, this.baseUrl + '/train', error, { request });
          return this.handleError(error);
        })
      );
    }
  }

  /**
   * POST /generate - Start generation process
   */
  startGeneration(request: GenerateRequest): Observable<ApiResponse> {
    // NEW: Log request
    const requestId = this.frontendLogger.logRequest(this.baseUrl, 'POST', { 
      endpoint: '/generate',
      configLength: request.config?.length || 0,
      hasConfig: !!request.config
    });
    const startTime = Date.now();

    if (environment.mockMode) {
      return this.mockApiService.startGeneration(request);
    }
    
    // Check if this is a RunPod endpoint
    const isRunPodEndpoint = this.baseUrl.includes('api.runpod.ai');
    
    if (isRunPodEndpoint) {
      // RunPod format - use /run for generation tasks (can be long-running)
      const runpodPayload = {
        input: {
          type: 'generate',
          config: request.config
        }
      };
      
      const headers = new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${environment.runpodToken}`
      });
      
      return this.http.post<any>(`${this.baseUrl}/run`, runpodPayload, { headers }).pipe(
        map(response => {
          const result = response.output || response;
          this.frontendLogger.logResponse(requestId, this.baseUrl + '/generate', result, 200, Date.now() - startTime);
          return result;
        }),
        catchError(error => {
          this.frontendLogger.logError(requestId, this.baseUrl + '/generate', error, { request });
          return this.handleError(error);
        })
      );
    } else {
      // Regular FastAPI format
      return this.http.post<ApiResponse>(`${this.baseUrl}/generate`, request, {
        headers: this.getHeaders()
      }).pipe(
        map(response => {
          this.frontendLogger.logResponse(requestId, this.baseUrl + '/generate', response, 200, Date.now() - startTime);
          return response;
        }),
        catchError(error => {
          this.frontendLogger.logError(requestId, this.baseUrl + '/generate', error, { request });
          return this.handleError(error);
        })
      );
    }
  }

  /**
   * GET /download/{id} - Get download URL for generated content
   */
  getDownloadUrl(id: string): Observable<string> {
    if (environment.mockMode) {
      return this.mockApiService.getDownloadUrl(id);
    }
    
    // Check if this is a RunPod endpoint
    const isRunPodEndpoint = this.baseUrl.includes('api.runpod.ai');
    
    if (isRunPodEndpoint) {
      // RunPod format - use /runsync for quick URL generation
      const runpodPayload = {
        input: {
          type: 'download',
          process_id: id
        }
      };
      
      const headers = new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${environment.runpodToken}`
      });
      
      return this.http.post<any>(`${this.baseUrl}/runsync`, runpodPayload, { headers }).pipe(
        map(response => {
          const data = response.output || response;
          return data.url || '';
        }),
        catchError(this.handleError)
      );
    } else {
      // Regular FastAPI format
      return this.http.get<ApiResponse<{ url: string }>>(`${this.baseUrl}/download/${id}`, {
        headers: this.getHeaders()
      }).pipe(
        map(response => response.data?.url || ''),
        catchError(this.handleError)
      );
    }
  }

  /**
   * DELETE /processes/{id} - Cancel process
   */
  cancelProcess(id: string): Observable<ApiResponse> {
    // NEW: Log request
    const requestId = this.frontendLogger.logRequest(this.baseUrl, 'DELETE', { 
      endpoint: `/processes/${id}`,
      processId: id
    });
    const startTime = Date.now();

    if (environment.mockMode) {
      return this.mockApiService.cancelProcess(id);
    }
    
    // Check if this is a RunPod endpoint
    const isRunPodEndpoint = this.baseUrl.includes('api.runpod.ai');
    
    if (isRunPodEndpoint) {
      // RunPod format - use /runsync for quick cancellation
      const runpodPayload = {
        input: {
          type: 'cancel',
          process_id: id
        }
      };
      
      const headers = new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${environment.runpodToken}`
      });
      
      return this.http.post<any>(`${this.baseUrl}/runsync`, runpodPayload, { headers }).pipe(
        map(response => {
          const data = response.output || response;
          // Convert RunPod response to ApiResponse format for consistency
          const result = {
            success: !data.error,
            data: data.error ? null : data,
            message: data.message || (data.error ? data.error : 'Process cancelled successfully'),
            error: data.error || undefined
          };
          this.frontendLogger.logResponse(requestId, this.baseUrl + '/cancel', result, 200, Date.now() - startTime);
          return result;
        }),
        catchError(error => {
          this.frontendLogger.logError(requestId, this.baseUrl + '/cancel', error, { processId: id });
          return this.handleError(error);
        })
      );
    } else {
      // Regular FastAPI format
      return this.http.delete<ApiResponse>(`${this.baseUrl}/processes/${id}`, {
        headers: this.getHeaders()
      }).pipe(
        map(response => {
          this.frontendLogger.logResponse(requestId, this.baseUrl + `/processes/${id}`, response, 200, Date.now() - startTime);
          return response;
        }),
        catchError(error => {
          this.frontendLogger.logError(requestId, this.baseUrl + `/processes/${id}`, error, { processId: id });
          return this.handleError(error);
        })
      );
    }
  }

  /**
   * GET /processes/{id} - Get specific process details
   */
  getProcess(id: string): Observable<Process> {
    if (environment.mockMode) {
      return this.mockApiService.getProcess(id);
    }
    
    // Check if this is a RunPod endpoint
    const isRunPodEndpoint = this.baseUrl.includes('api.runpod.ai');
    
    if (isRunPodEndpoint) {
      // RunPod format - use /runsync for quick status check
      const runpodPayload = {
        input: {
          type: 'process_status',
          process_id: id
        }
      };
      
      const headers = new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${environment.runpodToken}`
      });
      
      return this.http.post<any>(`${this.baseUrl}/runsync`, runpodPayload, { headers }).pipe(
        map(response => {
          const data = response.output || response;
          if (data.status === 'success' && data.process) {
            return {
              id: data.process.id || id,
              name: data.process.name || `Process ${id}`,
              status: data.process.status || 'pending',
              type: data.process.type || 'training',
              created_at: data.process.created_at || new Date().toISOString(),
              updated_at: data.process.updated_at || new Date().toISOString(),
              progress: data.process.progress || 0,
              error: data.process.error || null,
              output_path: data.process.output_path || null
            };
          }
          if (data.error) {
            throw new Error(data.error);
          }
          return { 
            id, 
            name: `Process ${id}`,
            status: 'pending', 
            type: 'training',
            progress: 0,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          } as Process;
        }),
        catchError(this.handleError)
      );
    } else {
      // Regular FastAPI format
      return this.http.get<ApiResponse<Process>>(`${this.baseUrl}/processes/${id}`, {
        headers: this.getHeaders()
      }).pipe(
        map(response => response.data!),
        catchError(this.handleError)
      );
    }
  }

  // 📁 FILE UPLOAD METHODS

  /**
   * POST /upload/training-data - Upload training images and captions
   */
  uploadTrainingData(request: TrainingDataUploadRequest): Observable<TrainingDataUploadResponse> {
    if (environment.mockMode) {
      // Mock implementation would return simulated data
      return this.mockApiService.uploadTrainingData(request);
    }

    // Log request with enhanced logger
    const requestId = this.frontendLogger.logRequest(
      this.baseUrl,
      'POST',
      {
        filesCount: request.files.length,
        trainingName: request.training_name,
        triggerWord: request.trigger_word,
        cleanupExisting: request.cleanup_existing,
        environment: {
          apiBaseUrl: environment.apiBaseUrl,
          runpodToken: environment.runpodToken ? '***EXISTS***' : 'MISSING',
          mockMode: environment.mockMode
        }
      }
    );

    // Log file operation
    this.frontendLogger.logFileOperation('upload_preparation', request.files, requestId);

    console.log('🚀 [API] Upload Training Data Request:', {
      baseUrl: this.baseUrl,
      filesCount: request.files.length,
      trainingName: request.training_name,
      triggerWord: request.trigger_word,
      cleanupExisting: request.cleanup_existing,
      requestId: requestId,
      environment: {
        apiBaseUrl: environment.apiBaseUrl,
        runpodToken: environment.runpodToken ? '***EXISTS***' : 'MISSING',
        mockMode: environment.mockMode
      }
    });

    // Check if this is a RunPod endpoint
    const isRunPodEndpoint = this.baseUrl.includes('api.runpod.ai');
    
    if (isRunPodEndpoint) {
      // RunPod format: convert files to base64 and send as JSON
      console.log('🔄 [API] Using RunPod serverless format');
      
             return this.convertFilesToBase64(request.files).pipe(
         switchMap((base64Files: any[]) => {
          const runpodPayload = {
            input: {
              type: 'upload_training_data',
              training_name: request.training_name,
              trigger_word: request.trigger_word,
              cleanup_existing: request.cleanup_existing,
              files: base64Files
            }
          };
          
          console.log('📡 [API] RunPod Payload:', {
            type: runpodPayload.input.type,
            training_name: runpodPayload.input.training_name,
            files_count: runpodPayload.input.files.length
          });
          
          const headers = new HttpHeaders({
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${environment.runpodToken}`
          });
          
          return this.http.post<any>(`${this.baseUrl}/run`, runpodPayload, { headers }).pipe(
            map(response => {
              console.log('✅ [API] RunPod Upload Success Response:', response);
              this.frontendLogger.logResponse(requestId, this.baseUrl, response, 200);
              
              if (response.error) {
                this.frontendLogger.logError(requestId, this.baseUrl, new Error(response.error), response);
                throw new Error(response.error);
              }
              return response.output || response;
            }),
            catchError(error => {
              console.error('❌ [API] RunPod Upload Error:', error);
              this.frontendLogger.logError(requestId, this.baseUrl, error, { runpodPayload });
              return this.handleError(error);
            })
          );
        })
      );
    } else {
      // Regular FastAPI format
      console.log('🔄 [API] Using regular FastAPI format');
      
      const requestUrl = `${this.baseUrl}/upload/training-data`;
      const formData = new FormData();
      
      // Add files
      request.files.forEach((file, index) => {
        formData.append('files', file, file.name);
        console.log(`📎 [API] File ${index + 1}:`, {
          name: file.name,
          size: file.size,
          type: file.type
        });
      });
      
      // Add metadata
      formData.append('training_name', request.training_name);
      formData.append('trigger_word', request.trigger_word);
      formData.append('cleanup_existing', request.cleanup_existing ? 'true' : 'false');

      // For file uploads, don't set Content-Type header (let browser set it with boundary)
      const headers = this.getHeaders().delete('Content-Type');
      
      console.log('📡 [API] Request Headers:', headers.keys().map(key => ({
        key,
        value: key.includes('Token') ? '***HIDDEN***' : headers.get(key)
      })));

      return this.http.post<ApiResponse<TrainingDataUploadResponse>>(requestUrl, formData, {
        headers: headers
      }).pipe(
        map(response => {
          console.log('✅ [API] Upload Success Response:', response);
          this.frontendLogger.logResponse(requestId, requestUrl, response, 200);
          return response.data!;
        }),
        catchError(error => {
          console.error('❌ [API] Upload Error Details:', {
            error,
            status: error.status,
            statusText: error.statusText,
            url: error.url,
            message: error.message,
            headers: error.headers
          });
          this.frontendLogger.logError(requestId, requestUrl, error, { formData: 'FormData object' });
          return this.handleError(error);
        })
      );
    }
  }

  /**
   * POST /download/bulk - Create bulk download URLs
   */
  getBulkDownloadUrls(request: BulkDownloadRequest): Observable<BulkDownloadResponse> {
    if (environment.mockMode) {
      return this.mockApiService.getBulkDownloadUrls(request);
    }
    
    // Check if this is a RunPod endpoint
    const isRunPodEndpoint = this.baseUrl.includes('api.runpod.ai');
    
    if (isRunPodEndpoint) {
      // RunPod format - use /runsync for quick bulk URL generation
      const runpodPayload = {
        input: {
          type: 'bulk_download',
          process_ids: request.process_ids,
          include_images: request.include_images,
          include_loras: request.include_loras
        }
      };
      
      const headers = new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${environment.runpodToken}`
      });
      
      return this.http.post<any>(`${this.baseUrl}/runsync`, runpodPayload, { headers }).pipe(
        map(response => {
          const data = response.output || response;
          if (data.error) {
            throw new Error(data.error);
          }
          return data as BulkDownloadResponse;
        }),
        catchError(this.handleError)
      );
    } else {
      // Regular FastAPI format
      return this.http.post<ApiResponse<BulkDownloadResponse>>(`${this.baseUrl}/download/bulk`, request, {
        headers: this.getHeaders()
      }).pipe(
        map(response => response.data!),
        catchError(this.handleError)
      );
    }
  }

  /**
   * Helper method to format file size for display
   */
  formatFileSize(bytes: number): string {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  }

  /**
   * Convert files to base64 format for RunPod
   */
  private convertFilesToBase64(files: File[]): Observable<any[]> {
    const fileReaders: Observable<any>[] = files.map(file => {
      return new Observable(observer => {
        const reader = new FileReader();
        reader.onload = () => {
          const base64Content = (reader.result as string).split(',')[1]; // Remove data:type/subtype;base64,
          observer.next({
            filename: file.name,
            content: base64Content,
            content_type: file.type,
            size: file.size
          });
          observer.complete();
        };
        reader.onerror = () => {
          observer.error(new Error(`Failed to read file: ${file.name}`));
        };
        reader.readAsDataURL(file);
      });
    });

    return forkJoin(fileReaders);
  }

  /**
   * GET /logs/stats - Get backend log statistics
   */
  getLogStats(): Observable<any> {
    // Check if this is a RunPod endpoint
    const isRunPodEndpoint = this.baseUrl.includes('api.runpod.ai');
    
    if (environment.mockMode) {
      return of({
        log_directory: "/workspace/logs",
        files: [
          { name: "app.log", size: 15420, modified: new Date().toISOString() },
          { name: "requests.log", size: 45600, modified: new Date().toISOString() },
          { name: "errors.log", size: 2340, modified: new Date().toISOString() }
        ]
      });
    }

    if (isRunPodEndpoint) {
      // For RunPod, logs are not directly accessible via API
      // Return mock data or indicate logs need to be accessed via RunPod console
      return of({
        message: "Log access via RunPod Serverless - use RunPod console for detailed logs",
        runpod_console: "https://www.runpod.io/console/serverless",
        note: "Enhanced request/response logging is active on backend"
      });
    } else {
      // Regular FastAPI format
      const endpoint = `${this.baseUrl}/logs/stats`;
      return this.http.get<any>(endpoint, {
        headers: this.getHeaders()
      }).pipe(
        map(response => response.data || response),
        catchError(this.handleError)
      );
    }
  }

  /**
   * GET /logs/tail/{logType} - Get backend logs
   */
  getBackendLogs(logType: string, lines: number = 100): Observable<any> {
    // Check if this is a RunPod endpoint
    const isRunPodEndpoint = this.baseUrl.includes('api.runpod.ai');
    
    if (environment.mockMode) {
      return of({
        lines: [
          `[${new Date().toISOString()}] INFO: Mock log entry 1`,
          `[${new Date().toISOString()}] INFO: Mock log entry 2`,
          `[${new Date().toISOString()}] ERROR: Mock error entry`
        ],
        total_lines: 150,
        returned_lines: 3,
        log_type: logType
      });
    }

    if (isRunPodEndpoint) {
      // For RunPod Serverless, direct log access is limited
      return of({
        message: "RunPod Serverless logs accessible via console",
        runpod_console: "https://www.runpod.io/console/serverless",
        endpoint_id: this.baseUrl.split('/v2/')[1]?.split('/')[0] || 'unknown',
        recommendation: "Use RunPod console or check enhanced logging in request/response flow",
        log_type: logType
      });
    } else {
      // Regular FastAPI format
      const endpoint = `${this.baseUrl}/logs/tail/${logType}?lines=${lines}`;
      return this.http.get<any>(endpoint, {
        headers: this.getHeaders()
      }).pipe(
        map(response => response.data || response),
        catchError(this.handleError)
      );
    }
  }
}
