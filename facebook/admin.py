from django.contrib import admin
from .models import Creds, AccountsAd, AccountPages, IgnoredComments

admin.site.register(Creds)
admin.site.register(AccountsAd)
admin.site.register(AccountPages)
admin.site.register(IgnoredComments)