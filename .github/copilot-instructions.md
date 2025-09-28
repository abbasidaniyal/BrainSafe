# BabyShield - AI-Powered Video Content Safety Platform

## Project Overview
BabyShield is a comprehensive video content safety platform consisting of three main components that work together to provide real-time video content analysis and protection for children online.

## Components
1. **Chrome Extension**: Browser-based video interception and safety controls
2. **Backend API**: Django-based content analysis service with AI/ML models
3. **SDK Agent**: Integration toolkit for third-party platforms

## Features
- **Real-time Video Detection**: Automatically detects video elements across all websites
- **AI-Powered Analysis**: Uses machine learning models to classify content safety
- **Dynamic Safety Controls**: Applies speed reduction, visual filters, and warnings
- **Comprehensive Settings**: User-configurable safety policies and preferences
- **Developer-Friendly**: SDKs and APIs for easy platform integration

## Architecture

### Extension (`/extension/`)
- `manifest.json`: Chrome extension configuration (Manifest V3)
- `src/content.js`: Video detection and manipulation logic
- `src/background.js`: Service worker for API communication
- `src/popup.html/js`: User interface and control panel
- `src/styles.css`: UI styling and visual effects
- `test-page.html`: Demo page for testing functionality
- `icons/`: Extension icons and branding assets

### Backend (`/backend/`)
- Django REST API with PostgreSQL database
- Machine learning models for content analysis
- Authentication and rate limiting
- Analytics and reporting capabilities
- Docker containerization for deployment
- See `backend/README.md` for detailed setup

### SDK Agent (`/sdk-agent/`)
- JavaScript, Python, and Node.js SDKs
- Platform integration tools and examples
- Custom safety policy configuration
- Analytics and monitoring integration
- See `sdk-agent/README.md` for integration guides

### Documentation (`/docs/`)
- Comprehensive API documentation
- SDK integration guides
- Deployment instructions
- Developer tutorials and examples