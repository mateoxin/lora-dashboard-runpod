/**
 * Mock API Service
 * Provides mock data for testing without backend
 */

import { Injectable } from '@angular/core';
import { Observable, of, throwError } from 'rxjs';
import { delay } from 'rxjs/operators';
import { 
  MOCK_PROCESSES, 
  MOCK_LORA_MODELS, 
  updateRunningProcesses
} from './mock-data';
import { 
  ApiResponse, 
  Process, 
  LoRAModel, 
  GenerateRequest, 
  TrainRequest 
} from './models';

@Injectable({
  providedIn: 'root'
})
export class MockApiService {
  private processes = [...MOCK_PROCESSES];
  private loraModels = [...MOCK_LORA_MODELS];

  constructor() {
    // Simulate real-time updates for running processes
    setInterval(() => {
      updateRunningProcesses();
    }, 5000);
  }

  /**
   * GET /health - Health check
   */
  getHealth(): Observable<ApiResponse> {
    const response = {
      success: true,
      data: {
        status: 'healthy',
        services: {
          process_manager: 'healthy',
          storage: 'healthy',
          gpu_manager: {
            total_gpus: 3,
            allocated_gpus: 1,
            max_concurrent: 10
          }
        }
      },
      message: 'API is healthy'
    };
    return of(response).pipe(delay(200));
  }

  /**
   * GET /processes - Get all processes
   */
  getProcesses(): Observable<Process[]> {
    // Sort by created_at descending (newest first)
    const sortedProcesses = [...this.processes].sort((a, b) => 
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );
    
    return of(sortedProcesses).pipe(delay(300));
  }

  /**
   * GET /lora - Get available LoRA models
   */
  getLoRAModels(): Observable<LoRAModel[]> {
    return of([...this.loraModels]).pipe(delay(400));
  }

  /**
   * POST /train - Start training process
   */
  startTraining(request: TrainRequest): Observable<ApiResponse> {
    const newProcessId = 'training-' + Date.now();
    
    // Parse config to get name
    let processName = 'New Training Process';
    try {
      // Basic YAML parsing for name
      const lines = request.config.split('\n');
      const nameLine = lines.find(line => line.includes('name:'));
      if (nameLine) {
        processName = nameLine.split('name:')[1].trim().replace(/['"]/g, '');
      }
    } catch (e) {
      console.warn('Could not parse training config name');
    }

    const newProcess: Process = {
      id: newProcessId,
      name: processName,
      type: 'training',
      status: 'pending',
      progress: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      elapsed_time: 0,
      step: 0,
      total_steps: 1000,
      config: request.config
    };

    // Add to processes list
    this.processes.unshift(newProcess);

    // Simulate starting the process after a delay
    setTimeout(() => {
      const process = this.processes.find(p => p.id === newProcessId);
      if (process) {
        process.status = 'running';
        process.gpu_id = 'A40-' + Math.floor(Math.random() * 3);
        process.updated_at = new Date().toISOString();
      }
    }, 2000);

    const response = {
      success: true,
      data: { process_id: newProcessId },
      message: 'Training process started successfully'
    };

    return of(response).pipe(delay(500));
  }

  /**
   * POST /generate - Start generation process
   */
  startGeneration(request: GenerateRequest): Observable<ApiResponse> {
    const newProcessId = 'generation-' + Date.now();
    
    // Parse config to get name
    let processName = 'New Generation Process';
    try {
      const lines = request.config.split('\n');
      const nameLine = lines.find(line => line.includes('name:'));
      if (nameLine) {
        processName = nameLine.split('name:')[1].trim().replace(/['"]/g, '');
      }
    } catch (e) {
      console.warn('Could not parse generation config name');
    }

    const newProcess: Process = {
      id: newProcessId,
      name: processName,
      type: 'generation',
      status: 'pending',
      progress: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      elapsed_time: 0,
      step: 0,
      total_steps: 20,
      config: request.config
    };

    // Add to processes list
    this.processes.unshift(newProcess);

    // Simulate starting the process after a delay
    setTimeout(() => {
      const process = this.processes.find(p => p.id === newProcessId);
      if (process) {
        process.status = 'running';
        process.gpu_id = 'A40-' + Math.floor(Math.random() * 3);
        process.updated_at = new Date().toISOString();
      }
    }, 1000);

    const response = {
      success: true,
      data: { process_id: newProcessId },
      message: 'Generation process started successfully'
    };

    return of(response).pipe(delay(400));
  }

  /**
   * GET /download/{id} - Get download URL
   */
  getDownloadUrl(id: string): Observable<string> {
    const process = this.processes.find(p => p.id === id);
    
    if (!process) {
      return throwError(() => new Error('Process not found'));
    }
    
    if (process.status !== 'completed') {
      return throwError(() => new Error('Process not completed'));
    }
    
    // Generate mock download URL
    const mockUrl = `https://storage.runpod.io/bucket/results/${id}/output.zip?expires=${Date.now() + 3600000}`;
    
    return of(mockUrl).pipe(delay(300));
  }

  /**
   * DELETE /processes/{id} - Cancel process
   */
  cancelProcess(id: string): Observable<ApiResponse> {
    const processIndex = this.processes.findIndex(p => p.id === id);
    
    if (processIndex === -1) {
      return throwError(() => new Error('Process not found'));
    }
    
    const process = this.processes[processIndex];
    
    if (process.status !== 'pending' && process.status !== 'running') {
      return throwError(() => new Error('Cannot cancel process in current state'));
    }
    
    // Update process status
    process.status = 'cancelled';
    process.updated_at = new Date().toISOString();
    process.gpu_id = undefined;
    
    const response = {
      success: true,
      message: 'Process cancelled successfully'
    };
    
    return of(response).pipe(delay(200));
  }

  /**
   * GET /processes/{id} - Get specific process
   */
  getProcess(id: string): Observable<Process> {
    const process = this.processes.find(p => p.id === id);
    
    if (!process) {
      return throwError(() => new Error('Process not found'));
    }
    
    return of({ ...process }).pipe(delay(200));
  }

  /**
   * Add a new LoRA model (for testing)
   */
  addMockLoRAModel(name: string): void {
    const newModel: LoRAModel = {
      id: 'lora-' + Date.now(),
      name: name,
      path: `/workspace/ai-toolkit/output/${name}/${name}.safetensors`,
      created_at: new Date().toISOString(),
      size: 150 * 1024 * 1024, // 150 MB
      metadata: {
        steps: 1000,
        trigger_word: name.toLowerCase(),
        model_type: 'FLUX'
      }
    };
    
    this.loraModels.unshift(newModel);
  }

  /**
   * Simulate random events for demo purposes
   */
  simulateRandomEvents(): void {
    setInterval(() => {
      // Sometimes add a new pending process
      if (Math.random() < 0.1) { // 10% chance every 10 seconds
        const randomNames = [
          'Auto_generated_training',
          'Style_experiment_v' + Math.floor(Math.random() * 10),
          'Test_generation_' + Math.floor(Math.random() * 100)
        ];
        
        const randomName = randomNames[Math.floor(Math.random() * randomNames.length)];
        const isTraining = Math.random() < 0.6; // 60% chance of training
        
        const newProcess: Process = {
          id: 'auto-' + Date.now(),
          name: randomName,
          type: isTraining ? 'training' : 'generation',
          status: 'pending',
          progress: 0,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          elapsed_time: 0,
          step: 0,
          total_steps: isTraining ? 1000 : 20
        };
        
        this.processes.unshift(newProcess);
        
        // Start it after a random delay
        setTimeout(() => {
          const process = this.processes.find(p => p.id === newProcess.id);
          if (process && process.status === 'pending') {
            process.status = 'running';
            process.gpu_id = 'A40-' + Math.floor(Math.random() * 3);
            process.updated_at = new Date().toISOString();
          }
        }, Math.random() * 5000 + 1000);
      }
    }, 10000); // Check every 10 seconds
  }

  // 📁 FILE UPLOAD MOCK METHODS

  /**
   * Mock upload training data
   */
  uploadTrainingData(request: any): Observable<any> {
    const mockResponse = {
      uploaded_files: request.files.map((file: any, index: number) => ({
        filename: file.name || `image_${index}.jpg`,
        path: `/workspace/training_data/mock_training/${file.name || `image_${index}.jpg`}`,
        size: file.size || 1024000,
        content_type: file.type || 'image/jpeg',
        uploaded_at: new Date().toISOString()
      })),
      training_folder: `/workspace/training_data/mock_training`,
      total_images: request.files.filter((f: any) => f.type?.startsWith('image/')).length,
      total_captions: request.files.filter((f: any) => f.name?.endsWith('.txt')).length,
      message: 'Training data uploaded successfully (Mock Mode)'
    };

    return of(mockResponse).pipe(delay(2000));
  }

  /**
   * Mock bulk download URLs
   */
  getBulkDownloadUrls(request: any): Observable<any> {
    const mockItems = [];
    
    for (const processId of request.process_ids) {
      if (request.include_images !== false) {
        mockItems.push({
          filename: `generated_image_${processId}_1.png`,
          url: `https://mock-storage.example.com/results/${processId}/generated_image_1.png`,
          size: 2048000,
          type: 'image'
        });
        mockItems.push({
          filename: `generated_image_${processId}_2.png`,
          url: `https://mock-storage.example.com/results/${processId}/generated_image_2.png`,
          size: 1856000,
          type: 'image'
        });
      }

      if (request.include_loras !== false) {
        mockItems.push({
          filename: `lora_model_${processId}.safetensors`,
          url: `https://mock-storage.example.com/results/${processId}/lora_model.safetensors`,
          size: 147456000,
          type: 'lora'
        });
      }
    }

    const mockResponse = {
      download_items: mockItems,
      total_files: mockItems.length,
      total_size: mockItems.reduce((sum, item) => sum + (item.size || 0), 0)
    };

    return of(mockResponse).pipe(delay(1000));
  }
} 