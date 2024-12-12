import asyncio
from src.proposal_generator.config import Config
from src.proposal_generator.workflow.proposal_workflow import ProposalWorkflow

async def main():
    config = Config()
    workflow = ProposalWorkflow(config)
    
    topic = "AI-powered legal research solutions"
    requirements = {
        'target_audience': 'law firms',
        'tone': 'professional',
        'max_length': 2000
    }
    
    try:
        result = await workflow.generate_proposal(topic, requirements)
        print("\nProposal generated successfully!")
    except Exception as e:
        print(f"\nError generating proposal: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 