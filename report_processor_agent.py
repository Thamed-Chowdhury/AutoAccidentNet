def report_processor(merged_df, Gemini_API_Keys):
    import pandas as pd
    import time
    import os
    from google.generativeai.types import HarmCategory, HarmBlockThreshold

    def page_content_to_string(url):
        from bs4 import BeautifulSoup
        import requests

        # Define the User-Agent header to mimic a browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            # Fetch the webpage with headers
            response = requests.get(url, headers=headers, timeout=10)  # Add a timeout for requests

            # Check if the request was successful
            response.raise_for_status()

            # Parse the webpage content
            soup = BeautifulSoup(response.content, "html.parser")

            # Extract all the text
            page_content = soup.get_text(separator="\n")

            # Clean up unnecessary new lines
            cleaned_content = "\n".join(line.strip() for line in page_content.split("\n") if line.strip())

            return cleaned_content

        except requests.exceptions.RequestException as e:
            # Handle request errors (e.g., network issues, 404, etc.)
            print(f"Error fetching {url}: {e}")
            return f"Error fetching {url}: {e}"
        except Exception as e:
            # Handle other errors
            print(f"An unexpected error occurred: {e}")
            return f"An unexpected error occurred: {e}"

    # def llm_initialize(API,prompt):
    #     #2
    #     ## Initialize LLM ##
    #     import time
    #     import google.generativeai as genai
    #     import os
    #     os.environ["API_KEY"] = API
    #     genai.configure(api_key=os.environ["API_KEY"])
    #     model = genai.GenerativeModel("gemini-exp-1206")
    #     response = model.generate_content(prompt)
    #     return response.text

    #3
    def report_processing_agent(string, API):
        #2
        ## Initialize LLM ##
        import time
        import google.generativeai as genai
        import os
        os.environ["API_KEY"] = API
        genai.configure(api_key=os.environ["API_KEY"])
        model = genai.GenerativeModel("gemini-2.0-flash")
        

        prompt = f"""
        Here is a string that contains a news article: 
    {string}

    ---

    **Instructions**

    1. **General Guidelines:**
    - Read the article carefully and determine if it is related to **road vehicle accidents.**
    - News articles may contain unrelated information; focus only on the actual news content.
    - Always respond in **English.**

    2. **Classification Rules:**
    - If the article is about **non-road incidents** such as drowning, fire, people colliding or fighting, natural disasters, or non-road-related events, classify it as **General.**
    - If the article mentions **summarized data, statistics, or aggregated information** about multiple accidents over time or across regions (e.g., "592 killed in a month on Dhaka-Chittagong highways"), classify it as **General.**
    - If the article describes **more than two accident incidents**, classify it as **General.**
    - Only classify as **Specific** if the article provides **detailed information about a single road vehicle accident incident.**

    3. **Verification Step:**
    - Be cautious about summarized data or reports that cover multiple incidents across a large area or over a period of time (e.g., "Monthly accident reports," "Annual accident statistics"). These should always be classified as **General**, even if specific numbers are mentioned.

    4. **Output Format:**
    - **General:** For articles that are not about specific road vehicle accidents.
    - **Specific:** For articles about a single, detailed road vehicle accident. Also extract the following details, separated by `<sep>` tags:
        1) **Publish Date**: When the news was published. Must be in numerical 'day-month-year' format.
        2) **Accident Date**: When the accident occurred. If not explicitly mentioned, deduce the date if possible. Must be in numerical 'day-month-year' format.
        3) **Accident Time**: Time of the accident, if mentioned.
        4) **Number of Deaths**: People killed in the accident.
        5) **Number of Injuries**: People injured in the accident.
        6) **Accident Location**: Place where the accident occurred.
        7) **Road Type**: Type of road where the accident occurred (e.g., highway, expressway).
        8) **Pedestrian Involvement**: Indicate if pedestrians were involved.
        9) **Vehicle Types**: Types of vehicles involved, separated by hyphens (e.g., "bus-car").
        10) **District**: Specific district in Bangladesh where the accident occurred. If outside Bangladesh, respond "Foreign."

    ---

    **Examples:**

    1. **News:**
    "Ferry capsizes in Meghna River, 25 missing."
    **Output:**
    General

    2. **News:**
    "450 road accidents reported during Eid holidays, 120 dead."
    **Output:**
    General

    3. **News:**
    "Car crashes into rickshaw in Old Dhaka, killing 3 people."
    **Output:**
    Specific<sep>15-05-2024<sep>15-05-2024<sep>Not mentioned<sep>3<sep>2<sep>Old Dhaka<sep>Urban street<sep>No<sep>Car-rickshaw<sep>Dhaka

    4. **News:**
    "Fire at a garment factory in Narayanganj injures 50 workers."
    **Output:**
    General

    5. **News:**
    "Train collides with bus at railway crossing in Tangail, 8 dead."
    **Output:**
    Specific<sep>12-07-2024<sep>12-07-2024<sep>6:30 PM<sep>8<sep>15<sep>Railway crossing near Tangail<sep>Railway crossing<sep>No<sep>Train-bus<sep>Tangail

    6. **News:**
    "বিল দখল নিয়ে দুপক্ষের সংঘর্ষ, আহত ৫০"
    **Output:**
    General

    ---

    Now classify the article based on the above instructions.
        """
        response = model.generate_content(
                prompt,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
            )
        try:
            print("LLM Response:  ", response.text)
            return response.text
        # except ValueError as e:
        #     if "Invalid operation" in str(e) and "The candidate's safety_ratings are:" in str(e):
        #         print("Caught ValueError related to safety ratings. Setting response to 'General'.")
        #         response = "General"
        #         print("LLM Response:  ", response)
        #         return response
        #     else:
        #         print(f"Unexpected ValueError: {e}")
        #         raise
        except Exception as e:
            print(f"Error occurred: {e}")
            return "General"

    urls=[]
    for i in range(len(merged_df)):
        urls.append(merged_df['News Link'][i])
    descriptions=[]
    for url in urls:
        descriptions.append(page_content_to_string(url))


    llm_responses = []
    j=0
    for i in range(len(descriptions)):
        time.sleep(7)
        try:
            print(f"trying index no {i} with API {j}, value = {Gemini_API_Keys[j]}")
            llm_responses.append(report_processing_agent(descriptions[i], Gemini_API_Keys[j]))
        except Exception as e:
            print(f"Error occurred: {e}")
            time.sleep(7)
            j+=1
            if j == len(Gemini_API_Keys):
                j=0
                print("All API keys exhausted. Going to sleep for 1 hour before trying again.")
                time.sleep(3700)
            print(f"trying index no {i} with API {j}, value = {Gemini_API_Keys[j]}")
            llm_responses.append(report_processing_agent(descriptions[i], Gemini_API_Keys[j]))
        

    Gemini_responses = llm_responses
    merged_df['Gemini_responses'] = Gemini_responses

    # Split each row in the "Report" column into 11 parts based on <sep> and create new columns
    merged_df2 = merged_df

    # Remove rows where the value in the "Report" column is "General"
    merged_df2 = merged_df2[merged_df2["Gemini_responses"].str.contains("Specific", na=False)].reset_index(drop=True)
    if len(merged_df2) == 0:
        return merged_df2
    else:
        new_columns = ['Gemini Report Type', 'Publish Date','Accident Date','Time of Accident','Killed','Injured','Location','Road Type', 'Pedestrian Involved', 'Vehicles Involced', 'District']  # Generate column names
        # Split the "Gemini_responses" column and handle discrepancies
        split_df = merged_df2["Gemini_responses"].str.split("<sep>", expand=True)

        # Ensure the resulting DataFrame has the same number of columns as `new_columns`
        split_df = split_df.reindex(columns=range(len(new_columns)), fill_value="ERROR")

        # Assign the split data to the new columns
        merged_df2[new_columns] = split_df
        return merged_df2