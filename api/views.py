import json
import os
import sys
from random import random
from datetime import datetime

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import numpy

from api.models import Key


API_URL = 'http://localhost:8000/api/'


@csrf_exempt
def prediction(request):
    try:
        request_data = json.loads(request.body.decode('utf-8'))
        key_queryset = Key.objects.filter(key=request_data['key'])
        if not key_queryset.exists():
            return JsonResponse({'error': "Key doesn't exists"})
        key_in_db = key_queryset.first()
        if not key_in_db.is_available():
            return JsonResponse({'error': 'Wait until end of a timeout'})

        proportions = key_in_db.calculate_recommended_proportions(
            M=numpy.array(request_data['matrix'])
        )
        return JsonResponse({'result': [float(proportion) for proportion in proportions],
                             'error': False})
    except Exception as e:
        traceback = sys.exc_info()[-1]
        file_with_error = os.path.split(traceback.tb_frame.f_code.co_filename)[1]
        line_with_error = traceback.tb_lineno
        return JsonResponse({'error': 'File: {} Line:{} Error:{}'.format(file_with_error, line_with_error, e)})


@csrf_exempt
def test_predictions(request, key, features_amount, timeframes_amount, currencies_amount):
    key_in_db = get_object_or_404(Key, key=key)
    last_request_time = key_in_db.last_request_time
    if request.method == 'GET':
        matrix = [[
            [random() for feature in range(int(features_amount))]
            for timeframe in range(int(timeframes_amount))] for currency in range(int(currencies_amount))]
    elif request.method == 'POST':
        request_data = json.loads(request.body.decode('utf-8'))
        matrix = request_data['matrix']
    else:
        return JsonResponse({'TEST_RESULT': 'Forbidden method'})
    response = requests.post(API_URL, json={'key': key, 'matrix': matrix}).text
    print(response)
    key_in_db.last_request_time = last_request_time
    key_in_db.save()
    return JsonResponse({'TEST_RESULT': response})
