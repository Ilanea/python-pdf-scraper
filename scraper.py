import os
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


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
            pdf_links.append(absolute_url)

        # If the link is an HTML link and has not been visited yet, add it to the HTML links list
        elif scrape_html and absolute_url.startswith(url) and absolute_url not in visited_pages:
            html_links.append(absolute_url)

    # Add the current URL to the visited pages set
    visited_pages.add(url)


    # Recursively scrape all HTML links on the page
    for link in html_links:
        pdf_links_recursive, html_links_recursive = scrape_links(link, scrape_html, visited_pages)
        pdf_links += pdf_links_recursive
        html_links += html_links_recursive

    # Return the PDF and HTML links found on the page
    return pdf_links, html_links

def download_file(url, folder):
    response = requests.get(url)
    file_name = os.path.basename(url)
    file_path = os.path.join(folder, file_name)

    with open(file_path, 'wb') as file:
        file.write(response.content)

    print(f"Downloaded: {file_name}")

# Parse command-line arguments
parser = argparse.ArgumentParser(description='PDF and HTML Scraper')
parser.add_argument('--url', '-u', default='', type=str, help='Website URL to scrape PDF and HTML links from')
parser.add_argument('--output-dir', '-o', default='', type=str, help='Folder path to save downloaded files')
parser.add_argument('--disable-html', action='store_true', help='Disable scraping HTML pages')
args = parser.parse_args()

# Convert relative paths to absolute paths
output_dir = os.path.abspath(args.output_dir)

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Scrape PDF and HTML links
pdf_links, html_links = scrape_links(args.url, not args.disable_html)

# Remove initial URL from HTML links
html_links = [link for link in html_links if link != args.url]

# Download PDF and HTML files
for link in pdf_links:
    download_file(link, output_dir)

if not args.disable_html:
    for link in html_links:
        download_file(link, output_dir)

print("Download complete.")