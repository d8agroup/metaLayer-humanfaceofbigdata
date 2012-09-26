from random import randint
from django.shortcuts import render_to_response
from hfobd.solrbridge.models import FacetMapping
from hfobd.utils import JSONResponse
from django.conf import settings

def home(request):
    template_data = {
        'questions':FacetMapping.objects.filter(display_as_question=True),
    }
    return render_to_response('home.html', template_data)

def get_graph_data(request):
    facet_name = request.GET.get('facet_name')
    results = settings.SOLR.select('*:*', row=0, facet='true', facet_field=facet_name)
    graph_dict = results.facet_counts['facet_fields'][facet_name]
    graph_data = []
    for key in graph_dict.keys():
        graph_data.append({'key':key, 'y':graph_dict[key]})
    graph_data = sorted(graph_data, key=lambda x: x['y'])
    graph_data = graph_data[:10]
    return JSONResponse({ 'graph_data':graph_data})