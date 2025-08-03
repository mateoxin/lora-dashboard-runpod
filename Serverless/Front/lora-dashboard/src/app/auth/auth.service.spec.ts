import { TestBed } from '@angular/core/testing';
import { AuthService } from './auth.service';
import { CryptoService } from '../core/crypto.service';
import { BehaviorSubject } from 'rxjs';
import { AuthUser, HARDCODED_CREDENTIALS } from '../core/models';

describe('AuthService', () => {
  let service: AuthService;
  let cryptoService: jasmine.SpyObj<CryptoService>;
  let localStorageSpy: jasmine.SpyObj<Storage>;

  const mockUser: AuthUser = {
    username: 'testuser',
    token: 'test-token-123',
    loginTime: '2024-01-01T00:00:00.000Z'
  };

  beforeEach(() => {
    const cryptoServiceSpy = jasmine.createSpyObj('CryptoService', ['encrypt', 'decrypt']);
    
    // Mock localStorage
    localStorageSpy = jasmine.createSpyObj('Storage', ['getItem', 'setItem', 'removeItem', 'clear']);
    Object.defineProperty(window, 'localStorage', { value: localStorageSpy });

    TestBed.configureTestingModule({
      providers: [
        AuthService,
        { provide: CryptoService, useValue: cryptoServiceSpy }
      ]
    });

    service = TestBed.inject(AuthService);
    cryptoService = TestBed.inject(CryptoService) as jasmine.SpyObj<CryptoService>;
  });

  afterEach(() => {
    localStorageSpy.clear.calls.reset();
    localStorageSpy.getItem.calls.reset();
    localStorageSpy.setItem.calls.reset();
    localStorageSpy.removeItem.calls.reset();
  });

  describe('Initialization', () => {
  it('should be created', () => {
    expect(service).toBeTruthy();
    });

    it('should initialize with no current user', () => {
      localStorageSpy.getItem.and.returnValue(null);
      cryptoService.decrypt.and.returnValue(null);

      const authService = new AuthService(cryptoService);
      
      authService.currentUser$.subscribe(user => {
        expect(user).toBeNull();
      });
    });

    it('should load user from localStorage on initialization', () => {
      const encryptedData = 'encrypted-user-data';
      const userData = JSON.stringify(mockUser);
      
      localStorageSpy.getItem.and.returnValue(encryptedData);
      cryptoService.decrypt.and.returnValue(userData);

      const authService = new AuthService(cryptoService);
      
      authService.currentUser$.subscribe(user => {
        expect(user).toEqual(mockUser);
      });

      expect(localStorageSpy.getItem).toHaveBeenCalledWith('currentUser');
      expect(cryptoService.decrypt).toHaveBeenCalledWith(encryptedData);
    });

    it('should handle corrupted localStorage data', () => {
      const encryptedData = 'encrypted-user-data';
      
      localStorageSpy.getItem.and.returnValue(encryptedData);
      cryptoService.decrypt.and.returnValue('invalid json');

      const authService = new AuthService(cryptoService);
      
      authService.currentUser$.subscribe(user => {
        expect(user).toBeNull();
      });
    });

    it('should handle decryption failure', () => {
      const encryptedData = 'encrypted-user-data';
      
      localStorageSpy.getItem.and.returnValue(encryptedData);
      cryptoService.decrypt.and.throwError('Decryption failed');

      const authService = new AuthService(cryptoService);
      
      authService.currentUser$.subscribe(user => {
        expect(user).toBeNull();
      });
    });
  });

  describe('Login', () => {
    it('should login with valid hardcoded credentials', () => {
      cryptoService.encrypt.and.returnValue('encrypted-data');
      
      service.login({
        username: HARDCODED_CREDENTIALS.username,
        password: HARDCODED_CREDENTIALS.password
      }).subscribe(result => {
        expect(result).toBe(true);
      });
      expect(cryptoService.encrypt).toHaveBeenCalled();
      expect(localStorageSpy.setItem).toHaveBeenCalled();
      
      service.currentUser$.subscribe(user => {
        expect(user).toBeTruthy();
        expect(user?.username).toBe(HARDCODED_CREDENTIALS.username);
        expect(user?.token).toBeTruthy();
        expect(user?.loginTime).toBeTruthy();
      });
    });

    it('should fail login with invalid username', () => {
      const result = service.login('invalid-user', HARDCODED_CREDENTIALS.password);
      
      expect(result).toBe(false);
      expect(cryptoService.encrypt).not.toHaveBeenCalled();
      expect(localStorageSpy.setItem).not.toHaveBeenCalled();
      
      service.currentUser$.subscribe(user => {
        expect(user).toBeNull();
      });
    });

    it('should fail login with invalid password', () => {
      const result = service.login(HARDCODED_CREDENTIALS.username, 'invalid-password');
      
      expect(result).toBe(false);
      expect(cryptoService.encrypt).not.toHaveBeenCalled();
      expect(localStorageSpy.setItem).not.toHaveBeenCalled();
      
      service.currentUser$.subscribe(user => {
        expect(user).toBeNull();
      });
    });

    it('should fail login with empty credentials', () => {
      const result1 = service.login('', HARDCODED_CREDENTIALS.password);
      const result2 = service.login(HARDCODED_CREDENTIALS.username, '');
      const result3 = service.login('', '');
      
      expect(result1).toBe(false);
      expect(result2).toBe(false);
      expect(result3).toBe(false);
    });

    it('should fail login with null/undefined credentials', () => {
      const result1 = service.login(null as any, HARDCODED_CREDENTIALS.password);
      const result2 = service.login(HARDCODED_CREDENTIALS.username, null as any);
      const result3 = service.login(undefined as any, undefined as any);
      
      expect(result1).toBe(false);
      expect(result2).toBe(false);
      expect(result3).toBe(false);
    });

    it('should handle encryption failure during login', () => {
      cryptoService.encrypt.and.throwError('Encryption failed');
      
      const result = service.login(HARDCODED_CREDENTIALS.username, HARDCODED_CREDENTIALS.password);
      
      expect(result).toBe(false);
      expect(localStorageSpy.setItem).not.toHaveBeenCalled();
    });

    it('should generate unique tokens for each login', () => {
      cryptoService.encrypt.and.returnValue('encrypted-data');
      
      service.login(HARDCODED_CREDENTIALS.username, HARDCODED_CREDENTIALS.password);
      let firstToken: string;
      service.currentUser$.subscribe(user => {
        firstToken = user?.token || '';
      });
      
      service.logout();
      service.login(HARDCODED_CREDENTIALS.username, HARDCODED_CREDENTIALS.password);
      let secondToken: string;
      service.currentUser$.subscribe(user => {
        secondToken = user?.token || '';
      });
      
      expect(firstToken).not.toBe(secondToken);
      expect(firstToken.length).toBeGreaterThan(0);
      expect(secondToken.length).toBeGreaterThan(0);
    });

    it('should set login time correctly', () => {
      const beforeLogin = new Date().getTime();
      cryptoService.encrypt.and.returnValue('encrypted-data');
      
      service.login(HARDCODED_CREDENTIALS.username, HARDCODED_CREDENTIALS.password);
      const afterLogin = new Date().getTime();
      
      service.currentUser$.subscribe(user => {
        const loginTime = new Date(user?.loginTime || '').getTime();
        expect(loginTime).toBeGreaterThanOrEqual(beforeLogin);
        expect(loginTime).toBeLessThanOrEqual(afterLogin);
      });
    });
  });

  describe('Logout', () => {
    beforeEach(() => {
      cryptoService.encrypt.and.returnValue('encrypted-data');
      service.login(HARDCODED_CREDENTIALS.username, HARDCODED_CREDENTIALS.password);
    });

    it('should logout and clear user data', () => {
      service.logout();
      
      expect(localStorageSpy.removeItem).toHaveBeenCalledWith('currentUser');
      
      service.currentUser$.subscribe(user => {
        expect(user).toBeNull();
      });
    });

    it('should handle logout when not logged in', () => {
      service.logout();
      service.logout(); // Second logout
      
      expect(localStorageSpy.removeItem).toHaveBeenCalledTimes(2);
    });
  });

  describe('Authentication State', () => {
    it('should return false for isAuthenticated when not logged in', () => {
      localStorageSpy.getItem.and.returnValue(null);
      
      expect(service.isAuthenticated()).toBe(false);
    });

    it('should return true for isAuthenticated when logged in', () => {
      cryptoService.encrypt.and.returnValue('encrypted-data');
      service.login(HARDCODED_CREDENTIALS.username, HARDCODED_CREDENTIALS.password);
      
      expect(service.isAuthenticated()).toBe(true);
    });

    it('should return null token when not authenticated', () => {
      expect(service.getToken()).toBeNull();
    });

    it('should return token when authenticated', () => {
      cryptoService.encrypt.and.returnValue('encrypted-data');
      service.login(HARDCODED_CREDENTIALS.username, HARDCODED_CREDENTIALS.password);
      
      const token = service.getToken();
      expect(token).toBeTruthy();
      expect(typeof token).toBe('string');
    });
  });

  describe('Token Expiration', () => {
    it('should detect token expiring soon (within 5 minutes)', () => {
      cryptoService.encrypt.and.returnValue('encrypted-data');
      service.login(HARDCODED_CREDENTIALS.username, HARDCODED_CREDENTIALS.password);
      
      // Mock a login time from 23 hours ago (token expires in 1 hour)
      const almostExpiredUser: AuthUser = {
        username: HARDCODED_CREDENTIALS.username,
        token: 'test-token',
        loginTime: new Date(Date.now() - 23 * 60 * 60 * 1000).toISOString()
      };
      
      service['currentUserSubject'].next(almostExpiredUser);
      
      expect(service.isTokenExpiringSoon()).toBe(true);
    });

    it('should not detect token expiring when recently logged in', () => {
      cryptoService.encrypt.and.returnValue('encrypted-data');
      service.login(HARDCODED_CREDENTIALS.username, HARDCODED_CREDENTIALS.password);
      
      expect(service.isTokenExpiringSoon()).toBe(false);
    });

    it('should return false for token expiring when not authenticated', () => {
      expect(service.isTokenExpiringSoon()).toBe(false);
    });

    it('should detect expired token', () => {
      cryptoService.encrypt.and.returnValue('encrypted-data');
      service.login(HARDCODED_CREDENTIALS.username, HARDCODED_CREDENTIALS.password);
      
      // Mock a login time from 25 hours ago (expired)
      const expiredUser: AuthUser = {
        username: HARDCODED_CREDENTIALS.username,
        token: 'test-token',
        loginTime: new Date(Date.now() - 25 * 60 * 60 * 1000).toISOString()
      };
      
      service['currentUserSubject'].next(expiredUser);
      
      expect(service.isTokenExpired()).toBe(true);
    });

    it('should auto-logout when token is expired', () => {
      cryptoService.encrypt.and.returnValue('encrypted-data');
      service.login(HARDCODED_CREDENTIALS.username, HARDCODED_CREDENTIALS.password);
      
      // Mock an expired token
      const expiredUser: AuthUser = {
        username: HARDCODED_CREDENTIALS.username,
        token: 'test-token',
        loginTime: new Date(Date.now() - 25 * 60 * 60 * 1000).toISOString()
      };
      
      service['currentUserSubject'].next(expiredUser);
      
      // Check authentication status (should trigger auto-logout)
      const isAuth = service.isAuthenticated();
      
      expect(isAuth).toBe(false);
      expect(localStorageSpy.removeItem).toHaveBeenCalledWith('currentUser');
    });
  });

  describe('Observable Behavior', () => {
    it('should emit user changes to subscribers', () => {
      const userChanges: (AuthUser | null)[] = [];
      
      service.currentUser$.subscribe(user => {
        userChanges.push(user);
      });
      
      // Initial state
      expect(userChanges[0]).toBeNull();
      
      // Login
      cryptoService.encrypt.and.returnValue('encrypted-data');
      service.login(HARDCODED_CREDENTIALS.username, HARDCODED_CREDENTIALS.password);
      
      expect(userChanges[1]).toBeTruthy();
      expect(userChanges[1]?.username).toBe(HARDCODED_CREDENTIALS.username);
      
      // Logout
      service.logout();
      
      expect(userChanges[2]).toBeNull();
      expect(userChanges.length).toBe(3);
    });

    it('should be a BehaviorSubject (emit current value to new subscribers)', () => {
      cryptoService.encrypt.and.returnValue('encrypted-data');
      service.login(HARDCODED_CREDENTIALS.username, HARDCODED_CREDENTIALS.password);
      
      // New subscriber should immediately get current value
      service.currentUser$.subscribe(user => {
        expect(user).toBeTruthy();
        expect(user?.username).toBe(HARDCODED_CREDENTIALS.username);
      });
    });
  });

  describe('Edge Cases', () => {
    it('should handle localStorage being unavailable', () => {
      // Mock localStorage throwing errors
      localStorageSpy.getItem.and.throwError('localStorage unavailable');
      localStorageSpy.setItem.and.throwError('localStorage unavailable');
      localStorageSpy.removeItem.and.throwError('localStorage unavailable');
      
      // Should not crash
      expect(() => {
        const authService = new AuthService(cryptoService);
        authService.login(HARDCODED_CREDENTIALS.username, HARDCODED_CREDENTIALS.password);
        authService.logout();
      }).not.toThrow();
    });

    it('should handle very long usernames and passwords', () => {
      const longUsername = 'a'.repeat(1000);
      const longPassword = 'b'.repeat(1000);
      
      const result = service.login(longUsername, longPassword);
      expect(result).toBe(false); // Should reject long credentials
    });

    it('should handle special characters in credentials', () => {
      const specialUsername = 'user@domain.com';
      const specialPassword = 'p@ssw0rd!#$%';
      
      const result = service.login(specialUsername, specialPassword);
      expect(result).toBe(false); // Should only accept hardcoded credentials
    });

    it('should handle concurrent login attempts', () => {
      cryptoService.encrypt.and.returnValue('encrypted-data');
      
      const result1 = service.login(HARDCODED_CREDENTIALS.username, HARDCODED_CREDENTIALS.password);
      const result2 = service.login(HARDCODED_CREDENTIALS.username, HARDCODED_CREDENTIALS.password);
      
      expect(result1).toBe(true);
      expect(result2).toBe(true); // Should allow re-login
      
      service.currentUser$.subscribe(user => {
        expect(user).toBeTruthy();
      });
    });

    it('should handle case sensitivity in credentials', () => {
      const result1 = service.login(HARDCODED_CREDENTIALS.username.toUpperCase(), HARDCODED_CREDENTIALS.password);
      const result2 = service.login(HARDCODED_CREDENTIALS.username, HARDCODED_CREDENTIALS.password.toUpperCase());
      
      expect(result1).toBe(false);
      expect(result2).toBe(false);
    });

    it('should handle whitespace in credentials', () => {
      const result1 = service.login(` ${HARDCODED_CREDENTIALS.username} `, HARDCODED_CREDENTIALS.password);
      const result2 = service.login(HARDCODED_CREDENTIALS.username, ` ${HARDCODED_CREDENTIALS.password} `);
      
      expect(result1).toBe(false);
      expect(result2).toBe(false);
    });
  });

  describe('Security', () => {
    it('should not expose password in any form', () => {
      cryptoService.encrypt.and.returnValue('encrypted-data');
      service.login(HARDCODED_CREDENTIALS.username, HARDCODED_CREDENTIALS.password);
      
      service.currentUser$.subscribe(user => {
        expect(user).not.toEqual(jasmine.objectContaining({ password: jasmine.any(String) }));
        expect(JSON.stringify(user)).not.toContain(HARDCODED_CREDENTIALS.password);
      });
    });

    it('should encrypt user data before storing', () => {
      cryptoService.encrypt.and.returnValue('encrypted-data');
      
      service.login(HARDCODED_CREDENTIALS.username, HARDCODED_CREDENTIALS.password);
      
      expect(cryptoService.encrypt).toHaveBeenCalled();
      expect(localStorageSpy.setItem).toHaveBeenCalledWith('currentUser', 'encrypted-data');
    });

    it('should generate cryptographically secure tokens', () => {
      cryptoService.encrypt.and.returnValue('encrypted-data');
      
      const tokens = new Set<string>();
      
      // Generate multiple tokens
      for (let i = 0; i < 100; i++) {
        service.login(HARDCODED_CREDENTIALS.username, HARDCODED_CREDENTIALS.password);
        const token = service.getToken();
        if (token) {
          tokens.add(token);
        }
        service.logout();
      }
      
      // All tokens should be unique
      expect(tokens.size).toBe(100);
      
      // Tokens should be of reasonable length
      tokens.forEach(token => {
        expect(token.length).toBeGreaterThan(10);
      });
    });

    it('should validate token format', () => {
      cryptoService.encrypt.and.returnValue('encrypted-data');
      service.login(HARDCODED_CREDENTIALS.username, HARDCODED_CREDENTIALS.password);
      
      const token = service.getToken();
      
      expect(token).toMatch(/^[a-zA-Z0-9-_]+$/); // Should only contain safe characters
      expect(token?.length).toBeGreaterThan(0);
    });
  });
});
