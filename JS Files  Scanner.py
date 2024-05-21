import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging

# Configure logging
logging.basicConfig(filename='js_extraction.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_js_files(url):
    try:
        logging.info(f"Fetching URL: {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        js_files = []

        # Find all script tags and extract the 'src' attribute
        for script in soup.find_all('script'):
            if script.get('src'):
                js_file_url = urljoin(url, script['src'])
                js_files.append(js_file_url)
                logging.info(f"Found JS file: {js_file_url}")

        return js_files
    except requests.RequestException as e:
        logging.error(f"Failed to retrieve the website content: {e}")
        return []

if __name__ == "__main__":
    website_url = input("Enter the URL of the website: ")
    logging.info(f"Starting JS extraction for {website_url}")
    js_files = extract_js_files(website_url)
    if js_files:
        print("JavaScript files found:")
        for js_file in js_files:
            print(js_file)
    else:
        print("No JavaScript files found.")
