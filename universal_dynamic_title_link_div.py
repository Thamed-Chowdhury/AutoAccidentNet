def title_link_dict_func(API_KEY, url, newspaper_name, button_click_times):
    ## Initialize LLM ##
    import time
    import google.generativeai as genai
    import os
    os.environ["API_KEY"] = API_KEY
    genai.configure(api_key=os.environ["API_KEY"])
    model = genai.GenerativeModel("gemini-2.0-flash-exp")

    from vertexai.preview import tokenization
    def string2token_count(string):
        model_name = "gemini-1.5-pro"
        tokenizer = tokenization.get_tokenizer_for_model(model_name)
        result = tokenizer.count_tokens(string) 
        token = int(result.total_tokens *1.1)
        return token

    def llm_div_tag_extract(div_string):
        prompt = f"""
    You are an expert at analyzing HTML code to extract specific information and categorize it. Your task is to perform the following steps:

    1. **Extract Information**:
    From the provided HTML code, extract:
    - The **news title**
    - The **hyperlink** associated with the news. Make sure you provide the full URL.

    2. **Categorize News**:
    Based on the extracted news title, categorize the news into one of the following categories:
    - **check**: If the news title strongly suggests that it is about a road accident.
    - **pass**: If it is certain from the title that the news is NOT about a road accident.
    - **check**: If the title is unclear, or it is not obvious whether the news is about an accident or not.

    3. **Output the Result**:
    Provide the output in the following format for each piece of news:
    <news>NEWS_TITLE<seperator>NEWS_LINK<seperator>CATEGORY</news>
    Replace `NEWS_TITLE`, `NEWS_LINK`, and `CATEGORY` with the actual extracted information and assigned category.

    ### Additional Feature: Handling Relative URLs  
    - If the `href` in the HTML snippet starts with `/`, treat it as a relative URL and prepend the given **base URL** to construct the full URL.  
    - If the `href` already contains a full URL (starting with `http://` or `https://`), use it as is.  

    ---

    ### Example  

    #### Input HTML Snippet:  
    ```html
    <h3 class="headline-title   _1d6-d">
        <a target="_self" aria-label="Title link" class="title-link" href="/bangladesh/district/y31oxxh4cw">
            <span class="tilte-no-link-parent">দাঁড়িয়ে থাকা ট্রাকে মোটরসাইকেলের ধাক্কা, কলেজছাত্রসহ দুজন নিহত</span>
        </a>
    </h3>
    ```
    #### Given Base URL:  
    https://www.prothomalo.com  

    #### Expected Output:  
    ```xml
    <news>দাঁড়িয়ে থাকা ট্রাকে মোটরসাইকেলের ধাক্কা, কলেজছাত্রসহ দুজন নিহত<seperator>https://www.prothomalo.com/bangladesh/district/y31oxxh4cw<seperator>check</news>
    ```

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

    Base URL: {url}
    HTML code snippet:
    -------------------
    {div_string}
    """
        try:
            response = model.generate_content(prompt)
        except Exception as e:
            print(f"Error occurred:{e}. Going to sleep for 2 minutes")
            time.sleep(120)
            response = model.generate_content(prompt)
        try:
            print(response.text)
            return response.text
        except Exception as e:
            print(f"Error occurred while processing the div tag in LLM. Exception: {e}")
            return "Error occurred. Ignore the current page."
        

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
    # Find all <div> tags
    div_tags = soup.find_all("div")

    # save the response as a string
    div_string=""
    llm_response=""

    for i, div_tag in enumerate(div_tags, 1):
        txt = f"a #{i}:\n" + div_tag.prettify() + "\n"+"-" * 50+"\n"
        prev_div_string = div_string
        div_string = div_string + txt
        if string2token_count(div_string)>100000:# Send the string to LLM if the character length exceeds 500000
            div_string = prev_div_string
            i=i-1
            print(string2token_count(div_string))
            llm_response = llm_response +  llm_div_tag_extract(div_string) 
            div_string=""
        else:
            if i == len(div_tags):
                div_string = prev_div_string
                print(string2token_count(div_string))
                llm_response = llm_response +  llm_div_tag_extract(div_string) 

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
    print(f"Number of news in original dataframe = {len(news_df)}")
    news_df = news_df[news_df["Checking condition"] == "check"]
    news_df.reset_index(inplace = True, drop = True)
    print(f"Number of news in fast filtered dataframe = {len(news_df)}")
    return news_df