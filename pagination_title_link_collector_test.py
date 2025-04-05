def collect(API, url_list):
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    import time
    import google.generativeai as genai
    import os
    os.environ["API_KEY"] = 'AIzaSyBFD1MUkUXh5CliWDBb68QAooshP2XCEyE'
    genai.configure(api_key=os.environ["API_KEY"])
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
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
    for i in range(len(url_list)):
        print(f"Processing URL no: {i+1}, URL: {url_list[i]}")
        html = fetch_html_with_selenium(url_list[i])
        prompt = prompt = f"""
    You are an expert at analyzing HTML code to extract specific information and categorize it. Your task is to perform the following steps:

    1. **Extract Information**:
    From the provided HTML code, extract:
    - The **news title**
    - The **hyperlink** associated with the news

    The **news title** can be found within the `<span class="tilte-no-link-parent">` tag or a similar structure. The **hyperlink** is present in the `href` attribute of the `<a>` tag associated with the title.

    2. **Categorize News**:
    Based on the extracted news title, categorize the news into one of the following categories:
    - **check**: If the news title strongly suggests that it is about a road accident.
    - **pass**: If it is certain from the title that the news is NOT about a road accident.
    - **check**: If the title is unclear, or it is not obvious whether the news is about an accident or not.

    3. **Output the Result**:
    Provide the output in the following format for each piece of news:
    <news>NEWS_TITLE<seperator>NEWS_LINK<seperator>CATEGORY</news>
    Replace `NEWS_TITLE`, `NEWS_LINK`, and `CATEGORY` with the actual extracted information and assigned category.

    ### Example
    If the HTML snippet is:
    <h3 class="headline-title   _1d6-d"><a target="_self" aria-label="Title link" class="title-link" href="https://www.prothomalo.com/bangladesh/district/y31oxxh4cw"><span class="tilte-no-link-parent">দাঁড়িয়ে থাকা ট্রাকে মোটরসাইকেলের ধাক্কা, কলেজছাত্রসহ দুজন নিহত</span></a></h3>

    Your output should look like:
    <news>দাঁড়িয়ে থাকা ট্রাকে মোটরসাইকেলের ধাক্কা, কলেজছাত্রসহ দুজন নিহত<seperator>https://www.prothomalo.com/bangladesh/district/y31oxxh4cw<seperator>check</news>

    If the HTML snippet is:
    <h3 class="headline-title   _1d6-d"><a target="_self" aria-label="Title link" class="title-link" href="https://www.prothomalo.com/bangladesh/national/ab12345"><span class="tilte-no-link-parent">নির্বাচনের প্রস্তুতি নিয়ে প্রধানমন্ত্রীর সভা</span></a></h3>

    Your output should look like:
    <news>নির্বাচনের প্রস্তুতি নিয়ে প্রধানমন্ত্রীর সভা<seperator>https://www.prothomalo.com/bangladesh/national/ab12345<seperator>pass</news>

    ### Input for the Task
    The input will be an HTML code snippet containing multiple news items. Process each item individually and provide the result for each. Ensure the output format strictly matches the example.


    HTML code snippet:
    -------------------
    {html}
    """

        try:
            response = model.generate_content(prompt)
        except Exception as e:
            print(f"Error occurred:{e}. Going to sleep for 2 minutes")
            time.sleep(120)
            response = model.generate_content(prompt)
        print(response.text)
        llm_response = llm_response + response.text
    import re

    def extract_news_details(llm_response):
        # Regular expression to extract news title, link, and checking condition
        pattern = r"<news>(.*?)<seperator>(.*?)<seperator>(.*?)</news>"
        
        # Extract matches
        matches = re.findall(pattern, llm_response)
        
        # Create separate lists for news title, link, and checking condition
        news_titles = [match[0] for match in matches]
        news_links = [match[1] for match in matches]
        checking_conditions = [match[2] for match in matches]
        
        return news_titles, news_links, checking_conditions
    # Get the lists
    news_titles, news_links, checking_conditions = extract_news_details(llm_response)

    # Print the results
    print("News Titles:", news_titles)
    print("News Links:", news_links)
    print("Checking Conditions:", checking_conditions)

    import pandas as pd
    news_df = pd.DataFrame({
        "News Title": news_titles,
        "News Link": news_links,
        "Checking condition": checking_conditions
    })

    news_df.drop_duplicates(inplace=True)
    news_df = news_df[news_df["Checking condition"] == "check"]
    news_df.reset_index(inplace = True, drop = True)
    return news_df