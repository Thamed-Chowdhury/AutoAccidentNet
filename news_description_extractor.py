import requests
from bs4 import BeautifulSoup

def para_extract_func(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the main article div.
        article_div = soup.find('div', class_='pb-20 clearfix')  # Keep this specific to the target site

        if article_div:
            article_paragraphs = article_div.find_all('p')
            article_text = '\n'.join([p.get_text(strip=True) for p in article_paragraphs if p.get_text(strip=True)])
            return article_text
        else:
            return None  # Or raise an exception, return an empty string, etc.

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None



# Example Usage (you can remove this if you just want the function definition):
if __name__ == "__main__":
    test_url = "https://www.thedailystar.net/news/bangladesh/accidents-fires/news/ctg-port-authority-frames-sop-avert-fire-incidents-3753101"
    extracted_text = para_extract_func(test_url)

    if extracted_text:
        print(extracted_text)
    else:
        print("Failed to extract article content.")

