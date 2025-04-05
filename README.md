# Design and Application of Multimodal Large Language Model Based System for End to End Automation of Accident Dataset Generation
## Abstract
Road traffic accidents remain a critical public safety and socio-economic challenge, especially in lower developed countries like Bangladesh. The existing accident data collection framework is highly manual, fragmented, and unreliable, leading to significant underreporting and inconsistencies in accident records. This research proposes an end to end automated system utilizing Large Language Models (LLMs) and web scraping techniques to address these limitations. The study designs a fully automated pipeline comprising four key components: automated web scraping code generation, news collection from online media, accident news classification and structured information extraction and duplicate removal for dataset consolidation. The system integrates a multimodal generative LLM- Gemini-2.0-Flash to achieve seamless automation. The web scraping code generation component employs LLMs to classify webpage structures into three categories—pagination, dynamic, and infinite scrolling—and generate appropriate Python scripts for automated news extraction. The news classification and information extraction component utilizes LLMs to filter accident-related news and extract key accident attributes such as accident date, time, location, fatalities, injuries, road type, vehicle types, and pedestrian involvement. A deduplication algorithm further refines the dataset by identifying duplicate reports across multiple media sources. Leveraging this system, accident data were collected from 14 major Bangladeshi news websites spanning 111 days (October 1, 2024 – January 20, 2025). The system processed over 15,000 news reports, identifying 705 accident occurrences with detailed structured attributes. The performance evaluation showed that the web scraping code generation component demonstrated a calibration accuracy of 91.3% and a validation accuracy of 80%, successfully handling most news portals except for those with non-standard structures or additional security mechanisms. The extracted dataset revealed key insights into accident trends in Bangladesh. Chittagong recorded the highest number of accidents (80), fatalities (70), and injuries (115), followed by Dhaka, Faridpur, Gazipur, and Cox’s Bazar. Temporal analysis identified accident peaks during morning (8–9 AM), noon (12–1 PM), and evening (6–7 PM) rush hours, highlighting high-risk timeframes. The authors also developed a comprehensive repository with detailed instructions to use the system. This research demonstrates the feasibility of an LLM driven, fully automated accident data collection system, significantly reducing manual effort while improving accuracy, consistency, and scalability. Future extensions include integrating real-time traffic data, expanding the system to cover additional incident types, and developing an interactive dashboard for policymakers. The findings lay the groundwork for data-driven policymaking and enhanced road safety measures in Bangladesh.

## System Architecture
![Figure 2 System Architecture](https://github.com/user-attachments/assets/7067281b-89c6-441b-9dba-dbe4ed2a44db)

## How to use?:

## Step 1: 
Create a conda virtual environment with python == 3.12.4
## Step 2:
Clone the repository and change your current directory to the cloned repository file. 
## Step 3:
Open the notebook named **pipeline_notebook**
In the pipeline notebook, You have to at least input 4 fields: Gemini_API_Keys, newspaper_name , date and url. Note, date means the publish date of the last news that you want.
If you want to just test it quickly, set DEBUG = True. Otherwise, if you want the full output, set it to False. 
![image](https://github.com/user-attachments/assets/a359c0c1-23a6-48f2-b01e-a0c744d5cfb4)
## Step 4:
You can see the output logs at the end of the notebook. If everything goes correctly, a csv file will be saved in SCRAPED folder
## Step 5:
You can check the Deduplication and Visualization in the notebook named **duplicates_removal_and_visualization_notebook**
The deduplicated csv file will be saved in Duplicate_removal folder

