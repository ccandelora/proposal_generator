"""Preview image generation utilities."""
import logging
from pathlib import Path
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth

logger = logging.getLogger(__name__)

class PreviewGenerator:
    """Utility class for generating preview images using headless Chrome."""

    def __init__(self):
        """Initialize the preview generator."""
        self.driver = None

    def generate_preview(
        self,
        html_content: str,
        css_content: str,
        output_path: Path,
        width: int = 1920,
        height: int = 1080,
        device_pixel_ratio: int = 2,
        wait_for_network: bool = True,
        wait_for_animations: bool = True,
        full_page: bool = False
    ) -> Optional[str]:
        """
        Generate a preview image from HTML and CSS content.
        
        Args:
            html_content: HTML content to render
            css_content: CSS content to apply
            output_path: Path to save the preview image
            width: Viewport width
            height: Viewport height
            device_pixel_ratio: Device pixel ratio for high-DPI screenshots
            wait_for_network: Whether to wait for network requests to complete
            wait_for_animations: Whether to wait for animations to complete
            full_page: Whether to capture the full page or just the viewport
            
        Returns:
            Path to the generated preview image or None if generation failed
        """
        try:
            # Create temporary files for HTML and CSS
            temp_dir = output_path.parent / 'temp'
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            html_file = temp_dir / 'preview.html'
            css_file = temp_dir / 'styles.css'
            
            # Write content to files
            html_file.write_text(html_content)
            css_file.write_text(css_content)
            
            # Initialize headless Chrome
            self.driver = self._get_chrome_driver(width, height, device_pixel_ratio)
            
            # Navigate to the HTML file
            self.driver.get(f'file://{html_file.absolute()}')
            
            if wait_for_network:
                # Wait for network requests to complete
                WebDriverWait(self.driver, 10).until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )
            
            if wait_for_animations:
                # Wait a bit for animations to complete
                self.driver.implicitly_wait(1)
            
            # Take screenshot
            if full_page:
                # Get full page height
                height = self.driver.execute_script(
                    'return Math.max(document.body.scrollHeight, '
                    'document.documentElement.scrollHeight);'
                )
                self.driver.set_window_size(width, height)
            
            self.driver.save_screenshot(str(output_path))
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error generating preview: {str(e)}")
            return None
            
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
            
            # Cleanup temporary files
            if 'html_file' in locals():
                html_file.unlink(missing_ok=True)
            if 'css_file' in locals():
                css_file.unlink(missing_ok=True)
            if 'temp_dir' in locals():
                temp_dir.rmdir()

    def _get_chrome_driver(self, width: int, height: int, device_pixel_ratio: int) -> webdriver.Chrome:
        """Get configured Chrome driver instance."""
        chrome_options = Options()
        
        # Essential options for headless operation
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        # Set window size and device pixel ratio
        chrome_options.add_argument(f'--window-size={width},{height}')
        chrome_options.add_argument(f'--force-device-scale-factor={device_pixel_ratio}')
        
        # Additional options for better rendering
        chrome_options.add_argument('--hide-scrollbars')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--disable-extensions')
        
        # Initialize ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Apply stealth settings
        stealth(
            driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True
        )
        
        return driver 