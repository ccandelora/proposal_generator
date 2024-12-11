from typing import Dict, List, Any
import requests
from bs4 import BeautifulSoup
import re
import logging
import time
import random
from ..base_agent import BaseAgent

logger = logging.getLogger(__name__)

class DirectorySearcher(BaseAgent):
    """Handles searching legal directories for attorneys."""
    
    def __init__(self):
        super().__init__()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.directories = {
            'justia': 'https://www.justia.com/lawyers/',
            'avvo': 'https://www.avvo.com/find-a-lawyer/',
            'martindale': 'https://www.martindale.com/find-attorneys/',
            'findlaw': 'https://lawyers.findlaw.com/'
        }

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process method required by BaseAgent."""
        location = data.get('location', '')
        practice_areas = data.get('practice_areas', [])
        
        if not location:
            return {'error': 'Location not provided'}
        
        results = self.search(location, practice_areas)
        return {'results': results}

    def search(self, location: str, practice_areas: List[str]) -> List[Dict[str, Any]]:
        """Search all directories for attorneys."""
        results = []
        
        for directory, base_url in self.directories.items():
            try:
                directory_results = self._search_directory(directory, base_url, location, practice_areas)
                if directory_results:
                    results.extend(directory_results)
                time.sleep(random.uniform(2, 4))  # Respectful delay between directories
            except Exception as e:
                logger.warning(f"Error searching {directory}: {str(e)}")
        
        return results

    def _search_directory(self, directory: str, base_url: str, location: str, practice_areas: List[str]) -> List[Dict[str, Any]]:
        """Search a specific directory for attorneys."""
        if directory == 'justia':
            return self._search_justia(location, practice_areas)
        elif directory == 'avvo':
            return self._search_avvo(location, practice_areas)
        elif directory == 'martindale':
            return self._search_martindale(location, practice_areas)
        elif directory == 'findlaw':
            return self._search_findlaw(location, practice_areas)
        return []

    def _search_justia(self, location: str, practice_areas: List[str]) -> List[Dict[str, Any]]:
        """Search Justia for attorneys."""
        results = []
        
        try:
            # Format location for URL
            location_parts = location.lower().split(',')
            city = location_parts[0].strip().replace(' ', '-')
            state = location_parts[1].strip().replace(' ', '-') if len(location_parts) > 1 else ''
            
            # Search for each practice area
            for practice_area in practice_areas:
                practice_slug = practice_area.lower().replace(' ', '-')
                url = f"https://www.justia.com/lawyers/{state}/{city}/{practice_slug}-lawyers/"
                
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find attorney listings
                    listings = soup.find_all('div', class_=['lawyer-card', 'attorney-listing'])
                    
                    for listing in listings:
                        attorney = self._parse_justia_listing(listing, location)
                        if attorney:
                            results.append(attorney)
                
                time.sleep(random.uniform(2, 4))  # Respectful delay between searches
        
        except Exception as e:
            logger.warning(f"Error searching Justia: {str(e)}")
        
        return results

    def _parse_justia_listing(self, listing: BeautifulSoup, location: str) -> Dict[str, Any]:
        """Parse a Justia attorney listing."""
        attorney = {
            'name': '',
            'profile_url': '',
            'directory': 'justia',
            'practice_areas': [],
            'location': location,
            'rating': None,
            'reviews_count': 0,
            'years_experience': None,
            'languages': [],
            'education': [],
            'bar_admissions': [],
            'contact_info': {},
            'description': ''
        }
        
        # Extract name and profile URL
        name_elem = listing.find(['h2', 'h3'], class_='lawyer-name')
        if name_elem:
            attorney['name'] = name_elem.text.strip()
            link = name_elem.find('a')
            if link:
                attorney['profile_url'] = link['href'] if link['href'].startswith('http') else f"https://www.justia.com{link['href']}"
        
        # Extract practice areas
        practice_elem = listing.find('div', class_=['practice-areas', 'areas-of-practice'])
        if practice_elem:
            areas = [area.strip() for area in practice_elem.text.split(',')]
            attorney['practice_areas'].extend(areas)
        
        # Extract description
        desc_elem = listing.find('div', class_=['description', 'lawyer-description'])
        if desc_elem:
            attorney['description'] = desc_elem.text.strip()
        
        # Extract contact information
        contact_section = listing.find('div', class_=['contact-info', 'lawyer-contact'])
        if contact_section:
            attorney['contact_info'] = self._parse_contact_info(contact_section)
        
        # Extract years of experience
        exp_elem = listing.find(string=re.compile(r'years? experience|years? in practice|practicing since', re.I))
        if exp_elem:
            year_match = re.search(r'(?:since\s+)?(\d{4})|(\d+)\s+years?', exp_elem.lower())
            if year_match:
                if year_match.group(1):  # "since YYYY" format
                    attorney['years_experience'] = 2024 - int(year_match.group(1))
                elif year_match.group(2):  # "XX years" format
                    attorney['years_experience'] = int(year_match.group(2))
        
        return attorney

    def _parse_contact_info(self, contact_section: BeautifulSoup) -> Dict[str, str]:
        """Parse contact information from a section."""
        contact_info = {}
        
        # Extract phone
        phone_elem = contact_section.find(string=re.compile(r'Phone|Tel'))
        if phone_elem:
            phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', phone_elem.parent.text)
            if phone_match:
                contact_info['phone'] = phone_match.group(0)
        
        # Extract email
        email_elem = contact_section.find('a', href=re.compile(r'mailto:'))
        if email_elem:
            contact_info['email'] = email_elem['href'].replace('mailto:', '')
        
        # Extract address
        address_elem = contact_section.find('address') or contact_section.find(class_='address')
        if address_elem:
            contact_info['address'] = address_elem.text.strip()
        
        return contact_info 

    def _search_avvo(self, location: str, practice_areas: List[str]) -> List[Dict[str, Any]]:
        """Search Avvo for attorneys."""
        results = []
        
        try:
            # Format location for URL
            location_parts = location.lower().split(',')
            city = location_parts[0].strip().replace(' ', '-')
            state = location_parts[1].strip().replace(' ', '-') if len(location_parts) > 1 else ''
            
            # Search for each practice area
            for practice_area in practice_areas:
                practice_slug = practice_area.lower().replace(' ', '-')
                url = f"https://www.avvo.com/search/lawyer_search?q={practice_slug}&loc={city}%2C+{state}"
                
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find attorney listings
                    listings = soup.find_all('div', class_=['lawyer-search-result', 'v-lawyer-card'])
                    
                    for listing in listings:
                        attorney = self._parse_avvo_listing(listing, location)
                        if attorney:
                            results.append(attorney)
                
                time.sleep(random.uniform(2, 4))  # Respectful delay between searches
        
        except Exception as e:
            logger.warning(f"Error searching Avvo: {str(e)}")
        
        return results

    def _parse_avvo_listing(self, listing: BeautifulSoup, location: str) -> Dict[str, Any]:
        """Parse an Avvo attorney listing."""
        attorney = {
            'name': '',
            'profile_url': '',
            'directory': 'avvo',
            'practice_areas': [],
            'location': location,
            'rating': None,
            'reviews_count': 0,
            'years_experience': None,
            'languages': [],
            'education': [],
            'bar_admissions': [],
            'contact_info': {},
            'description': ''
        }
        
        # Extract name and profile URL
        name_elem = listing.find(['h3', 'a'], class_=['lawyer-name', 'v-lawyer-name'])
        if name_elem:
            attorney['name'] = name_elem.text.strip()
            link = name_elem if name_elem.name == 'a' else name_elem.find('a')
            if link and link.get('href'):
                attorney['profile_url'] = link['href'] if link['href'].startswith('http') else f"https://www.avvo.com{link['href']}"
        
        # Extract practice areas
        practice_elem = listing.find('p', class_=['practice-areas', 'v-practice-areas'])
        if practice_elem:
            areas = [area.strip() for area in practice_elem.text.split(',')]
            attorney['practice_areas'].extend(areas)
        
        # Extract rating
        rating_elem = listing.find(['div', 'span'], class_=['avvo-rating', 'v-rating'])
        if rating_elem:
            try:
                attorney['rating'] = float(re.search(r'\d+\.?\d*', rating_elem.text).group())
            except (AttributeError, ValueError):
                pass
        
        # Extract reviews count
        reviews_elem = listing.find(string=re.compile(r'reviews?', re.I))
        if reviews_elem:
            try:
                attorney['reviews_count'] = int(re.search(r'\d+', reviews_elem).group())
            except (AttributeError, ValueError):
                pass
        
        return attorney

    def _search_martindale(self, location: str, practice_areas: List[str]) -> List[Dict[str, Any]]:
        """Search Martindale for attorneys."""
        results = []
        
        try:
            # Format location for URL
            location_parts = location.lower().split(',')
            city = location_parts[0].strip().replace(' ', '-')
            state = location_parts[1].strip().replace(' ', '-') if len(location_parts) > 1 else ''
            
            # Search for each practice area
            for practice_area in practice_areas:
                practice_slug = practice_area.lower().replace(' ', '-')
                url = f"https://www.martindale.com/search/attorneys/{state}/{city}/{practice_slug}/"
                
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find attorney listings
                    listings = soup.find_all('div', class_=['attorney-search-card', 'lawyer-card'])
                    
                    for listing in listings:
                        attorney = self._parse_martindale_listing(listing, location)
                        if attorney:
                            results.append(attorney)
                
                time.sleep(random.uniform(2, 4))  # Respectful delay between searches
        
        except Exception as e:
            logger.warning(f"Error searching Martindale: {str(e)}")
        
        return results

    def _parse_martindale_listing(self, listing: BeautifulSoup, location: str) -> Dict[str, Any]:
        """Parse a Martindale attorney listing."""
        attorney = {
            'name': '',
            'profile_url': '',
            'directory': 'martindale',
            'practice_areas': [],
            'location': location,
            'rating': None,
            'reviews_count': 0,
            'years_experience': None,
            'languages': [],
            'education': [],
            'bar_admissions': [],
            'contact_info': {},
            'description': ''
        }
        
        # Extract name and profile URL
        name_elem = listing.find(['h3', 'a'], class_='attorney-name')
        if name_elem:
            attorney['name'] = name_elem.text.strip()
            link = name_elem if name_elem.name == 'a' else name_elem.find('a')
            if link and link.get('href'):
                attorney['profile_url'] = link['href'] if link['href'].startswith('http') else f"https://www.martindale.com{link['href']}"
        
        # Extract practice areas
        practice_elem = listing.find('div', class_='attorney-practice-areas')
        if practice_elem:
            areas = [area.strip() for area in practice_elem.text.split(',')]
            attorney['practice_areas'].extend(areas)
        
        # Extract rating
        rating_elem = listing.find(['div', 'span'], class_='peer-review-rating')
        if rating_elem:
            try:
                attorney['rating'] = float(re.search(r'\d+\.?\d*', rating_elem.text).group())
            except (AttributeError, ValueError):
                pass
        
        # Extract years of experience
        exp_elem = listing.find(string=re.compile(r'years? experience|practicing since', re.I))
        if exp_elem:
            year_match = re.search(r'(?:since\s+)?(\d{4})|(\d+)\s+years?', exp_elem.lower())
            if year_match:
                if year_match.group(1):  # "since YYYY" format
                    attorney['years_experience'] = 2024 - int(year_match.group(1))
                elif year_match.group(2):  # "XX years" format
                    attorney['years_experience'] = int(year_match.group(2))
        
        return attorney

    def _search_findlaw(self, location: str, practice_areas: List[str]) -> List[Dict[str, Any]]:
        """Search FindLaw for attorneys."""
        results = []
        
        try:
            # Format location for URL
            location_parts = location.lower().split(',')
            city = location_parts[0].strip().replace(' ', '-')
            state = location_parts[1].strip().replace(' ', '-') if len(location_parts) > 1 else ''
            
            # Search for each practice area
            for practice_area in practice_areas:
                practice_slug = practice_area.lower().replace(' ', '-')
                url = f"https://lawyers.findlaw.com/{state}/{city}/{practice_slug}-lawyer.html"
                
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find attorney listings
                    listings = soup.find_all('div', class_=['listing', 'lawyer-card'])
                    
                    for listing in listings:
                        attorney = self._parse_findlaw_listing(listing, location)
                        if attorney:
                            results.append(attorney)
                
                time.sleep(random.uniform(2, 4))  # Respectful delay between searches
        
        except Exception as e:
            logger.warning(f"Error searching FindLaw: {str(e)}")
        
        return results

    def _parse_findlaw_listing(self, listing: BeautifulSoup, location: str) -> Dict[str, Any]:
        """Parse a FindLaw attorney listing."""
        attorney = {
            'name': '',
            'profile_url': '',
            'directory': 'findlaw',
            'practice_areas': [],
            'location': location,
            'rating': None,
            'reviews_count': 0,
            'years_experience': None,
            'languages': [],
            'education': [],
            'bar_admissions': [],
            'contact_info': {},
            'description': ''
        }
        
        # Extract name and profile URL
        name_elem = listing.find(['h2', 'h3', 'a'], class_=['listing-title', 'lawyer-name'])
        if name_elem:
            attorney['name'] = name_elem.text.strip()
            link = name_elem if name_elem.name == 'a' else name_elem.find('a')
            if link and link.get('href'):
                attorney['profile_url'] = link['href'] if link['href'].startswith('http') else f"https://lawyers.findlaw.com{link['href']}"
        
        # Extract practice areas
        practice_elem = listing.find('div', class_=['practice-areas', 'areas-of-practice'])
        if practice_elem:
            areas = [area.strip() for area in practice_elem.text.split(',')]
            attorney['practice_areas'].extend(areas)
        
        # Extract description
        desc_elem = listing.find('div', class_=['description', 'lawyer-description'])
        if desc_elem:
            attorney['description'] = desc_elem.text.strip()
        
        # Extract contact information
        contact_section = listing.find('div', class_=['contact-info', 'lawyer-contact'])
        if contact_section:
            attorney['contact_info'] = self._parse_contact_info(contact_section)
        
        # Extract years of experience
        exp_elem = listing.find(string=re.compile(r'years? experience|practicing since', re.I))
        if exp_elem:
            year_match = re.search(r'(?:since\s+)?(\d{4})|(\d+)\s+years?', exp_elem.lower())
            if year_match:
                if year_match.group(1):  # "since YYYY" format
                    attorney['years_experience'] = 2024 - int(year_match.group(1))
                elif year_match.group(2):  # "XX years" format
                    attorney['years_experience'] = int(year_match.group(2))
        
        return attorney