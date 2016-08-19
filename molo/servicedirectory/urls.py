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

    url(r'^organisation-results/$',
        views.OrganisationResultsView.as_view(),
        name='organisation-results'),

    url(r'^organisation/(?P<organisation_id>[0-9]+)/$',
        views.OrganisationDetailView.as_view(),
        name='organisation-detail'),

    url(r'^organisation/(?P<organisation_id>[0-9]+)/report/$',
        views.OrganisationReportIncorrectInformationView.as_view(),
        name='organisation-report'),

    url(r'^organisation/(?P<organisation_id>[0-9]+)/rate/$',
        views.OrganisationRateView.as_view(),
        name='organisation-rate'),

    url(r'^organisation/(?P<organisation_id>[0-9]+)/sms/$',
        views.OrganisationSendSmsView.as_view(),
        name='organisation-sms'),

    url(r'^organisation/(?P<organisation_id>[0-9]+)/sms-self/$',
        views.OrganisationSelfSendSMSView.as_view(),
        name='organisation-sms-self')
]
