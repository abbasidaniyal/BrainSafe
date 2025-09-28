// BabyShield Popup Script
// Handles the extension popup interface

class BabyShieldPopup {
  constructor() {
    this.currentTab = null;
    this.settings = {
      isEnabled: true
    };
    
    this.init();
  }

  async init() {
    console.log('BabyShield: Popup initialized');
    
    // Get current tab
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    this.currentTab = tabs[0];
    
    // Load current settings
    await this.loadSettings();

    console.log(this.settings);
    
    // Setup event listeners
    this.setupEventListeners();
    
    // Update UI
    this.updateUI();
    
  }

  setupEventListeners() {
    // Main toggle
    const enabledToggle = document.getElementById('enabledToggle');
    enabledToggle.addEventListener('change', (e) => {
      this.updateSetting('isEnabled', e.target.checked);
    });
  }

  async loadSettings() {
      this.settings = await this.sendToBackground({ action: 'getSettings' });
      console.log('BabyShield: Settings loaded:', this.settings); 
  }

  updateUI() {
    // Update toggle states
    document.getElementById('enabledToggle').checked = this.settings.isEnabled;

    // Update status indicator
    this.updateStatusIndicator();
  }

  updateStatusIndicator() {
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');
    
    if (this.settings.isEnabled) {
      statusDot.className = 'status-dot active';
      statusText.textContent = 'Active';
    } else {
      statusDot.className = 'status-dot inactive';
      statusText.textContent = 'Disabled';
    }
  }

  async updateSetting(key, value) {
    try {
      this.settings[key] = value;
      
      await this.sendToBackground({
        action: 'updateSettings',
        settings: { [key]: value }
      });
      
      this.updateStatusIndicator();
      console.log(`BabyShield: Updated ${key} to:`, value);
      
    } catch (error) {
      console.error('BabyShield: Failed to update setting:', error);
    }
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

  sendToTab(message) {
    return new Promise((resolve, reject) => {
      if (!this.currentTab) {
        reject(new Error('No active tab'));
        return;
      }
      
      chrome.tabs.sendMessage(this.currentTab.id, message, (response) => {
        if (chrome.runtime.lastError) {
          reject(chrome.runtime.lastError);
        } else {
          resolve(response);
        }
      });
    });
  }
}

// Initialize popup when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new BabyShieldPopup();
});