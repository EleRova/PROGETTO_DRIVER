# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from .login import LoginForm
from .models import Driver, Market, Temperature, Trip
from datetime import datetime
from django.core import serializers
import subprocess
import random
import threading
import time




def index(request):
    return HttpResponse("Hello, world. You're at the PCC index.")


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            queryset = Driver.objects.filter(username=username, password=password)

            if queryset.exists():
                # Do something if the values exist in the database
                request.session['driver']= serializers.serialize('json', [queryset.first()])
                return render(request, 'home.html', {'driver': queryset.first()})
            else:
                # Do something if the values don't exist in the database
                return render(request, 'login.html', {'form': form, 'error': 'Invalid login credentials'})

    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def driver_markets(request):
    t.start()

    return render(request, 'lista_negozi.html', {'market': Market.objects.all().values()})

def generate_temperature():
    while True:
        valore_temp = random.uniform(-20, 5)
        if valore_temp > -7:
            subprocess.run(['telegram-send', "La temperatura è fuori range!"], check=True)
        temperature = Temperature.objects.create(temperatura_registrata=valore_temp)
        temperature.save()
        global stop
        if stop:
            break
        time.sleep(5)


def driver_enddeliveries(request):
    global stop
    stop = True
    t.join()
    return render(request, 'fine_giro.html')

stop = False
t = threading.Thread(target=generate_temperature)


def inizio_consegna(request, market_id):
    driver = list(serializers.deserialize("json", request.session.get('driver', None)))
    if driver:
        driver_data=driver[0].object
        market = get_object_or_404(Market,id_negozio = market_id)
        trip = Trip.objects.create(autista=driver_data, negozio=market, data_ora_partenza=datetime.now())
        request.session['market_id'] = market_id
        print(market_id)
        print(trip.id)
        return render(request, 'lista_negozi.html', {'market': Market.objects.all().values(), 'trip_id':trip.id})
    else:
        return JsonResponse({'error':'driver not found in session'})

def consegna_effettuata(request, trip_id):
    trip=get_object_or_404(Trip, id =trip_id)
    trip.data_ora_arrivo=datetime.now()
    print(trip.data_ora_arrivo)
    market_id= request.session.get('market_id', None)
    print(market_id)
    market = get_object_or_404(Market, id_negozio=market_id)
    ora_arrivo=datetime.strptime(trip.data_ora_arrivo.strftime("%H:%M:%S"),"%H:%M:%S")
    fine_ora = datetime.strptime(market.fine_fascia_consegna.strftime("%H:%M:%S"),"%H:%M:%S")
    ritardo=False
    if ora_arrivo > fine_ora:
        ritardo = True
        print(ora_arrivo)
        print(fine_ora)
        tempo_ritardo = ora_arrivo - fine_ora
        print(tempo_ritardo)
        trip.tempo_ritardo=str(tempo_ritardo)
    trip.ritardo =ritardo
    trip.save()
    del request.session['market_id']
    return render(request, 'lista_negozi.html', {'market': Market.objects.all().values()})

