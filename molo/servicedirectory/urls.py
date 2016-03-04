from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$',
        views.HomeView.as_view(),
        name='home'),

    url(r'^location-search/$',
        views.LocationSearchView.as_view(),
        name='location-search'),

    url(r'^location-results/$',
        views.LocationResultsView.as_view(),
        name='location-results'),

    url(r'^service-results/$',
        views.ServiceResultsView.as_view(),
        name='service-results'),

    url(r'^service/(?P<service_id>[0-9]+)/$',
        views.ServiceDetailView.as_view(),
        name='service-detail'),

    url(r'^service/(?P<service_id>[0-9]+)/report/$',
        views.ServiceReportIncorrectInformationView.as_view(),
        name='service-report'),

    url(r'^service/(?P<service_id>[0-9]+)/rate/$',
        views.ServiceRateView.as_view(),
        name='service-rate'),

    url(r'^service/(?P<service_id>[0-9]+)/sms/$',
        views.ServiceSendSMSView.as_view(),
        name='service-sms'),

    url(r'^service/(?P<service_id>[0-9]+)/sms-self/$',
        views.ServiceSelfSendSMSView.as_view(),
        name='service-sms-self')
]
