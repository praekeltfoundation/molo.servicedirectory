import base64
import json
import urllib2

from django.shortcuts import render

from django.template import loader

from django.http import HttpResponse
from molo.servicedirectory import settings


def index(request):
    template = loader.get_template('servicedirectory/index.html')
    context = {}
    return HttpResponse(template.render(context, request))

def home(request):
    template = loader.get_template('servicedirectory/home.html')
    context = {}
    return HttpResponse(template.render(context, request))

def result_summaries(request):
    search_term = request.GET['search']

    service_directory_api_base_url = settings.SERVICE_DIRECTORY_API_BASE_URL

    url = '{0}service_lookup/?keyword={1}'.format(service_directory_api_base_url, search_term)

    api_request = urllib2.Request(url)

    basic_auth_username = settings.SERVICE_DIRECTORY_API_LOGIN['username']
    basic_auth_password = settings.SERVICE_DIRECTORY_API_LOGIN['password']
    base64string = base64.encodestring('{0}:{1}'.format(basic_auth_username, basic_auth_password)).replace('\n', '')
    api_request.add_header("Authorization", "Basic {0}".format(base64string))

    serialized_data = urllib2.urlopen(api_request).read()

    search_results = json.loads(serialized_data)

    template = loader.get_template('servicedirectory/result_summaries.html')
    context = {
        'search': search_term,
        'result_json': search_results,
    }

    return HttpResponse(template.render(context, request))
