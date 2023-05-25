# python-scraper
 
- pip install -r requirements.txt
- python scraper.py [OPTIONS]

Options:
  - Required Arguments:
    - --url / -u Website URL to scrape PDF and HTML links from
    - --file / -f File path with URLs (one per line) to scrape PDF and HTML links from
    - --output-dir / -o Folder path to save downloaded files
  - Optional Arguments:
    - --disable-html Disable scraping HTML pages
    - --workers / -w Number of parallel workers (Default: 4)


Example:
```
python scraper.py --file urls.txt --output-dir tmp
