import base64
import json

from django.core.urlresolvers import reverse
from django.http import QueryDict, HttpResponseRedirect
from django.views.generic import TemplateView, View
from molo.servicedirectory import settings
from molo.core.models import SiteSettings

from six.moves.urllib.request import Request, urlopen


def get_service_directory_api_username(request):
    site_settings = SiteSettings.for_site(request.site)
    return (site_settings.service_directory_api_username or
            settings.SERVICE_DIRECTORY_API_USERNAME)


def get_service_directory_api_password(request):
    site_settings = SiteSettings.for_site(request.site)
    return (site_settings.service_directory_api_password or
            settings.SERVICE_DIRECTORY_API_PASSWORD)


def get_service_directory_api_base_url(request):
    site_settings = SiteSettings.for_site(request.site)
    return (site_settings.service_directory_api_base_url or
            settings.SERVICE_DIRECTORY_API_BASE_URL)


def get_google_places_api_server_key(request):
    site_settings = SiteSettings.for_site(request.site)
    return (site_settings.google_places_api_server_key or
            settings.GOOGLE_PLACES_API_SERVER_KEY)


def make_request_to_servicedirectory_api(url, request, data=None):
    if data is not None:
        data = json.dumps(data)

    api_request = Request(url, data=data)

    basic_auth_username = get_service_directory_api_username(request)
    basic_auth_password = get_service_directory_api_password(request)
    base64string = base64.encodestring(
        '{0}:{1}'.format(basic_auth_username, basic_auth_password)
    ).replace('\n', '')
    api_request.add_header("Authorization", "Basic {0}".format(base64string))
    api_request.add_header("Content-Type", "application/json")

    response = urlopen(api_request).read()

    json_result = json.loads(response)

    return json_result


def make_request_to_google_api(url, querydict):
    full_url = '{0}?{1}'.format(url, querydict.urlencode())

    api_request = Request(full_url)

    serialized_data = urlopen(api_request).read()

    json_result = json.loads(serialized_data)

    return json_result


class HomeView(TemplateView):
    template_name = 'servicedirectory/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        category = self.request.GET.get('category', None)
        keywords = self.request.GET.getlist('keywords[]', [])
        categories = self.request.GET.getlist('categories[]', [])

        if not category:
            categories_keywords_url = '{0}homepage_categories_keywords/'\
                .format(get_service_directory_api_base_url(self.request))

            categories_keywords = make_request_to_servicedirectory_api(
                categories_keywords_url,
                self.request
            )

        else:
            service_directory_query_parms = QueryDict('', mutable=True)
            service_directory_query_parms['category'] = category

            keywords_url = '{0}keywords/?{1}'.format(
                get_service_directory_api_base_url(self.request),
                service_directory_query_parms.urlencode())

            keywords = make_request_to_servicedirectory_api(
                keywords_url,
                self.request
            )

            categories_keywords = [
                {
                    'name': category,
                    'keywords': [keyword['name'] for keyword in keywords]
                }
            ]

        context['keywords'] = keywords
        context['and_more'] = not category
        context['categories'] = [int(i) for i in categories]
        context['categories_keywords'] = categories_keywords
        return context


class LocationSearchView(TemplateView):
    template_name = 'servicedirectory/location_search.html'

    def get_context_data(self, **kwargs):
        context = super(LocationSearchView, self).get_context_data(**kwargs)
        search_term = self.request.GET.get('search')
        keywords = self.request.GET.getlist('keywords[]', [])
        categories = self.request.GET.getlist('categories[]', [])

        context['keywords'] = keywords
        context['categories'] = categories
        context['search_term'] = search_term
        context['categories'] = [int(i) for i in categories]
        return context


class LocationResultsView(TemplateView):
    template_name = 'servicedirectory/location_results.html'

    def get_context_data(self, **kwargs):
        context = super(LocationResultsView, self).get_context_data(**kwargs)

        search_term = self.request.GET.get('search')
        location_term = self.request.GET.get('location')
        keywords = self.request.GET.getlist('keywords[]', [])
        categories = self.request.GET.getlist('categories[]', [])

        google_query_parms = QueryDict('', mutable=True)
        google_query_parms['input'] = location_term
        google_query_parms['types'] = 'geocode'
        google_query_parms['key'] = get_google_places_api_server_key(
            self.request)

        url = 'https://maps.googleapis.com/maps/api/place/autocomplete/json'

        autocomplete_suggestions = make_request_to_google_api(
            url, google_query_parms
        )

        context['keywords'] = keywords
        context['categories'] = categories
        context['search_term'] = search_term
        context['location_term'] = location_term
        context['categories'] = [int(i) for i in categories]
        context['autocomplete_suggestions'] = autocomplete_suggestions

        return context


class OrganisationResultsView(TemplateView):
    template_name = 'servicedirectory/organisation_results.html'

    def get_context_data(self, **kwargs):
        context = super(OrganisationResultsView, self).get_context_data(
            **kwargs
        )

        place_id = self.request.GET.get('place_id')
        search_term = self.request.GET.get('search')
        location_term = self.request.GET.get('location')
        keywords = self.request.GET.getlist('keywords[]', [])
        categories = self.request.GET.getlist('categories[]', [])
        place_latlng = self.request.GET.get('place_latlng', None)
        place_formatted_address = self.request.GET.get(
            'place_formatted_address', None
        )

        site_settings = SiteSettings.for_site(self.request.site)

        radius = site_settings.default_service_directory_radius
        if radius:
            radius = self.request.GET.get('radius', radius)

        if place_latlng is None:
            google_query_parms = QueryDict('', mutable=True)
            google_query_parms['placeid'] = place_id
            google_query_parms['key'] = get_google_places_api_server_key(
                self.request)

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
        service_directory_query_parms['radius'] = radius
        service_directory_query_parms['search_term'] = search_term

        if keywords:
            service_directory_query_parms['keywords'] = keywords

        if place_latlng:
            service_directory_query_parms['location'] = place_latlng

        if categories:
            service_directory_query_parms['categories'] = categories

        if place_formatted_address is not None:
            service_directory_query_parms['place_name'] =\
                place_formatted_address

        url = '{0}search/?{1}'.format(
            get_service_directory_api_base_url(self.request),
            service_directory_query_parms.urlencode()
        )
        search_results = make_request_to_servicedirectory_api(
            url, self.request)

        categories_keywords = []
        if not search_results:
            # TODO: consider caching the categories and keywords when we fetch
            # them for the home page, then retrieving them from the cache here
            categories_keywords_url = '{0}homepage_categories_keywords/'\
                .format(get_service_directory_api_base_url(self.request))

            categories_keywords = make_request_to_servicedirectory_api(
                categories_keywords_url,
                self.request
            )

        location_query_parms = QueryDict('', mutable=True)
        location_query_parms['location'] = location_term
        location_query_parms['search'] = search_term

        context['place_id'] = place_id
        context['keywords_filter'] = keywords
        context['search_term'] = search_term
        context['place_latlng'] = place_latlng
        context['location_term'] = location_term
        context['categories'] = [int(i) for i in categories]
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

        service_directory_api_base_url =\
            get_service_directory_api_base_url(self.request)
        organisation_id = self.kwargs['organisation_id']

        url = '{0}organisation/{1}/'.format(service_directory_api_base_url,
                                            organisation_id)

        json_result = make_request_to_servicedirectory_api(url, self.request)

        context['organisation'] = json_result
        context['message'] = self.request.GET.get('msg', None)

        return context


class OrganisationReportIncorrectInformationView(TemplateView):
    template_name = 'servicedirectory/organisation_report.html'

    def get_context_data(self, **kwargs):
        context = super(OrganisationReportIncorrectInformationView, self).\
            get_context_data(**kwargs)

        organisation_name = self.request.GET.get('org_name')

        context['organisation_name'] = organisation_name

        return context

    def post(self, request, *args, **kwargs):
        service_directory_api_base_url =\
            get_service_directory_api_base_url(self.request)
        organisation_id = kwargs['organisation_id']

        url = '{0}organisation/{1}/report/'.format(
            service_directory_api_base_url,
            organisation_id
        )

        data = request.POST.dict()
        if 'csrfmiddlewaretoken' in data:
            data.pop('csrfmiddlewaretoken')  # no point passing this to the API

        make_request_to_servicedirectory_api(url, self.request, data=data)

        query_params = QueryDict('', mutable=True)
        query_params['msg'] = 'Thanks! We\'ve received your report and will' \
                              ' look into it.'

        redirect_url = '{0}?{1}'.format(
            reverse('molo.servicedirectory:organisation-detail',
                    kwargs={'organisation_id': organisation_id}),
            query_params.urlencode()
        )

        return HttpResponseRedirect(redirect_to=redirect_url)


class OrganisationRateView(View):
    def post(self, request, *args, **kwargs):
        service_directory_api_base_url =\
            get_service_directory_api_base_url(request)
        organisation_id = kwargs['organisation_id']

        url = '{0}organisation/{1}/rate/'.format(
            service_directory_api_base_url,
            organisation_id
        )

        data = request.POST.dict()
        if 'csrfmiddlewaretoken' in data:
            data.pop('csrfmiddlewaretoken')  # no point passing this to the API

        make_request_to_servicedirectory_api(url, request, data=data)

        query_params = QueryDict('', mutable=True)
        query_params['msg'] = 'Thanks for telling us how helpful this service'\
                              ' was. You can always update your response when'\
                              ' you change your mind.'

        redirect_url = '{0}?{1}'.format(
            reverse('molo.servicedirectory:organisation-detail',
                    kwargs={'organisation_id': organisation_id}),
            query_params.urlencode()
        )

        return HttpResponseRedirect(redirect_to=redirect_url)


class OrganisationSendSmsView(TemplateView):
    template_name = 'servicedirectory/organisation_sms.html'

    def post(self, request, *args, **kwargs):
        service_directory_api_base_url =\
            get_service_directory_api_base_url(self.request)
        organisation_id = kwargs['organisation_id']

        url = '{0}organisation/sms/'.format(service_directory_api_base_url)

        data = request.POST.dict()
        data['organisation_url'] = request.build_absolute_uri(
            reverse('molo.servicedirectory:organisation-detail',
                    kwargs={'organisation_id': organisation_id})
        )

        if 'csrfmiddlewaretoken' in data:
            data.pop('csrfmiddlewaretoken')  # no point passing this to the API

        make_request_to_servicedirectory_api(url, request, data=data)

        query_params = QueryDict('', mutable=True)
        query_params['msg'] = 'Thanks! We''ve sent an SMS with a link for' \
                              ' this service to {0}.'.format(
            data['cell_number'])

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
