import json
import os
import django
import sys
from django.core.management import call_command

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FOM_project.settings')
django.setup()

from my_main_app.models import MaterialLimit


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
            results.append({
                'name': name,
                'x_data': list(x_data),
                'y_data': list(y_data)
            })
    return results

def insert_into_db(dataset):
    materials = list(MaterialLimit.objects.values_list('material', flat=True))
    for data in dataset:
        print(materials)
        if data['name'] in materials:
            #material already in database
            print('already there')
            None
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

json_data = extract_limits('./charts/limits_brV_Ron(1).json')

insert_into_db(json_data)

