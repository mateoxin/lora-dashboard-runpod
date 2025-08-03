import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ApiService } from './api.service';
import { AuthService } from '../auth/auth.service';
import { MockApiService } from './mock-api.service';
import { environment } from '../../environments/environment';
import { 
  Process, 
  LoRAModel, 
  GenerateRequest, 
  TrainRequest,
  ProcessesResponse,
  LoRAResponse,
  ApiResponse 
} from './models';

describe('ApiService', () => {
  let service: ApiService;
  let httpMock: HttpTestingController;
  let authService: jasmine.SpyObj<AuthService>;
  let mockApiService: jasmine.SpyObj<MockApiService>;

  const mockProcess: Process = {
    id: 'test-process-123',
    name: 'Test Process',
    type: 'training',
    status: 'running',
    progress: 50,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T01:00:00Z',
    elapsed_time: 3600,
    gpu_id: 'cuda:0',
    step: 500,
    total_steps: 1000,
    eta: 1800,
    config: { name: 'test_config' },
    error_message: null,
    output_path: '/output/test'
  };

  const mockLoRAModel: LoRAModel = {
    id: 'lora-001',
    name: 'Test LoRA Model',
    path: '/models/test.safetensors',
    created_at: '2024-01-01T00:00:00Z',
    size: 1048576,
    metadata: {
      steps: 1000,
      trigger_word: 'test_style',
      model_type: 'LoRA'
    }
  };

  beforeEach(() => {
    const authServiceSpy = jasmine.createSpyObj('AuthService', ['getToken']);
    const mockApiServiceSpy = jasmine.createSpyObj('MockApiService', [
      'getHealth',
      'getProcesses',
      'getLoRAModels',
      'startTraining',
      'startGeneration',
      'getDownloadUrl',
      'cancelProcess',
      'getProcess'
    ]);

    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        ApiService,
        { provide: AuthService, useValue: authServiceSpy },
        { provide: MockApiService, useValue: mockApiServiceSpy }
      ]
    });

    service = TestBed.inject(ApiService);
    httpMock = TestBed.inject(HttpTestingController);
    authService = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
    mockApiService = TestBed.inject(MockApiService) as jasmine.SpyObj<MockApiService>;
  });

  afterEach(() => {
    httpMock.verify();
  });

  describe('Health Check', () => {
    it('should get health status in production mode', () => {
      spyOnProperty(environment, 'mockMode', 'get').and.returnValue(false);
      const mockResponse: ApiResponse = {
        success: true,
        data: { status: 'healthy', services: { gpu: 'available' } },
        message: 'All systems operational'
      };

      service.getHealth().subscribe(response => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne(`${environment.apiBaseUrl}/health`);
      expect(req.request.method).toBe('GET');
      req.flush(mockResponse);
    });

    it('should get health status in mock mode', () => {
      spyOnProperty(environment, 'mockMode', 'get').and.returnValue(true);
      const mockResponse: ApiResponse = {
        success: true,
        data: { status: 'healthy' },
        message: 'Mock health check'
      };
      mockApiService.getHealth.and.returnValue(of(mockResponse));

      service.getHealth().subscribe(response => {
        expect(response).toEqual(mockResponse);
      });

      expect(mockApiService.getHealth).toHaveBeenCalled();
      httpMock.expectNone(`${environment.apiBaseUrl}/health`);
    });

    it('should handle health check error', () => {
      spyOnProperty(environment, 'mockMode', 'get').and.returnValue(false);
      const errorMessage = 'Server error';

      service.getHealth().subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.message).toContain(errorMessage);
        }
      });

      const req = httpMock.expectOne(`${environment.apiBaseUrl}/health`);
      req.flush({ message: errorMessage }, { status: 500, statusText: 'Server Error' });
    });
  });

  describe('Authentication Headers', () => {
    it('should include authorization header when token exists', () => {
      spyOnProperty(environment, 'mockMode', 'get').and.returnValue(false);
      authService.getToken.and.returnValue('test-token-123');

      service.getHealth().subscribe();

      const req = httpMock.expectOne(`${environment.apiBaseUrl}/health`);
      expect(req.request.headers.get('Authorization')).toBe('Bearer test-token-123');
      req.flush({ success: true });
    });

    it('should include RunPod token when available', () => {
      spyOnProperty(environment, 'mockMode', 'get').and.returnValue(false);
      spyOnProperty(environment, 'runpodToken', 'get').and.returnValue('runpod-token-456');

      service.getHealth().subscribe();

      const req = httpMock.expectOne(`${environment.apiBaseUrl}/health`);
      expect(req.request.headers.get('X-RunPod-Token')).toBe('runpod-token-456');
      req.flush({ success: true });
    });

    it('should not include auth headers when tokens are missing', () => {
      spyOnProperty(environment, 'mockMode', 'get').and.returnValue(false);
      authService.getToken.and.returnValue(null);
      spyOnProperty(environment, 'runpodToken', 'get').and.returnValue(undefined);

      service.getHealth().subscribe();

      const req = httpMock.expectOne(`${environment.apiBaseUrl}/health`);
      expect(req.request.headers.has('Authorization')).toBeFalse();
      expect(req.request.headers.has('X-RunPod-Token')).toBeFalse();
      req.flush({ success: true });
    });
  });

  describe('Processes', () => {
    it('should get all processes', () => {
      spyOnProperty(environment, 'mockMode', 'get').and.returnValue(false);
      const mockResponse: ProcessesResponse = {
        processes: [mockProcess]
      };

      service.getProcesses().subscribe(processes => {
        expect(processes).toEqual([mockProcess]);
      });

      const req = httpMock.expectOne(`${environment.apiBaseUrl}/processes`);
      expect(req.request.method).toBe('GET');
      expect(req.request.headers.get('Content-Type')).toBe('application/json');
      req.flush(mockResponse);
    });

    it('should get specific process', () => {
      spyOnProperty(environment, 'mockMode', 'get').and.returnValue(false);
      const processId = 'test-process-123';
      const mockResponse: ApiResponse<Process> = {
        success: true,
        data: mockProcess
      };

      service.getProcess(processId).subscribe(process => {
        expect(process).toEqual(mockProcess);
      });

      const req = httpMock.expectOne(`${environment.apiBaseUrl}/processes/${processId}`);
      expect(req.request.method).toBe('GET');
      req.flush(mockResponse);
    });

    it('should handle get process error', () => {
      spyOnProperty(environment, 'mockMode', 'get').and.returnValue(false);
      const processId = 'nonexistent-process';

      service.getProcess(processId).subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.message).toContain('Process not found');
        }
      });

      const req = httpMock.expectOne(`${environment.apiBaseUrl}/processes/${processId}`);
      req.flush({ message: 'Process not found' }, { status: 404, statusText: 'Not Found' });
    });

    it('should cancel process', () => {
      spyOnProperty(environment, 'mockMode', 'get').and.returnValue(false);
      const processId = 'test-process-123';
      const mockResponse: ApiResponse = {
        success: true,
        message: 'Process cancelled successfully'
      };

      service.cancelProcess(processId).subscribe(response => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne(`${environment.apiBaseUrl}/processes/${processId}`);
      expect(req.request.method).toBe('DELETE');
      req.flush(mockResponse);
    });
  });

  describe('LoRA Models', () => {
    it('should get LoRA models', () => {
      spyOnProperty(environment, 'mockMode', 'get').and.returnValue(false);
      const mockResponse: LoRAResponse = {
        models: [mockLoRAModel]
      };

      service.getLoRAModels().subscribe(models => {
        expect(models).toEqual([mockLoRAModel]);
      });

      const req = httpMock.expectOne(`${environment.apiBaseUrl}/lora`);
      expect(req.request.method).toBe('GET');
      req.flush(mockResponse);
    });

    it('should handle empty LoRA models response', () => {
      spyOnProperty(environment, 'mockMode', 'get').and.returnValue(false);
      const mockResponse: LoRAResponse = {
        models: []
      };

      service.getLoRAModels().subscribe(models => {
        expect(models).toEqual([]);
      });

      const req = httpMock.expectOne(`${environment.apiBaseUrl}/lora`);
      req.flush(mockResponse);
    });
  });

  describe('Training', () => {
    it('should start training process', () => {
      spyOnProperty(environment, 'mockMode', 'get').and.returnValue(false);
      const trainRequest: TrainRequest = {
        config: 'job: extension\nconfig:\n  name: test_training'
      };
      const mockResponse: ApiResponse = {
        success: true,
        data: { process_id: 'training-123' },
        message: 'Training started'
      };

      service.startTraining(trainRequest).subscribe(response => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne(`${environment.apiBaseUrl}/train`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(trainRequest);
      req.flush(mockResponse);
    });

    it('should handle training start error', () => {
      spyOnProperty(environment, 'mockMode', 'get').and.returnValue(false);
      const trainRequest: TrainRequest = {
        config: 'invalid yaml: ['
      };

      service.startTraining(trainRequest).subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.message).toContain('Invalid configuration');
        }
      });

      const req = httpMock.expectOne(`${environment.apiBaseUrl}/train`);
      req.flush({ message: 'Invalid configuration' }, { status: 400, statusText: 'Bad Request' });
    });

    it('should validate training config format', () => {
      spyOnProperty(environment, 'mockMode', 'get').and.returnValue(false);
      const trainRequest: TrainRequest = {
        config: ''  // Empty config
      };

      service.startTraining(trainRequest).subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.message).toContain('Configuration required');
        }
      });

      const req = httpMock.expectOne(`${environment.apiBaseUrl}/train`);
      req.flush({ message: 'Configuration required' }, { status: 422, statusText: 'Unprocessable Entity' });
    });
  });

  describe('Generation', () => {
    it('should start generation process', () => {
      spyOnProperty(environment, 'mockMode', 'get').and.returnValue(false);
      const generateRequest: GenerateRequest = {
        config: 'job: generate\nconfig:\n  name: test_generation'
      };
      const mockResponse: ApiResponse = {
        success: true,
        data: { process_id: 'generation-456' },
        message: 'Generation started'
      };

      service.startGeneration(generateRequest).subscribe(response => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne(`${environment.apiBaseUrl}/generate`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(generateRequest);
      req.flush(mockResponse);
    });

    it('should handle generation start error', () => {
      spyOnProperty(environment, 'mockMode', 'get').and.returnValue(false);
      const generateRequest: GenerateRequest = {
        config: 'invalid yaml'
      };

      service.startGeneration(generateRequest).subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.message).toContain('Invalid configuration');
        }
      });

      const req = httpMock.expectOne(`${environment.apiBaseUrl}/generate`);
      req.flush({ message: 'Invalid configuration' }, { status: 400, statusText: 'Bad Request' });
    });
  });

  describe('Downloads', () => {
    it('should get download URL', () => {
      spyOnProperty(environment, 'mockMode', 'get').and.returnValue(false);
      const processId = 'completed-process-123';
      const downloadUrl = 'https://storage.com/download/results.zip';
      const mockResponse: ApiResponse<{ url: string }> = {
        success: true,
        data: { url: downloadUrl }
      };

      service.getDownloadUrl(processId).subscribe(url => {
        expect(url).toBe(downloadUrl);
      });

      const req = httpMock.expectOne(`${environment.apiBaseUrl}/download/${processId}`);
      expect(req.request.method).toBe('GET');
      req.flush(mockResponse);
    });

    it('should handle download URL error for incomplete process', () => {
      spyOnProperty(environment, 'mockMode', 'get').and.returnValue(false);
      const processId = 'running-process-123';

      service.getDownloadUrl(processId).subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.message).toContain('Process not completed');
        }
      });

      const req = httpMock.expectOne(`${environment.apiBaseUrl}/download/${processId}`);
      req.flush({ message: 'Process not completed' }, { status: 400, statusText: 'Bad Request' });
    });

    it('should handle missing download URL in response', () => {
      spyOnProperty(environment, 'mockMode', 'get').and.returnValue(false);
      const processId = 'test-process-123';
      const mockResponse: ApiResponse<{ url?: string }> = {
        success: true,
        data: {}  // Missing URL
      };

      service.getDownloadUrl(processId).subscribe(url => {
        expect(url).toBe('');  // Should return empty string
      });

      const req = httpMock.expectOne(`${environment.apiBaseUrl}/download/${processId}`);
      req.flush(mockResponse);
    });
  });

  describe('Mock Mode Behavior', () => {
    beforeEach(() => {
      spyOnProperty(environment, 'mockMode', 'get').and.returnValue(true);
    });

    it('should use mock service for all operations in mock mode', () => {
      const mockResponse: ApiResponse = { success: true, data: 'mock data' };
      
      // Setup all mock service methods
      mockApiService.getHealth.and.returnValue(of(mockResponse));
      mockApiService.getProcesses.and.returnValue(of([mockProcess]));
      mockApiService.getLoRAModels.and.returnValue(of([mockLoRAModel]));
      mockApiService.startTraining.and.returnValue(of(mockResponse));
      mockApiService.startGeneration.and.returnValue(of(mockResponse));
      mockApiService.getDownloadUrl.and.returnValue(of('mock-url'));
      mockApiService.cancelProcess.and.returnValue(of(mockResponse));
      mockApiService.getProcess.and.returnValue(of(mockProcess));

      // Test all methods use mock service
      service.getHealth().subscribe();
      service.getProcesses().subscribe();
      service.getLoRAModels().subscribe();
      service.startTraining({ config: 'test' }).subscribe();
      service.startGeneration({ config: 'test' }).subscribe();
      service.getDownloadUrl('test-id').subscribe();
      service.cancelProcess('test-id').subscribe();
      service.getProcess('test-id').subscribe();

      expect(mockApiService.getHealth).toHaveBeenCalled();
      expect(mockApiService.getProcesses).toHaveBeenCalled();
      expect(mockApiService.getLoRAModels).toHaveBeenCalled();
      expect(mockApiService.startTraining).toHaveBeenCalled();
      expect(mockApiService.startGeneration).toHaveBeenCalled();
      expect(mockApiService.getDownloadUrl).toHaveBeenCalled();
      expect(mockApiService.cancelProcess).toHaveBeenCalled();
      expect(mockApiService.getProcess).toHaveBeenCalled();

      // Verify no HTTP calls were made
      httpMock.expectNone(() => true);
    });
  });

  describe('Error Handling', () => {
    beforeEach(() => {
      spyOnProperty(environment, 'mockMode', 'get').and.returnValue(false);
    });

    it('should handle network errors', () => {
      service.getHealth().subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.message).toContain('network');
        }
      });

      const req = httpMock.expectOne(`${environment.apiBaseUrl}/health`);
      req.error(new ErrorEvent('network error'));
    });

    it('should handle HTTP error responses', () => {
      const errorCodes = [400, 401, 403, 404, 500, 502, 503];
      
      errorCodes.forEach(statusCode => {
        service.getHealth().subscribe({
          next: () => fail(`should have failed for ${statusCode}`),
          error: (error) => {
            expect(error.message).toContain(statusCode.toString());
          }
        });

        const req = httpMock.expectOne(`${environment.apiBaseUrl}/health`);
        req.flush({ message: 'Error' }, { status: statusCode, statusText: 'Error' });
      });
    });

    it('should handle malformed JSON responses', () => {
      service.getHealth().subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error).toBeDefined();
        }
      });

      const req = httpMock.expectOne(`${environment.apiBaseUrl}/health`);
      req.flush('invalid json', { headers: { 'Content-Type': 'application/json' } });
    });

    it('should handle timeout errors', fakeAsync(() => {
      service.getHealth().subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.message).toContain('timeout');
        }
      });

      const req = httpMock.expectOne(`${environment.apiBaseUrl}/health`);
      tick(30000); // Simulate timeout
      req.error(new ErrorEvent('timeout'));
    }));
  });

  describe('Request Validation', () => {
    beforeEach(() => {
      spyOnProperty(environment, 'mockMode', 'get').and.returnValue(false);
    });

    it('should validate process ID format', () => {
      const invalidIds = ['', null, undefined, '   ', 'invalid/id', 'id with spaces'];
      
      invalidIds.forEach(id => {
        if (id !== null && id !== undefined) {
          service.getProcess(id as string).subscribe();
          const req = httpMock.expectOne(`${environment.apiBaseUrl}/processes/${id}`);
          req.flush({ success: true, data: mockProcess });
        }
      });
    });

    it('should handle special characters in URLs', () => {
      const specialIds = ['id%20with%20encoding', 'id-with-dashes', 'id_with_underscores'];
      
      specialIds.forEach(id => {
        service.getProcess(id).subscribe();
        const req = httpMock.expectOne(`${environment.apiBaseUrl}/processes/${id}`);
        req.flush({ success: true, data: mockProcess });
      });
    });
  });

  describe('Concurrent Requests', () => {
    beforeEach(() => {
      spyOnProperty(environment, 'mockMode', 'get').and.returnValue(false);
    });

    it('should handle multiple concurrent requests', () => {
      const requestCount = 5;
      const responses: ApiResponse[] = [];

      for (let i = 0; i < requestCount; i++) {
        service.getHealth().subscribe(response => {
          responses.push(response);
        });
      }

      const requests = httpMock.match(`${environment.apiBaseUrl}/health`);
      expect(requests.length).toBe(requestCount);

      requests.forEach((req, index) => {
        req.flush({ success: true, data: { id: index } });
      });

      expect(responses.length).toBe(requestCount);
    });
  });
});

// Helper function for Observable creation
import { of } from 'rxjs';
import { fakeAsync, tick } from '@angular/core/testing';
