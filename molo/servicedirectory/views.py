import json
import base64

from django.contrib import messages
from django.utils.http import urlquote
from django.urls import reverse
from django.views.generic import TemplateView, View
from django.http import QueryDict, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from molo.core.models import SiteSettings
from molo.servicedirectory import settings as molo_settings

from six.moves.urllib.request import Request, urlopen


def get_service_directory_api_username(request):
    site = request._wagtail_site
    site_settings = SiteSettings.for_site(site)
    return (site_settings.service_directory_api_username or
            molo_settings.SERVICE_DIRECTORY_API_USERNAME)


def get_service_directory_api_password(request):
    site = request._wagtail_site
    site_settings = SiteSettings.for_site(site)
    return (site_settings.service_directory_api_password or
            molo_settings.SERVICE_DIRECTORY_API_PASSWORD)


def get_service_directory_api_base_url(request):
    site = request._wagtail_site
    site_settings = SiteSettings.for_site(site)
    return (site_settings.service_directory_api_base_url or
            molo_settings.SERVICE_DIRECTORY_API_BASE_URL)


def get_google_places_api_server_key(request):
    site = request._wagtail_site
    site_settings = SiteSettings.for_site(site)
    return (site_settings.google_places_api_server_key or
            molo_settings.GOOGLE_PLACES_API_SERVER_KEY)


def make_request_to_servicedirectory_api(url, request, data=None):
    if data is not None:
        data = json.dumps(data)

    api_request = Request(url, data=data)

    username = get_service_directory_api_username(request)
    password = get_service_directory_api_password(request)
    base64string = base64.encodestring(
        ('%s:%s' % (username, password)).encode()).decode().replace('\n', '')
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


class StepDataMixin(object):

    def get_data(self):
        site = self.request._wagtail_site
        site_settings = SiteSettings.for_site(site)
        self.radius = site_settings.default_service_directory_radius
        self.place_id = self.request.GET.get('place_id')
        self.search_term = self.request.GET.get('search')
        self.category = self.request.GET.get('category', None)
        self.location_term = self.request.GET.get('location', '')
        self.radius = self.request.GET.get('radius', self.radius)
        self.keywords = self.request.GET.getlist('keywords[]', [])
        self.place_latlng = self.request.GET.get('place_latlng', None)
        self.categories = self.request.GET.getlist('categories[]', [])
        self.all_categories = self.request.GET.getlist('all_categories')
        self.place_formatted_address = self.request.GET.get(
            'place_formatted_address', None
        )

    def get_form_data_context(self):
        context = dict()
        context['place_id'] = self.place_id
        context['keywords'] = self.keywords
        context['search_term'] = self.search_term
        context['place_latlng'] = self.place_latlng
        context['location_term'] = self.location_term
        context['categories'] = [
            int(i) for i in self.categories if i.isdigit()
        ]
        return context


class HomeView(StepDataMixin, TemplateView):
    template_name = 'servicedirectory/home.html'

    def get_context_data(self, **kwargs):
        self.get_data()
        context = super(HomeView, self).get_context_data(**kwargs)

        keywords = []
        keyword_list = None

        site = self.request._wagtail_site
        site_settings = SiteSettings.for_site(site)
        if site_settings.enable_multi_category_service_directory_search:
            keywords_url = '{0}keywords?show_on_home_page=True'.format(
                get_service_directory_api_base_url(self.request))

            keyword_list = make_request_to_servicedirectory_api(
                keywords_url, self.request)

        if not self.category:
            categories_keywords_url = '{0}homepage_categories_keywords/'\
                .format(get_service_directory_api_base_url(self.request))

            categories_keywords = make_request_to_servicedirectory_api(
                categories_keywords_url, self.request)

        else:
            service_directory_query_parms = QueryDict('', mutable=True)
            service_directory_query_parms['category'] = self.category

            keywords_url = '{0}keywords/?{1}'.format(
                get_service_directory_api_base_url(self.request),
                service_directory_query_parms.urlencode())

            keywords = make_request_to_servicedirectory_api(
                keywords_url, self.request)

            categories_keywords = [{
                'name': self.category,
                'keywords': [keyword['name'] for keyword in keywords]
            }]

        context['keywords'] = keywords
        context['and_more'] = not self.category
        context['keyword_list'] = keyword_list
        context['categories_keywords'] = categories_keywords
        context.update(self.get_form_data_context())
        return context


class LocationSearchView(StepDataMixin, TemplateView):
    template_name = 'servicedirectory/location_search.html'

    def dispatch(self, request, *args, **kwargs):
        site = request._wagtail_site
        site_settings = SiteSettings.for_site(site)

        multi_category_select = site_settings. \
            enable_multi_category_service_directory_search

        keywords = self.request.GET.getlist('keywords[]', [])
        categories = self.request.GET.getlist('categories[]', [])

        if multi_category_select and not any([keywords, categories]):
            messages.add_message(
                request, messages.ERROR,
                _("Please select at least one category or service")
            )

            search_url = '{}?{}'.format(
                reverse('molo.servicedirectory:home'),
                self.request.GET.urlencode()
            )
            return HttpResponseRedirect(redirect_to=search_url)

        return super(LocationSearchView, self)\
            .dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.get_data()
        context = super(LocationSearchView, self).get_context_data(**kwargs)
        context.update(self.get_form_data_context())
        return context


class LocationResultsView(StepDataMixin, TemplateView):
    template_name = 'servicedirectory/location_results.html'

    def dispatch(self, request, *args, **kwargs):

        if not self.request.GET.get('location'):
            messages.add_message(
                request, messages.ERROR, _("Please select a location")
            )

            search_url = '{}?{}'.format(
                reverse('molo.servicedirectory:location-search'),
                self.request.GET.urlencode()
            )
            return HttpResponseRedirect(redirect_to=search_url)

        return super(LocationResultsView, self)\
            .dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.get_data()
        context = super(LocationResultsView, self).get_context_data(**kwargs)

        google_query_parms = QueryDict('', mutable=True)
        google_query_parms['input'] = self.location_term
        google_query_parms['types'] = 'geocode'
        google_query_parms['key'] = get_google_places_api_server_key(
            self.request)

        url = 'https://maps.googleapis.com/maps/api/place/autocomplete/json'

        autocomplete_suggestions = make_request_to_google_api(
            url, google_query_parms
        )

        context['autocomplete_suggestions'] = autocomplete_suggestions
        context.update(self.get_form_data_context())
        return context


class OrganisationResultsView(StepDataMixin, TemplateView):
    template_name = 'servicedirectory/organisation_results.html'

    def dispatch(self, request, *args, **kwargs):
        site = request._wagtail_site
        site_settings = SiteSettings.for_site(site)

        multi_category_select = site_settings. \
            enable_multi_category_service_directory_search

        keywords = self.request.GET.getlist('keywords[]', [])
        categories = self.request.GET.getlist('categories[]', [])

        if multi_category_select and not any([keywords, categories]):
            messages.add_message(
                request, messages.ERROR,
                _("Please select at least one category or service")
            )

            search_url = '{}?{}'.format(
                reverse('molo.servicedirectory:home'),
                self.request.GET.urlencode()
            )
            return HttpResponseRedirect(redirect_to=search_url)

        return super(OrganisationResultsView, self)\
            .dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.get_data()
        context = super(OrganisationResultsView, self).get_context_data(
            **kwargs
        )

        if self.place_latlng is None:
            google_query_parms = QueryDict('', mutable=True)
            google_query_parms['placeid'] = self.place_id
            google_query_parms['key'] = get_google_places_api_server_key(
                self.request)

            url = 'https://maps.googleapis.com/maps/api/place/details/json'
            place_details = make_request_to_google_api(url, google_query_parms)

            place_details_result = place_details.get('result', {})

            self.place_formatted_address = place_details_result.get(
                'formatted_address', None
            )
            self.place_location = place_details_result.get(
                'geometry', {}
            ).get('location', None)

            if self.place_location:
                self.place_latlng = '{0},{1}'.format(
                    self.place_location['lat'], self.place_location['lng']
                )

        service_directory_query_parms = QueryDict('', mutable=True)
        service_directory_query_parms['radius'] = self.radius
        service_directory_query_parms['search_term'] = self.search_term

        if self.place_latlng:
            service_directory_query_parms['location'] = self.place_latlng

        if self.all_categories:
            service_directory_query_parms[
                'all_categories'] = self.all_categories

        if self.place_formatted_address is not None:
            service_directory_query_parms['place_name'] =\
                self.place_formatted_address

        url = '{0}search/?{1}'.format(
            get_service_directory_api_base_url(self.request),
            service_directory_query_parms.urlencode()
        )

        for keyword in self.keywords:
            url += '&keywords[]={}'.format(urlquote(keyword))

        for category in self.categories:
            url += '&categories[]={}'.format(urlquote(category))

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
        location_query_parms['location'] = self.location_term
        location_query_parms['search'] = self.search_term

        context['place_formatted_address'] = self.place_formatted_address
        context['change_location_url'] = '{0}?{1}'.format(
            reverse('molo.servicedirectory:location-results'),
            location_query_parms.urlencode()
        )
        context['search_results'] = search_results
        context['categories_keywords'] = categories_keywords
        context.update(self.get_form_data_context())
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
