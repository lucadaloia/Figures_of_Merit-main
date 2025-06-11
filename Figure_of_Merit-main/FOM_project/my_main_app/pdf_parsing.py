import re #library to search and match text
import PyPDF2 #library to read and extract data/text from PDF document
import requests
from urllib.parse import quote
import pdf_select

import django
import os
import sys

# Add the directory containing FOM_project to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add the parent directory to sys.path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FOM_project.settings')  # Use your project name
django.setup()

import insert_data

global doi, dois
dois = []

# function to extract data from pdf
def pdf_doi_extraction(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = "" #create empty string for text
        for page in reader.pages:
            text += page.extract_text() or ""  #append data/text if any

    # Search for DOI
    doi_found = re.search(r'(doi:|DOI:)\s*([^\s]+)', text)
    if doi_found:
        doi = doi_found.group(2)
    else:
        print('DOI not found')
    return doi



# File path variable - change to GUI to allow user to select multiple from file explorer

file_paths = list(pdf_select.select_pdfs())

for file_path in file_paths:
    doi = pdf_doi_extraction(file_path)
    #print('DOI:',doi)
    doi_encoded = quote(str(doi), safe='')
    dois.append(doi_encoded)
    



global title, author, journal, year
title = None
author = None
journal = None
year = None



def file_data_extraction(dois, paths):
    for doi, path in zip(dois, paths):
        url = f"https://api.crossref.org/works/{doi}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            metadata = data['message']
            # get title
            title = metadata.get('title', [None])[0]

            # get authors and add them to a string (list separated by comma)
            authors = metadata.get('author', []) 
            authors_list = []
            for author in authors:
                # Combine given and family names, if available
                name_parts = []
                if 'given' in author:
                    name_parts.append(author['given'])
                if 'family' in author:
                    name_parts.append(author['family'])
                full_name = ' '.join(name_parts)
                authors_list.append(full_name)
        
            authors_string = ', '.join(authors_list)
            author = authors_string

            # Get Journal
            journal = metadata.get('container-title', [None])[0]

            # Get year
            year = metadata.get('issued', {}).get('date-parts', [[None]])[0][0]

            metadata = [doi, title, author, journal, year]
            insert_data.insert_metadata(metadata, path)
            print("File: '",title,"' has been added succesfully")
            
        else:
            print("An error occurred.")

file_data_extraction(dois, file_paths)



