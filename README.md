# BabyShield - AI-Powered Video Content Safety Platform# BabyShield Chrome Extension



<!-- Main intro section - to be filled -->A Chrome extension that monitors video content on web pages and provides safety controls for children.



---## Features



## 🏗️ Project Structure- **Video Detection**: Automatically detects all video elements on web pages

- **Content Analysis**: Sends video data to backend API for content safety analysis

This is a monorepo containing three interconnected components that work together to provide comprehensive video content safety monitoring:- **Playback Control**: Adjusts video playback speed based on content analysis

- **Visual Filters**: Applies color tone filters to reduce harsh visuals

```- **Safety Warnings**: Shows alerts and pauses inappropriate content

babyshield/

├── extension/          # Chrome Extension - Frontend client## Installation

├── backend/           # Django API - Content analysis service  

├── sdk-agent/         # SDK Agent - Integration toolkit1. Open Chrome and navigate to `chrome://extensions/`

└── docs/             # Documentation and resources2. Enable "Developer mode" in the top right corner

```3. Click "Load unpacked extension" button

4. Select the `extension` folder (not the root `babyshield` folder)

### 🔧 Components Overview5. The BabyShield extension will appear in your browser toolbar



| Component | Technology | Purpose | Status |## Testing

|-----------|------------|---------|--------|

| **Chrome Extension** | JavaScript, HTML, CSS | Browser-based video interception and safety controls | ✅ Complete |1. After installation, open the `extension/test-page.html` file in Chrome

| **Backend API** | Django, Python, AI/ML | Video content analysis and safety scoring | 🚧 In Development |2. Click the BabyShield extension icon to open the control panel

| **SDK Agent** | Python/Node.js | Integration toolkit for third-party platforms | 📋 Planned |3. Play the test videos to see different safety behaviors:

   - Video 1: Normal playback (safe content)

---   - Video 2: Reduced speed + filters (moderate content)

   - Video 3: Warning dialog + pause (risky content)

## 🚀 Quick Start4. Check the browser console (F12) for debug messages



### Prerequisites## Usage

- Node.js 16+ 

- Python 3.8+1. Navigate to any webpage with video content (YouTube, news sites, etc.)

- Chrome Browser2. The extension automatically detects and monitors videos

- Git3. Content is analyzed using a mock backend API (placeholder)

4. Safety measures are applied automatically:

### 1. Clone Repository   - **Speed Reduction**: Slows down intense content

```bash   - **Visual Filters**: Tone down colors and brightness

git clone <repository-url>   - **Warnings**: Shows alerts for inappropriate content

cd babyshield

```## Development



### 2. Set Up Chrome Extension### Project Structure

```bash```

cd extensionbabyshield/

# Follow extension/README.md for installation├── extension/           # Chrome Extension

```│   ├── manifest.json   # Extension configuration

│   ├── content.js      # Content script for video manipulation

### 3. Set Up Backend API│   ├── background.js   # Service worker for API communication

```bash│   ├── popup.html      # Extension popup interface

cd backend│   ├── popup.js        # Popup functionality

pip install -r requirements.txt│   ├── styles.css      # Styling

python manage.py migrate│   ├── test-page.html  # Demo page for testing

python manage.py runserver│   └── icons/          # Extension icons

# Follow backend/README.md for detailed setup├── backend/            # Backend API (planned)

```│   └── README.md       # Backend documentation

├── .github/            # Project configuration

### 4. Set Up SDK Agent└── README.md           # Main documentation

```bash```

cd sdk-agent

# Follow sdk-agent/README.md for installation### API Integration

```The extension communicates with a backend API endpoint to analyze video content and receive safety recommendations.



---**Current Status**: Uses mock API responses for demonstration

**API Endpoint**: `https://api.babyshield.placeholder.com/analyze` (placeholder)

## 📚 Component Documentation

#### API Request Format:

### [Chrome Extension](./extension/README.md)```json

Browser extension that intercepts video elements on web pages and applies safety measures in real-time.{

  "videoData": {

**Key Features:**    "src": "video_url",

- Automatic video detection across all websites    "duration": 120,

- Real-time content analysis integration    "videoWidth": 1920,

- Playback speed control and visual filters      "videoHeight": 1080,

- Parental warning system with user controls    "url": "page_url",

- Comprehensive settings and monitoring dashboard    "title": "page_title"

  },

### [Backend API](./backend/README.md)    "timestamp": 1640995200000

Django-based REST API that provides AI-powered video content analysis and safety scoring.}

```

**Key Features:**

- Video content analysis using ML models#### API Response Format:

- Safety level classification (safe/moderate/risky)```json

- RESTful API with authentication{

- Database storage for analysis results  "safetyLevel": "safe|moderate|risky",

- Scalable deployment architecture  "confidence": 0.85,

  "actions": {

### [SDK Agent](./sdk-agent/README.md)    "reduceSpeed": false,

Integration toolkit that enables third-party platforms to incorporate BabyShield functionality.    "speedFactor": 0.75,

    "applyFilters": true,

**Key Features:**    "filters": ["tone-down"],

- Easy integration APIs for web platforms    "showWarning": false,

- Customizable safety policies    "warningMessage": "Custom warning text"

- Analytics and reporting tools  },

- Multi-language support  "analysisId": "unique_id",

- Enterprise-grade security  "timestamp": 1640995200000

}

---```



## 🔄 System Architecture#### Integration Steps:

1. Replace the placeholder API endpoint in `extension/background.js`

```2. Add authentication headers if required

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐3. Update the `analyzeVideo()` method to use real API calls

│  Chrome         │    │  Backend API    │    │  SDK Agent      │4. Handle error cases and fallbacks appropriately

│  Extension      │◄──►│  (Django)       │◄──►│  (Integration)  │5. Deploy backend API (see `backend/README.md` for details)

│                 │    │                 │    │                 │

│ • Video Detection│    │ • Content Analysis│   │ • Platform APIs │## License

│ • Safety Controls│    │ • ML Models     │    │ • Custom Policies│MIT License
│ • User Interface │    │ • Database      │    │ • Analytics     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 🛠️ Development Workflow

### Setting Up Development Environment
```bash
# Install all dependencies
npm run install-all

# Start all services in development mode
npm run dev

# Run tests across all components
npm run test

# Build for production
npm run build
```

### Code Standards
- **JavaScript**: ESLint + Prettier configuration
- **Python**: Black formatter + Flake8 linting  
- **Git**: Conventional commit messages
- **Testing**: Unit tests required for all components

---

## 🚢 Deployment

### Chrome Extension
1. Build extension package
2. Submit to Chrome Web Store
3. Configure API endpoints for production

### Backend API  
1. Deploy to cloud provider (AWS/GCP/Azure)
2. Set up database and ML model services
3. Configure authentication and rate limiting

### SDK Agent
1. Package and publish to npm/PyPI
2. Generate API documentation
3. Provide integration examples

---

## 📊 Monitoring & Analytics

- **Extension Usage**: User engagement and safety interventions
- **API Performance**: Response times and analysis accuracy  
- **Content Analysis**: Safety trend analysis and model improvements
- **Error Tracking**: Comprehensive logging and alerting

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Follow component-specific development guides
4. Run tests and ensure code quality
5. Submit pull request with detailed description

See individual component READMEs for specific contribution guidelines.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

- **Documentation**: Check component-specific READMEs
- **Issues**: Create GitHub issues for bugs and feature requests  
- **Community**: Join our Discord/Slack for discussions
- **Enterprise**: Contact team for business inquiries

---

*Building a safer digital environment for children, one video at a time.* 🛡️👶