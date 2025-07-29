import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { 
  ApiResponse, 
  Process, 
  LoRAModel, 
  GenerateRequest, 
  TrainRequest,
  ProcessesResponse,
  LoRAResponse 
} from './models';
import { AuthService } from '../auth/auth.service';
import { MockApiService } from './mock-api.service';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly baseUrl = environment.apiBaseUrl;

  constructor(
    private http: HttpClient,
    private authService: AuthService,
    private mockApiService: MockApiService
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
    if (environment.mockMode) {
      return this.mockApiService.getHealth();
    }
    
    return this.http.get<ApiResponse>(`${this.baseUrl}/health`)
      .pipe(catchError(this.handleError));
  }

  /**
   * GET /processes - Get all processes
   */
  getProcesses(): Observable<Process[]> {
    if (environment.mockMode) {
      return this.mockApiService.getProcesses();
    }
    
    return this.http.get<ProcessesResponse>(`${this.baseUrl}/processes`, {
      headers: this.getHeaders()
    }).pipe(
      map(response => response.processes),
      catchError(this.handleError)
    );
  }

  /**
   * GET /lora - Get available LoRA models
   */
  getLoRAModels(): Observable<LoRAModel[]> {
    if (environment.mockMode) {
      return this.mockApiService.getLoRAModels();
    }
    
    return this.http.get<LoRAResponse>(`${this.baseUrl}/lora`, {
      headers: this.getHeaders()
    }).pipe(
      map(response => response.models),
      catchError(this.handleError)
    );
  }

  /**
   * POST /train - Start training process
   */
  startTraining(request: TrainRequest): Observable<ApiResponse> {
    if (environment.mockMode) {
      return this.mockApiService.startTraining(request);
    }
    
    return this.http.post<ApiResponse>(`${this.baseUrl}/train`, request, {
      headers: this.getHeaders()
    }).pipe(catchError(this.handleError));
  }

  /**
   * POST /generate - Start generation process
   */
  startGeneration(request: GenerateRequest): Observable<ApiResponse> {
    if (environment.mockMode) {
      return this.mockApiService.startGeneration(request);
    }
    
    return this.http.post<ApiResponse>(`${this.baseUrl}/generate`, request, {
      headers: this.getHeaders()
    }).pipe(catchError(this.handleError));
  }

  /**
   * GET /download/{id} - Get download URL for generated content
   */
  getDownloadUrl(id: string): Observable<string> {
    if (environment.mockMode) {
      return this.mockApiService.getDownloadUrl(id);
    }
    
    return this.http.get<ApiResponse<{ url: string }>>(`${this.baseUrl}/download/${id}`, {
      headers: this.getHeaders()
    }).pipe(
      map(response => response.data?.url || ''),
      catchError(this.handleError)
    );
  }

  /**
   * DELETE /processes/{id} - Cancel process
   */
  cancelProcess(id: string): Observable<ApiResponse> {
    if (environment.mockMode) {
      return this.mockApiService.cancelProcess(id);
    }
    
    return this.http.delete<ApiResponse>(`${this.baseUrl}/processes/${id}`, {
      headers: this.getHeaders()
    }).pipe(catchError(this.handleError));
  }

  /**
   * GET /processes/{id} - Get specific process details
   */
  getProcess(id: string): Observable<Process> {
    if (environment.mockMode) {
      return this.mockApiService.getProcess(id);
    }
    
    return this.http.get<ApiResponse<Process>>(`${this.baseUrl}/processes/${id}`, {
      headers: this.getHeaders()
    }).pipe(
      map(response => response.data!),
      catchError(this.handleError)
    );
  }
}
