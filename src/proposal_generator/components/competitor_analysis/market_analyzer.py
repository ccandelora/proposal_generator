from typing import Dict, List, Any
import logging
from ..base_agent import BaseAgent

logger = logging.getLogger(__name__)

class MarketAnalyzer(BaseAgent):
    """Analyzes market trends and competitor data."""
    
    def analyze_market(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze market data from competitor profiles."""
        try:
            if not competitors:
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
                    },
                    'insights': [
                        "No competitor data available for market analysis",
                        "Consider expanding search criteria or geographic area"
                    ]
                }
            
            practice_areas = self._analyze_practice_areas(competitors)
            experience_levels = self._analyze_experience_levels(competitors)
            education_stats = self._analyze_education(competitors)
            fee_structures = self._analyze_fee_structures(competitors)
            market_position = self._determine_market_position(competitors)
            
            return {
                'practice_areas': practice_areas,
                'experience_levels': experience_levels,
                'education_stats': education_stats,
                'fee_structures': fee_structures,
                'market_position': market_position,
                'insights': self._generate_market_insights(
                    practice_areas,
                    experience_levels,
                    education_stats,
                    fee_structures,
                    market_position
                )
            }
        except Exception as e:
            logger.error(f"Error in market analysis: {str(e)}")
            return {'error': str(e)}

    def _analyze_practice_areas(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze practice area distribution."""
        area_counts = {}
        total_competitors = len(competitors)
        
        for comp in competitors:
            areas = comp.get('practice_areas', [])
            for area in areas:
                area_name = area.strip() if isinstance(area, str) else area.get('name', '').strip()
                if area_name:
                    area_counts[area_name] = area_counts.get(area_name, 0) + 1
        
        # Calculate percentages
        area_percentages = {
            area: (count / total_competitors) * 100
            for area, count in area_counts.items()
        }
        
        # Sort by percentage
        sorted_areas = sorted(area_percentages.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'most_common': sorted_areas[:5],
            'total_areas': len(area_counts),
            'average_areas_per_competitor': sum(len(comp.get('practice_areas', [])) for comp in competitors) / total_competitors if total_competitors > 0 else 0,
            'specialization_level': 'High' if len([a for a in sorted_areas if a[1] > 50]) > 0 else 'Medium' if len([a for a in sorted_areas if a[1] > 30]) > 0 else 'Low'
        }

    def _analyze_experience_levels(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze experience level distribution."""
        experience_ranges = {
            '0-5 years': 0,
            '6-10 years': 0,
            '11-20 years': 0,
            '20+ years': 0
        }
        
        total_years = 0
        counted_competitors = 0
        
        for comp in competitors:
            years = comp.get('years_experience')
            if years:
                total_years += years
                counted_competitors += 1
                
                if years <= 5:
                    experience_ranges['0-5 years'] += 1
                elif years <= 10:
                    experience_ranges['6-10 years'] += 1
                elif years <= 20:
                    experience_ranges['11-20 years'] += 1
                else:
                    experience_ranges['20+ years'] += 1
        
        return {
            'distribution': experience_ranges,
            'average_years': total_years / counted_competitors if counted_competitors > 0 else 0,
            'total_analyzed': counted_competitors,
            'market_maturity': 'Mature' if total_years / counted_competitors > 15 else 'Developing' if total_years / counted_competitors > 8 else 'Emerging' if counted_competitors > 0 else 'Unknown'
        }

    def _analyze_education(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze education credentials."""
        schools = {}
        degrees = {}
        honors_count = 0
        total_degrees = 0
        
        for comp in competitors:
            education = comp.get('education', [])
            for edu in education:
                total_degrees += 1
                
                # Count schools
                school = edu.get('school')
                if school:
                    schools[school] = schools.get(school, 0) + 1
                
                # Count degrees
                degree = edu.get('degree')
                if degree:
                    degrees[degree] = degrees.get(degree, 0) + 1
                
                # Count honors
                if edu.get('honors'):
                    honors_count += 1
        
        total_competitors = len(competitors)
        
        return {
            'top_schools': dict(sorted(schools.items(), key=lambda x: x[1], reverse=True)[:5]),
            'degree_distribution': degrees,
            'honors_percentage': (honors_count / total_competitors * 100) if total_competitors > 0 else 0,
            'average_degrees': total_degrees / total_competitors if total_competitors > 0 else 0,
            'education_level': 'High' if total_degrees / total_competitors > 2 else 'Medium' if total_degrees / total_competitors > 1 else 'Low' if total_competitors > 0 else 'Unknown'
        }

    def _analyze_fee_structures(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze fee structures."""
        fee_types = {
            'hourly': 0,
            'contingency': 0,
            'flat_rate': 0,
            'hybrid': 0,
            'not_specified': 0
        }
        
        consultation_types = {
            'free': 0,
            'paid': 0,
            'not_specified': 0
        }
        
        payment_methods = {}
        pro_bono_count = 0
        
        for comp in competitors:
            fee_info = comp.get('fee_info', {})
            
            # Count fee types
            fee_structure = fee_info.get('fee_structure', '').lower()
            if 'hour' in fee_structure:
                fee_types['hourly'] += 1
            elif 'contingency' in fee_structure or 'contingent' in fee_structure:
                fee_types['contingency'] += 1
            elif 'flat' in fee_structure or 'fixed' in fee_structure:
                fee_types['flat_rate'] += 1
            elif fee_structure:
                fee_types['hybrid'] += 1
            else:
                fee_types['not_specified'] += 1
            
            # Count consultation types
            consultation = fee_info.get('consultation', '').lower()
            if 'free' in consultation:
                consultation_types['free'] += 1
            elif consultation:
                consultation_types['paid'] += 1
            else:
                consultation_types['not_specified'] += 1
            
            # Count payment methods
            for method in fee_info.get('payment_methods', []):
                payment_methods[method] = payment_methods.get(method, 0) + 1
            
            # Count pro bono
            if fee_info.get('pro_bono'):
                pro_bono_count += 1
        
        total_competitors = len(competitors)
        
        return {
            'fee_structure_distribution': fee_types,
            'consultation_types': consultation_types,
            'payment_methods': payment_methods,
            'pro_bono_percentage': (pro_bono_count / total_competitors * 100) if total_competitors > 0 else 0,
            'pricing_position': self._determine_pricing_position(fee_types, consultation_types, pro_bono_count, total_competitors)
        }

    def _determine_market_position(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Determine overall market position."""
        total_competitors = len(competitors)
        if total_competitors == 0:
            return {'position': 'Unknown', 'factors': []}
        
        # Analyze key factors
        factors = []
        
        # Experience level
        avg_years = sum(comp.get('years_experience', 0) for comp in competitors) / total_competitors
        if avg_years > 15:
            factors.append("Highly experienced market")
        elif avg_years > 8:
            factors.append("Moderately experienced market")
        else:
            factors.append("Emerging market")
        
        # Education level
        honors_count = sum(1 for comp in competitors 
                         for edu in comp.get('education', [])
                         if edu.get('honors'))
        honors_percentage = (honors_count / total_competitors) * 100
        if honors_percentage > 30:
            factors.append("High academic credentials")
        
        # Specialization
        practice_areas = {}
        for comp in competitors:
            areas = comp.get('practice_areas', [])
            for area in areas:
                area_name = area.strip() if isinstance(area, str) else area.get('name', '').strip()
                if area_name:
                    practice_areas[area_name] = practice_areas.get(area_name, 0) + 1
        
        max_area_percentage = max(count / total_competitors * 100 for count in practice_areas.values()) if practice_areas else 0
        if max_area_percentage > 50:
            factors.append("Highly specialized market")
        elif max_area_percentage > 30:
            factors.append("Moderately specialized market")
        else:
            factors.append("Diverse practice areas")
        
        # Determine position
        if avg_years > 15 and honors_percentage > 30:
            position = "Premium Market"
        elif avg_years > 8 and honors_percentage > 20:
            position = "Established Market"
        else:
            position = "Developing Market"
        
        return {
            'position': position,
            'factors': factors,
            'avg_years_experience': avg_years,
            'academic_credentials': honors_percentage,
            'specialization_level': max_area_percentage
        }

    def _determine_pricing_position(self, fee_types: Dict[str, int], consultation_types: Dict[str, int], pro_bono_count: int, total_competitors: int) -> str:
        """Determine the pricing position in the market."""
        if total_competitors == 0:
            return "Unknown"
        
        # Calculate percentages
        hourly_percentage = (fee_types['hourly'] / total_competitors) * 100
        contingency_percentage = (fee_types['contingency'] / total_competitors) * 100
        flat_rate_percentage = (fee_types['flat_rate'] / total_competitors) * 100
        free_consult_percentage = (consultation_types['free'] / total_competitors) * 100
        pro_bono_percentage = (pro_bono_count / total_competitors) * 100
        
        if hourly_percentage > 60 and free_consult_percentage < 30:
            return "Premium Market"
        elif contingency_percentage > 40 and free_consult_percentage > 50:
            return "Competitive Market"
        elif flat_rate_percentage > 30 and pro_bono_percentage > 20:
            return "Value-Oriented Market"
        elif hourly_percentage > 40 and contingency_percentage > 30:
            return "Balanced Market"
        else:
            return "Mixed Market"

    def _generate_market_insights(self, practice_areas: Dict[str, Any], experience_levels: Dict[str, Any], 
                                education_stats: Dict[str, Any], fee_structures: Dict[str, Any], 
                                market_position: Dict[str, Any]) -> List[str]:
        """Generate market insights from analysis results."""
        insights = []
        
        # Market maturity insights
        if experience_levels['market_maturity'] == 'Mature':
            insights.append(f"Mature market with average {experience_levels['average_years']:.1f} years of experience")
        elif experience_levels['market_maturity'] == 'Developing':
            insights.append(f"Developing market with growing expertise ({experience_levels['average_years']:.1f} years average)")
        else:
            insights.append("Emerging market with opportunities for innovation")
        
        # Practice area insights
        if practice_areas['specialization_level'] == 'High':
            insights.append("Highly specialized market with focused practice areas")
            if practice_areas['most_common']:
                top_area = practice_areas['most_common'][0]
                insights.append(f"Dominant focus on {top_area[0]} ({top_area[1]:.1f}% of competitors)")
        else:
            insights.append("Diverse market with broad practice coverage")
        
        # Education insights
        if education_stats['honors_percentage'] > 30:
            insights.append(f"Highly credentialed market ({education_stats['honors_percentage']:.1f}% with honors)")
        if education_stats['average_degrees'] > 2:
            insights.append("Strong emphasis on advanced education and specialization")
        
        # Fee structure insights
        if fee_structures['pro_bono_percentage'] > 20:
            insights.append(f"Strong community focus with {fee_structures['pro_bono_percentage']:.1f}% offering pro bono services")
        
        # Market position insights
        if market_position['position'] == 'Premium Market':
            insights.append("Premium market positioning with emphasis on expertise and credentials")
        elif market_position['position'] == 'Established Market':
            insights.append("Well-established market with balanced service offerings")
        else:
            insights.append("Dynamic market with opportunities for differentiation")
        
        return insights 

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process method required by BaseAgent."""
        competitors = data.get('competitors', [])
        if not competitors:
            return {'error': 'No competitor data provided'}
            
        market_data = self.analyze_market(competitors)
        return {'market_analysis': market_data} 