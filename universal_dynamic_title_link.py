def title_link_dict_func(API_KEY, url, newspaper_name, button_click_times):
    ## Initialize LLM ##
    import time
    import google.generativeai as genai
    import os
    os.environ["API_KEY"] = API_KEY
    genai.configure(api_key=os.environ["API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")

    from vertexai.preview import tokenization
    def string2token_count(string):
        model_name = "gemini-1.5-pro"
        tokenizer = tokenization.get_tokenizer_for_model(model_name)
        result = tokenizer.count_tokens(string) 
        token = int(result.total_tokens *1.1)
        return token

    def llm_a_tag_extract(a_string):
        prompt = f"""
        Here is a string that contains some <a > tags of a Bengali newspaper- {url}:
        {a_string}

        ** Instructions **
        - List me all the news titles and their corresponding links. Do not use any programming. Just list them yourself. 
        - Enclose every news title-link pair in a token of the form <news> [title <seperator> link] <news>
        - Between every title and link, put a token of the form: <seperator>
        - Example:
        <news>দেশে ফিরলেন প্রধান উপদেষ্টা, বিমানবন্দরে ওয়েটিং লাউঞ্জ উদ্বোধন<seperator>https://www.prothomalo.com/bangladesh/qllmc2doql<news>
        <news>ফেনীতে ছুরিকাঘাতে কলেজছাত্র নিহত<seperator>https://www.prothomalo.com/bangladesh/district/17dhwc2gss<news>
        - Make sure there is no duplicate in your response
        - Make sure you only list the news titles and links. There are titles and links to other pages of the newspaper and you should exclude them.
        - Make sure your links are in full url format.
        - Make sure you properly list all the news you encounter. Never truncate your response by 'the rest is given similarly....'
        """
        try:
            response = model.generate_content(prompt)
        except Exception as e:
            print(f"Error occurred:{e}. Going to sleep for 2 minutes")
            time.sleep(120)
            response = model.generate_content(prompt)
        print(response.text)
        return response.text

    #12
    from bs4 import BeautifulSoup

    # Importing Button Click Function and Using it #
    import importlib

    # Define the directory name and function to call
    module_path = f"{newspaper_name}.button_click"  # Adjust module path for Python import

    try:
        # Dynamically import the module
        button_click = importlib.import_module(module_path)
        
        # Run the function
        result = button_click.button_func(button_click_times)
        print(f"Function Result: {result}")

    except ModuleNotFoundError as e:
        print(f"Error: Module '{module_path}' not found. Ensure the directory and file structure is correct.\n{e}")
    except AttributeError as e:
        print(f"Error: Function 'button_func' not found in module '{module_path}'.\n{e}")
    except Exception as e:
        print(f"An error occurred while running the function:\n{e}")

    # Path to your HTML.txt file
    file_path = f'{newspaper_name}/HTML.txt'

    # Read the content of the file
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')


    # 13
    # Find all <a> tags
    a_tags = soup.find_all("a")

    # save the response as a string
    a_string=""
    llm_response=""
    # Print each <a> tag and its contents
    for i, a_tag in enumerate(a_tags, 1):
        txt = f"a #{i}:\n" + a_tag.prettify() + "\n"+"-" * 50+"\n"
        prev_a_string = a_string
        a_string = a_string + txt
        if string2token_count(a_string)>500000:# Send the string to LLM if the character length exceeds 500000
            a_string = prev_a_string
            i=i-1
            print(string2token_count(a_string))
            llm_response = llm_response +  llm_a_tag_extract(a_string) 
            a_string=""
        else:
            if i == len(a_tags):
                a_string = prev_a_string
                print(string2token_count(a_string))
                llm_response = llm_response +  llm_a_tag_extract(a_string) 

    #14 (End of news title and link extraction task)
    import re
    import pandas as pd

    input_string = llm_response
    # Regular expression to match each news title and link
    pattern = r"<news>(.*?)<seperator>(.*?)<news>"

    # Find all matches
    matches = re.findall(pattern, input_string)

    # Convert matches to a DataFrame
    news_df = pd.DataFrame(matches, columns=['News Title', 'News Link'])
    
    # Return the DataFrame
    return news_df
