'''
Stock Sentiment Evaluator

By Jason Pelkey

Credit to ChatGPT for help with dynamic Web Scraping and advice on some errors with Apis
Thanks to RealPython for Web their Scraping Tutorial https://realpython.com/python-web-scraping-practical-introduction/
Thanks to Geeks for Geeks for yet another Web Scraping Tutorial https://www.geeksforgeeks.org/python-web-scraping-tutorial/
Thanks to Mr. Winikka for helping me get over my fear of APIS
Thanks to Rapid API for their easy access to free APIS and easy to use software https://rapidapi.com/hub

Given a topic, the Google News Search API will find the top 100 search results of that topic.
We then take the top 10 (for relevancy's sake) and extract the body text from it.
Using a Sentiment API calculator, we then establish whether the content was generally positive or negative about the topic
After all links have been scanned, the program will give a stock assessment of whether to hold stocks, sell stocks, or buy stocks

NOTE: Be careful using the program, I only get 25 google searches per month!
'''

import requests
from selenium import webdriver
from bs4 import BeautifulSoup

#URL = "https://www.cnbc.com/2024/04/03/stock-market-today-live-updates.html"


# THANKS TO ChatGPT For the alternate approach
def get_soup_from_url(URL : str) -> BeautifulSoup:
    '''
    Gets the soup/html from a given URL

    Args:
        str URL: The url to get the soup from

    Returns:
        BeautifulSoup: The html of the URL
    '''

    # Initialize Selenium WebDriver
    driver = webdriver.Chrome()  # You may need to download the Chrome driver from https://sites.google.com/a/chromium.org/chromedriver/downloads

    # Open the URL
    driver.get(URL)

    # Get the page source after it's been fully loaded
    page_source = driver.page_source

    # Close the WebDriver
    driver.quit()

    soup = BeautifulSoup(page_source, "html.parser")

    return soup

def find_text_body(soup : BeautifulSoup) -> BeautifulSoup:
    '''
    Searches for known main body sections of popular websites to optimize the 
    information gathered

    Args:
        BeautifulSoup soup: The page content gathered from a given URL

    Returns:
        BeautifulSoup or None: A trimmed down section of the website that contains only the important
                               information on the website (If the website had a known main body section)
                               If no body section was found, it will return None
    '''

    potential_ids = ["js-article__body",]
    potential_classes = ["FeaturedContent-articleBody"]
    text_body = None

    for i in range(len(potential_ids)):
        text_body = soup.find(id=potential_ids[i])

        if (text_body != None):
            break

    # If no body was found yet, try looking for classes instead
    if (text_body == None):
        for i in range(len(potential_classes)):
            text_body = soup.find(class_=potential_classes[i])

            if (text_body != None):
                break
    

    return text_body

def extract_text(original_soup : BeautifulSoup, text_body : BeautifulSoup) -> str:
    '''
    Recieves the text from the html website body and arranges them into paragraphs
    It ignores any text that is 70 characters or below in length
    
    Args:
        BeautifulSoup soup: The html body to extract text from

    Returns:
        str[]: An array of every extracted paragraph from the html body
    '''
    # Extract the paragraphs either through the entire website or
    # from the text body found
    if (text_body == None):
        print("No matches found...")
        paragraphs = original_soup.find_all("p")
    else:
        paragraphs = text_body.find_all("p")

    # Add the header to the start of the paragraphs list
    #paragraphs.insert(0, header.text)

    # Filter out any sentences less than 70 characters long
    filtered_paragraphs = [p.text for p in paragraphs if len(p.text) > 70]
    blacklisted_paragraphs = [p.text for p in paragraphs if len(p.text) <= 70]

    # Extracts the header from the article as well
    header = original_soup.find("h1")

    # Only add if it exists
    if (header != None):

        # Extract the text
        header = header.text

        # Add the header to the list of paragraphs
        filtered_paragraphs.insert(0, header)

    print("Num paragrapghs found:", len(filtered_paragraphs))
    print("Num blacklisted paragraphs:", len(blacklisted_paragraphs))
    print()

    return filtered_paragraphs

# Thanks to https://www.geeksforgeeks.org/python-remove-substring-list-from-string/
def remove_word_from_text(text : str, word : str) -> str:
    return text.replace(' ' + word + ' ', ' ')

def clean_text(text : str) -> str:

    clean_text = text.lower()

    blacklisted_words = ["i", "the", "an", "and", "be", "so", "or", "at", "to", "a", "in", "its", "for", "is"]

    # Remove all blacklisted words from the text
    for word in blacklisted_words:
        clean_text = remove_word_from_text(clean_text, word)

    return clean_text

def get_total_sentiment(text : str, get_sentiment = False) -> dict:

    '''
    Calculates the sentiment value of a given text

    Args:
        str text: The text to get the sentiment value from
        bool get_sentiment : Determines whether to actually get the sentiment data from the given text
                             or just use an example response for testing purposes

    Returns:
        dict: Contains the sentiment value of the given text
            Example of dictionary tree:
                {'outputs': {'neutral': 0.8971490263938904, 'negative': 0.7393637895584106, 'positive': 0.20099657773971558}, 'truncated': False}
    '''

    # Uses API from https://rapidapi.com/knowledgator-knowledgator-default/api/comprehend-it/
    # Calculates the overall sentiment of a given article
    # NOTE: I ONLY GET 300 REQUESTS PLEASE DON'T WASTE IT (262/300)
    url = "https://comprehend-it.p.rapidapi.com/predictions/ml-zero-nli-model"

    payload = {
        "labels": ["positive", "negative", "neutral"],
        "text": text
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "d0911aed33mshfad6c36de6f8832p1311c4jsn34e12f8dfef9",
        "X-RapidAPI-Host": "comprehend-it.p.rapidapi.com"
    }

    # Make get_sentiment true if we want to use a real data set - otherwise, use the originally generated one
    print("Use True Data:", get_sentiment)
    if (get_sentiment):

        try:
            response = requests.post(url, json=payload, headers=headers)
            #print(response.json())
        except:
            print("<!> Sentiment grab failed, returning default values...")
            return {'neutral': 0.0, 'negative': 0.0, 'positive': 0.0}
            return
        
        return response.json()
    else:
        response = {'outputs': {'neutral': 0.8971490263938904, 'negative': 0.7393637895584106, 'positive': 0.20099657773971558}, 'truncated': False}
        # Another response that is positive - {'outputs': {'positive': 0.9282442927360535, 'neutral': 0.9151404500007629, 'negative': 0.1627216339111328}, 'truncated': False}
        return response

def assess_sentiment(neutral_sent : float, negative_sent : float, positive_sent : float) -> str:
    net_sentiment = positive_sent - negative_sent

    if abs(net_sentiment) < 0.3:
        return "Hold Stocks"
    elif net_sentiment > 0:
        return "Buy Stocks!"
    else:
        return "Sell Stocks!"

def get_sentiment_from_url(URL : str, get_sentiment : bool) -> dict:
    '''
    Given a URL, it will grab information from that website and calculate its sentiment

    Args:
        str URL: The url to get the sentiment from
        bool get_sentiment: Determines whether to return the sample sentiment
                            or to use the API to calculate it

    Returns:
        dict: A dictionary containing the sentiment of the website
              {'positive' : float, 'neutral' : float, 'negative' : float}
    '''

    # The URL to test
    #URL = "https://www.aol.com/news/stock-market-today-asian-shares-072407487.html"

    soup = get_soup_from_url(URL)

    # Get the section of text from the website to begin extracting
    html_body = find_text_body(soup)

    # Get an array of paragraphs from the html body
    extracted_text = extract_text(soup, html_body)

    # If we think that the scrape failed, return default values in order to not interfere with the test
    if (len(extracted_text) <= 3):
        print("<?> Source is likely using bot protection, returning default values...")
        return {'neutral': 0.0, 'negative': 0.0, 'positive': 0.0}

    # Create a variable to store all the paragraphs into a single variable
    full_text = ""

    # Add each paragraph to the full_text variable
    # At the same time, clean each paragraph before 
    #   it goes in to reduce strain on the sentiment dictionary
    for paragraph in extracted_text:
        full_text += '\n' + clean_text(paragraph)

    # Calculate the total sentiment from the cleaned data
    sentiment_dict = get_total_sentiment(full_text, get_sentiment)

    print("Full Text: " + full_text)
    print("Sentiment dictionary: " + str(sentiment_dict))

    outputs = sentiment_dict['outputs']

    return outputs

# (22/25) uses left!!!
def get_news_website_urls(topic : str, use_test_data : bool) -> dict:

    if (use_test_data):
        url = "https://google-news13.p.rapidapi.com/search"

        querystring = {"keyword":topic,"lr":"en-US"}

        headers = {
            "X-RapidAPI-Key": "d0911aed33mshfad6c36de6f8832p1311c4jsn34e12f8dfef9",
            "X-RapidAPI-Host": "google-news13.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)

        print(response.json())
    else:
        return ['https://www.cnbc.com/2024/04/03/stock-market-today-live-updates.html', 
                'https://www.marketwatch.com/livecoverage/stock-market-today-dow-futures-rise-as-bond-yields-steady', 
                'https://www.wsj.com/livecoverage/stock-market-today-dow-jones-04-04-2024', 
                'https://finance.yahoo.com/news/live/stock-market-today-tech-leads-market-bounce-as-powell-soothes-rate-cut-nerves-133121789.html', 
                'https://www.investors.com/market-trend/stock-market-today/dow-jones-sp500-nasdaq-nvidia-nvda-stock-google-googl-meta/', 
                'https://www.barrons.com/livecoverage/stock-market-today-040424', 
                'https://www.investopedia.com/dow-jones-today-04042024-8624640', 
                'https://www.bloomberg.com/news/articles/2024-04-03/stock-market-today-dow-s-p-live-updates', 
                'https://markets.businessinsider.com/news/stocks/stock-market-today-weekly-jobless-claims-fed-rate-cut-plan-2024-4', 
                'https://www.investors.com/market-trend/stock-market-today/dow-jones-sp500-nasdaq-nvidia-nvda-stock-tesla-tsla/']

    response_dict = response.json()

    response_results = response_dict['items']

    urls = []
    for i in range(10):
        response_result = response_results[i]
        url = response_result["newsUrl"]
        urls.append(url)

    return urls

def filter_out_blacklisted_urls(URLs : str) -> str:

    # Initialize the list of blacklisted websites
    blacklisted_websites = ["wsj.com"] #, "marketwatch.com", "bloomberg.com", "investors.com"]

    cleaned_url_list = []

    for i in range(len(URLs)):

        url = URLs[i]

        # Remove the opener portion
        url = url.replace('https://www.', '').replace('http://www.','')

        # Extract the name.com from the url
        url = url.split('/')[0]

        # Add the url if it is not in the blacklist
        if url not in blacklisted_websites:
            cleaned_url_list.append(URLs[i])

    return cleaned_url_list

def get_stock_evaluation_from_topic(topic : str, use_api_data : bool) -> str:

    # Get a list of URLS for a relevant stock
    urls = get_news_website_urls(topic, use_api_data)
    print(urls)

    # Remove all URLS that have been found to be incompatible with the webscraper
    cleaned_urls = filter_out_blacklisted_urls(urls)

    print("cleaned urls:", cleaned_urls)

    total_positive_sentiment = 0
    total_neutral_sentiment = 0
    total_negative_sentiment = 0

    print("Number of URLS tested:", len(cleaned_urls))

    for URL in cleaned_urls:

        # Determines whether to actually use the Sentiment API or not
        get_sentiment = use_api_data

        print("Opening URL:", URL)
        print("Please wait, it will take a moment...")
        print()

        sentiment_output = get_sentiment_from_url(URL, get_sentiment)

        positive_sentiment = sentiment_output['positive']
        neutral_sentiment = sentiment_output['neutral']
        negative_sentiment = sentiment_output['negative']

        total_positive_sentiment += positive_sentiment
        total_neutral_sentiment += neutral_sentiment
        total_negative_sentiment += negative_sentiment
        
        print()
        print("Article's Stock Assessment:", assess_sentiment(neutral_sentiment, negative_sentiment, positive_sentiment))
        print("Stock Assessment So Far:", assess_sentiment(total_neutral_sentiment, total_negative_sentiment, total_positive_sentiment))
        print()

    return "Final Stock Assessment: " + assess_sentiment(total_neutral_sentiment, total_negative_sentiment, total_positive_sentiment)

def main():

    print(get_stock_evaluation_from_topic("dow jones", False))

    # FOR MR. WINIKKA - Comment the above function and uncomment the below one
    # This uses the APIs instead of default data - I have limited uses, so keep that in mind

    # Add your topic here (preferrably stock related)
    topic = ""

    # UNCOMMENT THIS
    #print(get_stock_evaluation_from_topic(topic, True))
    

main()