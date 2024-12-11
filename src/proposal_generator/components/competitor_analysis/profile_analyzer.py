from typing import Dict, List, Any
import requests
from bs4 import BeautifulSoup
import re
import logging
import time
import random
from ..base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ProfileAnalyzer(BaseAgent):
    """Analyzes attorney profiles to extract detailed information."""
    
    def __init__(self):
        super().__init__()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process method required by BaseAgent."""
        profile_url = data.get('profile_url')
        if not profile_url:
            return {'error': 'Profile URL not provided'}
            
        profile_data = self.analyze_profile(profile_url)
        return {'profile': profile_data}

    def analyze_profile(self, profile_url: str) -> Dict[str, Any]:
        """Analyze an attorney's profile page."""
        try:
            response = requests.get(profile_url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            profile = {
                'education': self._extract_education(soup),
                'bar_admissions': self._extract_bar_admissions(soup),
                'awards': self._extract_awards(soup),
                'publications': self._extract_publications(soup),
                'speaking_engagements': self._extract_speaking_engagements(soup),
                'languages': self._extract_languages(soup),
                'professional_associations': self._extract_professional_associations(soup),
                'fee_structure': self._extract_fee_structure(soup),
                'office_locations': self._extract_office_locations(soup),
                'website': self._extract_website(soup),
                'social_media': self._extract_social_media(soup),
                'practice_focus': self._extract_practice_focus(soup),
                'certifications': self._extract_certifications(soup)
            }
            
            return profile
            
        except Exception as e:
            logger.warning(f"Error analyzing profile {profile_url}: {str(e)}")
            return None

    def _extract_education(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract education information."""
        education = []
        edu_section = soup.find(['div', 'section'], string=re.compile(r'Education', re.I))
        
        if edu_section:
            edu_items = edu_section.find_all(['li', 'p', 'div'])
            for item in edu_items:
                edu_text = item.text.strip()
                if edu_text and not any(x in edu_text.lower() for x in ['education', 'school', 'university']):
                    edu_info = {
                        'degree': None,
                        'school': None,
                        'year': None,
                        'honors': None
                    }
                    
                    # Extract degree
                    degree_match = re.search(r'(J\.D\.|LL\.M\.|B\.A\.|B\.S\.|M\.A\.|Ph\.D\.)', edu_text)
                    if degree_match:
                        edu_info['degree'] = degree_match.group(1)
                    
                    # Extract school
                    school_pattern = re.compile(r'(University|College|School|Institute) of [\w\s]+|[\w\s]+ (University|College|School|Institute)')
                    school_match = school_pattern.search(edu_text)
                    if school_match:
                        edu_info['school'] = school_match.group(0)
                    
                    # Extract year
                    year_match = re.search(r'\b(19|20)\d{2}\b', edu_text)
                    if year_match:
                        edu_info['year'] = year_match.group(0)
                    
                    # Extract honors
                    honors_match = re.search(r'(cum laude|magna cum laude|summa cum laude|honors|distinction)', edu_text, re.I)
                    if honors_match:
                        edu_info['honors'] = honors_match.group(0)
                    
                    education.append(edu_info)
        
        return education

    def _extract_bar_admissions(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract bar admission information."""
        admissions = []
        bar_section = soup.find(['div', 'section'], string=re.compile(r'Bar Admission|Jurisdictions', re.I))
        
        if bar_section:
            bar_items = bar_section.find_all(['li', 'p', 'div'])
            for item in bar_items:
                bar_text = item.text.strip()
                if bar_text and not any(x in bar_text.lower() for x in ['bar admission', 'jurisdiction']):
                    admission = {
                        'jurisdiction': bar_text,
                        'year': None,
                        'status': 'Active'
                    }
                    
                    # Extract year
                    year_match = re.search(r'\b(19|20)\d{2}\b', bar_text)
                    if year_match:
                        admission['year'] = year_match.group(0)
                    
                    # Check status
                    if re.search(r'inactive|suspended|retired', bar_text, re.I):
                        admission['status'] = 'Inactive'
                    
                    admissions.append(admission)
        
        return admissions

    def _extract_awards(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract awards and honors."""
        awards = []
        awards_section = soup.find(['div', 'section'], string=re.compile(r'Awards|Honors|Recognition', re.I))
        
        if awards_section:
            award_items = awards_section.find_all(['li', 'p', 'div'])
            for item in award_items:
                award_text = item.text.strip()
                if award_text and not any(x in award_text.lower() for x in ['award', 'honor', 'recognition']):
                    award = {
                        'name': award_text,
                        'year': None,
                        'organization': None
                    }
                    
                    # Extract year
                    year_match = re.search(r'\b(19|20)\d{2}\b', award_text)
                    if year_match:
                        award['year'] = year_match.group(0)
                    
                    # Extract organization
                    org_match = re.search(r'from|by\s+([^,\.]+)', award_text)
                    if org_match:
                        award['organization'] = org_match.group(1).strip()
                    
                    awards.append(award)
        
        return awards

    def _extract_publications(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract publications."""
        publications = []
        pub_section = soup.find(['div', 'section'], string=re.compile(r'Publications|Articles|Writing', re.I))
        
        if pub_section:
            pub_items = pub_section.find_all(['li', 'p', 'div'])
            for item in pub_items:
                pub_text = item.text.strip()
                if pub_text and not any(x in pub_text.lower() for x in ['publication', 'article', 'writing']):
                    pub = {
                        'title': pub_text,
                        'year': None,
                        'publisher': None,
                        'type': None
                    }
                    
                    # Extract year
                    year_match = re.search(r'\b(19|20)\d{2}\b', pub_text)
                    if year_match:
                        pub['year'] = year_match.group(0)
                    
                    # Extract publisher
                    pub_match = re.search(r'in|by\s+([^,\.]+)', pub_text)
                    if pub_match:
                        pub['publisher'] = pub_match.group(1).strip()
                    
                    # Determine type
                    if re.search(r'book|treatise', pub_text, re.I):
                        pub['type'] = 'Book'
                    elif re.search(r'article|paper', pub_text, re.I):
                        pub['type'] = 'Article'
                    elif re.search(r'blog|post', pub_text, re.I):
                        pub['type'] = 'Blog Post'
                    
                    publications.append(pub)
        
        return publications

    def _extract_speaking_engagements(self, soup: BeautifulSoup) -> List[str]:
        """Extract speaking engagements."""
        engagements = []
        speaking_section = soup.find(['div', 'section'], string=re.compile(r'Speaking|Presentations|Lectures', re.I))
        
        if speaking_section:
            speaking_items = speaking_section.find_all(['li', 'p', 'div'])
            for item in speaking_items:
                speaking_text = item.text.strip()
                if speaking_text and not any(x in speaking_text.lower() for x in ['speaking', 'presentation', 'lecture']):
                    engagements.append(speaking_text)
        
        return engagements

    def _extract_languages(self, soup: BeautifulSoup) -> List[str]:
        """Extract languages."""
        languages = []
        lang_section = soup.find(['div', 'section'], string=re.compile(r'Languages', re.I))
        
        if lang_section:
            lang_items = lang_section.find_all(['li', 'p', 'div'])
            for item in lang_items:
                lang_text = item.text.strip()
                if lang_text and not 'languages' in lang_text.lower():
                    languages.append(lang_text)
        
        return languages

    def _extract_professional_associations(self, soup: BeautifulSoup) -> List[str]:
        """Extract professional associations."""
        associations = []
        assoc_section = soup.find(['div', 'section'], string=re.compile(r'Professional|Associations|Memberships', re.I))
        
        if assoc_section:
            assoc_items = assoc_section.find_all(['li', 'p', 'div'])
            for item in assoc_items:
                assoc_text = item.text.strip()
                if assoc_text and not any(x in assoc_text.lower() for x in ['professional', 'association', 'membership']):
                    associations.append(assoc_text)
        
        return associations

    def _extract_fee_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract fee structure information."""
        fee_info = {
            'consultation': None,
            'fee_structure': None,
            'payment_methods': [],
            'pro_bono': False
        }
        
        fee_section = soup.find(['div', 'section'], string=re.compile(r'Fees|Payment|Rates', re.I))
        if fee_section:
            text = fee_section.text.lower()
            
            # Extract consultation info
            if 'free consultation' in text:
                fee_info['consultation'] = 'Free'
            elif 'consultation' in text:
                fee_match = re.search(r'\$\d+', text)
                if fee_match:
                    fee_info['consultation'] = fee_match.group(0)
            
            # Extract fee structure
            if 'contingency' in text or 'contingent' in text:
                fee_info['fee_structure'] = 'Contingency'
            elif 'hourly' in text or 'per hour' in text:
                fee_info['fee_structure'] = 'Hourly'
            elif 'flat' in text or 'fixed' in text:
                fee_info['fee_structure'] = 'Flat Rate'
            
            # Extract payment methods
            if 'credit card' in text:
                fee_info['payment_methods'].append('Credit Card')
            if 'check' in text:
                fee_info['payment_methods'].append('Check')
            if 'cash' in text:
                fee_info['payment_methods'].append('Cash')
            
            # Check for pro bono
            if 'pro bono' in text:
                fee_info['pro_bono'] = True
        
        return fee_info

    def _extract_office_locations(self, soup: BeautifulSoup) -> List[str]:
        """Extract office locations."""
        locations = []
        office_section = soup.find(['div', 'section'], string=re.compile(r'Office|Location', re.I))
        
        if office_section:
            office_items = office_section.find_all(['li', 'p', 'div'])
            for item in office_items:
                loc_text = item.text.strip()
                if loc_text and not any(x in loc_text.lower() for x in ['office', 'location']):
                    locations.append(loc_text)
        
        return locations

    def _extract_website(self, soup: BeautifulSoup) -> str:
        """Extract website URL."""
        website_link = soup.find('a', href=re.compile(r'http'), string=re.compile(r'website|visit|home', re.I))
        return website_link['href'] if website_link else None

    def _extract_social_media(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract social media links."""
        social_media = {}
        social_patterns = {
            'linkedin': r'linkedin\.com',
            'twitter': r'twitter\.com',
            'facebook': r'facebook\.com'
        }
        
        for platform, pattern in social_patterns.items():
            social_link = soup.find('a', href=re.compile(pattern))
            if social_link:
                social_media[platform] = social_link['href']
        
        return social_media

    def _extract_practice_focus(self, soup: BeautifulSoup) -> Dict[str, int]:
        """Extract practice focus percentages."""
        focus = {}
        focus_section = soup.find(['div', 'section'], string=re.compile(r'Practice Areas|Areas of Practice', re.I))
        
        if focus_section:
            focus_items = focus_section.find_all(['li', 'p', 'div'])
            for item in focus_items:
                focus_text = item.text.strip()
                percentage_match = re.search(r'([\w\s]+)\s*[:-]\s*(\d+)%', focus_text)
                if percentage_match:
                    area = percentage_match.group(1).strip()
                    percentage = int(percentage_match.group(2))
                    focus[area] = percentage
        
        return focus

    def _extract_certifications(self, soup: BeautifulSoup) -> List[str]:
        """Extract certifications."""
        certifications = []
        cert_section = soup.find(['div', 'section'], string=re.compile(r'Certifications|Specialties', re.I))
        
        if cert_section:
            cert_items = cert_section.find_all(['li', 'p', 'div'])
            for item in cert_items:
                cert_text = item.text.strip()
                if cert_text and not any(x in cert_text.lower() for x in ['certification', 'specialty']):
                    certifications.append(cert_text)
        
        return certifications 