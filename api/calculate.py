from datetime import datetime, timedelta

import tensorflow as tf
import numpy as np


def norm_price_batch(batch):
    with np.errstate(divide='ignore', invalid='ignore'):
        c = np.divide(batch, batch[:, -1, np.newaxis])
        c[~ np.isfinite(c)] = 1  # -inf inf NaN
    return c.reshape(1, c.shape[0], c.shape[1], c.shape[2])


def calculate_recommended_proportions(path_to_neural, M):
    tf.reset_default_graph()
    with tf.Session(graph=tf.Graph()) as sess:
        tf.saved_model.loader.load(sess, [tf.saved_model.tag_constants.TRAINING], path_to_neural)
        portfolio_op = sess.graph.get_tensor_by_name("Softmax:0")
        M_norm = norm_price_batch(M)
        predictions = sess.run(portfolio_op, {'X:0': M_norm})
        return predictions