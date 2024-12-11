# AI-Driven Proposal Generator

An intelligent proposal generator built with CrewAI that helps create professional project proposals automatically. The system uses multiple AI agents to analyze requirements, create proposal content, and estimate costs.

## Features

- Client brief analysis
- Technical architecture design
- Automated proposal generation
- Cost estimation and pricing strategy
- Support for multiple templates
- PDF output with professional formatting
- Web interface for easy interaction
- Support for both interactive and file-based input
- Visual design and mockups:
  - Website wireframes and mockups
  - User interface designs
  - User flow diagrams
  - System architecture diagrams
  - Interactive prototypes
- Competitive research capabilities:
  - News article search and analysis
  - Market trend analysis using Google Trends
  - Web scraping for competitor research
  - Stock market data analysis (for public companies)
  - Wikipedia information retrieval
  - DuckDuckGo search integration
  - Competitive advantage analysis
  - Market positioning strategies
  - SWOT analysis generation
  - Feature comparison matrices
  - Pricing strategy analysis

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd proposal_generator
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your API keys:
```
OPENAI_API_KEY=your_api_key_here
NEWS_API_KEY=your_newsapi_key_here
```

## Usage

### Web Interface

Run the web application:
```bash
streamlit run src/web_app.py
```

The web interface provides:
- Template selection
- Easy form input
- PDF download
- Proposal preview
- Professional formatting

### Command Line Interface

Run the CLI in interactive mode:
```bash
python src/cli.py
```

Follow the prompts to enter:
- Project type
- Project description
- Features (comma-separated)
- Timeline
- Budget range

### File Input Mode

Create a JSON file with your client brief (e.g., `client_brief.json`):
```json
{
    "project_type": "Web Application Development",
    "description": "E-commerce website for a boutique fashion retailer",
    "features": [
        "Product catalog",
        "Shopping cart",
        "User authentication",
        "Payment integration",
        "Order management"
    ],
    "timeline": "3 months",
    "budget_range": "$30,000 - $40,000"
}
```

Then run:
```bash
python src/cli.py --input client_brief.json
```

The generated proposal will be saved as both a text file (`proposal.txt`) and a PDF file (`proposal.pdf`) in the current directory.

## How It Works

The proposal generator uses specialized AI agents:

1. **Business Analyst**: Analyzes client requirements and extracts key project details
2. **Technical Architect**: Designs and validates technical solutions
3. **UI/UX Designer**: Creates visual mockups and user experience designs
4. **Proposal Writer**: Creates compelling and detailed project proposals
5. **Cost Estimator**: Provides accurate project cost estimates and pricing strategies
6. **Competitive Research Agent**: Analyzes market trends, competitors, and industry news

These agents work together sequentially to create a comprehensive proposal that includes:
- Executive Summary
- Project Overview
- Scope of Work
- Technical Architecture
- Visual Mockups and Designs
- User Experience Flow
- Methodology
- Deliverables
- Timeline
- Team Structure
- Cost Breakdown
- Payment Schedule
- Market Analysis
- Competitive Positioning:
  - SWOT Analysis
  - Feature Comparison Matrix
  - Market Differentiation Strategy
  - Pricing Position Analysis
  - Technology Stack Advantages
  - User Experience Benefits

## Research Tools

The system includes several research tools for comprehensive market analysis:

- **News API**: Fetches latest industry news and developments
- **Google Trends**: Analyzes market trends and interest over time
- **Web Scraping**: Gathers competitor information and market data
- **Yahoo Finance**: Retrieves financial data for market analysis
- **Wikipedia**: Accesses general knowledge and industry information
- **DuckDuckGo Search**: Performs web searches for additional research
- **Competitive Analysis Tools**:
  - Feature comparison engine
  - Pricing analysis calculator
  - Market position mapper
  - Technology stack analyzer
  - User experience evaluator
  - SWOT analysis generator

## Design Tools

The system includes tools for creating visual assets:

- **UI/UX Design**:
  - Wireframe generation
  - Mockup creation
  - Interactive prototype design
  - User flow diagrams
  - System architecture visualizations
  - Responsive design previews
  - Color scheme and typography recommendations

## Templates

The system supports multiple templates for different types of proposals:
- Default
- Software Development
- Consulting
- Marketing

Templates can be selected via the web interface or by specifying the template name when creating a new ProposalGenerator instance.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
