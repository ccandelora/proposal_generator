"""HTML utility functions for SEO Screenshotter."""

from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By

def extract_text_content(driver: WebDriver) -> str:
    """Extract readable text content from webpage."""
    # Get visible text content
    text_elements = driver.find_elements(By.XPATH, 
                                       "//*[not(self::script or self::style)]/text()")
    
    # Filter and clean text
    text_content = []
    for element in text_elements:
        text = element.get_attribute("textContent")
        if text and text.strip():
            text_content.append(text.strip())
            
    return " ".join(text_content)

def get_element_styles(driver: WebDriver) -> List[Dict[str, Any]]:
    """Get computed styles for all elements."""
    elements = driver.find_elements(By.CSS_SELECTOR, "*")
    styles = []
    
    for element in elements:
        # Get element properties
        tag_name = element.tag_name
        element_id = element.get_attribute("id")
        element_class = element.get_attribute("class")
        
        # Get computed styles
        style = driver.execute_script("""
            var style = window.getComputedStyle(arguments[0]);
            var styles = {};
            for (var i = 0; i < style.length; i++) {
                var prop = style[i];
                styles[prop] = style.getPropertyValue(prop);
            }
            return styles;
        """, element)
        
        styles.append({
            "tag": tag_name,
            "id": element_id,
            "class": element_class,
            **style
        })
        
    return styles

def extract_semantic_structure(driver: WebDriver) -> Dict[str, Any]:
    """Extract semantic structure of the webpage."""
    # Get HTML content
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    return {
        "headings": _analyze_headings(soup),
        "landmarks": _analyze_landmarks(soup),
        "lists": _analyze_lists(soup),
        "links": _analyze_links(soup),
        "images": _analyze_images(soup),
        "forms": _analyze_forms(soup)
    }

def _analyze_headings(soup: BeautifulSoup) -> Dict[str, Any]:
    """Analyze heading structure."""
    headings = {}
    for i in range(1, 7):
        h_tags = soup.find_all(f'h{i}')
        if h_tags:
            headings[f'h{i}'] = {
                'count': len(h_tags),
                'text': [h.get_text(strip=True) for h in h_tags]
            }
    return headings

def _analyze_landmarks(soup: BeautifulSoup) -> Dict[str, Any]:
    """Analyze HTML5 landmarks and ARIA landmarks."""
    landmarks = {
        'header': len(soup.find_all('header')),
        'nav': len(soup.find_all('nav')),
        'main': len(soup.find_all('main')),
        'aside': len(soup.find_all('aside')),
        'footer': len(soup.find_all('footer')),
        'article': len(soup.find_all('article')),
        'section': len(soup.find_all('section'))
    }
    
    # Add ARIA landmarks
    for role in ['banner', 'navigation', 'main', 'complementary', 
                 'contentinfo', 'search', 'form']:
        landmarks[f'aria_{role}'] = len(soup.find_all(attrs={'role': role}))
        
    return landmarks

def _analyze_lists(soup: BeautifulSoup) -> Dict[str, Any]:
    """Analyze list structures."""
    return {
        'unordered': {
            'count': len(soup.find_all('ul')),
            'items': sum(len(ul.find_all('li')) for ul in soup.find_all('ul'))
        },
        'ordered': {
            'count': len(soup.find_all('ol')),
            'items': sum(len(ol.find_all('li')) for ol in soup.find_all('ol'))
        },
        'definition': {
            'count': len(soup.find_all('dl')),
            'terms': len(soup.find_all('dt')),
            'descriptions': len(soup.find_all('dd'))
        }
    }

def _analyze_links(soup: BeautifulSoup) -> Dict[str, Any]:
    """Analyze link structure and types."""
    links = soup.find_all('a')
    
    return {
        'total': len(links),
        'with_text': len([l for l in links if l.get_text(strip=True)]),
        'with_title': len([l for l in links if l.get('title')]),
        'external': len([l for l in links if l.get('href', '').startswith(('http', 'https'))]),
        'internal': len([l for l in links if l.get('href', '').startswith(('/', '#'))]),
        'empty': len([l for l in links if not l.get('href')])
    }

def _analyze_images(soup: BeautifulSoup) -> Dict[str, Any]:
    """Analyze image usage and accessibility."""
    images = soup.find_all('img')
    
    return {
        'total': len(images),
        'with_alt': len([img for img in images if img.get('alt')]),
        'without_alt': len([img for img in images if not img.get('alt')]),
        'with_title': len([img for img in images if img.get('title')]),
        'decorative': len([img for img in images if img.get('alt') == '']),
        'responsive': len([img for img in images if 'srcset' in img.attrs])
    }

def _analyze_forms(soup: BeautifulSoup) -> Dict[str, Any]:
    """Analyze form structure and accessibility."""
    forms = soup.find_all('form')
    form_analysis = {
        'total': len(forms),
        'with_labels': 0,
        'inputs': {
            'text': 0,
            'email': 0,
            'password': 0,
            'checkbox': 0,
            'radio': 0,
            'submit': 0,
            'other': 0
        },
        'required_fields': 0,
        'with_validation': 0
    }
    
    for form in forms:
        # Count inputs by type
        inputs = form.find_all('input')
        for input_elem in inputs:
            input_type = input_elem.get('type', 'text')
            if input_type in form_analysis['inputs']:
                form_analysis['inputs'][input_type] += 1
            else:
                form_analysis['inputs']['other'] += 1
                
        # Count labels
        labels = form.find_all('label')
        if labels:
            form_analysis['with_labels'] += 1
            
        # Count required fields
        required = form.find_all(attrs={'required': True})
        form_analysis['required_fields'] += len(required)
        
        # Check for HTML5 validation
        if form.find_all(attrs={'pattern': True}) or \
           form.find_all(attrs={'minlength': True}) or \
           form.find_all(attrs={'maxlength': True}):
            form_analysis['with_validation'] += 1
            
    return form_analysis

def analyze_accessibility(driver: WebDriver) -> Dict[str, Any]:
    """Analyze accessibility features of the webpage."""
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    return {
        'aria_usage': _analyze_aria_usage(soup),
        'color_contrast': _analyze_color_contrast(driver),
        'keyboard_navigation': _analyze_keyboard_navigation(soup),
        'multimedia_accessibility': _analyze_multimedia_accessibility(soup)
    }

def _analyze_aria_usage(soup: BeautifulSoup) -> Dict[str, Any]:
    """Analyze ARIA attributes usage."""
    aria_attrs = {}
    for tag in soup.find_all(True):
        for attr in tag.attrs:
            if attr.startswith('aria-'):
                aria_attrs[attr] = aria_attrs.get(attr, 0) + 1
                
    return {
        'total_aria_attributes': sum(aria_attrs.values()),
        'unique_aria_attributes': len(aria_attrs),
        'attribute_distribution': aria_attrs
    }

def _analyze_color_contrast(driver: WebDriver) -> Dict[str, Any]:
    """Analyze color contrast ratios."""
    # This is a placeholder - actual implementation would require
    # computing color contrast ratios for text elements
    return {
        'analyzed': False,
        'message': 'Color contrast analysis requires additional processing'
    }

def _analyze_keyboard_navigation(soup: BeautifulSoup) -> Dict[str, Any]:
    """Analyze keyboard navigation support."""
    return {
        'tabindex_usage': len(soup.find_all(attrs={'tabindex': True})),
        'focusable_elements': len(soup.find_all(['a', 'button', 'input', 'select', 'textarea'])),
        'skip_links': len(soup.find_all('a', attrs={'href': '#main-content'}))
    }

def _analyze_multimedia_accessibility(soup: BeautifulSoup) -> Dict[str, Any]:
    """Analyze multimedia accessibility features."""
    videos = soup.find_all('video')
    audios = soup.find_all('audio')
    
    return {
        'video': {
            'total': len(videos),
            'with_captions': len([v for v in videos if v.find('track', attrs={'kind': 'captions'})]),
            'with_descriptions': len([v for v in videos if v.find('track', attrs={'kind': 'descriptions'})])
        },
        'audio': {
            'total': len(audios),
            'with_transcripts': len([a for a in audios if a.find_next('a', attrs={'class': 'transcript'})])
        }
    }
