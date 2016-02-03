import base64
import json
import urllib2

from django.core.urlresolvers import reverse
from django.http import HttpResponse, QueryDict
from django.template import loader
from molo.servicedirectory import settings


def get_json_request_from_servicedirectory(url):
    api_request = urllib2.Request(url)

    basic_auth_username = settings.SERVICE_DIRECTORY_API_USERNAME
    basic_auth_password = settings.SERVICE_DIRECTORY_API_PASSWORD
    base64string = base64.encodestring(
        '{0}:{1}'.format(basic_auth_username, basic_auth_password)
    ).replace('\n', '')
    api_request.add_header("Authorization", "Basic {0}".format(base64string))

    serialized_data = urllib2.urlopen(api_request).read()

    json_result = json.loads(serialized_data)

    return json_result


def make_request_to_google_api(url, querydict):
    full_url = '{0}?{1}'.format(url, querydict.urlencode())

    api_request = urllib2.Request(full_url)

    serialized_data = urllib2.urlopen(api_request).read()

    json_result = json.loads(serialized_data)

    return json_result


def home(request):
    category = request.GET.get('category', None)

    if not category:
        categories_keywords_url = '{0}homepage_categories_keywords/'.format(
            settings.SERVICE_DIRECTORY_API_BASE_URL
        )
        categories_keywords = get_json_request_from_servicedirectory(
            categories_keywords_url
        )

    else:
        keywords_url = '{0}keywords/?{1}'.format(
            settings.SERVICE_DIRECTORY_API_BASE_URL, category
        )

        keywords = get_json_request_from_servicedirectory(
            keywords_url
        )

        categories_keywords = [
            {
                'name': category,
                'keywords': [keyword['name'] for keyword in keywords]
            }
        ]

    template = loader.get_template('servicedirectory/home.html')
    context = {
        'categories_keywords': categories_keywords,
        'and_more': not category,
    }

    return HttpResponse(template.render(context, request))


def location_search(request):
    search_term = request.GET['search']

    template = loader.get_template('servicedirectory/location_search.html')
    context = {
        'search_term': search_term,
    }
    return HttpResponse(template.render(context, request))


def location_results(request):
    search_term = request.GET['search']
    location_term = request.GET['location']

    google_query_parms = QueryDict('', mutable=True)
    google_query_parms['input'] = location_term
    google_query_parms['types'] = 'geocode'
    google_query_parms['key'] = settings.GOOGLE_PLACES_API_SERVER_KEY

    url = 'https://maps.googleapis.com/maps/api/place/autocomplete/json'

    autocomplete_suggestions = make_request_to_google_api(
        url, google_query_parms
    )

    template = loader.get_template('servicedirectory/location_results.html')
    context = {
        'search_term': search_term,
        'location_term': location_term,
        'autocomplete_suggestions': autocomplete_suggestions,

    }
    return HttpResponse(template.render(context, request))


def service_results(request):
    search_term = request.GET['search']
    location_term = request.GET['location']
    place_id = request.GET['place_id']
    place_latlng = request.GET.get('place_latlng', None)
    place_formatted_address = request.GET.get('place_formatted_address', None)

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
    service_directory_query_parms['keyword'] = search_term

    if place_latlng is not None:
        service_directory_query_parms['near'] = place_latlng

    url = '{0}service_lookup/?{1}'.format(
        settings.SERVICE_DIRECTORY_API_BASE_URL,
        service_directory_query_parms.urlencode()
    )
    search_results = get_json_request_from_servicedirectory(url)

    location_query_parms = QueryDict('', mutable=True)
    location_query_parms['location'] = location_term
    location_query_parms['search'] = search_term

    template = loader.get_template('servicedirectory/service_results.html')
    context = {
        'search_term': search_term,
        'location_term': location_term,
        'place_id': place_id,
        'place_latlng': place_latlng,
        'place_formatted_address': place_formatted_address,
        'change_location_url': '{0}?{1}'.format(
            reverse('location-results'), location_query_parms.urlencode()
        ),
        'search_results': search_results,
    }

    return HttpResponse(template.render(context, request))


def service_detail(request, service_id):
    service_directory_api_base_url = settings.SERVICE_DIRECTORY_API_BASE_URL

    url = '{0}service/{1}/'.format(service_directory_api_base_url, service_id)
    json_result = get_json_request_from_servicedirectory(url)

    template = loader.get_template('servicedirectory/service_detail.html')
    context = {
        'service': json_result
    }

    return HttpResponse(template.render(context, request))
