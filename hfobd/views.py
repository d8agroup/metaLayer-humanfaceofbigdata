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

def design2(request):
    template_data = {
        'questions':FacetMapping.objects.filter(display_as_question=True),
    }
    return render_to_response('design2.html', template_data, context_instance=RequestContext(request))

@csrf_exempt
def get_graph_data(request):
    facet_name = request.POST.get('facet_name')
    filters = request.POST.get('filters')
    if filters and filters != '[]':
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
def get_graph_data2(request):
    chart_area_id = request.POST.get('chart_area_id')
    search_data = request.POST.get('search_data')
    search_data = simplejson.loads(search_data)
    questions = search_data['questions']
    return_data = { 'chart_area_id':chart_area_id, 'graph_data':[] }
    query = "*:*"
    if len(questions) == 1:
        return_data['graph_type'] = 'pie'
        facet_names = [q['facet_name'] for q in questions]
        results = settings.SOLR.select(query, row=0, facet='true', facet_field=facet_names)
        for question in questions:
            facet_name = question['facet_name']
            graph_dict = results.facet_counts['facet_fields'][facet_name]
            graph_data = [{'label':key, 'value':value} for key, value in graph_dict.items()]
            graph_data = sorted(graph_data, key=lambda x: x['value'])
            graph_data = graph_data[:10]
            return_data['graph_data'].append({'key':question['display_name'], 'values':graph_data})
            return_data['graph_colors'] = generate_color_pallet(len(graph_data))
    else:
        facet_pivot = ','.join(q['facet_name'] for q in questions)
        results = settings.SOLR.select(query, row=0, facet='true', facet_pivot=facet_pivot)
        pivot_data = {}
        for x_axis_field in results.facet_counts['facet_pivot'][facet_pivot]:
            for y_axis_field in x_axis_field['pivot']:
                facet_field = y_axis_field['field']
                facet_field_display_name = [q['display_name'] for q in questions if q['facet_name'] == facet_field][0]
                facet_value = y_axis_field['value']
                facet_field_display_name += ': %s' % facet_value
                if facet_field_display_name not in pivot_data.keys():
                    pivot_data[facet_field_display_name] = []
                pivot_data[facet_field_display_name].append({ 'label':x_axis_field['value'], 'value':y_axis_field['count']})
        return_data['graph_data'] = [{'key':key.split(':')[-1].strip(), 'values':value} for key, value in pivot_data.items()]
#        colors = generate_color_pallet(len(return_data['graph_data']))
#        for x in range(return_data['graph_data']):
#            return_data['graph_data'][x]['color'] = colors[x]
    return JSONResponse(return_data)

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

def generate_color_pallet(number_needed):
    start_rgb = (216, 229, 39)
    end_rgb = (112, 120, 21)
    gaps = ((start_rgb[0] - end_rgb[0]) / number_needed,(start_rgb[1] - end_rgb[1]) / number_needed,(start_rgb[2] - end_rgb[2]) / number_needed)
    colors = []
    for x in range(number_needed):
        colors.append(((start_rgb[0] - (gaps[0] * x)), (start_rgb[1] - (gaps[1] * x)), (start_rgb[2] - (gaps[2] * x))))
    return ['#' + format((c[0]<<16)|(c[1]<<8)|c[2], '06x') for c in colors]
