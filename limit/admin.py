from django.contrib import admin
from .models import AdRecord, AdRecordSpenddate, Refresh

admin.site.register(AdRecord)
admin.site.register(AdRecordSpenddate)
admin.site.register(Refresh)