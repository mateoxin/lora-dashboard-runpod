import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatSelectModule } from '@angular/material/select';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { FormsModule } from '@angular/forms';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { of } from 'rxjs';

import { LogsTabComponent } from './logs-tab.component';
import { ApiService } from '../../core/api.service';
import { FrontendLoggerService } from '../../core/frontend-logger.service';

describe('LogsTabComponent', () => {
  let component: LogsTabComponent;
  let fixture: ComponentFixture<LogsTabComponent>;
  let mockApiService: jasmine.SpyObj<ApiService>;
  let mockLoggerService: jasmine.SpyObj<FrontendLoggerService>;

  beforeEach(async () => {
    const apiServiceSpy = jasmine.createSpyObj('ApiService', [
      'getBackendLogs',
      'getLogStats',
      'formatFileSize'
    ]);
    const loggerServiceSpy = jasmine.createSpyObj('FrontendLoggerService', [
      'getLogs',
      'clearLogs'
    ]);

    await TestBed.configureTestingModule({
      declarations: [LogsTabComponent],
      imports: [
        MatSnackBarModule,
        MatSelectModule,
        MatSlideToggleModule,
        MatIconModule,
        MatButtonModule,
        MatProgressSpinnerModule,
        MatTooltipModule,
        FormsModule,
        NoopAnimationsModule
      ],
      providers: [
        { provide: ApiService, useValue: apiServiceSpy },
        { provide: FrontendLoggerService, useValue: loggerServiceSpy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(LogsTabComponent);
    component = fixture.componentInstance;
    mockApiService = TestBed.inject(ApiService) as jasmine.SpyObj<ApiService>;
    mockLoggerService = TestBed.inject(FrontendLoggerService) as jasmine.SpyObj<FrontendLoggerService>;

    // Setup default mock returns
    mockApiService.getBackendLogs.and.returnValue(of({
      lines: ['Test log line 1', 'Test log line 2'],
      total_lines: 2,
      returned_lines: 2,
      log_type: 'app'
    }));
    mockApiService.getLogStats.and.returnValue(of({
      log_directory: '/workspace/logs',
      files: [
        { name: 'app.log', size: 1024, modified: new Date().toISOString() }
      ]
    }));
    mockApiService.formatFileSize.and.returnValue('1 KB');
    mockLoggerService.getLogs.and.returnValue([
      {
        timestamp: Date.now(),
        level: 'info',
        message: 'Test frontend log'
      }
    ]);
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load backend logs on init', () => {
    fixture.detectChanges();
    expect(mockApiService.getBackendLogs).toHaveBeenCalledWith('app', 100);
    expect(component.backendLogs).toEqual(['Test log line 1', 'Test log line 2']);
  });

  it('should load frontend logs on init', () => {
    fixture.detectChanges();
    expect(mockLoggerService.getLogs).toHaveBeenCalled();
    expect(component.frontendLogs.length).toBe(1);
  });

  it('should change log type and reload', () => {
    fixture.detectChanges();
    component.selectedLogType = 'errors';
    component.onLogTypeChange();
    expect(mockApiService.getBackendLogs).toHaveBeenCalledWith('errors', 100);
  });

  it('should change max lines and reload', () => {
    fixture.detectChanges();
    component.maxLines = 200;
    component.onMaxLinesChange();
    expect(mockApiService.getBackendLogs).toHaveBeenCalledWith('app', 200);
  });

  it('should toggle auto refresh', () => {
    component.autoRefresh = false;
    component.toggleAutoRefresh();
    expect(component.autoRefresh).toBe(true);
  });

  it('should return correct log level color class', () => {
    expect(component.getLogLevelColor('ERROR: Something went wrong')).toBe('text-red-600');
    expect(component.getLogLevelColor('WARNING: Be careful')).toBe('text-yellow-600');
    expect(component.getLogLevelColor('INFO: Information')).toBe('text-blue-600');
    expect(component.getLogLevelColor('DEBUG: Debug info')).toBe('text-gray-600');
    expect(component.getLogLevelColor('Regular log line')).toBe('text-gray-800');
  });

  it('should return correct frontend log level color', () => {
    expect(component.getFrontendLogLevelColor({ level: 'error' })).toBe('text-red-600');
    expect(component.getFrontendLogLevelColor({ level: 'warn' })).toBe('text-yellow-600');
    expect(component.getFrontendLogLevelColor({ level: 'info' })).toBe('text-blue-600');
    expect(component.getFrontendLogLevelColor({ level: 'debug' })).toBe('text-gray-600');
    expect(component.getFrontendLogLevelColor({ level: 'unknown' })).toBe('text-gray-800');
  });

  it('should format timestamp correctly', () => {
    const testDate = new Date('2023-01-01T12:00:00Z');
    const formatted = component.formatTimestamp(testDate.getTime());
    expect(formatted).toContain('1/1/2023'); // Basic date check
  });

  it('should clear frontend logs', () => {
    component.clearFrontendLogs();
    expect(mockLoggerService.clearLogs).toHaveBeenCalled();
    expect(mockLoggerService.getLogs).toHaveBeenCalled();
  });
});