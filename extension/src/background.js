// BabyShield Background Script (Service Worker)
// Handles API communication and extension management

class Settings {
    constructor() {
        this.isEnabled = true;
    }

    async load() {
        const settings = await chrome.storage.sync.get({
            isEnabled: this.isEnabled,
        });
        this.isEnabled = settings.isEnabled;
    }

    async save() {
        await chrome.storage.sync.set({
            isEnabled: this.isEnabled
        });
    }
}

class BabyShieldBackground {
  constructor() {
    this.settings = new Settings()
    
    this.init();
  }

  init() {
    console.log('BabyShield: Background script initialized');
    
    // Listen for messages from content scripts
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      this.handleMessage(message, sender, sendResponse);
      return true; // Keep message channel open for async response
    });

    // Listen for extension install/startup
    chrome.runtime.onStartup.addListener(() => {
      this.settings.load();
    });

    chrome.runtime.onInstalled.addListener(() => {
      this.settings.load();
    });
  }

  async handleMessage(message, sender, sendResponse) {
    try {
      switch (message.action) {
        case 'analyzeVideo':
          const analysisResult = await this.analyzeVideo(message.data);
          sendResponse(analysisResult);
          break;

        case 'getSettings':
          const settings = Object.values(this.settings);
          sendResponse(settings);
          break;

        case 'updateSettings':
          Object.assign(this.settings, message.settings);
          await this.settings.save();
          // send toggleEnabled to all tabs
          const tabs = await chrome.tabs.query({});
          tabs.forEach(tab => {
            chrome.tabs.sendMessage(tab.id, { action: 'toggleEnabled', isEnabled: this.settings.isEnabled });
          });
          sendResponse({ success: true });
          break;

        case 'getStatus':
          sendResponse({ 
            isEnabled: this.settings.isEnabled,
          });
          break;

        default:
          sendResponse({ error: 'Unknown action' });
      }
    } catch (error) {
      console.error('BabyShield: Background script error:', error);
      sendResponse({ error: error.message });
    }
  }

  async analyzeVideo(videoMetadata) {
    console.log('BabyShield: Analyzing video with metadata:', videoMetadata);
    
    try {

      // Real API call would look like this:
      const response = await fetch("http://127.0.0.1:8000/api/download-video/", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: videoMetadata.url,
        })
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
      }

      const result = await response.json();
      return {actions: result};
      
    } catch (error) {
      console.error('BabyShield: API call failed:', error);
      
      // Return safe default response on error
      return {
        confidence: 0.5,
        actions: {
          reduceSpeed: false,
          applyFilters: false,
          showWarning: false
        }
      };
    }
  }


}

// Initialize the background script
new BabyShieldBackground();