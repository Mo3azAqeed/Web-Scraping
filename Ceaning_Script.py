import pandas as pd
from deep_translator import GoogleTranslator
import ftfy
import re
import ast

# Load your data with the correct encoding
df = pd.read_csv("properties.csv", encoding='utf-8-sig')

# Function to check if text contains Arabic characters
def contains_arabic(text):
    arabic_pattern = re.compile(r'[\u0600-\u06FF]')
    return bool(arabic_pattern.search(text))

# Function to translate text using deep-translator
def translate_text(text, dest_lang="en"):
    try:
        translation = GoogleTranslator(source='auto', target=dest_lang).translate(text)
        print(f"Done Transalte : {text}")
        return translation
    except Exception as e:
        print(f"Failed to translate text: {text}. Error: {e}")
        return text 

# Function to clean and translate Arabic text in the DataFrame
def get_translated(df):
    for i, row in df.iterrows():
        title = row.get('Title', '')
        description = row.get('Description', '')
        if contains_arabic(title):
            cleaned_title = ftfy.fix_text(title)
            translated_title = translate_text(cleaned_title)
            df.at[i, 'Title'] = translated_title

        if contains_arabic(description):
            cleaned_description = ftfy.fix_text(description)
            translated_description = translate_text(cleaned_description)
            df.at[i, 'Description'] = translated_description
    return df

def extract_elements(df):
    # Initialize new columns for extracted elements
    df['Type'] = None
    df['Available_For'] = None
    df['Code'] = None
    df['Status'] = None 
    df['Date'] = None
    df['Furnished'] = None

    # Convert the string representation of lists to actual lists
    for index, row in df.iterrows():
        more_info_str = row['More Info']
        # Remove double quotes and convert the string to a list
        try:
            more_info_list = ast.literal_eval(more_info_str.replace('"', ''))
            # Check if it's a list and has enough elements
            if isinstance(more_info_list, list) and len(more_info_list) > 4:
                df.at[index, 'Type'] = more_info_list[0]
                df.at[index, 'Available_For'] = more_info_list[1]
                if more_info_list[1] == "For Rent":
                    df.at[index, 'Code'] = more_info_list[2]
                    df.at[index, 'Date'] = more_info_list[-1]
                    if 'Furnished' in more_info_list:
                        df.at[index, 'Furnished'] = True

                elif more_info_list[1] == "For Sale":
                    df.at[index, 'Code'] = more_info_list[2]
                    df.at[index, 'Status'] = more_info_list[3]
                    df.at[index, 'Date'] = more_info_list[-2]
                    if 'Furnished' in more_info_list:
                        df.at[index, 'Furnished'] = True

        except (ValueError, SyntaxError):
            # In case of an error, leave the default None values
            print(f"Failed to process row {index}: {more_info_str}")
            pass
    return df

# Translate Arabic text in the DataFrame
translated_df = get_translated(df)
translated_df = extract_elements(translated_df)

# Save the translated DataFrame to a new CSV file
translated_df.to_csv("translated_properties.csv", index=False, encoding='utf-8-sig')
