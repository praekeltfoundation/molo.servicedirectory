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
    template = loader.get_template('servicedirectory/result_summaries.html')
    context = {}
    return HttpResponse(template.render(context, request))
