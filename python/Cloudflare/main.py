import cloudscraper

def main():
    scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
    # Or: scraper = cloudscraper.CloudScraper()  # CloudScraper inherits from requests.Session
    print(scraper.get("https://moz.gov.ua").text)  # => "<!DOCTYPE html><html><head>..."

if __name__ == "__main__":
    main()
