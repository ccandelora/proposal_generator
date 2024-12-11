from typing import Dict, List, Any
import requests
from bs4 import BeautifulSoup
import re
import logging
from .base_agent import BaseAgent
import time
import random

logger = logging.getLogger(__name__)

class CompetitorAnalyzer(BaseAgent):
    """Analyzes competitor information from legal directories and websites."""
    
    def __init__(self):
        super().__init__()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def process(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process competitor information."""
        try:
            analyzed_competitors = []
            for competitor in competitors:
                if isinstance(competitor, dict):
                    profile_url = competitor.get('profile_url')
                    if profile_url:
                        analysis = self._analyze_competitor(profile_url)
                        if analysis:
                            analyzed_competitors.append(analysis)
                            time.sleep(random.uniform(2, 4))  # Respectful delay between requests
            
            market_insights = self._generate_market_insights(analyzed_competitors)
            
            return {
                'competitors': analyzed_competitors,
                'market_insights': market_insights,
                'summary': {
                    'total_competitors': len(analyzed_competitors),
                    'practice_areas': self._summarize_practice_areas(analyzed_competitors),
                    'experience_summary': self._summarize_experience(analyzed_competitors),
                    'education_summary': self._summarize_education(analyzed_competitors),
                    'fee_structures': self._summarize_fee_structures(analyzed_competitors)
                }
            }
        except Exception as e:
            logger.error(f"Error in competitor analysis: {str(e)}")
            return {'error': str(e)}

    def _analyze_competitor(self, profile_url: str) -> Dict[str, Any]:
        """Analyze a competitor's profile."""
        try:
            response = requests.get(profile_url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic information
            name = self._extract_name(soup)
            contact_info = self._extract_contact_info(soup)
            practice_areas = self._extract_practice_areas(soup)
            experience = self._extract_experience(soup)
            education = self._extract_education(soup)
            awards = self._extract_awards(soup)
            publications = self._extract_publications(soup)
            bar_admissions = self._extract_bar_admissions(soup)
            fee_info = self._extract_fee_info(soup)
            
            # Extract website if available
            website = self._extract_website(soup)
            website_analysis = None
            if website:
                website_analysis = self._analyze_website(website)
            
            return {
                'name': name,
                'profile_url': profile_url,
                'contact_info': contact_info,
                'practice_areas': practice_areas,
                'experience': experience,
                'education': education,
                'awards': awards,
                'publications': publications,
                'bar_admissions': bar_admissions,
                'fee_info': fee_info,
                'website': website,
                'website_analysis': website_analysis,
                'strengths': self._identify_strengths(practice_areas, experience, awards),
                'unique_features': self._identify_unique_features(practice_areas, experience, publications)
            }
        except Exception as e:
            logger.error(f"Error analyzing competitor profile {profile_url}: {str(e)}")
            return None

    def _extract_name(self, soup: BeautifulSoup) -> str:
        """Extract attorney name."""
        name_elem = soup.find('h1', class_='lawyer-name') or soup.find('h1')
        return name_elem.text.strip() if name_elem else "Unknown"

    def _extract_contact_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract contact information."""
        contact_info = {}
        
        # Find contact section
        contact_section = soup.find('div', class_=['contact-info', 'attorney-contact'])
        if contact_section:
            # Extract phone
            phone_elem = contact_section.find(string=re.compile(r'Phone|Tel'))
            if phone_elem:
                contact_info['phone'] = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', phone_elem.parent.text).group(0)
            
            # Extract email
            email_elem = contact_section.find('a', href=re.compile(r'mailto:'))
            if email_elem:
                contact_info['email'] = email_elem['href'].replace('mailto:', '')
            
            # Extract address
            address_elem = contact_section.find('address') or contact_section.find(class_='address')
            if address_elem:
                contact_info['address'] = address_elem.text.strip()
        
        return contact_info

    def _extract_practice_areas(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract practice areas with details."""
        practice_areas = []
        
        # Find practice areas section
        practice_section = soup.find('section', id=re.compile(r'practice-areas|areas-of-practice', re.I)) or \
                         soup.find('div', class_=re.compile(r'practice-areas|areas-of-practice', re.I))
        
        if practice_section:
            # Look for structured lists
            area_list = practice_section.find_all(['li', 'div'], class_='practice-area')
            
            for area in area_list:
                area_info = {
                    'name': area.text.strip(),
                    'description': '',
                    'percentage': None
                }
                
                # Look for percentage if available
                percentage_match = re.search(r'(\d+)%', area.text)
                if percentage_match:
                    area_info['percentage'] = int(percentage_match.group(1))
                
                # Look for description
                desc_elem = area.find_next_sibling('p')
                if desc_elem:
                    area_info['description'] = desc_elem.text.strip()
                
                practice_areas.append(area_info)
        
        return practice_areas

    def _extract_experience(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract experience information."""
        experience = {
            'years': None,
            'positions': [],
            'notable_cases': [],
            'specializations': []
        }
        
        # Find experience section
        exp_section = soup.find('section', id=re.compile(r'experience|background', re.I)) or \
                     soup.find('div', class_=re.compile(r'experience|background', re.I))
        
        if exp_section:
            # Extract years of experience
            year_pattern = re.compile(r'(\d{4})')
            years_text = exp_section.find(string=re.compile(r'years of experience|practicing since', re.I))
            if years_text:
                year_match = year_pattern.search(years_text)
                if year_match:
                    start_year = int(year_match.group(1))
                    experience['years'] = 2024 - start_year
            
            # Extract positions
            positions = exp_section.find_all(['li', 'p'], class_=re.compile(r'position|role', re.I))
            for pos in positions:
                position = {
                    'title': pos.text.strip(),
                    'duration': None,
                    'organization': None
                }
                
                # Try to extract duration and organization
                duration_match = re.search(r'(\d{4})\s*-\s*(\d{4}|\bpresent\b)', pos.text, re.I)
                if duration_match:
                    position['duration'] = duration_match.group(0)
                
                org_match = re.search(r'at\s+([^,\.]+)', pos.text)
                if org_match:
                    position['organization'] = org_match.group(1).strip()
                
                experience['positions'].append(position)
            
            # Extract notable cases
            cases_section = exp_section.find(string=re.compile(r'notable cases|significant cases', re.I))
            if cases_section:
                cases_list = cases_section.find_next('ul')
                if cases_list:
                    experience['notable_cases'] = [case.text.strip() for case in cases_list.find_all('li')]
            
            # Extract specializations
            spec_section = exp_section.find(string=re.compile(r'specializations|expertise', re.I))
            if spec_section:
                spec_list = spec_section.find_next('ul')
                if spec_list:
                    experience['specializations'] = [spec.text.strip() for spec in spec_list.find_all('li')]
        
        return experience

    def _extract_education(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract education information."""
        education = []
        
        # Find education section
        edu_section = soup.find('section', id=re.compile(r'education', re.I)) or \
                     soup.find('div', class_=re.compile(r'education', re.I))
        
        if edu_section:
            # Look for structured education entries
            edu_entries = edu_section.find_all(['li', 'div'], class_=re.compile(r'education|degree', re.I))
            
            for entry in edu_entries:
                edu_info = {
                    'degree': None,
                    'institution': None,
                    'year': None,
                    'honors': None
                }
                
                text = entry.text.strip()
                
                # Extract degree
                degree_match = re.search(r'(J\.D\.|LL\.M\.|B\.A\.|B\.S\.|M\.A\.|Ph\.D\.)', text)
                if degree_match:
                    edu_info['degree'] = degree_match.group(1)
                
                # Extract institution
                inst_pattern = re.compile(r'(University|College|School|Institute) of [\w\s]+|[\w\s]+ (University|College|School|Institute)')
                inst_match = inst_pattern.search(text)
                if inst_match:
                    edu_info['institution'] = inst_match.group(0)
                
                # Extract year
                year_match = re.search(r'\b(19|20)\d{2}\b', text)
                if year_match:
                    edu_info['year'] = year_match.group(0)
                
                # Extract honors
                honors_match = re.search(r'(cum laude|magna cum laude|summa cum laude|honors|distinction)', text, re.I)
                if honors_match:
                    edu_info['honors'] = honors_match.group(0)
                
                education.append(edu_info)
        
        return education

    def _extract_awards(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract awards and recognitions."""
        awards = []
        
        # Find awards section
        awards_section = soup.find('section', id=re.compile(r'awards|honors|recognitions', re.I)) or \
                        soup.find('div', class_=re.compile(r'awards|honors|recognitions', re.I))
        
        if awards_section:
            award_entries = awards_section.find_all(['li', 'div'], class_=re.compile(r'award|honor', re.I))
            
            for entry in award_entries:
                award_info = {
                    'name': entry.text.strip(),
                    'year': None,
                    'organization': None
                }
                
                # Extract year
                year_match = re.search(r'\b(19|20)\d{2}\b', entry.text)
                if year_match:
                    award_info['year'] = year_match.group(0)
                
                # Extract organization
                org_match = re.search(r'by\s+([^,\.]+)', entry.text)
                if org_match:
                    award_info['organization'] = org_match.group(1).strip()
                
                awards.append(award_info)
        
        return awards

    def _extract_publications(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract publications."""
        publications = []
        
        # Find publications section
        pub_section = soup.find('section', id=re.compile(r'publications|articles|writing', re.I)) or \
                     soup.find('div', class_=re.compile(r'publications|articles|writing', re.I))
        
        if pub_section:
            pub_entries = pub_section.find_all(['li', 'div'], class_=re.compile(r'publication|article', re.I))
            
            for entry in pub_entries:
                pub_info = {
                    'title': entry.text.strip(),
                    'year': None,
                    'publisher': None,
                    'type': None
                }
                
                # Extract year
                year_match = re.search(r'\b(19|20)\d{2}\b', entry.text)
                if year_match:
                    pub_info['year'] = year_match.group(0)
                
                # Extract publisher
                pub_match = re.search(r'in\s+([^,\.]+)', entry.text)
                if pub_match:
                    pub_info['publisher'] = pub_match.group(1).strip()
                
                # Determine type
                if re.search(r'book|treatise', entry.text, re.I):
                    pub_info['type'] = 'Book'
                elif re.search(r'article|paper', entry.text, re.I):
                    pub_info['type'] = 'Article'
                elif re.search(r'blog|post', entry.text, re.I):
                    pub_info['type'] = 'Blog Post'
                
                publications.append(pub_info)
        
        return publications

    def _extract_bar_admissions(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract bar admissions."""
        admissions = []
        
        # Find bar admissions section
        bar_section = soup.find('section', id=re.compile(r'bar-admissions|admissions', re.I)) or \
                     soup.find('div', class_=re.compile(r'bar-admissions|admissions', re.I))
        
        if bar_section:
            admission_entries = bar_section.find_all(['li', 'div'])
            
            for entry in admission_entries:
                admission_info = {
                    'jurisdiction': entry.text.strip(),
                    'year': None,
                    'status': 'Active'  # Default to active
                }
                
                # Extract year
                year_match = re.search(r'\b(19|20)\d{2}\b', entry.text)
                if year_match:
                    admission_info['year'] = year_match.group(0)
                
                # Check status
                if re.search(r'inactive|suspended|retired', entry.text, re.I):
                    admission_info['status'] = 'Inactive'
                
                admissions.append(admission_info)
        
        return admissions

    def _extract_fee_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract fee information."""
        fee_info = {
            'consultation': None,
            'fee_structure': None,
            'payment_methods': [],
            'pro_bono': False
        }
        
        # Find fee section
        fee_section = soup.find('section', id=re.compile(r'fees|payment|rates', re.I)) or \
                     soup.find('div', class_=re.compile(r'fees|payment|rates', re.I))
        
        if fee_section:
            # Extract consultation info
            consult_text = fee_section.find(string=re.compile(r'consultation|initial meeting', re.I))
            if consult_text:
                if re.search(r'free|no.?cost', consult_text, re.I):
                    fee_info['consultation'] = 'Free'
                elif re.search(r'\$\d+', consult_text):
                    fee_info['consultation'] = re.search(r'\$\d+', consult_text).group(0)
            
            # Extract fee structure
            if re.search(r'contingency|contingent', fee_section.text, re.I):
                fee_info['fee_structure'] = 'Contingency'
            elif re.search(r'hourly|per hour', fee_section.text, re.I):
                fee_info['fee_structure'] = 'Hourly'
            elif re.search(r'flat|fixed', fee_section.text, re.I):
                fee_info['fee_structure'] = 'Flat Rate'
            
            # Extract payment methods
            payment_text = fee_section.find(string=re.compile(r'payment|accept', re.I))
            if payment_text:
                if re.search(r'credit card', payment_text, re.I):
                    fee_info['payment_methods'].append('Credit Card')
                if re.search(r'check', payment_text, re.I):
                    fee_info['payment_methods'].append('Check')
                if re.search(r'cash', payment_text, re.I):
                    fee_info['payment_methods'].append('Cash')
            
            # Check for pro bono
            if re.search(r'pro bono|free legal', fee_section.text, re.I):
                fee_info['pro_bono'] = True
        
        return fee_info

    def _identify_strengths(self, practice_areas: List[Dict[str, Any]], experience: Dict[str, Any], awards: List[Dict[str, Any]]) -> List[str]:
        """Identify attorney's strengths based on their profile data."""
        strengths = []
        
        # Experience-based strengths
        if experience.get('years'):
            if experience['years'] > 20:
                strengths.append("Extensive legal experience spanning over two decades")
            elif experience['years'] > 10:
                strengths.append("Seasoned legal professional with over a decade of experience")
        
        # Practice area focus
        focused_areas = [area for area in practice_areas if area.get('percentage', 0) > 30]
        if focused_areas:
            strengths.append(f"Specialized expertise in {', '.join(area['name'] for area in focused_areas)}")
        
        # Notable cases
        if experience.get('notable_cases'):
            strengths.append("Track record of handling significant cases")
            if len(experience['notable_cases']) > 3:
                strengths.append("Extensive portfolio of successful cases")
        
        # Awards and recognition
        recent_awards = [award for award in awards if award.get('year') and int(award['year']) >= 2020]
        if recent_awards:
            strengths.append("Recent industry recognition and awards")
            if len(recent_awards) > 2:
                strengths.append("Consistently recognized for excellence")
        
        # Specializations
        if experience.get('specializations'):
            if len(experience['specializations']) > 3:
                strengths.append("Broad expertise across multiple specializations")
            else:
                strengths.append(f"Focused expertise in {', '.join(experience['specializations'][:2])}")
        
        return strengths

    def _identify_unique_features(self, practice_areas: List[Dict[str, Any]], experience: Dict[str, Any], publications: List[Dict[str, Any]]) -> List[str]:
        """Identify unique features that differentiate the attorney."""
        features = []
        
        # Practice area breadth
        if len(practice_areas) > 5:
            features.append("Comprehensive legal service offering")
        elif len([area for area in practice_areas if area.get('percentage', 0) > 40]) > 0:
            features.append("Deep specialization in core practice areas")
        
        # Experience highlights
        if experience.get('positions'):
            leadership_roles = [pos for pos in experience['positions'] if any(title in pos['title'].lower() for title in ['partner', 'director', 'head', 'chief', 'lead'])]
            if leadership_roles:
                features.append("Leadership experience in legal practice")
        
        # Publications and thought leadership
        if publications:
            recent_pubs = [pub for pub in publications if pub.get('year') and int(pub['year']) >= 2020]
            if recent_pubs:
                features.append("Active thought leadership through recent publications")
            
            pub_types = set(pub.get('type', '') for pub in publications if pub.get('type'))
            if len(pub_types) > 2:
                features.append("Diverse contributions to legal literature")
        
        # Specializations
        if experience.get('specializations'):
            niche_areas = [spec for spec in experience['specializations'] if any(term in spec.lower() for term in ['emerging', 'technology', 'international', 'complex', 'innovative'])]
            if niche_areas:
                features.append("Expertise in emerging and complex legal areas")
        
        return features

    def _summarize_practice_areas(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize practice areas across all competitors."""
        area_counts = {}
        total_competitors = len(competitors)
        
        for comp in competitors:
            areas = comp.get('practice_areas', [])
            for area in areas:
                if isinstance(area, dict):
                    area_name = area.get('name', '')
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

    def _summarize_experience(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize experience levels across competitors."""
        experience_ranges = {
            '0-5 years': 0,
            '6-10 years': 0,
            '11-20 years': 0,
            '20+ years': 0
        }
        
        total_years = 0
        counted_competitors = 0
        notable_cases = []
        specializations = set()
        
        for comp in competitors:
            exp = comp.get('experience', {})
            years = exp.get('years')
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
            
            # Collect notable cases
            if exp.get('notable_cases'):
                notable_cases.extend(exp['notable_cases'][:2])  # Take top 2 cases from each
            
            # Collect specializations
            if exp.get('specializations'):
                specializations.update(exp['specializations'])
        
        experience_summary = {
            'distribution': experience_ranges,
            'average_years': 0,
            'total_analyzed': counted_competitors,
            'notable_cases': notable_cases[:5],  # Return top 5 notable cases
            'common_specializations': list(specializations)[:10]  # Return top 10 specializations
        }
        
        if counted_competitors > 0:
            experience_summary['average_years'] = total_years / counted_competitors
        
        return experience_summary

    def _summarize_education(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize education credentials across competitors."""
        education_summary = {
            'top_schools': {},
            'degree_distribution': {},
            'honors_percentage': 0
        }
        
        total_competitors = len(competitors)
        honors_count = 0
        
        for comp in competitors:
            education = comp.get('education', [])
            for edu in education:
                # Count schools
                school = edu.get('institution')
                if school:
                    education_summary['top_schools'][school] = education_summary['top_schools'].get(school, 0) + 1
                
                # Count degrees
                degree = edu.get('degree')
                if degree:
                    education_summary['degree_distribution'][degree] = education_summary['degree_distribution'].get(degree, 0) + 1
                
                # Count honors
                if edu.get('honors'):
                    honors_count += 1
        
        # Calculate honors percentage
        if total_competitors > 0:
            education_summary['honors_percentage'] = (honors_count / total_competitors) * 100
        
        # Sort and limit top schools
        education_summary['top_schools'] = dict(sorted(education_summary['top_schools'].items(), key=lambda x: x[1], reverse=True)[:5])
        
        return education_summary

    def _summarize_fee_structures(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize fee structures across competitors."""
        fee_summary = {
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
        
        total_competitors = len(competitors)
        pro_bono_count = 0
        
        for comp in competitors:
            fee_info = comp.get('fee_info', {})
            
            # Count consultation types
            consultation = fee_info.get('consultation')
            if consultation == 'Free':
                fee_summary['consultation_types']['Free'] += 1
            elif consultation:
                fee_summary['consultation_types']['Paid'] += 1
            else:
                fee_summary['consultation_types']['Not Specified'] += 1
            
            # Count fee structures
            fee_structure = fee_info.get('fee_structure')
            if fee_structure:
                fee_summary['fee_structures'][fee_structure] = fee_summary['fee_structures'].get(fee_structure, 0) + 1
            else:
                fee_summary['fee_structures']['Not Specified'] += 1
            
            # Count payment methods
            for method in fee_info.get('payment_methods', []):
                fee_summary['payment_methods'][method] = fee_summary['payment_methods'].get(method, 0) + 1
            
            # Count pro bono
            if fee_info.get('pro_bono'):
                pro_bono_count += 1
        
        # Calculate pro bono percentage
        if total_competitors > 0:
            fee_summary['pro_bono_percentage'] = (pro_bono_count / total_competitors) * 100
        
        return fee_summary

    def _generate_market_insights(self, competitors: List[Dict[str, Any]]) -> List[str]:
        """Generate market insights from competitor analysis."""
        insights = []
        
        # Analyze practice area trends
        practice_summary = self._summarize_practice_areas(competitors)
        if practice_summary['most_common']:
            top_area = practice_summary['most_common'][0]
            insights.append(f"Dominant practice area: {top_area['name']} ({top_area['percentage']:.1f}% of competitors)")
        
        # Analyze experience levels
        exp_summary = self._summarize_experience(competitors)
        if exp_summary['average_years'] > 0:
            insights.append(f"Average attorney experience: {exp_summary['average_years']:.1f} years")
        
        # Analyze education
        edu_summary = self._summarize_education(competitors)
        if edu_summary['honors_percentage'] > 0:
            insights.append(f"{edu_summary['honors_percentage']:.1f}% of attorneys graduated with honors")
        
        # Analyze fee structures
        fee_summary = self._summarize_fee_structures(competitors)
        if fee_summary['pro_bono_percentage'] > 0:
            insights.append(f"{fee_summary['pro_bono_percentage']:.1f}% of attorneys offer pro bono services")
        
        return insights