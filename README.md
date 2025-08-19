# LinkedIn Post Automation

A comprehensive system for automating LinkedIn posts from DeepLearning.AI newsletter content. This tool fetches content from newsletters, processes it, generates engaging LinkedIn posts, and schedules them for optimal posting times.

## Features

- **Newsletter Scraping**: Automatically fetch content from DeepLearning.AI newsletters (The Batch and Data Points)
- **Content Processing**: Clean, format, and extract key insights from newsletter content
- **Post Generation**: Create engaging LinkedIn posts using customizable templates
- **Smart Scheduling**: Schedule posts at optimal times with configurable intervals
- **Quality Filtering**: Filter content based on relevance and quality scores
- **Analytics**: Track posting performance and engagement metrics
- **Web UI**: A user-friendly web interface to manage the automation pipeline.
- **Modular Design**: Easy to extend and customize for different content sources

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Tharikabalu/Linkedin_post_automation.git
   cd Linkedin_post_automation
   ```

2. **Create and activate virtual environment**:
   ```bash
   python3 -m venv linkedinagent
   source linkedinagent/bin/activate  # On Windows: linkedinagent\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your API keys and configuration
   ```

## Configuration

### Environment Variables

Copy `env.example` to `.env` and configure:

```bash
# LinkedIn API Configuration
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token

# OpenAI API (optional, for enhanced content generation)
OPENAI_API_KEY=your_openai_api_key
```

### Settings Configuration

Edit `config/settings.yaml` to customize:

- Newsletter sources and URLs
- Content processing parameters
- Post generation templates
- Scheduling preferences
- LinkedIn API settings

## Usage

### Command Line Interface

The system provides a comprehensive CLI for different operations:

#### Run Complete Pipeline
```bash
python -m src.main --pipeline --max-articles 10 --max-posts 5 --auto-schedule
```

#### Individual Steps
```bash
# Fetch content only
python -m src.main --fetch --max-articles 10

# Process fetched content
python -m src.main --process

# Generate posts from processed content
python -m src.main --generate --max-posts 5

# Schedule posts
python -m src.main --schedule --auto-schedule

# Show system status
python -m src.main --status

# Start scheduler daemon
python -m src.main --start-scheduler
```

### Web UI

The project includes a web-based UI for easier management.

**Start the UI:**
```bash
python start_ui.py
```
Or directly:
```bash
streamlit run web_ui.py
```

The UI provides:
- A dashboard with key metrics.
- A visual content pipeline.
- Post management features.
- Analytics and visualizations.

## Project Structure

```
Linkedin_post_automation/
├── src/                    # Source code
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── newsletter_scraper.py  # Newsletter content fetching
│   ├── content_processor.py   # Content processing and formatting
│   ├── post_generator.py      # LinkedIn post generation
│   ├── scheduler.py           # Post scheduling and automation
│   └── main.py               # Main CLI interface
├── scripts/                # Utility and test scripts
│   ├── get_linkedin_token.py
│   ├── test_linkedin_api.py
│   └── test_system.py
├── config/                # Configuration files
│   └── settings.yaml      # Main configuration
├── data/                  # Data storage
├── logs/                  # Log files
├── .gitignore             # Git ignore file
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables template
├── README.md             # This file
├── start_ui.py            # Web UI launcher
└── web_ui.py              # Web UI application
```

## Components

### 1. Newsletter Scraper (`newsletter_scraper.py`)
- Fetches content from DeepLearning.AI newsletters
- Supports multiple newsletter sources
- Handles rate limiting and error recovery
- Extracts articles, summaries, and key insights

### 2. Content Processor (`content_processor.py`)
- Cleans and formats newsletter content
- Extracts key insights using NLP
- Generates relevant hashtags
- Calculates content quality scores
- Filters content based on relevance

### 3. Post Generator (`post_generator.py`)
- Creates LinkedIn posts using customizable templates
- Validates post length and content
- Calculates engagement scores
- Provides post previews
- Supports custom post generation

### 4. Scheduler (`scheduler.py`)
- Schedules posts at optimal times
- Manages posting queue
- Handles failed posts and retries
- Provides analytics and status tracking
- Supports both automatic and manual scheduling

### 5. Configuration (`config.py`)
- Manages all system settings
- Supports YAML configuration files
- Provides easy access to configuration values
- Supports environment variable overrides

## Customization

### Adding New Newsletter Sources

1. Update `config/settings.yaml`:
```yaml
newsletter_sources:
  new_source:
    url: "https://example.com/newsletter"
    name: "Example Newsletter"
    type: "weekly"
```

2. Extend `NewsletterScraper` class with new parsing methods.

### Custom Post Templates

Edit `config/settings.yaml`:
```yaml
post_generation:
  templates:
    - "🎯 {title}\n\n{summary}\n\n💡 Key insights:\n{insights}\n\n🔗 Read more: {link}\n\n{hashtags}"
    - "📊 {title}\n\n{summary}\n\n🚀 Why this matters:\n{insights}\n\n📖 Full article: {link}\n\n{hashtags}"
```

### Scheduling Configuration

```yaml
scheduling:
  posting_times:
    - "09:00"
    - "12:00"
    - "17:00"
    - "20:00"
  max_posts_per_day: 3
  min_interval_hours: 4
```

## Monitoring and Analytics

The system provides comprehensive monitoring:

- **Post Status Tracking**: Monitor scheduled, posted, and failed posts
- **Engagement Analytics**: Track engagement scores and performance
- **Queue Management**: Monitor posting queue and scheduling status
- **Error Logging**: Detailed logs for debugging and monitoring

## Troubleshooting

### Common Issues

1. **No articles fetched**: Check newsletter URLs and network connectivity
2. **Posts too short/long**: Adjust `min_post_length` and `max_post_length` in settings
3. **Scheduling issues**: Verify timezone settings and posting times
4. **API errors**: Check LinkedIn API credentials and rate limits

### Logs

Check logs in `logs/linkedin_automation.log` for detailed error information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the logs for error details

## Roadmap

- [ ] LinkedIn API integration for actual posting
- [ ] Support for more newsletter sources
- [ ] Advanced content analysis using AI
- [ ] Web interface for management
- [ ] Mobile app for monitoring
- [ ] Integration with other social platforms
