export interface Process {
  id: string;
  name: string;
  type: 'training' | 'generation';
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  created_at: string;
  updated_at: string;
  elapsed_time?: number;
  gpu_id?: string;
  step?: number;
  total_steps?: number;
  eta?: number;
  config?: any;
  error_message?: string;
  output_path?: string;
}

export interface LoRAModel {
  id: string;
  name: string;
  path: string;
  created_at: string;
  size: number;
  metadata?: {
    steps: number;
    trigger_word?: string;
    model_type?: string;
  };
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface AuthUser {
  username: string;
  token: string;
  loginTime: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface GenerateRequest {
  config: string; // YAML configuration
}

export interface TrainRequest {
  config: string; // YAML configuration
}

export interface DownloadRequest {
  id: string;
}

export interface ProcessesResponse {
  processes: Process[];
}

export interface LoRAResponse {
  models: LoRAModel[];
}

// 📁 FILE UPLOAD INTERFACES

export interface UploadedFile {
  filename: string;
  path: string;
  size: number;
  content_type: string;
  uploaded_at: string;
}

export interface TrainingDataUploadRequest {
  files: File[];
  training_name: string;
  trigger_word: string;
  cleanup_existing?: boolean;
}

export interface TrainingDataUploadResponse {
  uploaded_files: UploadedFile[];
  training_folder: string;
  total_images: number;
  total_captions: number;
  message: string;
}

export interface BulkDownloadRequest {
  process_ids: string[];
  include_images?: boolean;
  include_loras?: boolean;
}

export interface DownloadItem {
  filename: string;
  url: string;
  size?: number;
  type: 'image' | 'lora' | 'other';
}

export interface BulkDownloadResponse {
  download_items: DownloadItem[];
  zip_url?: string;
  total_files: number;
  total_size: number;
}

export const HARDCODED_CREDENTIALS = {
  username: 'Mateusz',
  password: 'Gramercy'
} as const;

// Export enums as const objects for compatibility
export const ProcessStatus = {
  PENDING: 'pending',
  RUNNING: 'running', 
  COMPLETED: 'completed',
  FAILED: 'failed',
  CANCELLED: 'cancelled'
} as const;

export const ProcessType = {
  TRAINING: 'training',
  GENERATION: 'generation'
} as const;

export type ProcessStatusType = typeof ProcessStatus[keyof typeof ProcessStatus];
export type ProcessTypeType = typeof ProcessType[keyof typeof ProcessType]; 