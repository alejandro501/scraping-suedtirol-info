# Südtirol Accommodation Scraper

This is a web scraping tool to extract accommodation information from Südtirol (South Tyrol), Italy. The scraper extracts data either from live pages or from a sitemap. The project is designed to run both live scraping and sitemap-based scraping, or either one individually based on user input.

## Requirements

This scraper requires the following Python packages:

* `requests`
* `beautifulsoup4`
* `lxml`

At the start of the `main.py`, dependencies will be checked and installed automatically if missing.

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/scraping-suedtirol-info.git
cd scraping-suedtirol-info
```

### 2. Set Up Python Environment

It is recommended to use a virtual environment for managing dependencies. You can create a virtual environment as follows:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

Dependencies will be automatically checked and installed when you run the scraper. However, if you prefer to manually install them, run the following command:

```bash
pip install requests beautifulsoup4 lxml
```

### 4. Running the Scraper

The scraper is designed to be run from the command line. There are two main modes:

* **Live scraping**: Extracts data from live accommodation pages.
* **Sitemap scraping**: Extracts data from the url's provided in the sitemap.

You can run both scrapers sequentially, or choose to run only one by specifying the appropriate flag.

#### To run both scrapers (default):

```bash
python3 -m scraper.main
```

#### To run only the live scraper:

```bash
python3 -m scraper.main --live
```

#### To run only the sitemap scraper:

```bash
python3 -m scraper.main --sitemap
```

### 5. Language Support

The scraper supports two languages: English (`en`) and Hungarian (`hu`). You can specify the language with the `--lang` flag:

#### For English (default):

```bash
python3 -m scraper.main --lang en
```

#### For Hungarian:

```bash
python3 -m scraper.main --lang hu
```

## Configuration

The scraper is now running with conservative (slow) settings to avoid overload and unnecessary strain on the server. It can be configured by editing the `config/settings.py` file. You can adjust parameters such as:

* **Request timeouts**
* **Delays between requests**
* **Maximum pages to scrape**

## Output

The scraper will save the scraped data in a CSV file located at the path defined in `config/settings.py`. The data includes:

* Accommodation type
* Name
* URL
* Address (region)
* Telephone
* Email

Additionally, the emails found during scraping will be saved to a separate file.

## Troubleshooting

### Missing Dependencies

If the necessary dependencies are not installed, the scraper will automatically attempt to install them using Python's `pip` package manager. Ensure that your environment has internet access for the installation process. Please feel free to shoot a ticket or make a pull request if I missed anything or I should further tailor the script for startup errors.

### Errors During Scraping

If an error occurs during scraping (e.g., network issues, invalid page format), the scraper will log the error to the console. Check the logs for specific error details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
