import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpResponse, HttpErrorResponse } from '@angular/common/http';
import { Observable } from 'rxjs';
import { tap, finalize } from 'rxjs/operators';
import { FrontendLoggerService } from './frontend-logger.service';

@Injectable()
export class LoggingInterceptor implements HttpInterceptor {

  constructor(private frontendLogger: FrontendLoggerService) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Generate unique request ID
    const requestId = this.generateRequestId();
    const startTime = Date.now();
    
    // Extract endpoint from URL for cleaner logging
    const endpoint = this.extractEndpoint(req.url);
    
    // Skip logging for certain URLs (e.g., assets, config files)
    if (this.shouldSkipLogging(req.url)) {
      return next.handle(req);
    }

    // Log the request
    this.frontendLogger.logRequest(endpoint, req.method, {
      url: req.url,
      headers: this.sanitizeHeaders(req.headers),
      body: this.sanitizeBody(req.body),
      params: req.params.keys().length > 0 ? req.params : null
    }, requestId);

    // Handle the request and log the response
    return next.handle(req).pipe(
      tap({
        next: (event) => {
          if (event instanceof HttpResponse) {
            const duration = Date.now() - startTime;
            
            // Log successful response
            this.frontendLogger.logResponse(
              requestId,
              endpoint,
              {
                body: this.sanitizeResponseBody(event.body),
                headers: this.sanitizeHeaders(event.headers),
                status: event.status,
                statusText: event.statusText
              },
              event.status,
              duration
            );
          }
        },
        error: (error: HttpErrorResponse) => {
          const duration = Date.now() - startTime;
          
          // Log error response
          this.frontendLogger.logError(requestId, endpoint, {
            status: error.status,
            statusText: error.statusText,
            message: error.message,
            error: error.error,
            url: error.url
          }, {
            method: req.method,
            url: req.url,
            duration
          });
        }
      }),
      finalize(() => {
        // Optional: Log request completion
        const duration = Date.now() - startTime;
        if (duration > 5000) { // Log slow requests (>5s)
          console.warn(`🐌 [FRONTEND] SLOW REQUEST | ${req.method} ${endpoint} | Duration: ${duration}ms`);
        }
      })
    );
  }

  private generateRequestId(): string {
    return Math.random().toString(36).substr(2, 9);
  }

  private extractEndpoint(url: string): string {
    try {
      const urlObj = new URL(url);
      return urlObj.pathname + (urlObj.search || '');
    } catch {
      // If URL parsing fails, return the original URL
      return url;
    }
  }

  private shouldSkipLogging(url: string): boolean {
    const skipPatterns = [
      '/assets/',
      '.json',
      '.txt',
      '.ico',
      'config.json',
      'environment',
      '/favicon'
    ];
    
    return skipPatterns.some(pattern => url.includes(pattern));
  }

  private sanitizeHeaders(headers: any): any {
    if (!headers) return null;
    
    const sanitized: any = {};
    
    if (headers.keys) {
      // Angular HttpHeaders
      headers.keys().forEach((key: string) => {
        const value = headers.get(key);
        sanitized[key] = this.sanitizeHeaderValue(key, value);
      });
    } else {
      // Plain object
      Object.keys(headers).forEach(key => {
        sanitized[key] = this.sanitizeHeaderValue(key, headers[key]);
      });
    }
    
    return Object.keys(sanitized).length > 0 ? sanitized : null;
  }

  private sanitizeHeaderValue(key: string, value: any): string {
    const sensitiveHeaders = ['authorization', 'x-runpod-token', 'x-api-key', 'cookie'];
    
    if (sensitiveHeaders.some(h => key.toLowerCase().includes(h))) {
      return value ? '***HIDDEN***' : '';
    }
    
    return value || '';
  }

  private sanitizeBody(body: any): any {
    if (!body) return null;
    
    try {
      // If it's FormData, just log that it's a FormData object
      if (body instanceof FormData) {
        const formDataInfo: any = { type: 'FormData', entries: [] };
        body.forEach((value, key) => {
          if (value instanceof File) {
            formDataInfo.entries.push({ 
              key, 
              type: 'File', 
              name: value.name, 
              size: value.size 
            });
          } else {
            formDataInfo.entries.push({ 
              key, 
              value: this.sanitizeValue(key, value) 
            });
          }
        });
        return formDataInfo;
      }
      
      // For regular objects
      if (typeof body === 'object') {
        const sanitized: any = {};
        Object.keys(body).forEach(key => {
          sanitized[key] = this.sanitizeValue(key, body[key]);
        });
        return sanitized;
      }
      
      return body;
    } catch (e) {
      return '[Could not serialize body]';
    }
  }

  private sanitizeResponseBody(body: any): any {
    if (!body) return null;
    
    // Truncate large responses
    if (typeof body === 'string' && body.length > 1000) {
      return body.substring(0, 1000) + '... [TRUNCATED]';
    }
    
    if (typeof body === 'object') {
      const str = JSON.stringify(body);
      if (str.length > 2000) {
        return '[LARGE_OBJECT - ' + str.length + ' chars]';
      }
    }
    
    return body;
  }

  private sanitizeValue(key: string, value: any): any {
    const sensitiveKeys = ['password', 'token', 'key', 'secret', 'auth'];
    
    if (sensitiveKeys.some(k => key.toLowerCase().includes(k))) {
      return value ? '***HIDDEN***' : '';
    }
    
    // Truncate large strings
    if (typeof value === 'string' && value.length > 500) {
      return value.substring(0, 500) + '... [TRUNCATED]';
    }
    
    return value;
  }
}