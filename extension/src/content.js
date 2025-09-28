// BabyShield Content Script
// Intercepts and monitors video elements on web pages

class VideoInterceptor {
  constructor() {
    this.videos = new Map();
    this.isEnabled = true;
    this.init();
  }

  init() {
    console.log('BabyShield: Initializing video interceptor');
    
    // Listen for messages from background script
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      this.handleMessage(message, sendResponse);
    });

    chrome.runtime.sendMessage({ action: 'getStatus' }, (response) => {
      if (response && typeof response.isEnabled === 'boolean') {
        this.isEnabled = response.isEnabled;
        console.log(`BabyShield: Initial enabled state is ${this.isEnabled}`);
      }

          
    // Start monitoring videos
    this.startVideoMonitoring();
    
    // Listen for dynamically added videos
    this.observeVideoElements();
    });


  }

  startVideoMonitoring() {
    // Find existing videos
    const existingVideos = document.querySelectorAll('video');
    console.log(`BabyShield: Found ${existingVideos.length} existing video(s)`);
    existingVideos.forEach(video => this.interceptVideo(video));
    
    // Set up automatic checker every 5 seconds
    setInterval(() => {
      if (!this.isEnabled) return;
      
      const allVideos = document.querySelectorAll('video');
      
      allVideos.forEach(this.interceptVideo.bind(this));
    }, 5000); // Check every 5 seconds
  }


  observeVideoElements() {
    // Watch for iframe changes too (for embedded videos)
    const iframes = document.querySelectorAll('iframe');
    iframes.forEach(iframe => {
      try {
        iframe.addEventListener('load', () => {
          this.checkIframeForVideos(iframe);
        });
      } catch (e) {
        // Cross-origin iframe, can't access
        console.log('BabyShield: Cross-origin iframe detected');
      }
    });
  }

  checkIframeForVideos(iframe) {
    try {
      const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
      const videos = iframeDoc.querySelectorAll('video');
      videos.forEach(video => this.interceptVideo(video));
    } catch (e) {
      console.log('BabyShield: Cannot access iframe content (cross-origin)');
    }
  }

  interceptVideo(videoElement) {
    if (this.videos.has(videoElement.src)) {
      return; // Already intercepted
    }

    console.log('BabyShield: New video detected', videoElement);
    
    const videoData = {
      id: Date.now() + Math.random(),
      element: videoElement,
      originalPlaybackRate: videoElement.playbackRate,
      url: document.location.href,
      isAnalyzed: false,
      appliedFilters: []
    };

    this.videos.set(videoElement.src, {videoElement, videoData});
    
    // Add event listeners
    this.setupVideoEventListeners(videoElement, videoData);
    
    // Analyze video when it starts playing
    videoElement.addEventListener('play', () => {
      this.analyzeVideo(videoElement, videoData);
    });

    // Analyze if already playing
    if (!videoElement.paused) {
      this.analyzeVideo(videoElement, videoData);
    }
  }

  setupVideoEventListeners(videoElement, videoData) {
    // Monitor video source changes
    videoElement.addEventListener('loadstart', () => {
      videoData.isAnalyzed = false;
      this.clearVideoFilters(videoElement);
    });

    // Monitor play events
    videoElement.addEventListener('play', () => {
      if (!videoData.isAnalyzed) {
        this.analyzeVideo(videoElement, videoData);
      }
    });
  }

  async analyzeVideo(videoElement, videoData) {
    if (videoData.isAnalyzed) return;

    console.log('BabyShield: Analyzing video content');

    console.log("Video Data:", videoData);
    
    try {
      // Get video metadata
      const videoMetadata = this.extractVideoMetadata(videoElement);

      console.log('BabyShield: Video metadata:', videoMetadata);
      
      // Send to background script for API call
      const response = await this.sendToBackground({
        action: 'analyzeVideo',
        data: videoMetadata
      });

      videoData.isAnalyzed = true;
      
      // Apply safety measures based on response
      this.applySafetyMeasures(videoElement, videoData, response);
      
    } catch (error) {
      console.error('BabyShield: Error analyzing video:', error);
    }
  }

  extractVideoMetadata(videoElement) {
    return {
      src: videoElement.src || videoElement.currentSrc,
      duration: videoElement.duration,
      videoWidth: videoElement.videoWidth,
      videoHeight: videoElement.videoHeight,
      currentTime: videoElement.currentTime,
      volume: videoElement.volume,
      playbackRate: videoElement.playbackRate,
      url: window.location.href,
      title: document.title
    };
  }

  applySafetyMeasures(videoElement, videoData, analysisResponse) {
    const { actions } = analysisResponse;
    
    console.log(`BabyShield: Applying safety measures for content`);
    console.log("Analysis Response:", analysisResponse);

    if (actions) {
      // Apply speed reduction
      if (actions.reduceSpeed) {
        this.reducePlaybackSpeed(videoElement, actions.speedFactor || 0.5);
      }

      // Apply visual filters
      if (actions.applyFilters) {
        this.applyVisualFilters(videoElement, actions.filters || ['tone-down']);
      }

      // Show warning
      if (actions.showWarning) {
        this.showWarning(videoElement, videoData, actions.warningMessage);
      }
    }
  }

  reducePlaybackSpeed(videoElement, speedFactor) {
    console.log(`BabyShield: Reducing playback speed to ${speedFactor}x`);
    videoElement.playbackRate = speedFactor;
  }

  applyVisualFilters(videoElement, filters) {
    console.log('BabyShield: Applying visual filters:', filters);
    
    let filterString = '';
    
    filters.forEach(filter => {
      switch (filter) {
        case 'tone-down':
          filterString += 'brightness(0.8) contrast(0.9) saturate(0.7) ';
          break;
        case 'blur':
          filterString += 'blur(2px) ';
          break;
        case 'grayscale':
          filterString += 'grayscale(0.5) ';
          break;
      }
    });

    videoElement.style.filter = filterString.trim();
  }

  showWarning(videoElement, videoData, message) {
    console.log('BabyShield: Showing warning and pausing video');
    
    // Pause the video
    videoElement.pause();

    // Show alert dialog
    const warningMessage = message || 'This content may not be appropriate for children.';
    const userChoice = confirm(`⚠️ Content Warning\n\n${warningMessage}\n\nClick OK to continue watching, or Cancel to skip this video.`);
    
    if (userChoice) {
      // User chose to continue
      videoElement.play();
    } else {
      // User chose to skip
      videoElement.currentTime = videoElement.duration; // Skip to end
    }
  }

  clearVideoFilters(videoElement) {
    videoElement.style.filter = '';
  }

  sendToBackground(message) {
    return new Promise((resolve, reject) => {
      chrome.runtime.sendMessage(message, (response) => {
        if (chrome.runtime.lastError) {
          reject(chrome.runtime.lastError);
        } else {
          resolve(response);
        }
      });
    });
  }

  handleMessage(message, sendResponse) {
    switch (message.action) {
      case 'getVideoCount':
        sendResponse({ count: this.videos.size });
        break;
      
      case 'toggleEnabled':
        this.isEnabled = message.isEnabled;
        sendResponse({ success: true });
        break;
        
      default:
        sendResponse({ error: 'Unknown action' });
    }
  }
}

// Initialize the video interceptor when the page loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new VideoInterceptor();
  });
} else {
  new VideoInterceptor();
}