import json
import os
import sys
from random import random
from datetime import datetime

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import numpy

from api.models import Key


@csrf_exempt
def prediction(request):
    try:
        request_data = json.loads(request.body.decode('utf-8'))
        return JsonResponse({'result': get_prediction(request_data['key'], request_data['matrix']),
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
    prediction = get_prediction(key, matrix)
    key_in_db.last_request_time = last_request_time
    key_in_db.save()
    return JsonResponse({'TEST_RESULT': prediction})


def get_prediction(key, matrix):
    key_queryset = Key.objects.filter(key=key)
    if not key_queryset.exists():
        return JsonResponse({'error': "Key doesn't exists"})
    key_in_db = key_queryset.first()
    if not key_in_db.is_available():
        return JsonResponse({'error': 'Wait until end of a timeout'})

    proportions = key_in_db.calculate_recommended_proportions(
        M=numpy.array(matrix)
    )
    return [float(proportion) for proportion in proportions]
