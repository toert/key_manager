from datetime import datetime, timedelta

from django.db import models
import tensorflow as tf
import numpy as np

from . import calculate


class Key(models.Model):
    key = models.CharField(max_length=255)
    path_to_neural = models.CharField(max_length=255)
    cooldown = models.DurationField()
    always_available = models.BooleanField(default=False)
    function_name = models.CharField(max_length=255)
    last_request_time = models.DateTimeField(default=datetime.utcnow() - timedelta(days=1))

    def is_available(self):
        return datetime.now() - self.cooldown >= self.last_request_time.replace(tzinfo=None) or self.always_available

    def __str__(self):
        return '{}'.format(self.key)

    def calculate_recommended_proportions(self, M):
        predictions = getattr(calculate, self.function_name)(self.path_to_neural, M)
        self.last_request_time = datetime.now().replace(tzinfo=None)
        self.save()
        return predictions[0]