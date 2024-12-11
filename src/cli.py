import argparse
import json
import os
from proposal_generator.generator import ProposalGenerator

def get_boolean_input(prompt):
    while True:
        response = input(f"{prompt} (y/n): ").lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        print("Please enter 'y' or 'n'")

def main():
    parser = argparse.ArgumentParser(description='AI-Driven Proposal Generator')
    parser.add_argument(
        '--input',
        type=str,
        help='Path to JSON file containing client brief',
        required=False
    )
    parser.add_argument(
        '--template',
        type=str,
        choices=['default', 'software_development', 'consulting', 'marketing'],
        default='default',
        help='Template to use for the proposal'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='.',
        help='Directory to save the proposal and mockups'
    )
    
    args = parser.parse_args()
    
    if args.input:
        # Read client brief from JSON file
        with open(args.input, 'r') as f:
            client_brief = json.load(f)
    else:
        # Interactive mode
        print("\n=== Client Information ===")
        client_brief = {
            "client_name": input("Client name: "),
            "industry": input("Industry: "),
            "client_website": input("Client website URL: "),
            "project_type": input("Project type: "),
            "target_audience": input("Target audience: "),
            "description": input("Project description: "),
            "features": input("Features (comma-separated): ").split(','),
            "timeline": input("Timeline: "),
            "budget_range": input("Budget range: ")
        }
        
        print("\n=== Analysis Options ===")
        analysis_options = {
            "website_analysis": get_boolean_input("Include website analysis"),
            "competitor_analysis": get_boolean_input("Include competitor analysis"),
            "seo_analysis": get_boolean_input("Include SEO analysis"),
            "performance_analysis": get_boolean_input("Include performance analysis"),
            "design_mockups": get_boolean_input("Generate design mockups"),
            "sentiment_analysis": get_boolean_input("Include social media sentiment")
        }
        
        # If competitor analysis is enabled, get competitor websites
        if analysis_options["competitor_analysis"]:
            print("\nEnter competitor websites (one per line, empty line to finish):")
            competitors = []
            while True:
                competitor = input()
                if not competitor:
                    break
                competitors.append(competitor)
            client_brief["competitors"] = competitors
        
        client_brief["analysis_options"] = analysis_options
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    print("\nGenerating proposal... This may take a few minutes.")
    
    # Generate proposal
    generator = ProposalGenerator(template_name=args.template)
    result = generator.create_proposal(client_brief)
    
    # Save the proposal to a file
    proposal_file = os.path.join(args.output_dir, "proposal.txt")
    with open(proposal_file, 'w') as f:
        f.write(str(result.get('proposal', '')))
    
    print(f"\nProposal has been generated and saved to {proposal_file}")
    
    # Handle mockups if they were generated
    mockups = result.get('mockups')
    if mockups:
        print("\nGenerated mockups:")
        for page_name, mockup_path in mockups.items():
            if os.path.exists(mockup_path):
                target_path = os.path.join(args.output_dir, os.path.basename(mockup_path))
                if mockup_path != target_path:
                    os.rename(mockup_path, target_path)
                print(f"- {page_name}: {target_path}")
    
    # Generate PDF if possible
    try:
        pdf_file = os.path.join(args.output_dir, "proposal.pdf")
        generator.generate_pdf(str(result.get('proposal', '')), pdf_file)
        print(f"PDF version has been saved to {pdf_file}")
    except Exception as e:
        print(f"Could not generate PDF: {str(e)}")

if __name__ == "__main__":
    main() 