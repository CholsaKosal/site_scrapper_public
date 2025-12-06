import os
import html2text
import logging
import time
import re
from urllib.parse import urlparse, urljoin
from collections import deque

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SiteScraper:
    """
    A class to perform chain-fetching of a website, starting from a single URL.
    It manages state by keeping track of visited URLs and a queue of URLs to visit.
    """
    def __init__(self, start_url_file="inputsite.txt"):
        # --- File and Directory Configuration ---
        self.URLS_TO_FETCH_FILE = "urls_to_fetch.txt"
        self.FETCHED_URLS_FILE = "fetched_urls.txt"
        self.OUTPUT_DIR = "output_content_draft"
        self.PROCESSED_DIR = "processed_content"
        self.start_url_file = start_url_file

        # --- Initialize Data Structures ---
        self.urls_to_fetch = deque()
        self.fetched_urls = set()
        
        # --- Scraper Configuration ---
        self.base_domain = ""
        self.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        
        # --- Setup Directories ---
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)
        os.makedirs(self.PROCESSED_DIR, exist_ok=True)

    def _initialize_driver(self):
        """Sets up the Selenium WebDriver."""
        logging.info("Initializing headless Chrome driver...")
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1200')
        options.add_argument(f'user-agent={self.USER_AGENT}')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
        stealth(self.driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32", webgl_vendor="Intel Inc.", renderer="Intel Iris OpenGL Engine", fix_hairline=True)
        logging.info("Driver initialized successfully.")

    def _load_state(self):
        """Loads the queue and fetched URLs from files to resume a previous session."""
        try:
            if os.path.exists(self.URLS_TO_FETCH_FILE):
                with open(self.URLS_TO_FETCH_FILE, 'r', encoding='utf-8') as f:
                    self.urls_to_fetch.extend([line.strip() for line in f if line.strip()])
                    logging.info(f"Loaded {len(self.urls_to_fetch)} URLs from {self.URLS_TO_FETCH_FILE}")

            if os.path.exists(self.FETCHED_URLS_FILE):
                with open(self.FETCHED_URLS_FILE, 'r', encoding='utf-8') as f:
                    self.fetched_urls.update([line.strip() for line in f if line.strip()])
                    logging.info(f"Loaded {len(self.fetched_urls)} fetched URLs from {self.FETCHED_URLS_FILE}")
        except Exception as e:
            logging.error(f"Error loading state: {e}")

    def _save_state(self):
        """Saves the current state of the queue and fetched URLs to files."""
        try:
            with open(self.URLS_TO_FETCH_FILE, 'w', encoding='utf-8') as f:
                for url in self.urls_to_fetch:
                    f.write(f"{url}\n")
            
            with open(self.FETCHED_URLS_FILE, 'w', encoding='utf-8') as f:
                for url in sorted(list(self.fetched_urls)):
                    f.write(f"{url}\n")
        except Exception as e:
            logging.error(f"Error saving state: {e}")

    def get_filename_from_url(self, url):
        """Generates a safe filename from a URL."""
        path = urlparse(url).path
        if path == '/' or not path:
            return 'home.md'
        # Sanitize filename
        filename = path.strip('/').replace('/', '-')
        return re.sub(r'[\\/*?:"<>|]', "", filename) + ".md"

    def fetch_and_process_page(self, url):
        """Fetches a single page, saves its content, and extracts new links."""
        try:
            logging.info(f"Fetching: {url}")
            self.driver.get(url)
            time.sleep(10)  # Wait for dynamic content to load

            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 1. Save Content to Markdown
            main_content = soup.find('main') or soup.body
            if not main_content:
                logging.warning(f"Could not find main content for {url}. Skipping content save.")
                return None, []

            h = html2text.HTML2Text(baseurl=url)
            h.body_width = 0
            markdown_content = h.handle(str(main_content))

            header = f"The content below was extracted from {url}\n\n---\n\n"
            full_content = header + markdown_content

            filename = self.get_filename_from_url(url)
            filepath = os.path.join(self.OUTPUT_DIR, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_content)
            logging.info(f"Content saved to {filepath}")

            # 2. Extract and Filter Links
            new_links = set()
            for link in soup.find_all('a', href=True):
                href = link['href']
                if not href or href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:'):
                    continue
                
                # Resolve relative URLs to absolute URLs
                absolute_url = urljoin(url, href)
                
                # Only add URLs from the same base domain
                if urlparse(absolute_url).netloc == self.base_domain:
                    new_links.add(absolute_url)
            
            logging.info(f"Found {len(new_links)} new potential links.")
            return filepath, list(new_links)

        except Exception as e:
            logging.error(f"An error occurred while fetching {url}: {e}", exc_info=False)
            return None, []

    def run(self):
        """Main method to run the scraper."""
        self._load_state()

        # If the queue is empty, start from the initial site file
        if not self.urls_to_fetch and not self.fetched_urls:
            try:
                with open(self.start_url_file, 'r', encoding='utf-8') as f:
                    start_url = f.readline().strip()
                if start_url:
                    self.urls_to_fetch.append(start_url)
                    self.base_domain = urlparse(start_url).netloc
                    logging.info(f"Starting crawl with base URL: {start_url}")
                else:
                    logging.error(f"{self.start_url_file} is empty. Exiting.")
                    return
            except FileNotFoundError:
                logging.error(f"Start URL file not found: {self.start_url_file}. Exiting.")
                return
        
        self._initialize_driver()
        
        try:
            while self.urls_to_fetch:
                current_url = self.urls_to_fetch.popleft()

                if current_url in self.fetched_urls:
                    logging.info(f"Skipping already fetched URL: {current_url}")
                    continue
                
                # Your Step 4: Fetch the URL
                filepath, new_links = self.fetch_and_process_page(current_url)
                
                # Your Step 1: Add to finishedFetch.txt
                self.fetched_urls.add(current_url)

                if filepath:
                    # Your Step 2: Add new URLs to fetchNext.txt
                    for link in new_links:
                        if link not in self.fetched_urls and link not in self.urls_to_fetch:
                            self.urls_to_fetch.append(link)
                    
                    # Your Step 3: Move the processed file
                    try:
                        dest_path = os.path.join(self.PROCESSED_DIR, os.path.basename(filepath))
                        os.rename(filepath, dest_path)
                        logging.info(f"Moved processed file to {dest_path}")
                    except OSError as e:
                        logging.error(f"Could not move file {filepath}: {e}")

                # Save state after each iteration
                self._save_state()
                logging.info(f"{len(self.urls_to_fetch)} URLs left in queue. {len(self.fetched_urls)} URLs fetched.")

        except KeyboardInterrupt:
            logging.info("Process interrupted by user. Saving state...")
        finally:
            self._save_state()
            self.driver.quit()
            logging.info("Scraping complete. Driver has been quit.")

if __name__ == "__main__":
    scraper = SiteScraper()
    scraper.run()