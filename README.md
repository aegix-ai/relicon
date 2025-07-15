# Relicon AI Video Generation Platform

A cutting-edge AI-powered video generation platform that creates professional MP4 advertisements from text input. Features comprehensive performance tracking, autonomous learning from A/B test data, and continuous optimization through nightly feedback loops.

## 🚀 Key Features

- **AI-Powered Video Generation**: Create professional videos using OpenAI GPT-4o and Luma AI
- **Multi-Platform Support**: Optimized for Meta, TikTok, and universal platforms
- **Autonomous Learning**: Learns from winning ads to improve future generations
- **Performance Tracking**: Comprehensive metrics collection and analysis
- **Modular Architecture**: Clean, maintainable codebase with professional structure

## 📁 Project Structure

```
relicon/
├── config/                 # Configuration and settings
├── core/                   # Core system components
│   ├── api/               # API models and middleware
│   └── database/          # Database models and connections
├── ai/                    # AI components
│   ├── agents/           # AI agents for hook generation
│   └── planners/         # Video and script planning
├── video/                 # Video generation system
│   ├── generation/       # Core video generation
│   └── services/         # High-level video services
├── external/             # External API integrations
│   └── apis/            # API clients (OpenAI, Luma, etc.)
├── tasks/                # Task management
├── tests/                # Test suites
├── tools/                # Utilities and scripts
├── assets/               # Static assets
├── outputs/              # Generated video outputs
├── backup/               # Backup of old files
└── main.py              # Central application highway
```

## 🛠️ Installation

### Prerequisites

- Python 3.11+
- PostgreSQL database
- FFmpeg installed
- Required API keys (OpenAI, Luma AI)

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd relicon
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

4. **Initialize database**:
   ```bash
   python -c "from core.database import init_db; init_db()"
   ```

5. **Start the application**:
   ```bash
   python main.py
   ```

## 🔧 Configuration

### Required Environment Variables

```env
DATABASE_URL=postgresql://user:password@localhost:5432/relicon
OPENAI_API_KEY=your_openai_api_key
LUMA_API_KEY=your_luma_api_key
```

### Optional Environment Variables

```env
ELEVENLABS_API_KEY=your_elevenlabs_api_key
META_ACCESS_TOKEN=your_meta_access_token
TIKTOK_ACCESS_TOKEN=your_tiktok_access_token
SHOPIFY_WEBHOOK_SECRET=your_shopify_webhook_secret
```

## 🚀 Usage

### Generate a Video

```python
from video.services import video_service

brand_info = {
    "brand_name": "Your Brand",
    "brand_description": "Your brand description",
    "duration": 30,
    "platform": "universal"
}

result = video_service.generate_video(brand_info)
```

### API Endpoints

- `POST /api/generate-video` - Generate full video with AI planning
- `POST /api/generate-simple-video` - Generate simple video (faster)
- `POST /api/generate-hooks` - Generate next-generation hooks
- `POST /api/collect-metrics` - Collect advertising metrics
- `POST /api/evaluate-creatives` - Evaluate creative performance

## 🧪 Testing

### Run API Tests
```bash
python tests/test_api.py
```

### Run Video Generation Tests
```bash
python tests/test_video_generation.py
```

### System Health Check
```bash
python tools/scripts/system_check.py
```

## 🔄 Maintenance

### Cleanup System
```bash
python tools/scripts/cleanup.py
```

### Create Backup
```bash
python tools/utilities/backup_manager.py
```

### Prepare for Deployment
```bash
python tools/utilities/deployment_prep.py
```

## 📊 Architecture

### Central Highway Pattern
The `main.py` file serves as the central highway, routing all requests through a unified FastAPI application that coordinates:
- Video generation pipeline
- AI planning and optimization
- Performance tracking and feedback loops
- External API integrations

### Modular Design
- **Separation of Concerns**: Each module has a specific responsibility
- **Clean Imports**: Proper module organization with clear dependencies
- **Scalable Structure**: Easy to extend and maintain

### Database Layer
- PostgreSQL with SQLAlchemy ORM
- Performance metrics tracking
- Sales conversion tracking
- Creative performance analysis

## 🔌 Integrations

### Supported Platforms
- **Meta/Facebook Ads**: Metrics collection and optimization
- **TikTok Ads**: Performance tracking and audience insights
- **Shopify**: Sales conversion tracking

### AI Services
- **OpenAI GPT-4o**: Content generation and planning
- **Luma AI**: Video generation and visual content
- **ElevenLabs**: Voice synthesis (optional)

## 📈 Performance Optimization

### Autonomous Learning
- Analyzes winning ad performance
- Generates optimized hooks based on successful patterns
- Continuous improvement through feedback loops

### Metrics Collection
- Real-time performance tracking
- ROI analysis and optimization
- A/B testing insights

## 🚢 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Production Checklist
- [ ] Set up environment variables
- [ ] Configure database
- [ ] Set up API keys
- [ ] Configure webhooks
- [ ] Set up monitoring
- [ ] Configure backup strategy

## 🤝 Contributing

1. Follow the existing code structure
2. Add tests for new functionality
3. Update documentation
4. Ensure all checks pass

## 📝 License

This project is proprietary software. All rights reserved.

## 🆘 Support

For issues and questions:
1. Check the system health with `python tools/scripts/system_check.py`
2. Review logs in the application
3. Consult the deployment guide

---

**Built with ❤️ by the Relicon Team**