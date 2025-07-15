# Relicon Feedback Loop System

A nightly feedback system for optimizing ad performance using machine learning and AI analysis.

## Features

- **Automated Metrics Collection**: Fetches performance data from Meta and TikTok APIs
- **Revenue Tracking**: Processes Shopify webhooks for conversion tracking
- **Performance Analysis**: Calculates ROAS and identifies winning creatives
- **AI-Powered Optimization**: Generates next-generation hooks using OpenAI GPT-4o
- **Scheduled Tasks**: Automated nightly processing via Celery

## Installation

### Prerequisites
- Python 3.8+
- Redis server
- PostgreSQL database

### Install Dependencies
```bash
pip install fastapi uvicorn celery redis psycopg2-binary sqlalchemy alembic python-decouple pydantic langchain langchain-openai openai httpx python-multipart requests
```

### Environment Variables
Create a `.env` file with:
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost/relicon

# API Keys
OPENAI_API_KEY=your_openai_key_here
META_ACCESS_TOKEN=your_meta_token_here
TIKTOK_ACCESS_TOKEN=your_tiktok_token_here

# Webhooks
SHOPIFY_WEBHOOK_SECRET=your_shopify_webhook_secret

# Redis
REDIS_URL=redis://localhost:6379/0
```

## Usage

### Initialize Database
```bash
python database.py
```

### Start the API Server
```bash
uvicorn main:app --host 0.0.0.0 --port 3000
```

### Start Celery Worker
```bash
celery -A tasks worker --loglevel=info
```

### Start Celery Beat (Scheduler)
```bash
celery -A tasks beat --loglevel=info
```

## API Endpoints

### Core Endpoints
- `POST /webhook/shopify` - Shopify webhook for order tracking
- `GET /next-gen/{ad_id}` - Generate AI-powered hook suggestions
- `GET /analytics/summary` - Get performance analytics summary
- `GET /health` - Health check endpoint

### Webhook Integration

#### Shopify Webhook Setup
1. Go to your Shopify admin > Settings > Notifications
2. Add webhook URL: `https://your-domain.com/webhook/shopify`
3. Select "Order created" event
4. Set format to JSON
5. Add webhook secret to environment variables

## Database Schema

### Tables
- `metrics_meta` - Facebook/Meta advertising metrics
- `metrics_tt` - TikTok advertising metrics  
- `sales` - Shopify order/revenue tracking
- `ads` - Creative performance tracking

### Key Fields
- `ad_id` - Unique identifier for ads
- `roas` - Return on Ad Spend calculation
- `winner_tag` - Boolean flag for top 25% performers
- `creative_content` - Ad creative text/content

## Scheduled Tasks

### Nightly Processing (UTC)
- **02:00** - Fetch Meta metrics (`fetch_meta_metrics`)
- **02:15** - Fetch TikTok metrics (`fetch_tt_metrics`)
- **03:00** - Evaluate creatives and identify winners (`evaluate_creatives`)

### Manual Task Execution
```bash
# Fetch Meta metrics
celery -A tasks call tasks.fetch_meta_metrics

# Fetch TikTok metrics  
celery -A tasks call tasks.fetch_tt_metrics

# Evaluate creatives
celery -A tasks call tasks.evaluate_creatives
```

## AI Agent System

The AI agent analyzes winning ads and generates next-generation hooks using:

1. **Pattern Recognition**: Identifies successful creative elements
2. **Psychological Analysis**: Extracts emotional triggers that convert
3. **Platform Optimization**: Tailors hooks for specific platforms
4. **Confidence Scoring**: Ranks suggestions by predicted performance

### Hook Generation Process
1. Query top 25% ROAS performers from database
2. Extract creative patterns and success factors
3. Generate 5 personalized hooks using GPT-4o
4. Return structured JSON with confidence scores

## Monitoring

### Health Checks
```bash
curl http://localhost:3000/health
```

### Analytics Summary
```bash
curl http://localhost:3000/analytics/summary
```

### Celery Task Status
```bash
celery -A tasks inspect active
celery -A tasks inspect scheduled
```

## Development

### Local Testing
```bash
# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 3000
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## Deployment

### Replit Configuration
Add to `.replit` file:
```toml
run = "uvicorn main:app --host 0.0.0.0 --port 3000"

[deployment]
run = ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 3000"]
```

### Production Checklist
- [ ] Set all environment variables
- [ ] Configure Redis server
- [ ] Set up PostgreSQL database
- [ ] Configure Shopify webhooks
- [ ] Start Celery worker and beat processes
- [ ] Configure reverse proxy (nginx)
- [ ] Set up SSL certificates
- [ ] Configure monitoring/logging

## Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check DATABASE_URL format
echo $DATABASE_URL
```

**API Key Issues**
```bash
# Verify API keys are set
echo $OPENAI_API_KEY
echo $META_ACCESS_TOKEN
```

**Celery Connection Error**
```bash
# Check Redis connection
redis-cli ping
```

**Webhook Verification Failed**
- Verify SHOPIFY_WEBHOOK_SECRET matches Shopify settings
- Check webhook URL is accessible
- Ensure HTTPS is enabled for production

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request

## License

This project is licensed under the MIT License.