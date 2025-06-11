from my_main_app.models import DeviceData




def insert_metadata(metadata):
    entry = DeviceData(
        doi = metadata[0],
        title = metadata[1],
        first_author = metadata[2],
        journal = metadata[3],
        year = metadata[4],
        breakdown_voltage = 650,
        r_on = 20
        )
    entry.save()


