from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import DeviceData

@admin.register(DeviceData)
class DeviceDataAdmin(admin.ModelAdmin):
    list_display = ('semiconductor_material', 'device_type', 'breakdown_voltage', 'r_on', 'year')
    #readonly_fields = ('reference_file',)
