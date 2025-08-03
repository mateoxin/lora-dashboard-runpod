import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from './auth/auth.service';
import { ApiService } from './core/api.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  title = 'LoRA Dashboard';
  isLoading = false;

  constructor(
    public authService: AuthService,
    private router: Router,
    private apiService: ApiService
  ) {}

  ngOnInit(): void {
    // Authentication check temporarily disabled
    // if (!this.authService.isAuthenticated()) {
    //   this.router.navigate(['/login']);
    // }
  }

  /**
   * Logout user and redirect to login page
   */
  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  /**
   * Check application health (for testing)
   */
  checkHealth(): void {
    this.isLoading = true;
    this.apiService.getHealth().subscribe({
      next: (response) => {
        console.log('Health check:', response);
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Health check failed:', error);
        this.isLoading = false;
      }
    });
  }
}
