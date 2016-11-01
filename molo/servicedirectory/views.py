import json
import urllib2

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import QueryDict, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView, View
from molo.servicedirectory import api


def make_request_to_google_api(url, querydict):
    full_url = '{0}?{1}'.format(url, querydict.urlencode())

    api_request = urllib2.Request(full_url)

    serialized_data = urllib2.urlopen(api_request).read()

    json_result = json.loads(serialized_data)

    return json_result


class HomeView(TemplateView):
    template_name = 'servicedirectory/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        category = self.request.GET.get('category', None)

        if not category:
            categories_keywords = api.get_home_page_categories_with_keywords()

        else:
            keywords = api.get_keywords(self.request.path, [category])

            categories_keywords = [
                {
                    'name': category,
                    'filtered_keywords': [keyword.name for keyword in keywords]
                }
            ]

        context['categories_keywords'] = categories_keywords
        context['and_more'] = not category

        return context


class LocationSearchView(TemplateView):
    template_name = 'servicedirectory/location_search.html'

    def get_context_data(self, **kwargs):
        context = super(LocationSearchView, self).get_context_data(**kwargs)

        search_term = self.request.GET['q']
        context['search_term'] = search_term

        return context


class LocationResultsView(TemplateView):
    template_name = 'servicedirectory/location_results.html'

    def get_context_data(self, **kwargs):
        context = super(LocationResultsView, self).get_context_data(**kwargs)

        search_term = self.request.GET['q']
        location_term = self.request.GET['location']

        google_query_parms = QueryDict('', mutable=True)
        google_query_parms['input'] = location_term
        google_query_parms['types'] = 'geocode'
        google_query_parms['key'] = settings.GOOGLE_PLACES_API_SERVER_KEY

        url = 'https://maps.googleapis.com/maps/api/place/autocomplete/json'

        autocomplete_suggestions = make_request_to_google_api(
            url, google_query_parms
        )

        context['search_term'] = search_term
        context['location_term'] = location_term
        context['autocomplete_suggestions'] = autocomplete_suggestions

        return context


class OrganisationResultsView(TemplateView):
    template_name = 'servicedirectory/organisation_results.html'

    def get_context_data(self, **kwargs):
        context = super(OrganisationResultsView, self).get_context_data(
            **kwargs
        )

        search_term = self.request.GET['q']
        location_term = self.request.GET['location']
        place_id = self.request.GET['place_id']
        place_latlng = self.request.GET.get('place_latlng', None)
        place_formatted_address = self.request.GET.get(
            'place_formatted_address', None
        )

        if place_latlng is None:
            google_query_parms = QueryDict('', mutable=True)
            google_query_parms['placeid'] = place_id
            google_query_parms['key'] = settings.GOOGLE_PLACES_API_SERVER_KEY

            url = 'https://maps.googleapis.com/maps/api/place/details/json'
            place_details = make_request_to_google_api(url, google_query_parms)

            place_details_result = place_details.get('result', {})

            place_formatted_address = place_details_result.get(
                'formatted_address', None
            )
            place_location = place_details_result.get(
                'geometry', {}
            ).get('location', None)

            if place_location:
                place_latlng = '{0},{1}'.format(
                    place_location['lat'], place_location['lng']
                )

        search_results = api.search(
            self.request.path, search_term, place_latlng,
            place_formatted_address
        )

        categories_keywords = []
        if not search_results:
            # TODO: consider caching the categories and keywords when we fetch
            # them for the home page, then retrieving them from the cache here
            categories_keywords = api.get_home_page_categories_with_keywords()

        location_query_parms = QueryDict('', mutable=True)
        location_query_parms['location'] = location_term
        location_query_parms['q'] = search_term

        context['search_term'] = search_term
        context['location_term'] = location_term
        context['place_id'] = place_id
        context['place_latlng'] = place_latlng
        context['place_formatted_address'] = place_formatted_address
        context['change_location_url'] = '{0}?{1}'.format(
            reverse('molo.servicedirectory:location-results'),
            location_query_parms.urlencode()
        )
        context['search_results'] = search_results
        context['categories_keywords'] = categories_keywords

        return context


class OrganisationDetailView(TemplateView):
    template_name = 'servicedirectory/organisation_detail.html'

    def get_context_data(self, **kwargs):
        context = super(OrganisationDetailView, self).get_context_data(
            **kwargs
        )

        organisation_id = self.kwargs['organisation_id']
        organisation = api.get_organisation(self.request.path, organisation_id)

        context['organisation'] = organisation
        context['message'] = self.request.GET.get('msg', None)

        return context


class OrganisationReportIncorrectInformationView(TemplateView):
    template_name = 'servicedirectory/organisation_report.html'

    def get_context_data(self, **kwargs):
        context = super(OrganisationReportIncorrectInformationView, self).\
            get_context_data(**kwargs)

        organisation_name = self.request.GET['org_name']

        context['organisation_name'] = organisation_name

        return context

    def post(self, request, *args, **kwargs):
        organisation_id = kwargs['organisation_id']

        api.report_organisation(request.path, organisation_id,
                                request.POST.get('contact_details', None),
                                request.POST.get('address', None),
                                request.POST.get('trading_hours', None),
                                request.POST.get('other', None),
                                request.POST.get('other_detail', None))

        query_params = QueryDict('', mutable=True)
        query_params['msg'] = _('Thanks! We\'ve received your report and will'
                                ' look into it.')

        redirect_url = '{0}?{1}'.format(
            reverse('molo.servicedirectory:organisation-detail',
                    kwargs={'organisation_id': organisation_id}),
            query_params.urlencode()
        )

        return HttpResponseRedirect(redirect_to=redirect_url)


class OrganisationRateView(View):
    def post(self, request, *args, **kwargs):
        organisation_id = kwargs['organisation_id']

        api.rate_organisation(request.path, organisation_id,
                              request.POST['rating'])

        query_params = QueryDict('', mutable=True)
        query_params['msg'] = _('Thanks for telling us how helpful this'
                                ' service was. You can always update your'
                                ' response when you change your mind.')

        redirect_url = '{0}?{1}'.format(
            reverse('molo.servicedirectory:organisation-detail',
                    kwargs={'organisation_id': organisation_id}),
            query_params.urlencode()
        )

        return HttpResponseRedirect(redirect_to=redirect_url)


class OrganisationSendSmsView(TemplateView):
    template_name = 'servicedirectory/organisation_sms.html'

    def post(self, request, *args, **kwargs):
        organisation_id = kwargs['organisation_id']

        organisation_url = request.build_absolute_uri(
            reverse('molo.servicedirectory:organisation-detail',
                    kwargs={'organisation_id': organisation_id})
        )

        # TODO: validate cell_number
        api.sms_organisation(request.path,
                             request.POST['cell_number'],
                             organisation_url,
                             request.POST.get('your_name', None))

        query_params = QueryDict('', mutable=True)
        query_params['msg'] = _('Thanks! We\'ve sent an SMS with a link for'
                                ' this service to %(cell_number).') % \
            {'cell_number': request.POST['cell_number']}

        redirect_url = '{0}?{1}'.format(
            reverse('molo.servicedirectory:organisation-detail',
                    kwargs={'organisation_id': organisation_id}),
            query_params.urlencode()
        )

        return HttpResponseRedirect(redirect_to=redirect_url)


class OrganisationSelfSendSMSView(TemplateView):
    template_name = 'servicedirectory/organisation_self_sms.html'

    def get_context_data(self, **kwargs):
        context = super(OrganisationSelfSendSMSView, self).get_context_data(
            **kwargs
        )
        context['organisation_id'] = kwargs['organisation_id']

        return context
