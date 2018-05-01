from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.prediction),
    url(r'^(?P<key>[-\w]+)/(?P<features_amount>\d+)/(?P<timeframes_amount>\d+)/(?P<currencies_amount>\d+)',
        views.test_predictions),
    url(r'^proxy$', views.Proxy.as_view())
]