def collect(API, url_list):
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    import time
    import google.generativeai as genai
    import os
    os.environ["API_KEY"] = API
    genai.configure(api_key=os.environ["API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    def fetch_html_with_selenium(url):
        """
        Fetches the HTML content of a given URL using Selenium.
        
        Parameters:
        url (str): The URL of the website.
        
        Returns:
        str: The HTML content of the website.
        """
        try:
            # Configure Selenium options
            options = Options()
            options.add_argument("--headless")  # Run in headless mode (no UI)
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")

            driver = webdriver.Chrome(options=options)

            # Load the webpage
            driver.get(url)

            # Wait for the page to load completely (optional, adjust as needed)
            driver.implicitly_wait(10)

            # Get the HTML source
            html_content = driver.page_source

            # Close the WebDriver
            driver.quit()

            return html_content
        except Exception as e:
            return f"An error occurred: {e}"
        
    llm_response=""
    for url in url_list:
        html = fetch_html_with_selenium(url)
        prompt = f"""
        Here is a string that contains html code of a Bengali newspaper- {html}

        ** Instructions **
        - List me all the news titles and their corresponding links. Do not use any programming. Just list them yourself. 
        - Enclose every news title-link pair in a token of the form <news> [title <seperator> link] </news>
        - Between every title and link, put a token of the form: <seperator>
        - Example:
        <news>দেশে ফিরলেন প্রধান উপদেষ্টা, বিমানবন্দরে ওয়েটিং লাউঞ্জ উদ্বোধন<seperator>https://www.prothomalo.com/bangladesh/qllmc2doql</news>
        <news>ফেনীতে ছুরিকাঘাতে কলেজছাত্র নিহত<seperator>https://www.prothomalo.com/bangladesh/district/17dhwc2gss</news>
        - Make sure there is no duplicate in your response
        - Make sure you only list the news titles and links. There are titles and links to other pages of the newspaper and you should exclude them.
        - Make sure your links are in full url format.
        - Some urls may be hexadecimal encoded. In those cases, carefully provide the hexadecimal encoded url without any mistake. Example:
            <news>গাংনীতে সড়ক দুর্ঘটনায় ২ কলেজ শিক্ষার্থী নিহত<seperator>https://sharebiz.net/%e0%a6%97%e0%a6%be%e0%a6%82%e0%a6%a8%e0%a7%80%e0%a6%a4%e0%a7%87-%e0%a6%b8%e0%a6%a1%e0%a6%bc%e0%a6%95-%e0%a6%a6%e0%a7%81%e0%a6%b0%e0%a7%8d%e0%a6%98%e0%a6%9f%e0%a6%a8%e0%a6%be%e0%a6%af%e0%a6%bc-2/<news>
        - Make sure you properly list all the news you encounter. Never truncate your response by 'the rest is given similarly....'
        """
        try:
            response = model.generate_content(prompt)
        except Exception as e:
            print(f"Error occurred:{e}. Going to sleep for 2 minutes")
            time.sleep(120)
            response = model.generate_content(prompt)
        print(response.text)
        llm_response = llm_response + response.text

        #14 (End of news title and link extraction task)
    import re
    input_string = llm_response
    # Regular expression to match each news title and link
    pattern = r"<news>(.*?)<seperator>(.*?)</news>"

    # Find all matches
    matches = re.findall(pattern, input_string)

    news_title=[]
    news_link=[]
    for key,value in matches:
        news_title.append(key)
        news_link.append(value)

    import pandas as pd
    news_df = pd.DataFrame({
        "News Title": news_title,
        "News Link": news_link
    })

    news_df.drop_duplicates(inplace=True)
    return news_df