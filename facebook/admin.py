from django.contrib import admin
from .models import Creds, AccountsAd, AccountPages, IgnoredComments, ContactUs, DefaultApp

admin.site.register(Creds)
admin.site.register(AccountsAd)
admin.site.register(AccountPages)
admin.site.register(IgnoredComments)
admin.site.register(ContactUs)
admin.site.register(DefaultApp)