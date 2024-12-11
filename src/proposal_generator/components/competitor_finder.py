from typing import Dict, List, Any
import logging
from .base_agent import BaseAgent
from .competitor_analysis.directory_searcher import DirectorySearcher
from .competitor_analysis.profile_analyzer import ProfileAnalyzer
from .competitor_analysis.market_analyzer import MarketAnalyzer
from .competitor_analysis.data_aggregator import DataAggregator

logger = logging.getLogger(__name__)

class CompetitorFinder(BaseAgent):
    """Finds and analyzes competitors using specialized components."""
    
    def __init__(self):
        super().__init__()
        self.directory_searcher = DirectorySearcher()
        self.profile_analyzer = ProfileAnalyzer()
        self.market_analyzer = MarketAnalyzer()
        self.data_aggregator = DataAggregator()

    def process(self, client_brief: Dict[str, Any]) -> Dict[str, Any]:
        """Process client brief to find and analyze competitors."""
        try:
            # Extract location and practice areas
            location = client_brief.get('location', '')
            practice_areas = self._extract_practice_areas(client_brief)
            
            if not location:
                return {
                    'error': 'Location not provided',
                    'competitors': [],
                    'market_analysis': self._get_empty_market_analysis(),
                    'summary': self._get_empty_summary()
                }
            
            # Step 1: Search directories for competitors
            logger.info("Searching legal directories for competitors...")
            directory_results = self.directory_searcher.search(location, practice_areas)
            
            if not directory_results:
                logger.warning("No competitors found in directory search")
                return {
                    'competitors': [],
                    'market_analysis': self._get_empty_market_analysis(),
                    'summary': self._get_empty_summary(),
                    'market_trends': [],
                    'insights': [
                        "No competitors found in the specified location",
                        "Consider expanding search area or modifying search criteria"
                    ]
                }
            
            # Step 2: Get detailed profiles for found competitors
            logger.info("Analyzing competitor profiles...")
            profile_data = []
            for comp in directory_results[:10]:  # Limit to top 10 competitors
                if comp.get('profile_url'):
                    profile = self.profile_analyzer.analyze_profile(comp['profile_url'])
                    if profile:
                        profile_data.append(profile)
            
            # Step 3: Analyze market trends and patterns
            logger.info("Analyzing market trends...")
            market_analysis = self.market_analyzer.analyze_market(directory_results)
            
            # Step 4: Aggregate all data
            logger.info("Aggregating competitor data...")
            aggregated_data = self.data_aggregator.aggregate_data(
                directory_results,
                profile_data,
                market_analysis
            )
            
            # Ensure we have a valid return structure even if some components failed
            return {
                'competitors': directory_results,
                'market_analysis': market_analysis or self._get_empty_market_analysis(),
                'summary': aggregated_data.get('summary', self._get_empty_summary()),
                'market_trends': self._extract_market_trends(market_analysis),
                'insights': aggregated_data.get('key_findings', [
                    "Limited market data available",
                    "Consider additional research methods"
                ])
            }
            
        except Exception as e:
            logger.error(f"Error in competitor finder: {str(e)}")
            return {
                'error': str(e),
                'competitors': [],
                'market_analysis': self._get_empty_market_analysis(),
                'summary': self._get_empty_summary(),
                'market_trends': [],
                'insights': ["Error occurred during competitor analysis"]
            }

    def _get_empty_market_analysis(self) -> Dict[str, Any]:
        """Return empty market analysis structure."""
        return {
            'practice_areas': {
                'most_common': [],
                'total_areas': 0,
                'average_areas_per_competitor': 0,
                'specialization_level': 'Unknown'
            },
            'experience_levels': {
                'distribution': {
                    '0-5 years': 0,
                    '6-10 years': 0,
                    '11-20 years': 0,
                    '20+ years': 0
                },
                'average_years': 0,
                'total_analyzed': 0,
                'market_maturity': 'Unknown'
            },
            'education_stats': {
                'top_schools': {},
                'degree_distribution': {},
                'honors_percentage': 0,
                'average_degrees': 0,
                'education_level': 'Unknown'
            },
            'fee_structures': {
                'fee_structure_distribution': {
                    'hourly': 0,
                    'contingency': 0,
                    'flat_rate': 0,
                    'hybrid': 0,
                    'not_specified': 0
                },
                'consultation_types': {
                    'free': 0,
                    'paid': 0,
                    'not_specified': 0
                },
                'payment_methods': {},
                'pro_bono_percentage': 0,
                'pricing_position': 'Unknown'
            },
            'market_position': {
                'position': 'Unknown',
                'factors': [],
                'avg_years_experience': 0,
                'academic_credentials': 0,
                'specialization_level': 0
            }
        }

    def _get_empty_summary(self) -> Dict[str, Any]:
        """Return empty summary structure."""
        return {
            'total_competitors': 0,
            'data_completeness': {
                'contact_info': 0,
                'practice_areas': 0,
                'education': 0,
                'experience': 0,
                'fee_structure': 0,
                'overall': 0
            },
            'market_position': 'Unknown',
            'top_practice_areas': [],
            'experience_distribution': {
                '0-5 years': 0,
                '6-10 years': 0,
                '11-20 years': 0,
                '20+ years': 0
            },
            'education_stats': {
                'top_schools': {},
                'degree_distribution': {},
                'honors_percentage': 0
            },
            'fee_structures': {
                'consultation_types': {
                    'Free': 0,
                    'Paid': 0,
                    'Not Specified': 0
                },
                'fee_structures': {
                    'Contingency': 0,
                    'Hourly': 0,
                    'Flat Rate': 0,
                    'Mixed': 0,
                    'Not Specified': 0
                },
                'payment_methods': {},
                'pro_bono_percentage': 0
            }
        }

    def _extract_market_trends(self, market_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract market trends from market analysis."""
        if not market_analysis:
            return []
            
        trends = []
        
        # Extract practice area trends
        practice_areas = market_analysis.get('practice_areas', {})
        if practice_areas.get('most_common'):
            trends.append({
                'category': 'Practice Areas',
                'trend': f"Most common: {practice_areas['most_common'][0][0]}",
                'percentage': practice_areas['most_common'][0][1]
            })
        
        # Extract experience trends
        experience = market_analysis.get('experience_levels', {})
        if experience.get('average_years'):
            trends.append({
                'category': 'Experience',
                'trend': f"Average experience: {experience['average_years']:.1f} years",
                'percentage': None
            })
        
        # Extract education trends
        education = market_analysis.get('education_stats', {})
        if education.get('honors_percentage'):
            trends.append({
                'category': 'Education',
                'trend': 'Attorneys with honors',
                'percentage': education['honors_percentage']
            })
        
        # Extract fee structure trends
        fee_structures = market_analysis.get('fee_structures', {})
        if fee_structures.get('pro_bono_percentage'):
            trends.append({
                'category': 'Services',
                'trend': 'Pro bono services offered',
                'percentage': fee_structures['pro_bono_percentage']
            })
        
        return trends

    def _extract_practice_areas(self, client_brief: Dict[str, Any]) -> List[str]:
        """Extract practice areas from client brief."""
        practice_areas = []
        
        # Check direct practice areas field
        if client_brief.get('practice_areas'):
            if isinstance(client_brief['practice_areas'], list):
                practice_areas.extend(client_brief['practice_areas'])
            elif isinstance(client_brief['practice_areas'], str):
                practice_areas.append(client_brief['practice_areas'])
        
        # Check description for practice areas
        description = client_brief.get('description', '')
        if description:
            # Common practice area keywords
            keywords = [
                'corporate', 'litigation', 'family', 'criminal', 'real estate',
                'intellectual property', 'patent', 'trademark', 'employment',
                'tax', 'estate planning', 'immigration', 'bankruptcy'
            ]
            
            for keyword in keywords:
                if keyword.lower() in description.lower():
                    practice_areas.append(keyword)
        
        return list(set(practice_areas))  # Remove duplicates