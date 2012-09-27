from random import randint
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from hfobd.solrbridge.models import FacetMapping
from hfobd.utils import JSONResponse
from django.conf import settings

def home(request):
    template_data = {
        'questions':FacetMapping.objects.filter(display_as_question=True),
    }
    return render_to_response('home.html', template_data, context_instance=RequestContext(request))

def design1(request):
    template_data = {
        'questions':FacetMapping.objects.filter(display_as_question=True),
    }
    return render_to_response('design1.html', template_data, context_instance=RequestContext(request))

@csrf_exempt
def get_graph_data(request):
    facet_name = request.POST.get('facet_name')
    filters = request.POST.get('filters')
    if filters:
        filters = simplejson.loads(filters)
        query = ' AND '.join('%s:%s' % (f['facet_name'], f['facet_value']) for f in filters)
    else:
        query = "*:*"
    results = settings.SOLR.select(query, row=0, facet='true', facet_field=facet_name)
    graph_dict = results.facet_counts['facet_fields'][facet_name]
    graph_data = []
    for key in graph_dict.keys():
        graph_data.append({'label':key, 'value':graph_dict[key]})
    graph_data = sorted(graph_data, key=lambda x: x['value'])
    graph_data = graph_data[:10]
    question_display_name = FacetMapping.objects.get(facet_name=facet_name).display_name
    return JSONResponse({ 'graph_data':[{'key':question_display_name, 'values':graph_data}]})

@csrf_exempt
def add_a_filter(request):
    facet_mappings = FacetMapping.objects.filter(display_as_question=True)
    facet_fields = [f.facet_name for f in facet_mappings]
    filters = simplejson.loads(request.POST.get('filters'))
    if filters:
        query = ' AND '.join('%s:%s' % (f['facet_name'], f['facet_value']) for f in filters)
    else:
        query = "*:*"
    results = settings.SOLR.select(query, rows=0, facet='true', facet_field=facet_fields, facet_mincount=1)
    filters_from_solr = results.facet_counts['facet_fields']
    filters = []
    for facet_mapping in facet_mappings:
        filters.append({
            'display_name':facet_mapping.display_name,
            'facet_name':facet_mapping.facet_name,
            'facet_values':[k for k,v in filters_from_solr[facet_mapping.facet_name].items()]})
    template_data = {
        'filters':filters
    }
    return render_to_response('filter.html', template_data)