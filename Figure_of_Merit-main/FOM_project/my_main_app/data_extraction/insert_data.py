from my_main_app.models import DeviceData
from django.core.files import File




def insert_metadata(metadata, path):
    
        entry = DeviceData(
            doi = metadata[0],
            title = metadata[1],
            first_author = metadata[2],
            journal = metadata[3],
            year = metadata[4],
            breakdown_voltage = 0.0,
            r_on = 0.0,
            #reference_file = f
            )
        entry.save()
        if path != '':
            with open(path, 'rb') as f:
                entry.reference_file.save(path.split('/')[-1], File(f))
                entry.save()



