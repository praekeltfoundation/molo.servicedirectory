from django.conf.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.HomeView.as_view(), name='home'),

    re_path(r'^location-search/$',
            views.LocationSearchView.as_view(), name='location-search'),

    re_path(r'^location-results/$',
            views.LocationResultsView.as_view(), name='location-results'),

    re_path(r'^organisation-results/$',
            views.OrganisationResultsView.as_view(),
            name='organisation-results'),

    re_path(r'^organisation/(?P<organisation_id>[0-9]+)/$',
            views.OrganisationDetailView.as_view(),
            name='organisation-detail'),

    re_path(r'^organisation/(?P<organisation_id>[0-9]+)/report/$',
            views.OrganisationReportIncorrectInformationView.as_view(),
            name='organisation-report'),

    re_path(r'^organisation/(?P<organisation_id>[0-9]+)/rate/$',
            views.OrganisationRateView.as_view(), name='organisation-rate'),

    re_path(r'^organisation/(?P<organisation_id>[0-9]+)/sms/$',
            views.OrganisationSendSmsView.as_view(), name='organisation-sms'),

    re_path(r'^organisation/(?P<organisation_id>[0-9]+)/sms-self/$',
            views.OrganisationSelfSendSMSView.as_view(),
            name='organisation-sms-self')
]
