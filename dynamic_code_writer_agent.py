def dynamic_code_writer(API, url, newspaper_name):
    # CodeAct Agent
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

    # Javascript button click code writer
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

    ## Agent that will find the load more button HTML code ##
    def load_more_button_finder(div_string):
        print("div_string len: ",len(div_string))
        prompt = f"""
        Here is a string that contains some div tags of a Bengali newspaper website: 
        {div_string}

        ** Instructions **
        - Study these div tags carefully. 
        - Try to find a div tag that contains a button that will load more news when clicked upon.
        - The button may be named many things. Example: load-more, load-more-contents, আরও etc.
        - If you can find such a div tag, return the div tag as your response. your response should be in the format: Button found. Div tag: [HTML code of the div tag containing the button] 
        - If you cannot find such a button, return: 'Button not found'

        """
        try:
            response = model.generate_content(prompt)
        except Exception as e:
            print(f"Error occurred:{e}. Going to sleep for 2 minutes")
            time.sleep(120)
            response = model.generate_content(prompt)
        return response.text

    from vertexai.preview import tokenization
    def string2token_count(string):
        model_name = "gemini-1.5-pro"
        tokenizer = tokenization.get_tokenizer_for_model(model_name)
        result = tokenizer.count_tokens(string) 
        token = int(result.total_tokens *1.1)
        return token

    model = genai.GenerativeModel("gemini-1.5-flash")

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

                if 'Button found' in is_button:
                    print(is_button)
                    break  # Stop processing further if button is found

                # Reset the div_string and continue
                div_string = ""
            else:
                i -= 1

        # Handle the last remaining elements
        if div_string:
            is_button = load_more_button_finder(div_string)
            if 'Button found' in is_button:
                print(is_button)
                break

    def button_click_code_writer(response_string):
        prompt = f"""
        Here is a string that contains a div tag of the newspaper website: {url}
        {response_string}

        ** Instructions **
        1) This div tag contains a button and upon clicking on it, more news should load. Write a code in python using selenium that will do the following tasks:
        2) The chromedriver does not require a path now. Do not provide any Path.
        3) First load the page in selenium in full screen. Then add a waiting time of 60 seconds so that all the contents load properly.
        4) Find scroll height of the webpage and then scroll down to (0.85*scroll_height) of the webpage. 
        5) Click on this button.
        6) Use javascript to click the button. After every click wait for 30 seconds so that new contents can load properly.
        7) Don't use span ID number to locate the button as it may change after clicking once. 
        8) Make a variable named click_times. Store the value 3 in it. It means you have to click the load more button 3 times and redo all the previous steps from 4 to 6.
        9) After successfully clicking 3 times, download the entire HTML code of the webpage and save the HTML code in a txt file named: {newspaper_name}/HTML.txt
        10) Don't use headless browsing and don't close the browser when done
        11) The entire code should be in a function named button_func(click_times=3). This will take the click_times as input.
        12) Don't use example usage inside code snippet
        """
        try:
            response = model.generate_content(prompt)
        except:
            print("Error occurred. Going to sleep for 2 minutes")
            time.sleep(120)
            response = model.generate_content(prompt)
        return response.text

    #6
    model = genai.GenerativeModel("gemini-1.5-pro")
    res= button_click_code_writer(is_button)
    print(res)

    #7
    code_string = extract_python_code(res)[0]

    # Specify the filename
    directory = newspaper_name
    filename = f"{directory}/button_click.py"

    # Create the directory if it does not exist
    os.makedirs(directory, exist_ok=True)

    # Save the string to a .py file
    with open(filename, "w") as file:
        file.write(code_string)

    print(f"Code has been saved to {filename}")

    # Trial Run 1 #
    import importlib
    import io
    import sys
    from contextlib import redirect_stdout, redirect_stderr

    # Dynamically define module path
    module_path = f"{newspaper_name}.button_click"  # Adjusted for Python module path format

    # Ensure the newspaper directory is in the Python path
    sys.path.append(".")  # Add the current directory to sys.path if needed

    # Import the module dynamically
    try:
        button_click = importlib.import_module(module_path)
    except ModuleNotFoundError as e:
        print(f"ModuleNotFoundError: {e}")
        print("Ensure the directory and file structure is correct.")
        exit(1)

    # Create StringIO objects to capture output and errors
    output_capture = io.StringIO()
    error_capture = io.StringIO()

    try:
        # Redirect stdout and stderr to capture outputs and errors
        with redirect_stdout(output_capture), redirect_stderr(error_capture):
            # Call the function
            result = button_click.button_func(2)

        # Combine captured outputs
        code_output = output_capture.getvalue()
        if result is not None:  # Include the return value if it exists
            code_output += f"\nFunction Result: {result}"

    except Exception as e:
        # Capture the exception as well as any error output
        code_output = error_capture.getvalue()
        code_output += f"\nError: {str(e)}"

    # Print or save the captured output
    print(code_output)


    # Debugging if Error in 1st Trial #
    if 'Error' in code_output:
        print('The 1st button_click code gives error. Debugging...')
        prompt = f"""
    USER:
    Here is a string that contains a div tag of the newspaper website: {url}
    {is_button}

    ** Instructions **
    1) This div tag contains a button and upon clicking on it, more news should load. Write a code in python using selenium that will do the following tasks:
    2) The chromedriver does not require a path now. Do not provide any Path.
    3) First load the page in selenium. Then add a waiting time of 30 seconds so that all the contents load properly.
    4) Scroll to the bottom of the webpage. 
    5) Click on this button.
    6) Use javascript to click the button. After every click wait for 60 seconds so that new contents can load properly.
    7) Don't use span ID number to locate the button as it may change after clicking once.
    8) Try to avoid the visible button text as the locator as other clickable elements on the page may contain the same text. 
    8) Make a variable named click_times. Store the value 3 in it. It means you have to click the load more button 3 times and redo all the previous steps from 4 to 6.
    9) After successfully clicking 3 times, download the entire HTML code of the webpage and save the HTML code in a txt file named: HTML.txt
    10) Don't use headless browsing and don't close the browser when done
    11) The entire code should be in a function named button_func(click_times=3). This will take the click_times as input.
    12) Don't use example usage inside code snippet

    AGENT:
    {res}

    CODE OUTPUT:
    {code_output}


    USER:
    Your job now is to debug and fix the code.
    ** Instructions **
    - Use text based locator of the button instead of Xpath if you used it.
    - Provide the full corrected code.
            """

        try:
            response = model.generate_content(prompt)
        except Exception as e:
            # Capture and print the exception
            print(f"Error occurred: {e}. Going to sleep for 2 minutes")
            time.sleep(120)
            response = model.generate_content(prompt)
        ##########################
        #### DEBUGGING ##########
        print(response.text)

        code_string = extract_python_code(response.text)[0]
        #8
        # Specify the filename
        filename = f"{newspaper_name}/button_click.py"

        # Save the string to a .py file
        with open(filename, "w") as file:
            file.write(code_string)

        print(f"Code has been saved to {filename}")

        #Trial Run-2 after debugging
        import importlib
        import io
        import sys
        from contextlib import redirect_stdout, redirect_stderr

        # Dynamically define module path
        module_path = f"{newspaper_name}.button_click"  # Adjusted for Python module path format

        # Ensure the newspaper directory is in the Python path
        sys.path.append(".")  # Add the current directory to sys.path if needed

        # Import the module dynamically
        try:
            button_click = importlib.import_module(module_path)
        except ModuleNotFoundError as e:
            print(f"ModuleNotFoundError: {e}")
            print("Ensure the directory and file structure is correct.")
            exit(1)

        # Create StringIO objects to capture output and errors
        output_capture = io.StringIO()
        error_capture = io.StringIO()

        try:
            # Redirect stdout and stderr to capture outputs and errors
            with redirect_stdout(output_capture), redirect_stderr(error_capture):
                # Call the function
                result = button_click.button_func(2)

            # Combine captured outputs
            code_output = output_capture.getvalue()
            if result is not None:  # Include the return value if it exists
                code_output += f"\nFunction Result: {result}"

        except Exception as e:
            # Capture the exception as well as any error output
            code_output = error_capture.getvalue()
            code_output += f"\nError: {str(e)}"

        # Print or save the captured output
        print(code_output)