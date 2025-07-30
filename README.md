# Instagram-to-Social Media Agent System 

An AI-powered agentic system that automatically extracts Instagram videos from specific users and transforms them into optimized content for Twitter and LinkedIn.

##  Features

- **Multi-Agent Architecture**: Uses CrewAI for coordinated agent workflows
- **Instagram Content Extraction**: Automatically scrapes videos from target users
- **AI-Powered Content Transformation**: Converts content for different platforms using OpenAI/Anthropic
- **Multi-Platform Publishing**: Posts to Twitter and LinkedIn with platform-specific optimizations
- **Video Processing**: Analyzes, resizes, and optimizes videos for each platform
- **Content Scheduling**: Schedule posts for optimal engagement times
- **Web Dashboard**: User-friendly interface for monitoring and control
- **Rate Limiting**: Respects API limits and handles rate limiting gracefully
- **Engagement Monitoring**: Tracks performance metrics across platforms

##  Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Instagram Agent │───▶│ Content Transform│───▶│ Social Media    │
│                 │    │ Agent            │    │ Agents          │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                       │
         ▼                        ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Instagram       │    │ Content Analyzer │    │ Twitter API     │
│ Scraper         │    │ & Text Generator │    │ LinkedIn API    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Agent Roles

1. **Orchestrator Agent**: Coordinates the entire workflow
2. **Instagram Agent**: Extracts content from Instagram users
3. **Content Transformer Agent**: Transforms content for different platforms
4. **Twitter Agent**: Handles Twitter posting and engagement
5. **LinkedIn Agent**: Manages LinkedIn content publishing

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/Bravine-Kulei/social-agent.git
cd social-agent

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy the environment template and configure your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your API credentials:

```env
# AI API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Twitter API Credentials
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token

# LinkedIn API Credentials
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token

# Target Instagram Users
TARGET_INSTAGRAM_USERS=user1,user2,user3
```

### 3. Usage

#### Command Line Interface

```bash
# Process specific Instagram users
python main.py --users username1 username2 --platforms twitter linkedin

# Process single user
python main.py --single-user username

# Schedule posts instead of posting immediately
python main.py --users username1 --schedule

# Start web interface
python main.py --web
```

#### Web Interface

Start the web dashboard:

```bash
python main.py --web
```

Then open http://localhost:8000 in your browser.

#### Programmatic Usage

```python
import asyncio
from agents.orchestrator_agent import OrchestratorAgent

async def main():
    orchestrator = OrchestratorAgent()

    results = await orchestrator.execute_full_workflow(
        target_users=['username1', 'username2'],
        platforms=['twitter', 'linkedin'],
        schedule_posts=False
    )

    print(f"Processed {results['summary']['total_videos_extracted']} videos")

asyncio.run(main())
```

##  API Reference

### REST API Endpoints

- `GET /` - Web dashboard
- `POST /api/workflow/start` - Start new workflow
- `GET /api/workflow/{id}/status` - Get workflow status
- `GET /api/workflows` - List all workflows
- `DELETE /api/workflow/{id}` - Delete workflow
- `GET /api/health` - Health check
- `GET /api/config` - System configuration

### Workflow Request

```json
{
  "target_users": ["username1", "username2"],
  "platforms": ["twitter", "linkedin"],
  "schedule_posts": false
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for content generation | Yes |
| `TWITTER_API_KEY` | Twitter API key | Yes |
| `TWITTER_API_SECRET` | Twitter API secret | Yes |
| `TWITTER_ACCESS_TOKEN` | Twitter access token | Yes |
| `TWITTER_ACCESS_TOKEN_SECRET` | Twitter access token secret | Yes |
| `TWITTER_BEARER_TOKEN` | Twitter bearer token | Yes |
| `LINKEDIN_CLIENT_ID` | LinkedIn client ID | Yes |
| `LINKEDIN_CLIENT_SECRET` | LinkedIn client secret | Yes |
| `LINKEDIN_ACCESS_TOKEN` | LinkedIn access token | Yes |
| `TARGET_INSTAGRAM_USERS` | Default Instagram users to process | No |
| `MAX_VIDEOS_PER_USER` | Maximum videos to extract per user | No |
| `CONTENT_CHECK_INTERVAL` | How often to check for new content (seconds) | No |

### Platform Configurations

The system automatically optimizes content for each platform:

**Twitter:**
- Max 280 characters
- Max 10 hashtags
- Video max 140 seconds
- Casual, engaging tone

**LinkedIn:**
- Max 3000 characters
- Max 30 hashtags
- Video max 10 minutes
- Professional tone

##  Project Structure

```
social-agent/
├── agents/                 # Agent modules
│   ├── instagram_agent.py
│   ├── content_transformer_agent.py
│   ├── twitter_agent.py
│   ├── linkedin_agent.py
│   └── orchestrator_agent.py
├── services/              # Core services
│   ├── instagram_scraper.py
│   ├── content_analyzer.py
│   └── social_media_poster.py
├── utils/                 # Utilities
│   ├── video_processor.py
│   ├── text_generator.py
│   └── api_clients.py
├── storage/              # Downloaded content
├── temp/                 # Temporary files
├── main.py              # CLI entry point
├── web_interface.py     # Web dashboard
├── config.py           # Configuration
└── requirements.txt    # Dependencies
```

##  Security & Privacy

- API keys are stored securely in environment variables
- Instagram scraping respects rate limits and ToS
- Content is processed locally before posting
- Temporary files are cleaned up automatically
- Webhook signatures are verified for security

##  Rate Limiting

The system includes built-in rate limiting for all APIs:

- **Twitter**: 300 requests per hour
- **LinkedIn**: 100 requests per hour
- **Instagram**: 200 requests per hour

Rate limits are automatically managed with exponential backoff.

##  Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=agents --cov=services --cov=utils
```

##  Monitoring

The system includes comprehensive logging and monitoring:

- Structured logging with Loguru
- Workflow progress tracking
- Engagement metrics collection
- Error tracking and reporting
- Performance monitoring

##  Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

##  Disclaimer

This tool is for educational and legitimate business purposes only. Users are responsible for:

- Complying with Instagram's Terms of Service
- Respecting content creators' rights
- Following platform-specific guidelines
- Obtaining necessary permissions for content use

##  Support

For support and questions:

1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information
4. Join our community discussions

##  Roadmap

- [ ] Support for additional platforms (TikTok, YouTube)
- [ ] Advanced content filtering and moderation
- [ ] A/B testing for content variations
- [ ] Analytics dashboard with detailed insights
- [ ] Automated hashtag research
- [ ] Content calendar integration
- [ ] Team collaboration features
