import os
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import concurrent.futures

# Function to generate a random string of alphanumeric characters
def generate_random_string(length):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def scrape_links(url, scrape_html=True, visited_pages=None):
    if visited_pages is None:
        visited_pages = set()

    # Print out the URL being scraped
    print(f"Scraping URL: {url}")

    # Send HTTP request
    response = requests.get(url)

    # Parse HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Initialize lists for PDF and HTML links
    pdf_links = []
    html_links = []

    # Find all links on the page
    for link in soup.find_all('a'):
        href = link.get('href')
        absolute_url = urljoin(url, href)

        # If the link is a PDF, add it to the PDF links list
        if href.endswith('.pdf'):
            print(f"Found link to .pdf: {href}")
            pdf_links.append(absolute_url)

        # If the link is an HTML link and has not been visited yet, add it to the HTML links list
        elif href.endswith('.html') and scrape_html and absolute_url not in visited_pages:
            print(f"Found link to .html: {href}")
            if 'index.html' in href:
                print(f"Skipping index.html: {href}")
            else:
                html_links.append(absolute_url)

    # Add the current URL to the visited pages set
    visited_pages.add(url)

    #print(html_links)

    # Return the PDF and HTML links found on the page
    return pdf_links, html_links

def download_file(url, folder):
    response = requests.get(url)
    file_name = os.path.basename(url)

    # Check if the URL contains 'index.html'
    #if 'index.html' in url:
    #    print(f"Found index in url: {url}")
    #    # Generate a random number and append it to the filename
    #    random_number = generate_random_string(6)
    #    file_name = f"index_{random_number}.html"

    file_path = os.path.join(folder, file_name)

    with open(file_path, 'wb') as file:
        file.write(response.content)

    print(f"Downloaded: {file_name}")

def download_files(urls, output_dir):
    for url in urls:
        file_name = os.path.basename(url)
        file_path = os.path.join(output_dir, file_name)

        # Check if the file already exists in the output directory (caching)
        if os.path.exists(file_path):
            print(f"Skipping download: {file_name} (already exists)")
        else:
            download_file(url, output_dir)

# Parse command-line arguments
parser = argparse.ArgumentParser(description='PDF and HTML Scraper')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--url', '-u', default='', type=str, help='Website URL to scrape PDF and HTML links from')
group.add_argument('--file', '-f', default='', type=str, help='File path with URLs (one per line) to scrape PDF and HTML links from')
parser.add_argument('--output-dir', '-o', default='', type=str, help='Folder path to save downloaded files')
parser.add_argument('--disable-html', action='store_true', help='Disable scraping HTML pages')
parser.add_argument('--workers', '-w', default=4, type=int, help='Number of parallel workers')
args = parser.parse_args()

# Convert relative paths to absolute paths
output_dir = os.path.abspath(args.output_dir)

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Determine if the input is a single URL or a file with URLs
if args.file:
    with open(args.file, 'r') as file:
        urls = [line.strip() for line in file]
else:
    urls = [args.url]

# Scrape PDF and HTML links
pdf_links = set()
html_links = set()
visited_pages = set()

for url in urls:
    links = scrape_links(url, not args.disable_html, visited_pages)
    pdf_links.update(links[0])
    html_links.update(links[1])

# Remove initial URLs from HTML links
html_links = [link for link in html_links if link not in urls]

# Download PDF and HTML files in parallel using multi-threading
with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
    executor.submit(download_files, pdf_links, output_dir)
    if not args.disable_html:
        executor.submit(download_files, html_links, output_dir)

print("Download complete.")