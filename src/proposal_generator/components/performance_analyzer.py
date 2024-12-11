from typing import Dict, Any, List
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
import time
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class PerformanceAnalyzer(BaseAgent):
    """Analyzes website performance metrics."""
    
    def __init__(self):
        super().__init__()
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze website performance.
        
        Args:
            data: Dictionary containing website URL and analysis options
            
        Returns:
            Dictionary containing performance analysis results
        """
        try:
            url = data.get('website')
            if not url:
                return {'error': 'No website URL provided'}
            
            return self.analyze_performance(url)
        except Exception as e:
            return self._handle_error(e, "performance analysis")

    def analyze_performance(self, url: str) -> Dict[str, Any]:
        """Perform comprehensive performance analysis of a website."""
        driver = None
        try:
            driver = webdriver.Chrome(options=self.chrome_options)
            
            # Apply stealth mode to avoid detection
            stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
            )
            
            # Start performance measurement
            start_time = time.time()
            
            # Navigate to the URL
            driver.get(url)
            
            # Get performance metrics using Navigation Timing API
            navigation_timing = driver.execute_script("""
                const performance = window.performance;
                const timing = performance.timing;
                return {
                    loadTime: timing.loadEventEnd - timing.navigationStart,
                    domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                    firstPaint: performance.getEntriesByType('paint')[0].startTime,
                    firstContentfulPaint: performance.getEntriesByType('paint')[1].startTime,
                    domInteractive: timing.domInteractive - timing.navigationStart,
                    serverResponseTime: timing.responseEnd - timing.requestStart,
                    pageSize: document.documentElement.innerHTML.length,
                    resourceCount: performance.getEntriesByType('resource').length
                };
            """)
            
            # Get resource timing data
            resource_timing = driver.execute_script("""
                return performance.getEntriesByType('resource').map(resource => ({
                    name: resource.name,
                    type: resource.initiatorType,
                    duration: resource.duration,
                    size: resource.transferSize || 0
                }));
            """)
            
            # Analyze page content
            page_metrics = driver.execute_script("""
                return {
                    images: document.getElementsByTagName('img').length,
                    scripts: document.getElementsByTagName('script').length,
                    stylesheets: document.getElementsByTagName('link').length,
                    iframes: document.getElementsByTagName('iframe').length,
                    totalElements: document.getElementsByTagName('*').length
                };
            """)
            
            # Calculate scores and recommendations
            scores = self._calculate_performance_scores(navigation_timing, page_metrics)
            recommendations = self._generate_recommendations(navigation_timing, page_metrics, resource_timing)
            
            return {
                'timing_metrics': navigation_timing,
                'page_metrics': page_metrics,
                'resource_timing': resource_timing,
                'performance_scores': scores,
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.warning(f"Error analyzing performance for {url}: {str(e)}")
            return {'error': str(e)}
        finally:
            if driver:
                driver.quit()

    def _calculate_performance_scores(self, timing: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance scores based on metrics."""
        scores = {}
        
        # Load Time Score (0-100)
        load_time = timing['loadTime']
        if load_time < 2000:
            scores['load_time'] = 100
        elif load_time < 3000:
            scores['load_time'] = 90
        elif load_time < 4000:
            scores['load_time'] = 75
        elif load_time < 5000:
            scores['load_time'] = 60
        else:
            scores['load_time'] = max(0, 100 - (load_time - 5000) / 100)
        
        # Resource Efficiency Score
        resource_count = metrics['scripts'] + metrics['stylesheets'] + metrics['images']
        if resource_count < 20:
            scores['resource_efficiency'] = 100
        elif resource_count < 40:
            scores['resource_efficiency'] = 80
        elif resource_count < 60:
            scores['resource_efficiency'] = 60
        else:
            scores['resource_efficiency'] = max(0, 100 - (resource_count - 60))
        
        # First Paint Score
        first_paint = timing['firstPaint']
        if first_paint < 1000:
            scores['first_paint'] = 100
        elif first_paint < 2000:
            scores['first_paint'] = 85
        elif first_paint < 3000:
            scores['first_paint'] = 70
        else:
            scores['first_paint'] = max(0, 100 - (first_paint - 3000) / 50)
        
        # Overall Score (weighted average)
        scores['overall'] = int(
            (scores['load_time'] * 0.4) +
            (scores['resource_efficiency'] * 0.3) +
            (scores['first_paint'] * 0.3)
        )
        
        return scores

    def _generate_recommendations(self, timing: Dict[str, Any], metrics: Dict[str, Any], resources: List[Dict[str, Any]]) -> List[str]:
        """Generate performance recommendations based on analysis."""
        recommendations = []
        
        # Load time recommendations
        if timing['loadTime'] > 3000:
            recommendations.append("Improve page load time (current: {:.1f}s, target: < 3s)".format(timing['loadTime'] / 1000))
        
        # Resource count recommendations
        if metrics['scripts'] > 15:
            recommendations.append(f"Reduce number of JavaScript files (current: {metrics['scripts']}, recommended: < 15)")
        if metrics['stylesheets'] > 5:
            recommendations.append(f"Reduce number of CSS files (current: {metrics['stylesheets']}, recommended: < 5)")
        
        # Image optimization recommendations
        large_images = [r for r in resources if r['type'] == 'img' and r['size'] > 200000]
        if large_images:
            recommendations.append(f"Optimize {len(large_images)} large images (size > 200KB)")
        
        # Server response time
        if timing['serverResponseTime'] > 200:
            recommendations.append("Improve server response time (current: {:.1f}ms, target: < 200ms)".format(timing['serverResponseTime']))
        
        # First paint recommendations
        if timing['firstPaint'] > 1000:
            recommendations.append("Improve First Paint time (current: {:.1f}s, target: < 1s)".format(timing['firstPaint'] / 1000))
        
        return recommendations 