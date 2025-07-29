# Deploy Frontend - Complete Guide

Deploy the Angular LoRA Dashboard to Netlify and Vercel with production optimizations and proper routing configuration.

## 🏗️ Build Preparation

### 1. Production Build
```bash
cd Serverless/Front/lora-dashboard

# Install dependencies
npm install

# Build for production
ng build --configuration production

# Verify build
ls -la dist/lora-dashboard/
```

### 2. Environment Configuration
Update `src/environments/environment.prod.ts`:
```typescript
export const environment = {
  production: true,
  apiBaseUrl: 'https://your-runpod-endpoint.runpod.ai/api',
  encryptionKey: 'LoRA-Dashboard-Secret-Key-2024-PROD',
  autoRefreshInterval: 5000,
  maxFileSize: 50 * 1024 * 1024,
};
```

## 🚀 Netlify Deployment

### Method A: Netlify CLI (Recommended)

#### Install Netlify CLI
```bash
npm install -g netlify-cli
netlify login
```

#### Deploy
```bash
# One-time deployment
netlify deploy --prod --dir dist/lora-dashboard

# Or set up continuous deployment
netlify init

# Configure build settings
cat > netlify.toml << EOF
[build]
  base = "Serverless/Front/lora-dashboard"
  command = "npm run build:prod"
  publish = "dist/lora-dashboard"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/*.js"
  [headers.values]
    Cache-Control = "public, max-age=31536000"

[[headers]]
  for = "/*.css"
  [headers.values]
    Cache-Control = "public, max-age=31536000"

[[headers]]
  for = "/*.html"
  [headers.values]
    Cache-Control = "public, max-age=0, must-revalidate"
EOF
```

### Method B: Netlify Dashboard

1. **Login to Netlify Dashboard**
2. **Click "New site from Git"**
3. **Connect your repository**
4. **Configure build settings:**
   - Base directory: `Serverless/Front/lora-dashboard`
   - Build command: `npm run build:prod`
   - Publish directory: `dist/lora-dashboard`
   - Node version: `18`

5. **Add environment variables** (if needed):
   - Go to Site settings → Environment variables
   - Add any build-time variables

6. **Configure redirects:**
   - Create `public/_redirects` file:
   ```
   /*    /index.html   200
   ```

7. **Deploy and test**

### Netlify Production Optimizations

#### Custom Headers
```toml
# netlify.toml
[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
    Content-Security-Policy = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://your-runpod-endpoint.runpod.ai; font-src 'self' data:"

[[headers]]
  for = "/api/*"
  [headers.values]
    Access-Control-Allow-Origin = "https://your-domain.netlify.app"
```

#### Build Optimizations
```json
// angular.json - production configuration
"production": {
  "budgets": [
    {
      "type": "initial",
      "maximumWarning": "2mb",
      "maximumError": "5mb"
    }
  ],
  "outputHashing": "all",
  "optimization": true,
  "sourceMap": false,
  "namedChunks": false,
  "extractLicenses": true,
  "vendorChunk": false,
  "buildOptimizer": true,
  "serviceWorker": false
}
```

## ⚡ Vercel Deployment

### Method A: Vercel CLI

#### Install Vercel CLI
```bash
npm install -g vercel
vercel login
```

#### Deploy
```bash
# Initialize Vercel project
vercel

# Configure vercel.json
cat > vercel.json << EOF
{
  "version": 2,
  "name": "lora-dashboard",
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist/lora-dashboard"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*\\.(js|css|ico|png|jpg|jpeg|gif|svg|woff|woff2|ttf|eot))",
      "headers": {
        "Cache-Control": "public, max-age=31536000, immutable"
      }
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-Content-Type-Options", 
          "value": "nosniff"
        }
      ]
    }
  ]
}
EOF

# Add build script to package.json
cat > package.json << EOF
{
  "name": "lora-dashboard-vercel",
  "scripts": {
    "build": "cd Serverless/Front/lora-dashboard && npm install && ng build --configuration production"
  }
}
EOF

# Deploy
vercel --prod
```

### Method B: Vercel Dashboard

1. **Import project from Git**
2. **Configure framework preset:**
   - Framework: Other
   - Build command: `cd Serverless/Front/lora-dashboard && npm install && ng build --configuration production`
   - Output directory: `Serverless/Front/lora-dashboard/dist/lora-dashboard`
   - Install command: `npm install`

3. **Add environment variables** (if needed)
4. **Deploy**

### Vercel Production Optimizations

#### Edge Functions (Optional)
```typescript
// api/health.ts - Simple health check edge function
import { NextRequest, NextResponse } from 'next/server';

export const config = {
  runtime: 'edge',
};

export default async function handler(req: NextRequest) {
  return NextResponse.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    frontend: 'ok'
  });
}
```

#### Performance Configuration
```json
// vercel.json - performance settings
{
  "functions": {
    "app/build/**": {
      "maxDuration": 30
    }
  },
  "regions": ["iad1"],
  "github": {
    "silent": true
  }
}
```

## 🔧 Post-Deployment Configuration

### 1. Custom Domain Setup

#### Netlify
```bash
# Add custom domain
netlify domains:add yourdomain.com

# Configure DNS
# Add CNAME record: www.yourdomain.com → your-site.netlify.app
# Add ALIAS/ANAME record: yourdomain.com → your-site.netlify.app
```

#### Vercel
```bash
# Add custom domain
vercel domains add yourdomain.com

# Configure DNS (automatic with Vercel nameservers)
```

### 2. SSL Certificate
Both platforms provide automatic SSL certificates via Let's Encrypt.

### 3. Analytics Setup

#### Netlify Analytics
```toml
# netlify.toml
[build]
  command = "npm run build:prod"
  
[[plugins]]
  package = "@netlify/plugin-lighthouse"
```

#### Vercel Analytics
```bash
npm install @vercel/analytics

# Add to app.module.ts
import { inject } from '@vercel/analytics';
inject();
```

## 🧪 Testing Deployment

### Automated Testing
```bash
# Test production build locally
ng build --configuration production
cd dist/lora-dashboard
python -m http.server 8080

# Visit http://localhost:8080
```

### Performance Testing
```bash
# Lighthouse CI
npm install -g @lhci/cli

# Run Lighthouse
lhci autorun --collect.url=https://your-domain.com
```

### E2E Testing
```bash
# Update cypress.config.ts for production
export default defineConfig({
  e2e: {
    baseUrl: 'https://your-domain.com',
    video: false,
    screenshotOnRunFailure: false,
  },
});

# Run tests
npx cypress run --env production=true
```

## 📊 Monitoring & Optimization

### 1. Performance Monitoring
```typescript
// app.module.ts - Add performance monitoring
import { PerformanceObserver } from 'perf_hooks';

if (environment.production) {
  // Monitor Core Web Vitals
  const observer = new PerformanceObserver((list) => {
    for (const entry of list.getEntries()) {
      console.log(`${entry.name}: ${entry.value}`);
    }
  });
  
  observer.observe({entryTypes: ['measure', 'navigation']});
}
```

### 2. Error Tracking
```typescript
// Add error tracking (optional)
import * as Sentry from '@sentry/angular';

if (environment.production) {
  Sentry.init({
    dsn: 'your-sentry-dsn',
    environment: 'production'
  });
}
```

### 3. Bundle Analysis
```bash
# Analyze bundle size
npm install -g webpack-bundle-analyzer

# Generate stats
ng build --configuration production --stats-json

# Analyze
webpack-bundle-analyzer dist/lora-dashboard/stats.json
```

## 🚨 Troubleshooting

### Common Issues

**1. Routing not working (404 errors)**
- Ensure redirects are configured: `/* → /index.html`
- Check that `angular.json` has `"outputPath": "dist/lora-dashboard"`

**2. Build failures**
```bash
# Common fixes
rm -rf node_modules package-lock.json
npm install

# Clear Angular cache
ng cache clean

# Check Node version
node --version  # Should be 18+
```

**3. CORS issues in production**
```typescript
// Update environment.prod.ts
apiBaseUrl: 'https://your-actual-backend-url/api'
```

**4. Large bundle size**
```bash
# Enable tree shaking
ng build --configuration production --build-optimizer

# Lazy load modules
# Convert to standalone components or lazy-loaded modules
```

## 📋 Deployment Checklist

### Pre-deployment
- [ ] Environment variables configured
- [ ] Backend URL updated
- [ ] Production build tested locally
- [ ] Bundle size optimized
- [ ] Error handling implemented

### Netlify Deployment
- [ ] Repository connected
- [ ] Build settings configured
- [ ] Redirects configured (`_redirects` or `netlify.toml`)
- [ ] Environment variables set
- [ ] Custom domain configured (if applicable)
- [ ] SSL certificate active

### Vercel Deployment
- [ ] Project imported from Git
- [ ] Build command configured
- [ ] `vercel.json` created with routes
- [ ] Environment variables set
- [ ] Custom domain configured (if applicable)
- [ ] Edge functions configured (if applicable)

### Post-deployment
- [ ] All routes working (test SPA navigation)
- [ ] API connectivity verified
- [ ] Authentication flow tested
- [ ] Performance metrics acceptable
- [ ] Error tracking configured
- [ ] Monitoring set up

## 🔗 Useful Links

- [Netlify Documentation](https://docs.netlify.com/)
- [Vercel Documentation](https://vercel.com/docs)
- [Angular Deployment Guide](https://angular.io/guide/deployment)
- [Performance Best Practices](https://web.dev/performance/)

## 💡 Best Practices

1. **Use CDN** - Both platforms provide global CDN automatically
2. **Optimize images** - Use WebP format and lazy loading
3. **Minimize JavaScript** - Remove unused dependencies
4. **Enable compression** - Gzip/Brotli (automatic on both platforms)
5. **Cache static assets** - Long cache times for JS/CSS
6. **Monitor performance** - Regular Lighthouse audits
7. **Test on mobile** - Responsive design verification
8. **Security headers** - CSP, HSTS, X-Frame-Options 