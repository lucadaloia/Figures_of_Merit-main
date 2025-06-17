import re #library to search and match text
import PyPDF2 #library to read and extract data/text from PDF document
import requests
from urllib.parse import quote
import pdf_select
import plot_extract


import os
import sys
# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Go up N levels to reach the project root (adjust N as needed)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
# Add project root to sys.path
sys.path.append(project_root)


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FOM_project.settings')
import django
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
    doi_found = re.search(r'(10\.\d{4,9}/[-._;()/:A-Z0-9]+)', text, re.I)
    if doi_found:
        doi = doi_found.group(1)
    else:
        print('DOI not found')
    return doi



# File path variable - change to GUI to allow user to select multiple from file explorer


def doi_from_file_paths(file_paths):
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
            if not title:
                title = "Unknown Title"
            #plot_extract.extract(path)

            # get authors and add them to a string (list separated by comma)
            authors = metadata.get('author', [])
            if authors:
                first_author = authors[0]
                name_parts = []
                if 'given' in first_author:
                    name_parts.append(first_author['given'])
                if 'family' in first_author:
                    name_parts.append(first_author['family'])
                author = ' '.join(name_parts)
            else:
                author = ''

            # Get Journal
            journal = metadata.get('container-title', [None])[0]
            if not journal:
                journal = 'Unknown Journal'
            # Get year
            year = metadata.get('issued', {}).get('date-parts', [[None]])[0][0]
            if not year:
                year = 0000
            metadata = [doi, title, author, journal, year]
            insert_data.insert_metadata(metadata, path)
            print("File: '",title,"' has been added succesfully")
            
        else:
            print("An error occurred.")


#file_paths = list(pdf_select.select_pdfs())
#file_data_extraction(dois, file_paths)



