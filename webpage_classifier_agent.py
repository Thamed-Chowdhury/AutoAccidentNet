def classifier(API, url):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
    import time
    import os
    import PIL.Image
    import google.generativeai as genai
    genai.configure(api_key=API)

    def fetch_html_with_selenium(url):
        """
        Fetches the HTML content of a given URL using Selenium.
        
        Parameters:
        url (str): The URL of the website.
        
        Returns:
        str: The HTML content of the website.
        """
        driver = webdriver.Chrome()
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
    HTML_code = fetch_html_with_selenium(url)

    from vertexai.preview import tokenization
    def string2token_count(string):
        model_name = "gemini-1.5-pro"
        tokenizer = tokenization.get_tokenizer_for_model(model_name)
        result = tokenizer.count_tokens(string) 
        token = int(result.total_tokens *1.05)
        return token

    # Function to scroll to the end of a webpage
    def scroll_to_end(driver, factor=0.85):
        # Get the total height of the webpage
        total_height = driver.execute_script("return document.body.scrollHeight")

        # Calculate the target scroll position (200px above the bottom)
        scroll_position = total_height* factor

        # Scroll to the calculated position
        driver.execute_script(f"window.scrollTo(0, {scroll_position});")

        # Optional: Add a delay to view the scrolled position
        time.sleep(5)
    def is_infinite_scrolling(url):
        # Initialize the Chrome WebDriver
        driver = webdriver.Chrome()

        try:
            # Open the URL
            driver.get(url)
            driver.maximize_window()
            time.sleep(10)
            # Get the initial HTML code and its length
            html_code_1 = driver.page_source
            length_1 = len(html_code_1)

            driver.execute_script("document.body.style.zoom='50%'")
            # Get the scroll height of the webpage

            scroll_height = driver.execute_script("return document.body.scrollHeight")

            # Scroll down to the bottom of the page
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait for 30 seconds
            time.sleep(30)

            # Get the HTML code again and its length
            html_code_2 = driver.page_source
            length_2 = len(html_code_2)

            # Calculate the percentage increase in the HTML code
            percentage_increase = ((length_2 - length_1) / length_1) * 100

            print("Pecentage_Increase: ", percentage_increase)

            # Return True if the increase is more than 9%, else False
            return percentage_increase > 9

        finally:
            # Close the browser
            driver.quit()

    result_infinite_scroll = is_infinite_scrolling(url)
    print("Is infinite scrolling:", result_infinite_scroll)


    # Function to send the screenshot to Gemini and classify the website type
    def is_button_visible(image_path):
        sample_file = PIL.Image.open(image_path)

        # Choose a Gemini model
        model = genai.GenerativeModel(model_name="gemini-2.0-flash")

        # Prompt for Gemini
        prompt = (
            "In this webpage screenshot, can you see any numbered next page buttons (1,2,3 etc.), next page navigation button or 'load more'/আরও/আরো type of button?"
            "The buttons may be in bangla as the screenshot can be of a bengali or english newspaper website."
            "Your answer should be in this format: <answer> No <answer> or <answer> Yes <answer>"
        )

        response = model.generate_content([prompt, sample_file])
        return response.text.strip()

    # Function to send the screenshot to Gemini and classify the website type
    def classify_webpage(image_path):
        sample_file = PIL.Image.open(image_path)

        # Choose a Gemini model
        model = genai.GenerativeModel(model_name="gemini-2.0-flash")

        # Prompt for Gemini
        prompt1 = (
            "Classify the website based on the screenshot or url or html code as either 'dynamic' or 'pagination'. "
            "A 'dynamic' website uses buttons like 'Load More' to load additional content dynamically without changing the page. "
            "A 'pagination' website has numbered pages (e.g., 1, 2, 3) at the bottom or in the urls to navigate between different pages."
            "Your response should be in the format: <type>dynamic<type> or <type>pagination<type>"
            "----------------------------------"
            f"URL of the website: {url}"
            "----------------------------------"
            f"""HTML code of the website: 
            {HTML_code}
        """
        )

        prompt2 = (
            "Classify the website based on the screenshot as either 'dynamic' or 'pagination'. "
            "A 'dynamic' website uses buttons like 'Load More' to load additional content dynamically without changing the page. "
            "A 'pagination' website has numbered pages (e.g., 1, 2, 3) at the bottom or in the urls to navigate between different pages."
            "Your response should be in the format: <type>dynamic<type> or <type>pagination<type>"
            f"URL of the website: {url}"
        )

        if(string2token_count(prompt1)) < 30000:
            prompt = prompt1
        else:
            prompt = prompt2

        response = model.generate_content([prompt, sample_file])
        return response.text.strip()

    if result_infinite_scroll == True:
        return "The webpage is of type: <type>Infinite Scroll<type>"
    
    scroll_factors = [0.85, 0.65, 0.45, 0.35, 0.20, 0.10, 0.05]

    for factor in scroll_factors:
        time.sleep(7)
        driver = webdriver.Chrome()
        print("Trying factor: ",factor)
        driver.get(url)

        # Maximize the browser window
        driver.maximize_window()
        driver.execute_script("document.body.style.zoom='80%'")
        # Scroll to the end of the webpage
        scroll_to_end(driver, factor)

        # Take a screenshot
        screenshot_path = "webpage_screenshot.png"
        driver.save_screenshot(screenshot_path)
        # Classify webpage type using Gemini
        is_visible = is_button_visible(screenshot_path)
        print(is_visible)
        if 'Yes' in is_visible:
            break

    # Classify webpage type using Gemini
    website_type = classify_webpage(screenshot_path)
    print(f"The website is of type: {website_type}")
    return website_type