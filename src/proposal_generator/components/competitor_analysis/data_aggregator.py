from typing import Dict, List, Any
import logging
from ..base_agent import BaseAgent

logger = logging.getLogger(__name__)

class DataAggregator(BaseAgent):
    """Aggregates and combines data from different competitor analysis sources."""
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process method required by BaseAgent."""
        directory_results = data.get('directory_results', [])
        profile_data = data.get('profile_data', [])
        market_analysis = data.get('market_analysis', {})
        
        if not directory_results:
            return {'error': 'No directory results provided'}
            
        aggregated_data = self.aggregate_data(directory_results, profile_data, market_analysis)
        return {'aggregated_data': aggregated_data}

    def aggregate_data(self, directory_results: List[Dict[str, Any]], profile_data: List[Dict[str, Any]], 
                      market_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate data from all sources into a comprehensive analysis."""
        try:
            # Combine competitor profiles with directory data
            competitors = self._merge_competitor_data(directory_results, profile_data)
            
            # Generate summary statistics
            summary = self._generate_summary(competitors, market_analysis)
            
            # Generate key findings
            findings = self._generate_key_findings(competitors, market_analysis)
            
            return {
                'competitors': competitors,
                'market_analysis': market_analysis,
                'summary': summary,
                'key_findings': findings
            }
        except Exception as e:
            logger.error(f"Error aggregating data: {str(e)}")
            return {'error': str(e)}

    def _merge_competitor_data(self, directory_results: List[Dict[str, Any]], 
                             profile_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge directory results with detailed profile data."""
        merged_data = []
        
        # Create lookup of profile data by URL
        profile_lookup = {
            profile.get('profile_url', ''): profile
            for profile in profile_data
            if profile and profile.get('profile_url')
        }
        
        # Merge data for each competitor
        for competitor in directory_results:
            profile_url = competitor.get('profile_url', '')
            profile = profile_lookup.get(profile_url, {})
            
            merged_competitor = {
                # Basic information
                'name': competitor.get('name', ''),
                'profile_url': profile_url,
                'directory': competitor.get('directory', ''),
                'website': profile.get('website', competitor.get('website', '')),
                
                # Contact information
                'contact_info': profile.get('contact_info', competitor.get('contact_info', {})),
                
                # Practice information
                'practice_areas': profile.get('practice_areas', competitor.get('practice_areas', [])),
                'practice_focus': profile.get('practice_focus', {}),
                
                # Experience and credentials
                'years_experience': competitor.get('years_experience'),
                'education': profile.get('education', []),
                'bar_admissions': profile.get('bar_admissions', []),
                'certifications': profile.get('certifications', []),
                'awards': profile.get('awards', []),
                
                # Professional details
                'publications': profile.get('publications', []),
                'speaking_engagements': profile.get('speaking_engagements', []),
                'professional_associations': profile.get('professional_associations', []),
                'languages': profile.get('languages', []),
                
                # Business information
                'fee_structure': profile.get('fee_structure', {}),
                'office_locations': profile.get('office_locations', []),
                
                # Online presence
                'social_media': profile.get('social_media', {}),
                'rating': competitor.get('rating'),
                'reviews_count': competitor.get('reviews_count', 0)
            }
            
            merged_data.append(merged_competitor)
        
        return merged_data

    def _generate_summary(self, competitors: List[Dict[str, Any]], 
                         market_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics from the aggregated data."""
        total_competitors = len(competitors)
        
        summary = {
            'total_competitors': total_competitors,
            'data_completeness': self._calculate_data_completeness(competitors),
            'market_position': market_analysis.get('market_position', {}).get('position', 'Unknown'),
            'top_practice_areas': self._get_top_practice_areas(competitors),
            'experience_distribution': market_analysis.get('experience_levels', {}).get('distribution', {}),
            'education_stats': market_analysis.get('education_stats', {}),
            'fee_structures': market_analysis.get('fee_structures', {})
        }
        
        return summary

    def _calculate_data_completeness(self, competitors: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate completeness of data for different aspects."""
        total = len(competitors)
        if total == 0:
            return {}
        
        completeness = {
            'contact_info': sum(1 for c in competitors if c.get('contact_info')) / total * 100,
            'practice_areas': sum(1 for c in competitors if c.get('practice_areas')) / total * 100,
            'education': sum(1 for c in competitors if c.get('education')) / total * 100,
            'experience': sum(1 for c in competitors if c.get('years_experience') is not None) / total * 100,
            'fee_structure': sum(1 for c in competitors if c.get('fee_structure')) / total * 100
        }
        
        # Calculate overall completeness
        completeness['overall'] = sum(completeness.values()) / len(completeness)
        
        return completeness

    def _get_top_practice_areas(self, competitors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get the most common practice areas with percentages."""
        area_counts = {}
        total_competitors = len(competitors)
        
        for comp in competitors:
            areas = comp.get('practice_areas', [])
            for area in areas:
                area_name = area.strip() if isinstance(area, str) else area.get('name', '').strip()
                if area_name:
                    area_counts[area_name] = area_counts.get(area_name, 0) + 1
        
        # Calculate percentages and sort
        area_stats = [
            {
                'name': area,
                'count': count,
                'percentage': (count / total_competitors * 100) if total_competitors > 0 else 0
            }
            for area, count in area_counts.items()
        ]
        
        return sorted(area_stats, key=lambda x: x['percentage'], reverse=True)[:5]

    def _generate_key_findings(self, competitors: List[Dict[str, Any]], 
                             market_analysis: Dict[str, Any]) -> List[str]:
        """Generate key findings from the aggregated data."""
        findings = []
        
        # Add market insights
        findings.extend(market_analysis.get('insights', []))
        
        # Add competitive dynamics findings
        if competitors:
            # Experience distribution
            exp_levels = market_analysis.get('experience_levels', {})
            if exp_levels.get('market_maturity') == 'Mature':
                findings.append(f"Well-established competitor base with {exp_levels.get('average_years', 0):.1f} years average experience")
            
            # Education and credentials
            edu_stats = market_analysis.get('education_stats', {})
            if edu_stats.get('honors_percentage', 0) > 30:
                findings.append("Strong academic credentials in the market")
            
            # Fee structures
            fee_stats = market_analysis.get('fee_structures', {})
            if fee_stats.get('pro_bono_percentage', 0) > 20:
                findings.append("Significant pro bono commitment in the market")
            
            # Online presence
            online_presence = sum(1 for c in competitors if c.get('website') or c.get('social_media'))
            if online_presence / len(competitors) > 0.8:
                findings.append("Strong digital presence across competitors")
            
            # Specialization
            practice_areas = market_analysis.get('practice_areas', {})
            if practice_areas.get('specialization_level') == 'High':
                findings.append("Highly specialized market with focused practice areas")
        
        return findings 