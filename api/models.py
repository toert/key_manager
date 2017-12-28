from datetime import datetime, timedelta

from django.db import models
import tensorflow as tf
import numpy as np


class Key(models.Model):
    key = models.CharField(max_length=255)
    path_to_neural = models.CharField(max_length=255)
    cooldown = models.DurationField()
    always_available = models.BooleanField(default=False)
    last_request_time = models.DateTimeField(default=datetime.utcnow() - timedelta(days=1))

    def is_available(self):
        return datetime.now() - self.cooldown >= self.last_request_time.replace(tzinfo=None) or self.always_available

    def __str__(self):
        return '{}'.format(self.key)

    def norm_price_batch(self, batch):
        with np.errstate(divide='ignore', invalid='ignore'):
            c = np.divide(batch, batch[:, -1, np.newaxis])
            c[~ np.isfinite(c)] = 1  # -inf inf NaN
        return c.reshape(1, c.shape[0], c.shape[1], c.shape[2])

    def calculate_recommended_proportions(self, M):
        tf.reset_default_graph()
        with tf.Session(graph=tf.Graph()) as sess:
            tf.saved_model.loader.load(sess, [tf.saved_model.tag_constants.TRAINING], self.path_to_neural)
            portfolio_op = sess.graph.get_tensor_by_name("Softmax:0")
            M_norm = self.norm_price_batch(M)
            predictions = sess.run(portfolio_op, {'X:0': M_norm})
            self.last_request_time = datetime.now().replace(tzinfo=None)
            self.save()
            return predictions[0]
