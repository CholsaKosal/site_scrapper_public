import os
import html2text
import logging
import time
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth

# --- Configuration ---
SITEMAP_FILE = "inputsite.txt"
OUTPUT_DIR = "output_content_draft"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_filename_from_url(url):
    path = urlparse(url).path
    if path == '/' or not path: return 'home.md'
    return path.strip('/').replace('/', '-') + ".md"

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    try:
        with open(SITEMAP_FILE, 'r', encoding='utf-8') as f:
            url = f.readline().strip()
        if not url:
            raise ValueError("Sitemap file is empty.")
    except (FileNotFoundError, ValueError) as e:
        logging.error(f"Could not read URL from {SITEMAP_FILE}: {e}")
        exit()

    logging.info("--- Stage 1: Scraping initial content ---")
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') # Runs in the background
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1200')
    options.add_argument(f'user-agent={USER_AGENT}')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    stealth(driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32", webgl_vendor="Intel Inc.", renderer="Intel Iris OpenGL Engine", fix_hairline=True)
    
    try:
        driver.get(url)
        logging.info("Waiting 20 seconds for page to load in the background...")
        time.sleep(20)
        
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        main_content = soup.find('main') or soup.body

        if not main_content:
            raise Exception("Could not find main content of the page.")

        h = html2text.HTML2Text(baseurl=url)
        h.body_width = 0
        markdown_content = h.handle(str(main_content))

        header = f"The content below are extracted from {url}\n\n---\n\n"
        full_content = header + markdown_content

        filename = get_filename_from_url(url)
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)
        logging.info(f"Initial content successfully saved to {filepath}")

    except Exception as e:
        logging.error(f"An error occurred during Stage 1: {e}", exc_info=True)
    finally:
        driver.quit()
        logging.info("Stage 1 complete.")