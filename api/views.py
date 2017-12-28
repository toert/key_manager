import json
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import numpy

from api.models import Key


@csrf_exempt
def prediction(request):
    request_data = json.loads(request.body.decode('utf-8'))
    key_queryset = Key.objects.filter(key=request_data['key'])
    if not key_queryset.exists():
        return JsonResponse({'error': "Key doesn't exists"})
    key_in_db = key_queryset.first()
    if not key_in_db.is_available():
        return JsonResponse({'error': 'Wait until end of a timeout'})
    try:
        proportions = key_in_db.calculate_recommended_proportions(
            M=numpy.array(request_data['matrix'])
        )
    except Exception as e:
        return JsonResponse({'error': str(e)})
    return JsonResponse({'result': [float(proportion) for proportion in proportions],
                         'error': False})
