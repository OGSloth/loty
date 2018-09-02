from django.urls import path

from . import views

urlpatterns = [
    path('register', views.register, name='register'),
    path('login', views.log_in, name='login'),
    path('logout',  views.log_in, name='logout'),
    path('loty',  views.loty, name='loty'),
    path('lot_info/<flight_id>',  views.flight_info, name='flight_info'),
    path('add_ticket/<flight_id>',  views.add_ticket, name='add_ticket'),
    path('try_add/<flight_id>/<name>/<surname>/<int:places>',  views.try_add, name='try_add'),
    path('', views.index, name='index'),
]