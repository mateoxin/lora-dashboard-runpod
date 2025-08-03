import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { CryptoService } from '../core/crypto.service';
import { AuthUser, LoginRequest, HARDCODED_CREDENTIALS } from '../core/models';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly TOKEN_KEY = 'lora_dashboard_token';
  private readonly USER_KEY = 'lora_dashboard_user';
  
  private currentUserSubject = new BehaviorSubject<AuthUser | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(private cryptoService: CryptoService) {
    this.loadStoredUser();
  }

  /**
   * Login with hardcoded credentials
   */
  login(credentials: LoginRequest): Observable<boolean> {
    return new Observable(observer => {
      try {
        // Validate against hardcoded credentials
        if (credentials.username === HARDCODED_CREDENTIALS.username && 
            credentials.password === HARDCODED_CREDENTIALS.password) {
          
          // Generate encrypted token
          const token = this.cryptoService.generateToken(credentials.username);
          
          const user: AuthUser = {
            username: credentials.username,
            token: token,
            loginTime: new Date().toISOString()
          };
          
          // Store in localStorage (encrypted)
          const encryptedUser = this.cryptoService.encrypt(JSON.stringify(user));
          localStorage.setItem(this.TOKEN_KEY, token);
          localStorage.setItem(this.USER_KEY, encryptedUser);
          
          this.currentUserSubject.next(user);
          observer.next(true);
        } else {
          observer.next(false);
        }
        observer.complete();
      } catch (error) {
        console.error('Login error:', error);
        observer.error(error);
      }
    });
  }

  /**
   * Logout and clear stored data
   */
  logout(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
    this.currentUserSubject.next(null);
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    const token = localStorage.getItem(this.TOKEN_KEY);
    if (!token) return false;
    
    const tokenData = this.cryptoService.verifyToken(token);
    return tokenData !== null;
  }

  /**
   * Get current user
   */
  getCurrentUser(): AuthUser | null {
    return this.currentUserSubject.value;
  }

  /**
   * Get authentication token
   */
  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  /**
   * Load stored user from localStorage
   */
  private loadStoredUser(): void {
    try {
      const token = localStorage.getItem(this.TOKEN_KEY);
      const encryptedUser = localStorage.getItem(this.USER_KEY);
      
      if (token && encryptedUser) {
        // Verify token is still valid
        const tokenData = this.cryptoService.verifyToken(token);
        if (tokenData) {
          const decryptedUser = this.cryptoService.decrypt(encryptedUser);
          const user: AuthUser = JSON.parse(decryptedUser);
          this.currentUserSubject.next(user);
        } else {
          // Token expired, clear storage
          this.logout();
        }
      }
    } catch (error) {
      console.error('Failed to load stored user:', error);
      this.logout();
    }
  }

  /**
   * Check if token is about to expire (within 1 hour)
   */
  isTokenExpiringSoon(): boolean {
    const token = this.getToken();
    if (!token) return false;
    
    const tokenData = this.cryptoService.verifyToken(token);
    if (!tokenData) return true;
    
    const oneHourFromNow = Math.floor(Date.now() / 1000) + (60 * 60);
    return tokenData.exp < oneHourFromNow;
  }
}
