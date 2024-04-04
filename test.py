from selenium import webdriver
from bs4 import BeautifulSoup

get_sentiment = False

URL = "https://www.investopedia.com/dow-jones-today-04042024-8624640"

# Initialize Selenium WebDriver
driver = webdriver.Chrome()  # You may need to download the Chrome driver from https://sites.google.com/a/chromium.org/chromedriver/downloads

# Open the URL
driver.get(URL)

# Get the page source after it's been fully loaded
page_source = driver.page_source

# Close the WebDriver
driver.quit()

# Parse the page source with BeautifulSoup
soup = BeautifulSoup(page_source, "html.parser")

# Find the desired elements
paragraphs = soup.find_all("p")

for paragraph in paragraphs:
    print(paragraph.text)
