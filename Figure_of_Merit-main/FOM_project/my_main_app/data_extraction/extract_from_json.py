import json
import os
import django
import sys
from django.core.management import call_command
import math
from tkinter import filedialog
import tkinter as tk
import pandas as pd

import pdf_parsing


# Add the project root to sys.path
import sys
sys.path.append(r"C:\Users\Luca.DESKTOP-NPVSRVE\Desktop\Figure_of_Merit\Figures_of_Merit-main\Figure_of_Merit-main")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FOM_project.settings')
django.setup()

from my_main_app import models

def remove_outliers(data):
    i = 1
    removed = 0
    while i < (len(data)-1):
        if data[i-1] > data[i] or data[i] > 5*data[i-1]:
            data.pop(i)
            removed += 1
        else:
            i += 1
    return data

def extend_plot_lines(x_data, y_data, factor=1e6):
    if len(x_data) < 2 or len(y_data) < 2:
        return x_data, y_data  # Not enough points to extend
    
    # Use the last two points to calculate the slope in log-log space
    x1, x2 = x_data[-10], x_data[-8]
    y1, y2 = y_data[-10], y_data[-8]

    log_x1, log_x2 = math.log10(x1), math.log10(x2)
    log_y1, log_y2 = math.log10(y1), math.log10(y2)

    slope = (log_y2 - log_y1) / (log_x2 - log_x1)
    

    #extend to larger x
    new_log_x = math.log10(x2 * factor)
    new_log_y = log_y2 + slope * (new_log_x - log_x2)
    new_x = 10 ** new_log_x
    new_y = 10 ** new_log_y

    x_data_extended = list(x_data) + [new_x]
    y_data_extended = list(y_data) + [new_y]

    return x_data_extended, y_data_extended

def extract_limits(json_path):
    with open(json_path, 'r', encoding = 'utf-8') as f:
        data = json.load(f)
        results = []
        for dataset in data.get('datasetColl', []):
            name = dataset.get('name')
            values = dataset.get('data', [])
            values = [item['value'] for item in values]
            # Unzip the list of [x, y]
            x_data, y_data = zip(*values) if values else ([], [])
            x_data, y_data = extend_plot_lines(x_data, y_data)
            x_data = remove_outliers(list(x_data))
            y_data = remove_outliers(list(y_data))
            results.append({
                'name': name,
                'x_data': list(x_data),
                'y_data': list(y_data)
            })
    return results

def insert_into_db(dataset):
    materials = list(models.MaterialLimit.objects.values_list('material', flat=True))
    for data in dataset:
        if data['name'] in materials:
            #material already in database
            print(data['name'], 'already there')
        else:
            print('adding', data['name'])
            # add material to the database/table
            obj = models.MaterialLimit.objects.create(
                material = data['name'],
                br_voltage = data['x_data'],
                r_on = data['y_data']
            )
            obj.save()
    return



def extract_device_data(file_paths):
    for file_path in file_paths:
        # fetch file name from path
        file_name = os.path.basename(file_path)
        # remove extension
        file_name = os.path.splitext(file_name)[0]
        file_name = file_name.replace("_", " ")

        # Device type = file name (standard chosen)
        device_type = file_name
        #fetch device material from device type
        semiconductor_material = device_type.split()[0]
        device_type = " ".join(device_type.split()[1:])

        with open(file_path, 'r', encoding = 'utf-8') as f:
            data = json.load(f)
            devices_data = []
            for dataset in data.get('datasetColl', []):

                # name = 'company - doi'
                #DOI = name - company
                # Company or Univ = name - doi 
                name = dataset.get('name', '')
                if ' - ' in name:
                    company_univ, doi = name.split(' - ', 1)
                else:
                    company_univ = name
                    doi = ''
                
                # get metadata and insert into table
                exists = models.DeviceData.objects.filter(doi=doi).exists()
                if exists:
                    print('already there', doi)
                    None
                else:
                    pdf_parsing.file_data_extraction([doi], [''])
                    # get x and y values
                    values = dataset.get('data', [])
                    values = [item['value'] for item in values]
                    # Vb = x data and Ron = y data
                    
                    
                    if values:
                        breakdown_voltage, r_on = zip(*values)
                        breakdown_voltage, r_on = values[0]
                    else:
                        breakdown_voltage, r_on = 0, 0
                    device_data = [company_univ, doi, semiconductor_material, device_type, breakdown_voltage, r_on]

                    current_doi = doi
                    #search for device - obj created in  file_data_extraction
                    device = models.DeviceData.objects.get(doi=current_doi)
                    device.breakdown_voltage = breakdown_voltage
                    device.r_on = r_on
                    device.semiconductor_material = semiconductor_material
                    device.device_type = device_type
                    device.company_university = company_univ

                    device.save()
                








    return


def select_json(root):
    win = tk.Toplevel(root)
    win.withdraw()  # Hide the main window
    file_paths = filedialog.askopenfilenames(
        title="Select JSON files",
        filetypes=[("JSON files", "*.json")],
    )
    return list(file_paths)

def extract_material_parameters(root):
    select_path = select_doc(root)[0]
    df = pd.read_excel(select_path)

    for _, row in df.iterrows():
        models.MaterialLimit.objects.create(
            material=row['Material'],
            epsilon=row['epsilon'],
            miu=row['miu'],
            Ec=row['Ec'],
        )

    return

def select_doc(root):
    
    win = tk.Toplevel(root)
    win.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilenames(
        title="Select xlsx files",
        filetypes=[("xlsx files", "*.xlsx")],
    )
    return list(file_path)



def select_function():
    root = tk.Tk()
    root.title("Select Function")

    label = tk.Label(root, text="Which function do you want to use?")
    label.pack(pady=10)

    tk.Button(root, text="Add Material Limit (.xlsx)", command=lambda: extract_material_parameters(root)).pack(pady=5)
    tk.Button(root, text="Add device data (.json)", command=lambda: select_json(root)).pack(pady=5)
    

    root.mainloop()

#models.MaterialLimit.objects.all().delete()
#models.DeviceData.objects.all().delete()

select_function()



#models.DeviceData.objects.filter(doi="10.1109/LED.2015.2478907").delete()

#json_data = extract_limits('./charts/limits_brV_Ron(2).json')

#insert_into_db(json_data)

