from django.db import models

# Create your models here.
from django.db import models

class DeviceData(models.Model):
    # Reference metadata
    company_university =  models.CharField(max_length=255, blank=True, default='')
    first_author =  models.CharField(max_length=255, blank=True, default='')
    title =   models.CharField(max_length=255, blank=True, default='')
    journal = models.CharField(max_length=255, blank=True, default='')
    year = models.IntegerField(default=1900)
    doi = models.URLField(blank=True)

    # Device data
    part_number = models.CharField(max_length=255, blank=True, default='')
    rated_voltage = models.FloatField(default=0.0)
    rated_current = models.FloatField(default=0.0)
    r_on_at_25C = models.FloatField(default=0.0)
    semiconductor_material =models.CharField(max_length=255, blank=True, default='')
    device_type=models.CharField(max_length=255, blank=True, default='')
    breakdown_voltage = models.FloatField(default=0.0)  # in Volts
    r_on = models.FloatField(default=0.0)          # RdsA in mOhm·cm²

    # Upload field
    reference_file = models.FileField(upload_to='references/', blank=True, null=True)

    def __str__(self):
        return f"{self.semiconductor_material} {self.device_type} ({self.year})"
