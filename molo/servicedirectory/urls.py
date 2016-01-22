from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home,
        name='home'),

    url(r'^location-search/$', views.location_search,
        name='location-search'),

    url(r'^location-results/$', views.location_results,
        name='location-results'),

    url(r'^result-summaries/$', views.result_summaries,
        name='result-summaries'),

    url(r'^service-detail/(?P<service_id>[0-9]+)/$', views.service_detail,
        name='service-detail'),
]
