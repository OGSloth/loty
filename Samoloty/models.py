from django.db import models
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.db.models import Sum
# Create your models here.


class Passenger(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    surname = models.CharField(max_length=670, blank=False, null=False)

    class Meta:
        unique_together = (("name", "surname"),)

    def __str__(self):
        return self.name + ' ' + self.surname


class Plane(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    places = models.IntegerField()

    def clean(self):
        if self.places < 0:
            raise ValidationError("Ilość miejsc w samolocie nie może być ujemna")

    def __str__(self):
        return self.id


class Flight(models.Model):
    plane_id = models.ForeignKey(Plane, on_delete=models.CASCADE)
    flight_id = models.AutoField(primary_key=True)
    start_terminal = models.CharField(max_length=50,blank=False, null=False)
    land_terminal = models.CharField(max_length=50, blank=False, null=False)
    start_time = models.DateTimeField('Start Time')
    land_time = models.DateTimeField('Land Time')

    def __str__(self):
        return self.plane_id.id + ' o: ' + str(self.start_time)

    def clean(self):
        if self.land_time < self.start_time + timedelta(minutes=30):
            raise ValidationError("Lot nie może trwać mniej niż pół godziny.")
        plane_flights = Flight.objects.filter(plane_id=self.plane_id.id, start_time__day=self.start_time.day)
        if plane_flights.__len__() >= 4:
            raise ValidationError("Maksymalna ilość podróży samolotu jednego dnia wynosi 4")
        for p in plane_flights:
            if p.start_time < self.start_time < p.land_time \
                    or p.start_time < self.land_time < p.land_time:
                raise ValidationError("Ten samolot będzie w tym czasie w pordóży.")
        pass

    def left_seats(self):
        seats_sum = Ticket.objects.filter(flight_id=self).values('seats').aggregate(Sum('seats'))
        if seats_sum['seats__sum'] is None:
            seats_sum['seats__sum'] = 0
        left = self.plane_id.places - seats_sum['seats__sum']
        return left


class Ticket(models.Model):
    flight_id = models.ForeignKey(Flight, on_delete=models.CASCADE)
    owner = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    seats = models.IntegerField(default=1, blank=False, null=False)

    class Meta:
        unique_together = (("owner", "flight_id"),)

    def __str__(self):
        return self.owner.__str__() + ' lot: ' + self.flight_id.__str__()

    def add_tickets(self, new_seats):
        if new_seats < 1:
            raise ValidationError("Liczba dokupionych miejsc w samolocie musi być dodatnia.")
        seats_sum = Ticket.objects.filter(flight_id=self.flight_id).values('seats').aggregate(Sum('seats'))
        if seats_sum['seats__sum'] is None:
            seats_sum['seats__sum'] = 0
        left = self.flight_id.plane_id.places - seats_sum['seats__sum']
        if new_seats > left:
            raise ValidationError("Pozostało wyłącznie " + str(left) + " wolnych miejsc.")
        self.seats = self.seats + new_seats

    def clean(self):
        if self.seats < 1:
            raise ValidationError("Liczba wykupionych miejsc w samolocie musi być dodatnia.")
        seats_sum = Ticket.objects.filter(flight_id=self.flight_id).values('seats').aggregate(Sum('seats'))
        if seats_sum['seats__sum'] is None:
            seats_sum['seats__sum'] = 0
        left = self.flight_id.plane_id.places - seats_sum['seats__sum']
        if self.seats > left:
            raise ValidationError("Pozostało wyłącznie " + str(left) + " wolnych miejsc.")
        pass
