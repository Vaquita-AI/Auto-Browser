from combinecookies import combine_cookies
import random
import json
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from concurrent.futures import ThreadPoolExecutor

# Number of searches to perform
num_searches = 5

# Function to save cookies to a file
def save_cookies(driver, filename, directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    filepath = os.path.join(directory, filename)
    with open(filepath, 'w') as file:
        json.dump(driver.get_cookies(), file)
    print(f"Cookies saved to {filepath}")


# Function to wait for the page to be fully loaded
def wait_for_page_load(driver, timeout=60):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
    except TimeoutException:
        print(f"Page did not load within {timeout} seconds")
        return False
    return True


# Function to read lines from a file and return them as a list
def read_lines_from_file(filepath):
    with open(filepath, 'r') as file:
        return [line.strip() for line in file.readlines()]


# Path to your Chrome extension (replace with your actual extension path)
extension_paths = ['Accept all cookies.crx', "Random User-Agent (Switcher).crx"]

# Set up Chrome options to load the extension
chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument("--headless")  # Run in headless mode
for extension_path in extension_paths:
    chrome_options.add_extension(extension_path)

# Disable image loading
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)

# Directory to save cookies
cookie_directory = "cookies"

# List of websites to visit
websites = [
    "https://duckduckgo.com",
]

# Read adjectives and items from files
adjectives = read_lines_from_file('adjectives.txt')
items = read_lines_from_file('items.txt')


# Function to perform a search and click the first result
def perform_search_and_click(search_query):
    try:
        # Initialize a new browser instance for each search
        driver = webdriver.Chrome(options=chrome_options)

        # Visit DuckDuckGo
        driver.get("https://duckduckgo.com")
        print(f"Visiting DuckDuckGo for search: {search_query}")

        # Wait for the page to be fully loaded
        wait_for_page_load(driver)

        # Perform the search on DuckDuckGo
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'q'))
        )
        search_box.send_keys(search_query)
        search_box.submit()

        # Wait for the search results to load
        wait_for_page_load(driver)
        print(f"Search results for '{search_query}' loaded")

        # Click on the first link of the search results
        first_result = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-testid="result-title-a"]'))
        )

        # Retry clicking the first result if a stale element reference exception occurs
        retries = 3
        while retries > 0:
            try:
                first_result.click()
                break
            except StaleElementReferenceException:
                retries -= 1
                first_result = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-testid="result-title-a"]'))
                )

        print("Clicked on the first search result")

        # Wait for the clicked page to be fully loaded with a 5-second timeout
        if not wait_for_page_load(driver, timeout=5):
            print(f"Terminating browser session for '{search_query}' due to timeout")
            driver.quit()
            return

        print(f"Page for '{search_query}' fully loaded")

        # Save cookies for this search
        save_cookies(driver, f"{search_query.replace(' ', '_')}_cookies.json", cookie_directory)
        # time.sleep(333) # pause if you want to see changes
        # Close the browser instance
        driver.quit()

    except Exception as e:
        print(f"An error occurred during the search for '{search_query}': {e}")




# Perform the specified num_searches in parallel
for i in range (0,99):
    with ThreadPoolExecutor(max_workers=num_searches) as executor:
        # Create a list of search queries
        search_queries = [f"{random.choice(adjectives)} {random.choice(items)}" for _ in range(num_searches)]

        # Execute the searches in parallel
        futures = [executor.submit(perform_search_and_click, query) for query in search_queries]

        # Wait for all futures to complete
        for future in futures:
            future.result()

#combine_cookies(cookie_directory, words_to_exclude=["google", "amazon"])