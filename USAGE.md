# Instagram-to-Social Media Agent System - Usage Guide

## Quick Start

### 1. Basic Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 2. Post Specific Instagram Video
```bash
python specific_video_poster.py
```
Then provide:
- Instagram URL: `https://www.instagram.com/reel/ABC123/`
- Or shortcode: `ABC123`

### 3. Run Complete Pipeline
```bash
python complete_pipeline.py
```

### 4. Demo Mode
```bash
python auto_demo_pipeline.py
```

## Features

### ✅ Instagram Content Extraction
- Multiple extraction methods with fallbacks
- Rate limiting and error handling
- Support for public posts and reels

### ✅ AI Content Transformation
- OpenAI integration for smart content optimization
- Platform-specific formatting
- Maintains original message intent

### ✅ Twitter Integration
- Real Twitter API posting
- Clean format without clutter
- Automatic @idxcodehub tagging
- Character limit optimization

### ✅ Web Dashboard
```bash
python simple_web.py
```
Access at: http://localhost:8000

## API Configuration

### Twitter API
1. Create app at [Twitter Developer Portal](https://developer.twitter.com)
2. Set permissions to "Read and Write"
3. Generate OAuth 1.0a tokens
4. Add to `.env`:
```env
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_TOKEN_SECRET=your_token_secret
```

### OpenAI API
```env
OPENAI_API_KEY=your_openai_key
```

### Instagram (Optional)
```env
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
```

## Examples

### Post Specific Video
```python
from specific_video_poster import post_specific_video

# Using URL
await post_specific_video("https://www.instagram.com/reel/ABC123/")

# Using shortcode
await post_specific_video("ABC123")
```

### Batch Processing
```python
from complete_pipeline import run_complete_pipeline

# Process multiple videos from user
await run_complete_pipeline("username", max_videos=3)
```

## Output Format

All tweets follow this clean format:
```
[Optimized content from Instagram video]

@idxcodehub 📸 [shortcode]
```

## Troubleshooting

### Instagram Rate Limiting
- System includes automatic rate limiting
- Uses multiple extraction methods
- Fallback to realistic sample data

### Twitter API Errors
- Ensure "Read and Write" permissions
- Regenerate tokens after permission changes
- Check rate limits (300 tweets per 15 minutes)

### OpenAI Integration
- Optional - system works without it
- Falls back to rule-based transformation
- Improves content quality when available

## Advanced Usage

### Custom Content Transformation
Modify the `optimize_for_twitter()` function in any of the pipeline files to customize how content is transformed.

### Adding New Platforms
Extend the system by creating new publisher classes following the Twitter publisher pattern.

### Scheduling Posts
Integrate with task schedulers like Celery or APScheduler for automated posting.
