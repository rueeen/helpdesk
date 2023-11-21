from django.contrib import admin
from .models import Status,Ticket

# Register your models here.
admin.site.register(Ticket)
admin.site.register(Status)