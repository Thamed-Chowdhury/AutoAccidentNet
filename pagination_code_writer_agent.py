def paginate_code_writer(url, newspaper_name, API):
    ## CodeAct Agent ##
    #0
    import re
    import subprocess

    def extract_python_code(text):
        """Extract Python code from a string enclosed in triple backticks."""
        pattern = r'```python\n(.*?)\n```'
        matches = re.findall(pattern, text, re.DOTALL)
        return matches

    def run_python_code_from_string(text, result_container):
        """Extract Python code from string, write to file, and run the file."""
        # Extract Python code
        python_code_list = extract_python_code(text)
        
        if not python_code_list:
            result_container.append("No Python code found in the provided text.")
            return
        
        # Take the first extracted code block (if multiple, this takes the first one)
        python_code = python_code_list[0]
        
        # Write the extracted code to a Python file
        with open('TIR.py', 'w') as f:
            f.write(python_code)
        
        try:
            # Run the Python file in the subprocess, capturing the output
            result = subprocess.run(['python', 'TIR.py'], capture_output=True, text=True, check=True, encoding='utf-8')
            result_container.append(result.stdout.strip())  # Store the output
        except subprocess.CalledProcessError as e:
            result_container.append(f"Error occurred: {e.stderr.strip()}")
        except Exception as e:
            result_container.append(f"An error occurred: {str(e)}")

    def execute_code(text):
        """Execute the code and return the result without threading."""
        result_container = []
        run_python_code_from_string(text, result_container)
        return result_container[0]  # Return the result stored in the container


    ## Initialize LLM ##
    import time
    import google.generativeai as genai
    import os
    os.environ["API_KEY"] = API
    genai.configure(api_key=os.environ["API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")

    ## Download and Parse HTML code of the website + Seperate the div tags
    #1
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from bs4 import BeautifulSoup
    from selenium.webdriver.chrome.options import Options


    # Set up Selenium options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (without opening a browser window)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36")

    # Set up the WebDriver
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Open the website with Selenium
    driver.get(url)

    # Get page source after rendering JavaScript, if any
    page_source = driver.page_source

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(page_source, "html.parser")

    # Find all <div> tags
    div_tags = soup.find_all("div")

    # Save the response as a string
    div_string = ""

    ## Token Count Function ##
    from vertexai.preview import tokenization
    def string2token_count(string):
        model_name = "gemini-1.5-pro"
        tokenizer = tokenization.get_tokenizer_for_model(model_name)
        result = tokenizer.count_tokens(string) 
        token = int(result.total_tokens *1.1)
        return token

    ## Agent that will find the load more button HTML code ##
    def load_more_button_finder(div_string):
        time.sleep(40)
        print("div_string token count: ",string2token_count(div_string))
        prompt = f"""
        Here is a string that contains some div tags of a Bengali newspaper website: 
        {div_string}

        ** Instructions **
        - Study these div tags carefully.
        - This website has numbered pages (e.g., 1, 2, 3) at the bottom or next/previous buttons to navigate between different pages. The buttons may be in bengali or english. 
        - Try to find div tags that contain these number buttons.
        - If you can find such div tags, return the div tags as your response. your response should be in the format: Buttons found. Div tag: [HTML code of the div tags containing the button] 
        - If you cannot find such a button, return: 'button not found'

        """
        try:
            response = model.generate_content(prompt)
        except Exception as e:
            print(f"Error occurred:{e}. Going to sleep for 2 minutes")
            time.sleep(120)
            response = model.generate_content(prompt)
        # print(response.text)
        return response.text

    # Iterate backward through div_tags
    for i in range(len(div_tags) - 1, -1, -1):
        div_string = ""  # Reset the div_string for each iteration
        while i >= 0:
            prev_div_string = div_string
            div_string += f"Div #{i + 1}:\n" + div_tags[i].prettify() + "\n" + "-" * 50 + "\n"

            # Check if the token count exceeds the limit
            if string2token_count(div_string) > 500000:
                div_string = prev_div_string  # Exclude the last added element

                # Send the merged string to the load_more_button_finder function
                is_button = load_more_button_finder(div_string)

                if 'Buttons found' in is_button:
                    print(is_button)
                    break  # Stop processing further if button is found

                # Reset the div_string and continue
                div_string = ""
            else:
                i -= 1

        # Handle the last remaining elements
        if div_string:
            is_button = load_more_button_finder(div_string)
            if 'Buttons found' in is_button:
                print(is_button)
                break
    if "button not found" in is_button:
        is_button = page_source
    

    ## Changing model to pro for better performance in coding##
    os.environ["API_KEY"] = API
    genai.configure(api_key=os.environ["API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-pro")

    ## Next page code writer ##
    def next_page_code_writer(div_string):
        time.sleep(40)
        
        prompt = f"""You are given a string (`div_string`) that contains the HTML code of a Bengali newspaper website's page navigation section. This section includes numbered buttons (e.g., 1, 2, 3) used to navigate between pages. You are also given the homepage url of the website.

    Write a Python function called **`pagination_url_collector`** that performs the following tasks:
    1. Takes an integer input `n` from the user, representing the number of page URLs to retrieve.
    2. Analyzes the `div_string` to find the URL pattern used in the navigation buttons.
    3. Generates and returns a list of URLs for the first `n` pages based on the identified pattern.
    4. If you cannot determine any pattern for the next page urls from the div_string, try to deduce the pattern from its homepage url.
    4. Do not include example usage of the function in your code.
    5. The function will only take one input: 'n'. It will not take the div_string as input. It is your job to notice the pattern from div_string and use it in the function.

    Ensure the function works dynamically to extract the URLs and adapt to the navigation structure provided in the `div_string`. The output should be a Python list containing the URLs of the first `n` pages.
    Homepage url:
    {url}
    ----------------------
    div String:
    -----------------------
    {div_string}
    """
        print("Total Token Count ",string2token_count(prompt))
        try:
            response = model.generate_content(prompt)
        except Exception as e:
            print(f"Error occurred:{e}. Going to sleep for 2 minutes")
            time.sleep(120)
            response = model.generate_content(prompt)
        # print(response.text)
        return response.text

    res = next_page_code_writer(is_button)
    code_string = extract_python_code(res)[0]

    #8
    # Specify the filename
    directory = newspaper_name
    filename = f"{directory}/button_click.py"

    # Create the directory if it does not exist
    os.makedirs(directory, exist_ok=True)

    # Save the string to a .py file
    with open(filename, "w") as file:
        file.write(code_string)

    print(f"Code has been saved to {filename}")

