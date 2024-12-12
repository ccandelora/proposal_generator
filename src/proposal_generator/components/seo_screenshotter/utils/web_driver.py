"""Web driver utility module."""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
import logging

logger = logging.getLogger(__name__)

class WebDriverManager:
    """Utility class for managing web driver instances."""
    
    @staticmethod
    def get_chrome_driver():
        """
        Get a configured Chrome driver instance.
        
        Returns:
            webdriver.Chrome: Configured Chrome driver instance
        """
        try:
            chrome_options = Options()
            # Essential options for stability
            chrome_options.add_argument('--headless=new')  # Updated headless mode
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # Additional options for better stability
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-infobars')
            chrome_options.add_argument('--disable-notifications')
            chrome_options.add_argument('--disable-popup-blocking')
            chrome_options.add_argument('--remote-debugging-port=9222')
            
            # Initialize ChromeDriver using webdriver_manager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Apply stealth settings
            stealth(driver,
                   languages=["en-US", "en"],
                   vendor="Google Inc.",
                   platform="Win32",
                   webgl_vendor="Intel Inc.",
                   renderer="Intel Iris OpenGL Engine",
                   fix_hairline=True)
            
            return driver
            
        except Exception as e:
            logger.error(f"Error initializing Chrome driver: {str(e)}")
            raise 