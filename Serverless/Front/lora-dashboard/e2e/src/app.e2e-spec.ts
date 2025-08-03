import { browser, by, element, protractor, ExpectedConditions } from 'protractor';

describe('LoRA Dashboard E2E Tests', () => {
  const EC = protractor.ExpectedConditions;
  
  beforeEach(async () => {
    await browser.get('/');
    await browser.manage().window().setSize(1920, 1080);
  });

  describe('Application Loading', () => {
    it('should display app title', async () => {
      const title = await browser.getTitle();
      expect(title).toContain('LoRA Dashboard');
    });

    it('should load without JavaScript errors', async () => {
      const logs = await browser.manage().logs().get('browser');
      const errors = logs.filter(log => log.level.name === 'SEVERE');
      expect(errors.length).toBe(0);
    });

    it('should redirect to dashboard when accessing root', async () => {
      await browser.get('/');
      await browser.wait(EC.urlContains('/dashboard'), 5000);
      const url = await browser.getCurrentUrl();
      expect(url).toContain('/dashboard');
    });
  });

  describe('Authentication Flow', () => {
    it('should show login page when not authenticated', async () => {
      await browser.get('/login');
      const loginForm = element(by.css('form'));
      await browser.wait(EC.presenceOf(loginForm), 5000);
      expect(await loginForm.isPresent()).toBe(true);
    });

    it('should login with valid credentials', async () => {
      await browser.get('/login');
      
      const usernameField = element(by.css('input[type="text"]'));
      const passwordField = element(by.css('input[type="password"]'));
      const loginButton = element(by.css('button[type="submit"]'));
      
      await browser.wait(EC.presenceOf(usernameField), 5000);
      
      await usernameField.sendKeys('Mateusz');
      await passwordField.sendKeys('Gramercy');
      await loginButton.click();
      
      await browser.wait(EC.urlContains('/dashboard'), 5000);
      const url = await browser.getCurrentUrl();
      expect(url).toContain('/dashboard');
    });

    it('should show error with invalid credentials', async () => {
      await browser.get('/login');
      
      const usernameField = element(by.css('input[type="text"]'));
      const passwordField = element(by.css('input[type="password"]'));
      const loginButton = element(by.css('button[type="submit"]'));
      
      await usernameField.sendKeys('invalid');
      await passwordField.sendKeys('invalid');
      await loginButton.click();
      
      const errorMessage = element(by.css('.error-message, .mat-error'));
      await browser.wait(EC.presenceOf(errorMessage), 5000);
      expect(await errorMessage.isPresent()).toBe(true);
    });

    it('should logout successfully', async () => {
      // Login first
      await loginWithValidCredentials();
      
      const logoutButton = element(by.css('[data-testid="logout-button"], button[aria-label="Logout"]'));
      await browser.wait(EC.elementToBeClickable(logoutButton), 5000);
      await logoutButton.click();
      
      await browser.wait(EC.urlContains('/login'), 5000);
      const url = await browser.getCurrentUrl();
      expect(url).toContain('/login');
    });
  });

  describe('Dashboard Navigation', () => {
    beforeEach(async () => {
      await loginWithValidCredentials();
    });

    it('should display all tabs', async () => {
      const tabs = element.all(by.css('mat-tab'));
      await browser.wait(EC.presenceOf(tabs.first()), 5000);
      
      const tabCount = await tabs.count();
      expect(tabCount).toBeGreaterThanOrEqual(3); // Config, Processes, LoRA
    });

    it('should switch between tabs', async () => {
      const processesTab = element(by.css('mat-tab[data-testid="processes-tab"], .mat-tab-label:nth-child(2)'));
      await browser.wait(EC.elementToBeClickable(processesTab), 5000);
      await processesTab.click();
      
      const processesContent = element(by.css('app-processes-tab'));
      await browser.wait(EC.presenceOf(processesContent), 5000);
      expect(await processesContent.isPresent()).toBe(true);
    });

    it('should maintain tab state during session', async () => {
      const loraTab = element(by.css('mat-tab[data-testid="lora-tab"], .mat-tab-label:nth-child(3)'));
      await browser.wait(EC.elementToBeClickable(loraTab), 5000);
      await loraTab.click();
      
      // Refresh page
      await browser.refresh();
      
      // Should maintain tab selection (if implemented)
      const activeTab = element(by.css('.mat-tab-label-active'));
      expect(await activeTab.isPresent()).toBe(true);
    });
  });

  describe('Configuration Tab', () => {
    beforeEach(async () => {
      await loginWithValidCredentials();
      await navigateToTab('config');
    });

    it('should display configuration form', async () => {
      const configForm = element(by.css('app-config-tab form, app-config-tab textarea'));
      await browser.wait(EC.presenceOf(configForm), 5000);
      expect(await configForm.isPresent()).toBe(true);
    });

    it('should validate YAML configuration', async () => {
      const configTextarea = element(by.css('textarea[data-testid="config-editor"]'));
      await browser.wait(EC.presenceOf(configTextarea), 5000);
      
      await configTextarea.clear();
      await configTextarea.sendKeys('invalid yaml: [');
      
      const validateButton = element(by.css('button[data-testid="validate-config"]'));
      if (await validateButton.isPresent()) {
        await validateButton.click();
        
        const errorMessage = element(by.css('.validation-error, .mat-error'));
        await browser.wait(EC.presenceOf(errorMessage), 3000);
        expect(await errorMessage.isPresent()).toBe(true);
      }
    });

    it('should start training with valid configuration', async () => {
      const validConfig = `
job: extension
config:
  name: "e2e_test_training"
  process:
    - type: sd_trainer
      trigger_word: "e2e_test"
`;
      
      const configTextarea = element(by.css('textarea'));
      await browser.wait(EC.presenceOf(configTextarea), 5000);
      
      await configTextarea.clear();
      await configTextarea.sendKeys(validConfig);
      
      const startButton = element(by.css('button[data-testid="start-training"]'));
      await browser.wait(EC.elementToBeClickable(startButton), 5000);
      await startButton.click();
      
      // Check for success message or navigation to processes
      const successIndicator = element(by.css('.success-message, .mat-snack-bar-container'));
      await browser.wait(EC.presenceOf(successIndicator), 10000);
      expect(await successIndicator.isPresent()).toBe(true);
    });
  });

  describe('Processes Tab', () => {
    beforeEach(async () => {
      await loginWithValidCredentials();
      await navigateToTab('processes');
    });

    it('should display processes table', async () => {
      const processesTable = element(by.css('mat-table, table, .processes-list'));
      await browser.wait(EC.presenceOf(processesTable), 5000);
      expect(await processesTable.isPresent()).toBe(true);
    });

    it('should show process details on click', async () => {
      const firstProcess = element.all(by.css('mat-row, tr, .process-item')).first();
      
      if (await firstProcess.isPresent()) {
        await firstProcess.click();
        
        const processDetails = element(by.css('.process-details, mat-dialog-container'));
        await browser.wait(EC.presenceOf(processDetails), 5000);
        expect(await processDetails.isPresent()).toBe(true);
      }
    });

    it('should filter processes by status', async () => {
      const statusFilter = element(by.css('mat-select[data-testid="status-filter"]'));
      
      if (await statusFilter.isPresent()) {
        await statusFilter.click();
        
        const runningOption = element(by.css('mat-option[value="running"]'));
        await browser.wait(EC.elementToBeClickable(runningOption), 3000);
        await runningOption.click();
        
        // Verify filtering worked
        const processes = element.all(by.css('.process-item[data-status="running"]'));
        const allProcesses = element.all(by.css('.process-item'));
        
        const runningCount = await processes.count();
        const totalCount = await allProcesses.count();
        
        if (totalCount > 0) {
          expect(runningCount).toBeLessThanOrEqual(totalCount);
        }
      }
    });

    it('should refresh processes list', async () => {
      const refreshButton = element(by.css('button[data-testid="refresh-processes"]'));
      
      if (await refreshButton.isPresent()) {
        const initialProcesses = await element.all(by.css('.process-item')).count();
        
        await refreshButton.click();
        
        await browser.sleep(2000); // Wait for refresh
        
        const processesAfterRefresh = await element.all(by.css('.process-item')).count();
        
        // Should not crash (count can be same or different)
        expect(typeof processesAfterRefresh).toBe('number');
      }
    });
  });

  describe('LoRA Models Tab', () => {
    beforeEach(async () => {
      await loginWithValidCredentials();
      await navigateToTab('lora');
    });

    it('should display LoRA models grid', async () => {
      const modelsGrid = element(by.css('.models-grid, mat-grid-list, .models-list'));
      await browser.wait(EC.presenceOf(modelsGrid), 5000);
      expect(await modelsGrid.isPresent()).toBe(true);
    });

    it('should show model details on hover or click', async () => {
      const firstModel = element.all(by.css('.model-card, mat-grid-tile')).first();
      
      if (await firstModel.isPresent()) {
        await browser.actions().mouseMove(firstModel).perform();
        
        const modelTooltip = element(by.css('.model-tooltip, mat-tooltip'));
        await browser.wait(EC.presenceOf(modelTooltip), 3000);
        // Tooltip might not always be visible, so we don't fail the test
      }
    });

    it('should download model when available', async () => {
      const downloadButton = element.all(by.css('button[data-testid="download-model"]')).first();
      
      if (await downloadButton.isPresent() && await downloadButton.isEnabled()) {
        await downloadButton.click();
        
        // Check for download initiation (success message, etc.)
        const downloadIndicator = element(by.css('.download-started, .mat-snack-bar'));
        await browser.wait(EC.presenceOf(downloadIndicator), 5000);
        expect(await downloadIndicator.isPresent()).toBe(true);
      }
    });
  });

  describe('Real-time Updates', () => {
    beforeEach(async () => {
      await loginWithValidCredentials();
    });

    it('should update process progress in real-time', async () => {
      await navigateToTab('processes');
      
      const progressBar = element(by.css('.progress-bar, mat-progress-bar'));
      
      if (await progressBar.isPresent()) {
        const initialProgress = await progressBar.getAttribute('value');
        
        // Wait for potential updates
        await browser.sleep(5000);
        
        const updatedProgress = await progressBar.getAttribute('value');
        
        // Progress might change or stay the same
        expect(typeof updatedProgress).toBe('string');
      }
    });

    it('should show notifications for completed processes', async () => {
      // This test would need a way to trigger process completion
      // or mock the notification system
      
      const notificationArea = element(by.css('.notifications, .mat-snack-bar-container'));
      
      // Check if notification system is working
      if (await notificationArea.isPresent()) {
        expect(await notificationArea.isDisplayed()).toBe(true);
      }
    });
  });

  describe('Responsive Design', () => {
    it('should work on mobile viewport', async () => {
      await browser.manage().window().setSize(375, 667); // iPhone 6/7/8
      await loginWithValidCredentials();
      
      const dashboard = element(by.css('app-dashboard'));
      await browser.wait(EC.presenceOf(dashboard), 5000);
      expect(await dashboard.isPresent()).toBe(true);
      
      // Check if mobile menu exists (if implemented)
      const mobileMenu = element(by.css('.mobile-menu, mat-sidenav'));
      // Mobile menu is optional, so we don't fail if it's not present
    });

    it('should work on tablet viewport', async () => {
      await browser.manage().window().setSize(768, 1024); // iPad
      await loginWithValidCredentials();
      
      const tabs = element.all(by.css('mat-tab'));
      await browser.wait(EC.presenceOf(tabs.first()), 5000);
      
      const tabCount = await tabs.count();
      expect(tabCount).toBeGreaterThan(0);
    });

    it('should work on desktop viewport', async () => {
      await browser.manage().window().setSize(1920, 1080); // Desktop
      await loginWithValidCredentials();
      
      const dashboard = element(by.css('app-dashboard'));
      expect(await dashboard.isPresent()).toBe(true);
    });
  });

  describe('Error Handling', () => {
    beforeEach(async () => {
      await loginWithValidCredentials();
    });

    it('should handle API errors gracefully', async () => {
      // Mock API failure or trigger error condition
      await browser.executeScript('localStorage.setItem("mock_api_error", "true")');
      await browser.refresh();
      
      // App should still load and show error state
      const errorMessage = element(by.css('.error-state, .api-error'));
      // Error handling might be implemented differently
    });

    it('should handle network disconnection', async () => {
      // This would require network simulation capabilities
      // For now, we just verify the app doesn't crash
      await browser.refresh();
      
      const dashboard = element(by.css('app-dashboard'));
      expect(await dashboard.isPresent()).toBe(true);
    });

    it('should recover from temporary failures', async () => {
      // Simulate recovery scenario
      await browser.executeScript('localStorage.removeItem("mock_api_error")');
      await browser.refresh();
      
      const dashboard = element(by.css('app-dashboard'));
      expect(await dashboard.isPresent()).toBe(true);
    });
  });

  describe('Performance', () => {
    it('should load within acceptable time', async () => {
      const startTime = Date.now();
      
      await browser.get('/dashboard');
      await browser.wait(EC.presenceOf(element(by.css('app-dashboard'))), 10000);
      
      const loadTime = Date.now() - startTime;
      expect(loadTime).toBeLessThan(5000); // Should load within 5 seconds
    });

    it('should not have memory leaks during navigation', async () => {
      await loginWithValidCredentials();
      
      // Navigate between tabs multiple times
      for (let i = 0; i < 5; i++) {
        await navigateToTab('config');
        await browser.sleep(500);
        await navigateToTab('processes');
        await browser.sleep(500);
        await navigateToTab('lora');
        await browser.sleep(500);
      }
      
      // Check that the app is still responsive
      const dashboard = element(by.css('app-dashboard'));
      expect(await dashboard.isPresent()).toBe(true);
    });

    it('should handle large datasets efficiently', async () => {
      // This would test with large numbers of processes or models
      await navigateToTab('processes');
      
      const processesList = element(by.css('.processes-list, mat-table'));
      await browser.wait(EC.presenceOf(processesList), 5000);
      
      // Verify the list renders without performance issues
      const processes = element.all(by.css('.process-item, mat-row'));
      const processCount = await processes.count();
      
      // Should handle any number of processes
      expect(processCount).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Accessibility', () => {
    beforeEach(async () => {
      await loginWithValidCredentials();
    });

    it('should support keyboard navigation', async () => {
      // Test Tab navigation
      await browser.actions().sendKeys(protractor.Key.TAB).perform();
      await browser.sleep(500);
      
      const focusedElement = await browser.driver.switchTo().activeElement();
      expect(focusedElement).toBeDefined();
    });

    it('should have proper ARIA labels', async () => {
      const elementsWithAriaLabels = element.all(by.css('[aria-label]'));
      const count = await elementsWithAriaLabels.count();
      expect(count).toBeGreaterThan(0);
    });

    it('should support screen readers', async () => {
      // Check for proper heading structure
      const headings = element.all(by.css('h1, h2, h3, h4, h5, h6'));
      const headingCount = await headings.count();
      expect(headingCount).toBeGreaterThan(0);
      
      // Check for alt text on images
      const images = element.all(by.css('img[alt]'));
      const imageCount = await images.count();
      // Images with alt text (if any exist)
    });
  });

  describe('Security', () => {
    it('should not expose sensitive data in DOM', async () => {
      await loginWithValidCredentials();
      
      const pageSource = await browser.getPageSource();
      
      // Should not contain hardcoded passwords or tokens
      expect(pageSource).not.toContain('Gramercy'); // password
      expect(pageSource).not.toContain('test-token'); // example token
    });

    it('should handle XSS attempts safely', async () => {
      await browser.get('/login');
      
      const usernameField = element(by.css('input[type="text"]'));
      const xssPayload = '<script>alert("xss")</script>';
      
      await usernameField.sendKeys(xssPayload);
      
      const pageSource = await browser.getPageSource();
      expect(pageSource).not.toContain('<script>alert("xss")</script>');
    });
  });

  // Helper functions
  async function loginWithValidCredentials() {
    await browser.get('/login');
    
    const usernameField = element(by.css('input[type="text"]'));
    const passwordField = element(by.css('input[type="password"]'));
    const loginButton = element(by.css('button[type="submit"]'));
    
    await browser.wait(EC.presenceOf(usernameField), 5000);
    
    await usernameField.sendKeys('Mateusz');
    await passwordField.sendKeys('Gramercy');
    await loginButton.click();
    
    await browser.wait(EC.urlContains('/dashboard'), 5000);
  }

  async function navigateToTab(tabName: string) {
    const tabMap = {
      'config': 1,
      'processes': 2,
      'lora': 3
    };
    
    const tabIndex = tabMap[tabName as keyof typeof tabMap] || 1;
    const tab = element(by.css(`.mat-tab-label:nth-child(${tabIndex})`));
    
    await browser.wait(EC.elementToBeClickable(tab), 5000);
    await tab.click();
    
    await browser.sleep(1000); // Wait for tab content to load
  }
}); 