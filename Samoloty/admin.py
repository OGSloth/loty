from django.contrib import admin
from Samoloty.models import Flight, Plane, Passenger, Ticket
# Register your models here.

admin.site.register(Flight)
admin.site.register(Plane)
admin.site.register(Passenger)
admin.site.register(Ticket)
