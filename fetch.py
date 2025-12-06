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

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_base_filename(url):
    """Generates a base filename from the URL path."""
    parsed = urlparse(url)
    path = parsed.path
    
    # Handle root or empty paths
    if path == '/' or not path:
        return 'home.md'
    
    # Clean up the path to make it filesystem friendly
    filename = path.strip('/').replace('/', '-')
    
    # Ensure it ends in .md
    if not filename.endswith('.md'):
        filename += ".md"
        
    return filename

def get_unique_filepath(directory, filename):
    """
    Checks if a file exists. If so, appends a counter (_1, _2) 
    to ensure the new filename is unique.
    """
    base_name, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    full_path = os.path.join(directory, new_filename)

    while os.path.exists(full_path):
        new_filename = f"{base_name}_{counter}{ext}"
        full_path = os.path.join(directory, new_filename)
        counter += 1
    
    return full_path

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 1. Read all URLs from the file
    urls = []
    try:
        with open(SITEMAP_FILE, 'r', encoding='utf-8') as f:
            # Read all lines, strip whitespace, and ignore empty lines
            urls = [line.strip() for line in f if line.strip()]
        
        if not urls:
            logging.error("Sitemap file is empty.")
            exit()
            
        logging.info(f"Found {len(urls)} links to process.")
        
    except FileNotFoundError:
        logging.error(f"Could not find file: {SITEMAP_FILE}")
        exit()

    logging.info("--- Stage 1: Initializing Browser ---")
    
    # 2. Setup Driver (Once)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') # Uncomment to run in background
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1200')
    options.add_argument(f'user-agent={USER_AGENT}')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        stealth(driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32", webgl_vendor="Intel Inc.", renderer="Intel Iris OpenGL Engine", fix_hairline=True)
        
        # 3. Iterate through all URLs
        for index, url in enumerate(urls):
            logging.info(f"Processing ({index + 1}/{len(urls)}): {url}")
            
            try:
                driver.get(url)
                
                # Wait for load
                logging.info("Waiting 5 seconds for page load...")
                time.sleep(5) 
                
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # Attempt to find main content, fallback to body
                main_content = soup.find('main') or soup.body

                if not main_content:
                    logging.warning(f"Skipping {url}: Could not find main content.")
                    continue

                # Convert to Markdown
                h = html2text.HTML2Text(baseurl=url)
                h.body_width = 0
                markdown_content = h.handle(str(main_content))

                header = f"The content below is extracted from {url}\n\n---\n\n"
                full_content = header + markdown_content

                # 4. Generate Unique Filename
                base_filename = get_base_filename(url)
                final_filepath = get_unique_filepath(OUTPUT_DIR, base_filename)
                
                # Save
                with open(final_filepath, 'w', encoding='utf-8') as f:
                    f.write(full_content)
                logging.info(f"Saved to {final_filepath}")

            except Exception as e:
                # Log error but continue to next URL
                logging.error(f"Failed to process {url}: {e}")

    except Exception as e:
        logging.critical(f"Critical driver error: {e}")
        
    finally:
        if 'driver' in locals():
            driver.quit()
        logging.info("--- Processing Complete ---")