from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.views import generic
from django.views.generic import View
from .forms import UserForm
from .models import Plane, Flight, Ticket, Passenger
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


def index(request):
    form = UserForm(request.POST)
    context = {
        'form': form
    }
    return render(request, 'index.html', context=context)


@login_required
def flight_info(request, flight_id):
    my_flight = Flight.objects.filter(flight_id=flight_id)
    tickets = Ticket.objects.filter(flight_id=flight_id)
    if my_flight.__len__() > 0:
        left_seats = my_flight[0].left_seats()
    else:
        left_seats = 0
    context = {
        'my_flight': my_flight,
        'tickets': tickets,
        'left_seats': left_seats
    }
    return render(request, 'flight_info.html', context=context)


@login_required
def try_add(request, flight_id, name, surname, places):
    valid = 0
    switcher = 1
    my_flight = Flight.objects.filter(flight_id=flight_id)
    tickets = Ticket.objects.filter(flight_id=flight_id).values('owner')
    owners = Passenger.objects.exclude(id__in=tickets)
    if my_flight.__len__() > 0:
        left_seats = my_flight[0].left_seats()
    else:
        left_seats = 0
    try:
        owner = Passenger.objects.filter(name=name, surname=surname)
        print(owner[0])

        print(isinstance(places, int))
        if owner[0] is None:
            valid = 1
            raise Exception('Nie ma takiej osoby!')
        if not isinstance(places, int):
            valid = 2
            raise Exception('Places nie jest numerem!')
        new_ticket = Ticket(owner=owner[0], flight_id=my_flight[0], seats=places)
        new_ticket.clean()
        new_ticket.save()
    except Exception:
        switcher = 2
        valid += 1
    context = {
        'my_flight': my_flight,
        'owners': owners,
        'left_seats': left_seats,
        'valid': valid,
        'switcher': switcher
    }
    return render(request, 'add_ticket.html', context=context)


@login_required
def add_ticket(request, flight_id):
    my_flight = Flight.objects.filter(flight_id=flight_id)
    tickets = Ticket.objects.filter(flight_id=flight_id).values('owner')
    owners = Passenger.objects.exclude(id__in=tickets)
    if my_flight.__len__() > 0:
        left_seats = my_flight[0].left_seats()
    else:
        left_seats = 0
    context = {
        'my_flight': my_flight,
        'owners': owners,
        'left_seats': left_seats
    }
    return render(request, 'add_ticket.html', context=context)


@login_required
def loty(request):
    if request.GET:
        print(request.GET)
        if request.GET['switcher'] == '1':
            start_from = request.GET['start_from']
            start_to = request.GET['start_to']
            all_loty = Flight.objects.all().filter(start_time__gt=start_from, start_time__lt=start_to).\
                order_by('start_time')
        elif request.GET['switcher'] == '2':
            land_from = request.GET['land_from']
            land_to = request.GET['land_to']
            all_loty = Flight.objects.all().filter(start_time__gt=land_from, start_time__lt=land_to).\
                order_by('start_time')
        else:
            all_loty = Flight.objects.all().order_by('start_time')
    else:
        all_loty = Flight.objects.all().order_by('start_time')
    context = {
        'all_loty': all_loty,
    }
    print(all_loty)
    return render(request, 'flights.html', context=context)


def register(request):
    valid = 0
    form = UserForm(request.POST)
    if request.method == "POST":
        try:
            if form.is_valid:
                try:
                    name = request.POST['username']
                    password = request.POST['password']
                    user = User.objects.create_user(username=name, password=password)
                    login(request, user)
                    valid = 1
                    redirect('index')
                except Exception:
                    valid = 3
        except Exception:
            valid = 2

    context = {
        'form': form,
        'valid': valid
    }
    return render(request, 'register.html', context=context)


def log_in(request):
    valid = 0
    form = AuthenticationForm(data=request.POST)
    if request.user.is_authenticated:
        logout(request)
        redirect('index')
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            valid = 1
        else:
            valid = 2
    return render(request, 'login.html', context={'form': form, 'valid': valid})
