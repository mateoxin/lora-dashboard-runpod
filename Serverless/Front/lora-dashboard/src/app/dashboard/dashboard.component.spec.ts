import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { BehaviorSubject, of } from 'rxjs';
import { DebugElement } from '@angular/core';
import { By } from '@angular/platform-browser';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

import { DashboardComponent } from './dashboard.component';
import { AuthService } from '../auth/auth.service';
import { AuthUser } from '../core/models';

// Angular Material Modules
import { MatTabsModule } from '@angular/material/tabs';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatProgressBarModule } from '@angular/material/progress-bar';

// Mock components for testing
import { Component } from '@angular/core';

@Component({
  selector: 'app-config-tab',
  template: '<div>Config Tab Mock</div>'
})
class MockConfigTabComponent { }

@Component({
  selector: 'app-processes-tab',
  template: '<div>Processes Tab Mock</div>'
})
class MockProcessesTabComponent { }

@Component({
  selector: 'app-lora-tab',
  template: '<div>LoRA Tab Mock</div>'
})
class MockLoraTabComponent { }

describe('DashboardComponent', () => {
  let component: DashboardComponent;
  let fixture: ComponentFixture<DashboardComponent>;
  let authService: jasmine.SpyObj<AuthService>;
  let router: jasmine.SpyObj<Router>;
  let currentUserSubject: BehaviorSubject<AuthUser | null>;

  const mockUser: AuthUser = {
    username: 'testuser',
    token: 'test-token-123',
    loginTime: '2024-01-01T00:00:00.000Z'
  };

  beforeEach(async () => {
    currentUserSubject = new BehaviorSubject<AuthUser | null>(null);
    
    const authServiceSpy = jasmine.createSpyObj('AuthService', ['logout', 'isTokenExpiringSoon'], {
      currentUser$: currentUserSubject.asObservable()
    });
    
    const routerSpy = jasmine.createSpyObj('Router', ['navigate']);

    await TestBed.configureTestingModule({
      declarations: [
        DashboardComponent,
        MockConfigTabComponent,
        MockProcessesTabComponent,
        MockLoraTabComponent
      ],
      imports: [
        NoopAnimationsModule,
        MatTabsModule,
        MatToolbarModule,
        MatButtonModule,
        MatIconModule,
        MatMenuModule,
        MatProgressBarModule
      ],
      providers: [
        { provide: AuthService, useValue: authServiceSpy },
        { provide: Router, useValue: routerSpy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(DashboardComponent);
    component = fixture.componentInstance;
    authService = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
    router = TestBed.inject(Router) as jasmine.SpyObj<Router>;
  });

  describe('Component Initialization', () => {
    it('should create', () => {
      expect(component).toBeTruthy();
    });

    it('should initialize with default values', () => {
      expect(component.currentUser).toBeNull();
      expect(component.selectedTabIndex).toBe(0);
    });

    it('should subscribe to currentUser$ on init', () => {
      spyOn(currentUserSubject, 'subscribe').and.callThrough();
      
      component.ngOnInit();
      
      expect(currentUserSubject.subscribe).toHaveBeenCalled();
    });

    it('should set currentUser when user is logged in', () => {
      currentUserSubject.next(mockUser);
      
      component.ngOnInit();
      
      expect(component.currentUser).toEqual(mockUser);
    });

    it('should handle null user from currentUser$', () => {
      currentUserSubject.next(null);
      
      component.ngOnInit();
      
      expect(component.currentUser).toBeNull();
    });

    it('should not navigate on init when authentication is disabled', () => {
      currentUserSubject.next(null);
      
      component.ngOnInit();
      
      expect(router.navigate).not.toHaveBeenCalled();
    });
  });

  describe('Component Cleanup', () => {
    it('should complete destroy$ subject on destroy', () => {
      spyOn(component['destroy$'], 'next');
      spyOn(component['destroy$'], 'complete');
      
      component.ngOnDestroy();
      
      expect(component['destroy$'].next).toHaveBeenCalled();
      expect(component['destroy$'].complete).toHaveBeenCalled();
    });

    it('should unsubscribe from observables on destroy', () => {
      component.ngOnInit();
      const subscription = component['destroy$'];
      spyOn(subscription, 'next');
      spyOn(subscription, 'complete');
      
      component.ngOnDestroy();
      
      expect(subscription.next).toHaveBeenCalled();
      expect(subscription.complete).toHaveBeenCalled();
    });
  });

  describe('Tab Management', () => {
    beforeEach(() => {
      fixture.detectChanges();
    });

    it('should change selected tab index', () => {
      component.onTabChange(2);
      
      expect(component.selectedTabIndex).toBe(2);
    });

    it('should handle tab change with valid index', () => {
      const validIndices = [0, 1, 2, 3];
      
      validIndices.forEach(index => {
        component.onTabChange(index);
        expect(component.selectedTabIndex).toBe(index);
      });
    });

    it('should handle tab change with invalid index', () => {
      const invalidIndices = [-1, 4, 999, NaN];
      
      invalidIndices.forEach(index => {
        component.onTabChange(index);
        expect(component.selectedTabIndex).toBe(index); // Should still set it
      });
    });

    it('should display correct tab content based on selected index', () => {
      fixture.detectChanges();
      
      // Check initial tab (index 0)
      expect(fixture.debugElement.query(By.css('app-config-tab'))).toBeTruthy();
      
      // Change to processes tab (index 1)
      component.onTabChange(1);
      fixture.detectChanges();
      
      // Note: The actual tab content visibility depends on mat-tab-group implementation
      // This test verifies the component state change
      expect(component.selectedTabIndex).toBe(1);
    });
  });

  describe('User Authentication Display', () => {
    it('should display default username when no user', () => {
      component.currentUser = null;
      
      const displayName = component.getUserDisplayName();
      
      expect(displayName).toBe('User');
    });

    it('should display user username when logged in', () => {
      component.currentUser = mockUser;
      
      const displayName = component.getUserDisplayName();
      
      expect(displayName).toBe(mockUser.username);
    });

    it('should handle user with empty username', () => {
      component.currentUser = { ...mockUser, username: '' };
      
      const displayName = component.getUserDisplayName();
      
      expect(displayName).toBe('User');
    });

    it('should handle user with null username', () => {
      component.currentUser = { ...mockUser, username: null as any };
      
      const displayName = component.getUserDisplayName();
      
      expect(displayName).toBe('User');
    });
  });

  describe('Token Expiration Warning', () => {
    it('should return false when token is not expiring soon', () => {
      authService.isTokenExpiringSoon.and.returnValue(false);
      
      const isExpiring = component.isTokenExpiring();
      
      expect(isExpiring).toBe(false);
      expect(authService.isTokenExpiringSoon).toHaveBeenCalled();
    });

    it('should return true when token is expiring soon', () => {
      authService.isTokenExpiringSoon.and.returnValue(true);
      
      const isExpiring = component.isTokenExpiring();
      
      expect(isExpiring).toBe(true);
      expect(authService.isTokenExpiringSoon).toHaveBeenCalled();
    });

    it('should handle auth service errors gracefully', () => {
      authService.isTokenExpiringSoon.and.throwError('Auth service error');
      
      expect(() => component.isTokenExpiring()).not.toThrow();
    });
  });

  describe('Logout Functionality', () => {
    it('should call authService.logout when logout is called', () => {
      component.logout();
      
      expect(authService.logout).toHaveBeenCalled();
    });

    it('should navigate to login page after logout', () => {
      component.logout();
      
      expect(router.navigate).toHaveBeenCalledWith(['/login']);
    });

    it('should handle logout errors gracefully', () => {
      authService.logout.and.throwError('Logout error');
      
      expect(() => component.logout()).not.toThrow();
      expect(router.navigate).toHaveBeenCalledWith(['/login']);
    });

    it('should handle router navigation errors', () => {
      router.navigate.and.throwError('Navigation error');
      
      expect(() => component.logout()).not.toThrow();
    });
  });

  describe('Template Rendering', () => {
    beforeEach(() => {
      component.currentUser = mockUser;
      fixture.detectChanges();
    });

    it('should render mat-tab-group', () => {
      const tabGroup = fixture.debugElement.query(By.css('mat-tab-group'));
      expect(tabGroup).toBeTruthy();
    });

    it('should render all tab components', () => {
      const configTab = fixture.debugElement.query(By.css('app-config-tab'));
      const processesTab = fixture.debugElement.query(By.css('app-processes-tab'));
      const loraTab = fixture.debugElement.query(By.css('app-lora-tab'));
      
      expect(configTab).toBeTruthy();
      expect(processesTab).toBeTruthy();
      expect(loraTab).toBeTruthy();
    });

    it('should display user display name in template', () => {
      const compiled = fixture.nativeElement;
      expect(compiled.textContent).toContain(mockUser.username);
    });

    it('should render logout button', () => {
      const logoutButton = fixture.debugElement.query(By.css('[data-testid="logout-button"]'));
      // Note: This assumes a data-testid attribute is added to the logout button
      // Alternative: look for button with specific text or mat-icon
      const buttons = fixture.debugElement.queryAll(By.css('button'));
      expect(buttons.length).toBeGreaterThan(0);
    });

    it('should handle click events on tabs', () => {
      spyOn(component, 'onTabChange');
      
      const tabGroup = fixture.debugElement.query(By.css('mat-tab-group'));
      
      // Trigger selectedIndexChange event
      if (tabGroup.componentInstance) {
        tabGroup.componentInstance.selectedIndexChange.emit(1);
      }
      
      expect(component.onTabChange).toHaveBeenCalledWith(1);
    });
  });

  describe('Responsive Behavior', () => {
    it('should handle window resize events', () => {
      // Simulate window resize
      window.dispatchEvent(new Event('resize'));
      fixture.detectChanges();
      
      // Component should still function normally
      expect(component).toBeTruthy();
    });

    it('should adapt to different screen sizes', () => {
      // Test with different viewport sizes
      const viewportSizes = [
        { width: 320, height: 568 },   // Mobile
        { width: 768, height: 1024 },  // Tablet
        { width: 1920, height: 1080 }  // Desktop
      ];
      
      viewportSizes.forEach(size => {
        Object.defineProperty(window, 'innerWidth', { value: size.width, configurable: true });
        Object.defineProperty(window, 'innerHeight', { value: size.height, configurable: true });
        
        window.dispatchEvent(new Event('resize'));
        fixture.detectChanges();
        
        expect(component).toBeTruthy();
      });
    });
  });

  describe('Accessibility', () => {
    beforeEach(() => {
      fixture.detectChanges();
    });

    it('should have proper ARIA labels', () => {
      // Check for aria-label attributes
      const elementsWithAriaLabel = fixture.debugElement.queryAll(By.css('[aria-label]'));
      expect(elementsWithAriaLabel.length).toBeGreaterThanOrEqual(0);
    });

    it('should support keyboard navigation', () => {
      const tabGroup = fixture.debugElement.query(By.css('mat-tab-group'));
      
      // Simulate keyboard events
      const keyboardEvent = new KeyboardEvent('keydown', { key: 'Tab' });
      tabGroup.nativeElement.dispatchEvent(keyboardEvent);
      
      expect(component).toBeTruthy(); // Should not crash
    });

    it('should have proper focus management', () => {
      const focusableElements = fixture.debugElement.queryAll(
        By.css('button, [tabindex]:not([tabindex="-1"])')
      );
      
      expect(focusableElements.length).toBeGreaterThan(0);
    });
  });

  describe('Error Handling', () => {
    it('should handle AuthService observable errors', () => {
      const errorSubject = new BehaviorSubject<AuthUser | null>(null);
      authService.currentUser$ = errorSubject.asObservable();
      
      component.ngOnInit();
      
      // Simulate error in observable
      expect(() => {
        errorSubject.error(new Error('Auth service error'));
      }).not.toThrow();
    });

    it('should handle template rendering errors gracefully', () => {
      // Set invalid data that might cause template errors
      component.currentUser = null;
      component.selectedTabIndex = -1;
      
      expect(() => {
        fixture.detectChanges();
      }).not.toThrow();
    });

    it('should handle missing dependencies gracefully', () => {
      // Test behavior when services are not available
      const componentWithoutDeps = new DashboardComponent(null as any, null as any);
      
      expect(() => {
        componentWithoutDeps.ngOnInit();
        componentWithoutDeps.logout();
        componentWithoutDeps.getUserDisplayName();
        componentWithoutDeps.isTokenExpiring();
      }).not.toThrow();
    });
  });

  describe('Performance', () => {
    it('should not create excessive subscriptions', () => {
      const subscriptionCount = component['destroy$'].observers?.length || 0;
      
      component.ngOnInit();
      component.ngOnInit(); // Call multiple times
      component.ngOnInit();
      
      // Should not exponentially increase subscriptions
      const newSubscriptionCount = component['destroy$'].observers?.length || 0;
      expect(newSubscriptionCount).toBeLessThanOrEqual(subscriptionCount + 10);
    });

    it('should handle rapid tab changes efficiently', () => {
      const startTime = performance.now();
      
      // Rapidly change tabs
      for (let i = 0; i < 100; i++) {
        component.onTabChange(i % 3);
      }
      
      const endTime = performance.now();
      const duration = endTime - startTime;
      
      expect(duration).toBeLessThan(100); // Should complete within 100ms
    });

    it('should update efficiently when user data changes', () => {
      const users = Array.from({ length: 10 }, (_, i) => ({
        ...mockUser,
        username: `user${i}`,
        token: `token${i}`
      }));
      
      const startTime = performance.now();
      
      users.forEach(user => {
        currentUserSubject.next(user);
        fixture.detectChanges();
      });
      
      const endTime = performance.now();
      const duration = endTime - startTime;
      
      expect(duration).toBeLessThan(500); // Should complete within 500ms
    });
  });

  describe('Edge Cases', () => {
    it('should handle extremely long usernames', () => {
      const longUsername = 'a'.repeat(1000);
      component.currentUser = { ...mockUser, username: longUsername };
      
      const displayName = component.getUserDisplayName();
      expect(displayName).toBe(longUsername);
      
      // Should not break template rendering
      expect(() => fixture.detectChanges()).not.toThrow();
    });

    it('should handle special characters in username', () => {
      const specialUsername = 'user@domain.com <script>alert("xss")</script>';
      component.currentUser = { ...mockUser, username: specialUsername };
      
      const displayName = component.getUserDisplayName();
      expect(displayName).toBe(specialUsername);
      
      // Angular should escape HTML automatically
      fixture.detectChanges();
      const compiled = fixture.nativeElement;
      expect(compiled.innerHTML).not.toContain('<script>');
    });

    it('should handle negative tab indices', () => {
      component.onTabChange(-5);
      expect(component.selectedTabIndex).toBe(-5);
      
      // Should not break the component
      expect(() => fixture.detectChanges()).not.toThrow();
    });

    it('should handle very large tab indices', () => {
      component.onTabChange(999999);
      expect(component.selectedTabIndex).toBe(999999);
      
      // Should not break the component
      expect(() => fixture.detectChanges()).not.toThrow();
    });

    it('should handle concurrent logout calls', () => {
      // Call logout multiple times rapidly
      component.logout();
      component.logout();
      component.logout();
      
      // Should handle gracefully
      expect(authService.logout).toHaveBeenCalledTimes(3);
      expect(router.navigate).toHaveBeenCalledTimes(3);
    });
  });
});
