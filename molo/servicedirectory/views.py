import base64
import urllib2

from django.shortcuts import render

from django.template import loader

from django.http import HttpResponse

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

    url = 'http://0.0.0.0:8000/api/service_lookup/?keyword={0}'.format(search_term)

    api_request = urllib2.Request(url)
    base64string = base64.encodestring('{0}:{1}'.format('root', 'adminadmin')).replace('\n', '')
    api_request.add_header("Authorization", "Basic {0}".format(base64string))

    serialized_data = urllib2.urlopen(api_request).read()


    template = loader.get_template('servicedirectory/result_summaries.html')
    context = {
        'search': search_term,
        'result_json': serialized_data,
    }



    return HttpResponse(template.render(context, request))
