import requests
from bs4 import BeautifulSoup

get_sentiment = False

URL = "https://www.cnbc.com/2024/04/01/stock-market-today-live-updates.html"
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")

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
        paragraphs = soup.find_all("p")
    else:
        paragraphs = text_body.find_all("p")

    # Extracts the header from the article as well
    header = soup.find("h1")

    # Add the header to the start of the paragraphs list
    #paragraphs.insert(0, header.text)

    # Filter out any sentences less than 70 characters long
    filtered_paragraphs = [p.text for p in paragraphs if len(p.text) > 70]
    blacklisted_paragraphs = [p.text for p in paragraphs if len(p.text) <= 70]

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
    # NOTE: I ONLY GET 300 REQUESTS PLEASE DON'T WASTE IT (299/300)
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
    if (get_sentiment):
        response = requests.post(url, json=payload, headers=headers)
        print(response.json())
        return response.json()
    else:
        response = {'outputs': {'neutral': 0.8971490263938904, 'negative': 0.7393637895584106, 'positive': 0.20099657773971558}, 'truncated': False}
        return response

def assess_sentiment(neutral_sent : float, negative_sent : float, positive_sent : float) -> str:
    net_sentiment = positive_sent - negative_sent

    if abs(net_sentiment) < 0.3:
        return "Hold Stocks"
    elif net_sentiment > 0:
        return "Buy Stocks!"
    else:
        return "Sell Stocks!"

# Get the section of text from the website to begin extracting
html_body = find_text_body(soup)

# Get an array of paragraphs from the html body
extracted_text = extract_text(soup, html_body)

# Create a variable to store all the paragraphs into a single variable
full_text = ""

# Add each paragraph to the full_text variable
# At the same time, clean each paragraph before 
#   it goes in to reduce strain on the sentiment dictionary
for paragraph in extracted_text:
    full_text += '\n' + clean_text(paragraph)

# Calculate the total sentiment from the cleaned data
sentiment_dict = get_total_sentiment(full_text, False)

outputs = sentiment_dict['outputs']

positive_sentiment = outputs['positive']
neutral_sentiment = outputs['neutral']
negative_sentiment = outputs['negative']

print("Full Text", full_text)
print()
print("Total Sentiment", sentiment_dict)
print()
print("Stock Assessment:", assess_sentiment(neutral_sentiment, negative_sentiment, positive_sentiment))