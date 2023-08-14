from django.contrib import admin
from .models import LogNegativeComments, LogPositiveComments

admin.site.register(LogNegativeComments)
admin.site.register(LogPositiveComments)