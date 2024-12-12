from src.proposal_generator.generator import ProposalGenerator
from src.proposal_generator.components.website_screenshotter import WebsiteScreenshotter
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_proposal():
    # Test client brief
    client_brief = {
        'client_name': 'TechCorp Solutions',
        'project_type': 'Website Redesign',
        'industry': 'Technology Consulting',
        'website': 'https://www.python.org',  # Using Python.org as an example
        'description': 'Looking to modernize our website with a focus on user experience and mobile responsiveness.',
        'features': [
            'Interactive service showcase',
            'Client portal integration',
            'Case studies section',
            'Team member profiles'
        ],
        'timeline': '2 months',
        'budget_range': '$15,000-$20,000',
        'location': 'San Francisco'
    }

    logger.info("Starting proposal generation...")
    logger.info(f"Client: {client_brief['client_name']}")
    logger.info(f"Industry: {client_brief['industry']}")
    logger.info(f"Location: {client_brief['location']}")
    
    # Initialize generator with no template
    generator = ProposalGenerator()

    # Generate proposal
    proposal = generator.create_proposal(client_brief)

    # Save proposal to file
    with open('proposal.txt', 'w') as f:
        if isinstance(proposal, dict):
            json.dump(proposal, f, indent=2)
        else:
            f.write(str(proposal))

    logger.info("\nProposal generated and saved to proposal.txt")
    
    # Display competitor analysis results
    if proposal.get('analyses', {}).get('competitive', {}).get('competitors'):
        logger.info("\nFound Competitors:")
        for comp in proposal['analyses']['competitive']['competitors']:
            logger.info(f"- {comp['name']}")
            logger.info(f"  Website: {comp['website']}")
            logger.info(f"  Position: {comp.get('market_position', 'Unknown')}")
            if comp.get('unique_features'):
                logger.info(f"  Features: {', '.join(comp['unique_features'][:3])}")
            logger.info("")
    else:
        logger.info("\nNo competitors found in analysis.")

    # Display website analysis results
    if proposal.get('analyses', {}).get('website'):
        logger.info("\nWebsite Analysis:")
        wa = proposal['analyses']['website']
        if wa.get('pages'):
            logger.info(f"Analyzed {len(wa['pages'])} pages")
            for page in wa['pages']:
                logger.info(f"- {page['type']}: {page['url']}")
        if wa.get('responsive_issues'):
            logger.info("\nResponsive Issues:")
            for issue in wa['responsive_issues']:
                logger.info(f"- {issue}")
    
    logger.info("\nFull proposal content saved to proposal.txt")

if __name__ == "__main__":
    test_proposal() 