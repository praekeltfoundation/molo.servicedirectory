import base64
import json
import urllib2

from django.http import HttpResponse
from django.template import loader
from molo.servicedirectory import settings


def get_json_request_from_servicedirectory(url):
    api_request = urllib2.Request(url)

    basic_auth_username = settings.SERVICE_DIRECTORY_API_LOGIN['username']
    basic_auth_password = settings.SERVICE_DIRECTORY_API_LOGIN['password']
    base64string = base64.encodestring('{0}:{1}'.format(basic_auth_username, basic_auth_password)).replace('\n', '')
    api_request.add_header("Authorization", "Basic {0}".format(base64string))

    serialized_data = urllib2.urlopen(api_request).read()

    json_result = json.loads(serialized_data)

    return json_result


def home(request):
    template = loader.get_template('servicedirectory/home.html')
    context = {}
    return HttpResponse(template.render(context, request))


def result_summaries(request):
    search_term = request.GET['search']

    service_directory_api_base_url = settings.SERVICE_DIRECTORY_API_BASE_URL

    url = '{0}service_lookup/?keyword={1}'.format(service_directory_api_base_url, search_term)
    search_results = get_json_request_from_servicedirectory(url)

    template = loader.get_template('servicedirectory/result_summaries.html')
    context = {
        'search_term': search_term,
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
