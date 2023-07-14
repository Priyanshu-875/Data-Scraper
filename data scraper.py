"""This code scrape/extract data from Google Maps"""


# Import necessary libraries
from playwright.sync_api import sync_playwright  # Import the sync_playwright module from the playwright library
from dataclasses import dataclass, asdict, field  # Import the dataclass and field modules from the dataclasses library
import pandas as pd  # Import the pandas library with the alias pd

# Define a dataclass to hold business data
@dataclass
class Business:
    name: str = None  # Define a dataclass field 'name' of type str with a default value of None
    phone_number: str = None  # Define a dataclass field 'phone_number' of type str with a default value of None

# Define a dataclass to hold a list of Business objects and save to Excel
@dataclass
class BusinessList:
    business_list: list[Business] = field(default_factory=list)  # Define a dataclass field 'business_list' as a list of Business objects with a default factory of an empty list

    # Convert business_list to a pandas dataframe
    def dataframe(self):
        return pd.json_normalize((asdict(business) for business in self.business_list), sep="_")

    # Save the dataframe to an Excel file
    def save_to_excel(self, filename):
        self.dataframe().to_excel(f'{filename}.xlsx', index=False)

def main():
    # Launch Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Go to Google Maps website
        page.goto('https://www.google.com/maps', timeout=60000)

        # Fill the search box with the provided search term
        search_box_locator = '//input[@id="searchboxinput"]'
        page.locator(search_box_locator).fill(search_for)
        page.wait_for_timeout(3000)

        # Press Enter to perform the search
        page.keyboard.press('Enter')
        page.wait_for_timeout(5000)

        # Hover over the first listing to trigger infinite scroll
        page.hover('(//div[@role="article"])[1]')

        while True:
            # Scroll the page to load more listings
            page.mouse.wheel(0, 10000)
            page.wait_for_timeout(3000)

            # Check if the desired number of listings has been scraped
            if page.locator('//div[@role="article"]').count() >= number:
                listings = page.locator('//div[@role="article"]').all()[:number]
                print(f'Total scrapped: {len(listings)}')
                break
            else:
                print('Total scrapped: 000000000000000000000')

        business_list = BusinessList()

        # Iterate over the listings and retrieve business information
        for listing in listings:
            listing.click()
            page.wait_for_timeout(3000)

            name_xpath = '//h1[contains(@class, "fontHeadlineLarge")]'
            phone_number_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'

            business = Business()

            # If the name is present, assign it to the business object
            if page.locator(name_xpath).count() > 0:
                business.name = page.locator(name_xpath).inner_text()
            else:
                business.name = ""

            # If the phone number is present, assign it to the business object
            if page.locator(phone_number_xpath).count() > 0:
                business.phone_number = page.locator(phone_number_xpath).inner_text()
            else:
                business.phone_number = ""

            # Add the business object to the business_list
            business_list.business_list.append(business)

        # Save the business_list to an Excel file
        business_list.save_to_excel(nameOfFile)

        # Close the browser
        browser.close()

if __name__ == "__main__":
    # Get user input for search query, number of entries, and filename
    search = input("Enter the text to search: ")
    search_for = search
    number = int(input("Enter the number of entries required: "))
    nameOfFile = input("Please enter the name of the file to store the entries: ")

    main()
