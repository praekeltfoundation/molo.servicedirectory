import base64
import json
import urllib2

from django.core.urlresolvers import reverse
from django.http import QueryDict, HttpResponseRedirect
from django.views.generic import TemplateView, View
from molo.servicedirectory import settings


def make_request_to_servicedirectory_api(url, data=None):
    if data is not None:
        data = json.dumps(data)

    api_request = urllib2.Request(url, data=data)

    basic_auth_username = settings.SERVICE_DIRECTORY_API_USERNAME
    basic_auth_password = settings.SERVICE_DIRECTORY_API_PASSWORD
    base64string = base64.encodestring(
        '{0}:{1}'.format(basic_auth_username, basic_auth_password)
    ).replace('\n', '')
    api_request.add_header("Authorization", "Basic {0}".format(base64string))
    api_request.add_header("Content-Type", "application/json")

    response = urllib2.urlopen(api_request).read()

    json_result = json.loads(response)

    return json_result


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
            categories_keywords_url = '{0}homepage_categories_keywords/'\
                .format(settings.SERVICE_DIRECTORY_API_BASE_URL)

            categories_keywords = make_request_to_servicedirectory_api(
                categories_keywords_url
            )

        else:
            service_directory_query_parms = QueryDict('', mutable=True)
            service_directory_query_parms['category'] = category

            keywords_url = '{0}keywords/?{1}'.format(
                settings.SERVICE_DIRECTORY_API_BASE_URL,
                service_directory_query_parms.urlencode()
            )

            keywords = make_request_to_servicedirectory_api(
                keywords_url
            )

            categories_keywords = [
                {
                    'name': category,
                    'keywords': [keyword['name'] for keyword in keywords]
                }
            ]

        context['categories_keywords'] = categories_keywords
        context['and_more'] = not category

        return context


class LocationSearchView(TemplateView):
    template_name = 'servicedirectory/location_search.html'

    def get_context_data(self, **kwargs):
        context = super(LocationSearchView, self).get_context_data(**kwargs)

        search_term = self.request.GET['search']
        context['search_term'] = search_term

        return context


class LocationResultsView(TemplateView):
    template_name = 'servicedirectory/location_results.html'

    def get_context_data(self, **kwargs):
        context = super(LocationResultsView, self).get_context_data(**kwargs)

        search_term = self.request.GET['search']
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


class ServiceResultsView(TemplateView):
    template_name = 'servicedirectory/service_results.html'

    def get_context_data(self, **kwargs):
        context = super(ServiceResultsView, self).get_context_data(**kwargs)

        search_term = self.request.GET['search']
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

        service_directory_query_parms = QueryDict('', mutable=True)
        service_directory_query_parms['search_term'] = search_term

        if place_latlng is not None:
            service_directory_query_parms['location'] = place_latlng

        if place_formatted_address is not None:
            service_directory_query_parms['place_name'] =\
                place_formatted_address

        url = '{0}search/?{1}'.format(
            settings.SERVICE_DIRECTORY_API_BASE_URL,
            service_directory_query_parms.urlencode()
        )
        search_results = make_request_to_servicedirectory_api(url)

        categories_keywords = []
        if not search_results:
            # TODO: consider caching the categories and keywords when we fetch
            # them for the home page, then retrieving them from the cache here
            categories_keywords_url = '{0}homepage_categories_keywords/'\
                .format(settings.SERVICE_DIRECTORY_API_BASE_URL)

            categories_keywords = make_request_to_servicedirectory_api(
                categories_keywords_url
            )

        location_query_parms = QueryDict('', mutable=True)
        location_query_parms['location'] = location_term
        location_query_parms['search'] = search_term

        context['search_term'] = search_term
        context['location_term'] = location_term
        context['place_id'] = place_id
        context['place_latlng'] = place_latlng
        context['place_formatted_address'] = place_formatted_address
        context['change_location_url'] = '{0}?{1}'.format(
            reverse('location-results'), location_query_parms.urlencode()
        )
        context['search_results'] = search_results
        context['categories_keywords'] = categories_keywords

        return context


class ServiceDetailView(TemplateView):
    template_name = 'servicedirectory/service_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ServiceDetailView, self).get_context_data(**kwargs)

        service_directory_api_base_url =\
            settings.SERVICE_DIRECTORY_API_BASE_URL
        service_id = self.kwargs['service_id']

        url = '{0}organisation/{1}/'.format(service_directory_api_base_url,
                                       service_id)

        json_result = make_request_to_servicedirectory_api(url)

        context['organisation'] = json_result
        context['message'] = self.request.GET.get('msg', None)

        return context


class ServiceReportIncorrectInformationView(TemplateView):
    template_name = 'servicedirectory/service_report.html'

    def get_context_data(self, **kwargs):
        context = super(ServiceReportIncorrectInformationView, self).\
            get_context_data(**kwargs)

        service_name = self.request.GET['service_name']
        organisation_name = self.request.GET['org_name']

        context['service_name'] = service_name
        context['organisation_name'] = organisation_name

        return context

    def post(self, request, *args, **kwargs):
        service_directory_api_base_url =\
            settings.SERVICE_DIRECTORY_API_BASE_URL
        service_id = kwargs['service_id']

        url = '{0}organisation/{1}/report/'.format(service_directory_api_base_url,
                                              service_id)

        data = request.POST.dict()
        if 'csrfmiddlewaretoken' in data:
            data.pop('csrfmiddlewaretoken')  # no point passing this to the API

        make_request_to_servicedirectory_api(url, data=data)

        query_params = QueryDict('', mutable=True)
        query_params['msg'] = 'Thanks! We\'ve received your report and will' \
                              ' look into it.'

        redirect_url = '{0}?{1}'.format(
            reverse('service-detail', kwargs={'service_id': service_id}),
            query_params.urlencode()
        )

        return HttpResponseRedirect(redirect_to=redirect_url)


class ServiceRateView(View):
    def post(self, request, *args, **kwargs):
        service_directory_api_base_url =\
            settings.SERVICE_DIRECTORY_API_BASE_URL
        service_id = kwargs['service_id']

        url = '{0}organisation/{1}/rate/'.format(service_directory_api_base_url,
                                            service_id)

        data = request.POST.dict()
        if 'csrfmiddlewaretoken' in data:
            data.pop('csrfmiddlewaretoken')  # no point passing this to the API

        make_request_to_servicedirectory_api(url, data=data)

        query_params = QueryDict('', mutable=True)
        query_params['msg'] = 'Thanks for telling us how helpful this service'\
                              ' was. You can always update your response when'\
                              ' you change your mind.'

        redirect_url = '{0}?{1}'.format(
            reverse('service-detail', kwargs={'service_id': service_id}),
            query_params.urlencode()
        )

        return HttpResponseRedirect(redirect_to=redirect_url)


class ServiceSendSMSView(TemplateView):
    template_name = 'servicedirectory/service_sms.html'

    def post(self, request, *args, **kwargs):
        service_directory_api_base_url =\
            settings.SERVICE_DIRECTORY_API_BASE_URL
        service_id = kwargs['service_id']

        url = '{0}organisation/sms/'.format(service_directory_api_base_url)

        data = request.POST.dict()
        data['service_url'] = request.build_absolute_uri(
            reverse('service-detail', kwargs={'service_id': service_id})
        )

        if 'csrfmiddlewaretoken' in data:
            data.pop('csrfmiddlewaretoken')  # no point passing this to the API

        make_request_to_servicedirectory_api(url, data=data)

        query_params = QueryDict('', mutable=True)
        query_params['msg'] = 'Thanks! We''ve sent an SMS with a link for' \
                              ' this service to {0}.'.format(
            data['cell_number'])

        redirect_url = '{0}?{1}'.format(
            reverse('service-detail', kwargs={'service_id': service_id}),
            query_params.urlencode()
        )

        return HttpResponseRedirect(redirect_to=redirect_url)


class ServiceSelfSendSMSView(TemplateView):
    template_name = 'servicedirectory/service_self_sms.html'

    def get_context_data(self, **kwargs):
        context = super(ServiceSelfSendSMSView, self).get_context_data(
            **kwargs
        )
        context['service_id'] = kwargs['service_id']

        return context
