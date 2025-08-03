// Karma configuration file for LoRA Dashboard
module.exports = function (config) {
  config.set({
    basePath: '',
    frameworks: ['jasmine', '@angular-devkit/build-angular'],
    plugins: [
      require('karma-jasmine'),
      require('karma-chrome-headless'),
      require('karma-chrome-launcher'),
      require('karma-jasmine-html-reporter'),
      require('karma-coverage'),
      require('karma-junit-reporter'),
      require('karma-spec-reporter'),
      require('@angular-devkit/build-angular/plugins/karma')
    ],
    client: {
      jasmine: {
        // you can add configuration options for Jasmine here
        // the possible options are listed at https://jasmine.github.io/api/edge/Configuration.html
        random: true,
        seed: '4321',
        stopSpecOnExpectationFailure: false,
        failFast: false,
        timeoutInterval: 30000
      },
      clearContext: false // leave Jasmine Spec Runner output visible in browser
    },
    jasmineHtmlReporter: {
      suppressAll: true // removes the duplicated traces
    },
    coverageReporter: {
      dir: require('path').join(__dirname, './coverage/lora-dashboard'),
      subdir: '.',
      reporters: [
        { type: 'html' },
        { type: 'text-summary' },
        { type: 'lcov' },
        { type: 'json' },
        { type: 'cobertura' }
      ],
      check: {
        global: {
          statements: 80,
          branches: 75,
          functions: 80,
          lines: 80
        }
      }
    },
    junitReporter: {
      outputDir: './coverage/junit',
      outputFile: 'test-results.xml',
      suite: 'LoRA Dashboard Unit Tests',
      useBrowserName: false,
      nameFormatter: undefined,
      classNameFormatter: undefined,
      properties: {}
    },
    specReporter: {
      maxLogLines: 5,
      suppressErrorSummary: true,
      suppressFailed: false,
      suppressPassed: false,
      suppressSkipped: true,
      showSpecTiming: true,
      failFast: false
    },
    reporters: ['progress', 'kjhtml', 'coverage', 'junit', 'spec'],
    browsers: ['Chrome'],
    customLaunchers: {
      ChromeHeadlessCI: {
        base: 'ChromeHeadless',
        flags: [
          '--no-sandbox',
          '--disable-web-security',
          '--disable-features=VizDisplayCompositor',
          '--disable-gpu',
          '--remote-debugging-port=9222'
        ]
      },
      ChromeDebugging: {
        base: 'Chrome',
        flags: ['--remote-debugging-port=9333'],
        debug: true
      }
    },
    restartOnFileChange: true,
    
    // Performance and timeout settings
    browserDisconnectTimeout: 10000,
    browserDisconnectTolerance: 3,
    browserNoActivityTimeout: 60000,
    captureTimeout: 60000,
    processKillTimeout: 10000,
    
    // File watching
    autoWatch: true,
    usePolling: false,
    
    // Logging
    logLevel: config.LOG_INFO,
    colors: true,
    
    // Concurrency settings
    concurrency: Infinity,
    
    // Test execution settings
    singleRun: false,
    
    // Source map support
    preprocessors: {
      'src/**/*.ts': ['coverage']
    },
    
    // MIME types
    mime: {
      'text/x-typescript': ['ts','tsx']
    },
    
    // Webpack settings for Angular
    webpack: {
      stats: 'errors-only'
    },
    
    // Additional settings for CI environment
    ...(process.env.CI && {
      browsers: ['ChromeHeadlessCI'],
      singleRun: true,
      autoWatch: false,
      reporters: ['progress', 'coverage', 'junit'],
      logLevel: config.LOG_ERROR
    })
  });
}; 