# Design and Application of Multimodal Large Language Model Based System for End to End Automation of Accident Dataset Generation 
## Step 1: 
Create a conda virtual environment with python == 3.12.4
## Step 2:
Clone the repository and change your current directory to the cloned repository file. 
## Step 3:
Open the notebook named **pipeline_notebook**
In the pipeline notebook, You have to at least input 4 fields: Gemini_API_Keys, newspaper_name , date and url.
If you want to just test it quickly, set DEBUG = True. Otherwise, if you want the full output, set it to True
![image](https://github.com/user-attachments/assets/a359c0c1-23a6-48f2-b01e-a0c744d5cfb4)
## Step 4:
You can see the output logs ar the end of the notebook. If everything goes correct, a csv file will be saved in SCRAPED folder
## Step 5:
You can check the Deduplication and Visualization in the notebook named **duplicates_removal_and_visualization_notebook**
The deduplicated csv file will be saved in Duplicate_removal folder

