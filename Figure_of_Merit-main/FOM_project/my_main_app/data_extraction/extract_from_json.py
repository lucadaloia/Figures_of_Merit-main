import json
import os
import django
import sys
from django.core.management import call_command
import math


# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FOM_project.settings')
django.setup()

from my_main_app.models import MaterialLimit


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
            if name == "Diamond": print(y_data)
            results.append({
                'name': name,
                'x_data': list(x_data),
                'y_data': list(y_data)
            })
    return results

def insert_into_db(dataset):
    materials = list(MaterialLimit.objects.values_list('material', flat=True))
    for data in dataset:
        if data['name'] in materials:
            #material already in database
            print(data['name'], 'already there')
        else:
            print('adding', data['name'])
            # add material to the database/table
            obj = MaterialLimit.objects.create(
                material = data['name'],
                br_voltage = data['x_data'],
                r_on = data['y_data']
            )
            obj.save()
    return







#MaterialLimit.objects.all().delete()
#obj = MaterialLimit.objects.get(material="GaN Bulk Conduction")
#obj.delete()

#json_data = extract_limits('./charts/limits_brV_Ron(2).json')

#insert_into_db(json_data)

