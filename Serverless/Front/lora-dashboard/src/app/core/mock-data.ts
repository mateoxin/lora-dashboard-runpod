/**
 * Mock data for testing the LoRA Dashboard application
 */

import { Process, LoRAModel, ProcessStatus, ProcessType } from './models';

export const MOCK_PROCESSES: Process[] = [
  {
    id: '1',
    name: 'Matt_flux_lora_training_v1',
    type: ProcessType.TRAINING,
    status: ProcessStatus.RUNNING,
    progress: 45.5,
    created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
    updated_at: new Date(Date.now() - 5 * 60 * 1000).toISOString(), // 5 minutes ago
    elapsed_time: 7200, // 2 hours
    gpu_id: 'A40-0',
    step: 455,
    total_steps: 1000,
    eta: 3600, // 1 hour remaining
    config: {
      job: 'extension',
      config: {
        name: 'Matt_flux_lora_training_v1',
        process: [{
          type: 'sd_trainer',
          trigger_word: 'Matt',
          device: 'cuda:0'
        }]
      }
    }
  },
  {
    id: '2',
    name: 'Matt_generation_beach_scene',
    type: ProcessType.GENERATION,
    status: ProcessStatus.COMPLETED,
    progress: 100,
    created_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(), // 4 hours ago
    updated_at: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(), // 3 hours ago
    elapsed_time: 1800, // 30 minutes
    gpu_id: 'A40-1',
    step: 20,
    total_steps: 20,
    config: {
      job: 'generate',
      config: {
        name: 'Matt_generation_beach_scene',
        process: [{
          type: 'to_folder',
          device: 'cuda:0'
        }]
      }
    },
    output_path: 's3://lora-bucket/results/2/'
  },
  {
    id: '3',
    name: 'Landscape_LoRA_v2',
    type: ProcessType.TRAINING,
    status: ProcessStatus.PENDING,
    progress: 0,
    created_at: new Date(Date.now() - 10 * 60 * 1000).toISOString(), // 10 minutes ago
    updated_at: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
    elapsed_time: 0,
    config: {
      job: 'extension',
      config: {
        name: 'Landscape_LoRA_v2',
        process: [{
          type: 'sd_trainer',
          trigger_word: 'landscape',
          device: 'cuda:0'
        }]
      }
    }
  },
  {
    id: '4',
    name: 'Portrait_generation_test',
    type: ProcessType.GENERATION,
    status: ProcessStatus.FAILED,
    progress: 15,
    created_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(), // 6 hours ago
    updated_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(), // 5 hours ago
    elapsed_time: 300, // 5 minutes
    gpu_id: 'A40-2',
    step: 3,
    total_steps: 20,
    error_message: 'CUDA out of memory error during generation',
    config: {
      job: 'generate',
      config: {
        name: 'Portrait_generation_test'
      }
    }
  },
  {
    id: '5',
    name: 'Abstract_art_LoRA',
    type: ProcessType.TRAINING,
    status: ProcessStatus.COMPLETED,
    progress: 100,
    created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), // 1 day ago
    updated_at: new Date(Date.now() - 20 * 60 * 60 * 1000).toISOString(), // 20 hours ago
    elapsed_time: 14400, // 4 hours
    gpu_id: 'A40-0',
    step: 1000,
    total_steps: 1000,
    config: {
      job: 'extension',
      config: {
        name: 'Abstract_art_LoRA',
        process: [{
          type: 'sd_trainer',
          trigger_word: 'abstract',
          device: 'cuda:0'
        }]
      }
    },
    output_path: 's3://lora-bucket/results/5/'
  },
  {
    id: '6',
    name: 'Style_transfer_gen',
    type: ProcessType.GENERATION,
    status: ProcessStatus.CANCELLED,
    progress: 25,
    created_at: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(), // 8 hours ago
    updated_at: new Date(Date.now() - 7 * 60 * 60 * 1000).toISOString(), // 7 hours ago
    elapsed_time: 600, // 10 minutes
    gpu_id: 'A40-1',
    step: 5,
    total_steps: 20,
    config: {
      job: 'generate',
      config: {
        name: 'Style_transfer_gen'
      }
    }
  }
];

export const MOCK_LORA_MODELS: LoRAModel[] = [
  {
    id: 'lora-1',
    name: 'Matt_flux_lora_v1',
    path: '/workspace/ai-toolkit/output/mati_flux_lora_v1/mati_flux_lora_v1.safetensors',
    created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(), // 7 days ago
    size: 144 * 1024 * 1024, // 144 MB
    metadata: {
      steps: 1000,
      trigger_word: 'Matt',
      model_type: 'FLUX'
    }
  },
  {
    id: 'lora-2',
    name: 'Abstract_art_LoRA',
    path: '/workspace/ai-toolkit/output/abstract_lora_v2/abstract_lora_v2.safetensors',
    created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), // 2 days ago
    size: 156 * 1024 * 1024, // 156 MB
    metadata: {
      steps: 1500,
      trigger_word: 'abstract',
      model_type: 'FLUX'
    }
  },
  {
    id: 'lora-3',
    name: 'Portrait_style_v3',
    path: 's3://lora-bucket/models/portrait_v3.safetensors',
    created_at: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(), // 14 days ago
    size: 132 * 1024 * 1024, // 132 MB
    metadata: {
      steps: 800,
      trigger_word: 'portrait',
      model_type: 'FLUX'
    }
  },
  {
    id: 'lora-4',
    name: 'Landscape_hdri_v1',
    path: '/workspace/ai-toolkit/output/landscape_hdri/landscape_hdri.safetensors',
    created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(), // 5 days ago
    size: 168 * 1024 * 1024, // 168 MB
    metadata: {
      steps: 1200,
      trigger_word: 'landscape',
      model_type: 'FLUX'
    }
  },
  {
    id: 'lora-5',
    name: 'Anime_style_fusion',
    path: 's3://lora-bucket/models/anime_fusion_v2.safetensors',
    created_at: new Date(Date.now() - 21 * 24 * 60 * 60 * 1000).toISOString(), // 21 days ago
    size: 178 * 1024 * 1024, // 178 MB
    metadata: {
      steps: 2000,
      trigger_word: 'anime',
      model_type: 'FLUX'
    }
  }
];

// Mock API responses
export const MOCK_API_RESPONSES = {
  health: {
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
  },
  
  startTraining: {
    success: true,
    data: { process_id: 'new-training-' + Date.now() },
    message: 'Training process started successfully'
  },
  
  startGeneration: {
    success: true,
    data: { process_id: 'new-generation-' + Date.now() },
    message: 'Generation process started successfully'
  },
  
  downloadUrl: {
    success: true,
    data: {
      url: 'https://storage.runpod.io/bucket/results/example.zip?expires=1234567890'
    }
  },
  
  cancelProcess: {
    success: true,
    message: 'Process cancelled successfully'
  }
};

// Helper function to simulate network delay
export const simulateNetworkDelay = (ms: number = 500): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

// Function to randomly update running processes (for demo)
export const updateRunningProcesses = (): void => {
  MOCK_PROCESSES.forEach(process => {
    if (process.status === ProcessStatus.RUNNING && process.step && process.total_steps) {
      // Simulate progress
      if (process.step < process.total_steps) {
        process.step += Math.floor(Math.random() * 3) + 1;
        process.progress = (process.step / process.total_steps) * 100;
        process.elapsed_time = (process.elapsed_time || 0) + 30; // Add 30 seconds
        
        // Update ETA
        const remainingSteps = process.total_steps - process.step;
        const avgTimePerStep = process.elapsed_time / process.step;
        process.eta = Math.floor(remainingSteps * avgTimePerStep);
        
        process.updated_at = new Date().toISOString();
        
        // Sometimes complete the process
        if (process.step >= process.total_steps || Math.random() < 0.02) {
          process.status = ProcessStatus.COMPLETED;
          process.progress = 100;
          process.step = process.total_steps;
          process.eta = 0;
          process.gpu_id = undefined;
          
          if (process.type === ProcessType.GENERATION) {
            process.output_path = `s3://lora-bucket/results/${process.id}/`;
          }
        }
      }
    }
  });
}; 