import scrapy
import os
import requests


def download_pdf(url, report_name):
    """
    This function downloads the PDF from the given URL and saves it to a local folder.
    """
    # Path to save the downloaded PDF file
    local_folder = '/Users/anna/Desktop/MakeCents/Web_Scrapy/WebScraper/stock_data_scraper/stock_data_scraper/saved_PDF'

    if not os.path.exists(local_folder):
        os.makedirs(local_folder)

    local_file_path = os.path.join(local_folder, report_name)

    # Send a request to download the PDF
    response = requests.get(url)

    # Ensure the request was successful
    if response.status_code == 200:
        # Save the PDF to the local file path
        with open(local_file_path, 'wb') as pdf_file:
            pdf_file.write(response.content)
        print(f"PDF saved successfully: {local_file_path}")
    else:
        print(f"Failed to download PDF: {url}")


class MarketIndexSpider(scrapy.Spider):
    # Name of the spider
    name = "marketindex"
    allowed_domains = ["marketindex.com.au"]
    # Starting URL for scraping
    start_urls = ['https://www.marketindex.com.au/all-ordinaries']

    def parse(self, response):
        """
        This function parses the main page for links to individual company pages.
        """
        # Check for "Show All Companies" button and click it
        show_all_button = response.css(
            'button.control-company-display[data-quoteapi-name="quoteapi--"]:contains("Show All Companies")')
        if show_all_button:
            yield scrapy.FormRequest.from_response(
                response,
                formdata={'pageSize': '0'},
                callback=self.parse,
                dont_filter=True
            )
        else:
            # Loop through each company row in the table using the correct selector
            for company in response.css('tbody[data-quoteapi-items="true"] tr'):
                # Extract the link to the company's page
                company_page = company.css('a::attr(href)').get()
                if company_page:
                    # Follow the link to the company's page and call parse_company to handle the response
                    yield response.follow(company_page, callback=self.parse_company)

            # Handle pagination on the main page by finding the "next" page link
            next_page = response.css('a.next::attr(href)').get()
            if next_page:
                # Follow the link to the next page and call parse to handle the response
                yield response.follow(next_page, self.parse)

    def parse_company(self, response):
        """
        This function parses the individual company's page for PDF report links.
        """
        # Extract the company's name
        company_name = response.css('h1::text').get()
        # Loop through each report in the announcements table
        for report in response.css('#app-table tbody tr'):
            # Extract the link to the report
            report_link = report.css('a[data-srctype="pdf_icon"]::attr(href)').get()
            if report_link and report_link.endswith('.pdf'):
                # Get the report name from the link
                report_name = report_link.split('/')[-1]
                # Download the PDF report
                # download_pdf(response.urljoin(report_link), report_name)

        # Handle pagination within the company's page by finding the "next" button
        next_page = response.css('button[data-pagination="next"]::attr(data-pagination)').get()
        if next_page:
            # Follow the link to the next page and call parse_company to handle the response
            yield response.follow(response.url, self.parse_company, meta={'next_page': next_page})
