import StringIO
from random import randint
from urllib import quote
from django.core.mail.message import EmailMessage
from django.core.validators import email_re
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
import time
from hfobd.savedinsights.models import SavedInsight
from hfobd.solrbridge.models import FacetMapping
from hfobd.utils import JSONResponse
from django.conf import settings
from hashlib import md5
from PIL import Image

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
    questions = [q for q in FacetMapping.objects.filter(display_as_question=True)]
    questions.insert(0, {
        'display_name':'Mission Control Country',
        'facet_name':'country_s',
        'display_as_question':True
    })
    template_data = { 'questions': questions, }
    return render_to_response('create.html', template_data, context_instance=RequestContext(request))


@csrf_exempt
def get_graph_data3(request):
    chart_area_id = request.POST.get('chart_area_id')
    search_data = request.POST.get('search_data')
    search_data = simplejson.loads(search_data)
    questions = search_data['questions']
    filters = search_data['filters']
    return_data = { 'chart_area_id':chart_area_id, 'graph_data':{}, 'filters':{} }
    if len([f for f in filters if 'facet_value' in f and f['facet_value']]):
        query = ' AND '.join('%s:"%s"' % (f['facet_name'], f['facet_value']) for f in filters if 'facet_value' in f and f['facet_value'])
    else:
        query = "*:*"
    if len(questions) == 1:
        return_data['graph_type'] = 'pie'
        facet_names = [q['facet_name'] for q in questions]
        facet_names += [f['facet_name'] for f in filters]

        results = settings.SOLR.select(query, row=0, facet='true', facet_field=facet_names, facet_limit=100)
        for question in questions:
            facet_name = question['facet_name']
            if facet_name == False:#'country_s':
                graph_data = [{'label':c[0], 'value':c[1]} for c in [('United States', 70), ('United Kingdom', 20), ('Singapore', 10)]]
            else:
                graph_dict = results.facet_counts['facet_fields'][facet_name]
                graph_data = [{'label':key, 'value':int(100*(float(value)/sum(v for v in graph_dict.values())))} for key, value in graph_dict.items()]
                graph_data = sorted(graph_data, key=lambda x: x['value'], reverse=True)
                graph_data = graph_data[:10]
                graph_data = sorted(graph_data, key=lambda x: x['label'])
            return_data['graph_data'] = {
                'key':question['display_name'],
                'values':[[g['label'], g['value']] for g in graph_data],
                'labels':['%s : %i%s' % (g['label'], g['value'], "%") for g in graph_data]}
            return_data['graph_colors'] = generate_color_pallet(len(graph_data), 'green' if chart_area_id == 'chart_area_one' else 'orange')
            for f in filters:
                filter_facet_name = f['facet_name']
                if filter_facet_name == False:#'country_s':
                    if 'facet_value' in f and f['facet_value']:
                        filter_graph_data = [{'label':f['facet_value'], 'value':100}]
                    else:
                        filter_graph_data = [{'label':c[0], 'value':c[1]} for c in [('United States', 70), ('United Kingdom', 20), ('Singapore', 10)]]
                else:
                    filter_graph_dict = results.facet_counts['facet_fields'][filter_facet_name]
                    filter_graph_data = [{'label':key, 'value':int(100*(float(value)/sum(v for v in filter_graph_dict.values())))} for key, value in filter_graph_dict.items()]
                    filter_graph_data = sorted(filter_graph_data, key=lambda x: x['value'], reverse=True)
                    filter_graph_data = filter_graph_data[:10]
                    filter_graph_data = sorted(filter_graph_data, key=lambda x: x['label'], reverse=True)
                return_data['filters'][filter_facet_name] = {
                    'key':f['display_name'],
                    'colors':generate_color_pallet(len(filter_graph_data), 'blue') if not ('facet_value' in f and f['facet_value']) else generate_color_pallet(len(filter_graph_data), 'grey'),
                    'values':[[g['label'], g['value']] for g in filter_graph_data],
                    'labels':['%s : %i%s' % (g['label'], g['value'], "%") for g in filter_graph_data],
                    'is_selected':bool('facet_value' in f and f['facet_value'])}



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

def chart_area(request):
    return render_to_response('chart_area.html')

def gallery(request, image_id=None):
    template_data = {
        'gallery_images':SavedInsight.Gallery()
    }
    if image_id:
        template_data['image_id'] = image_id
        if request.GET.get('action') == 'save':
            SavedInsight.SetAsVisible(image_id)
            return render_to_response('gallery_images.html', {'gallery_images':SavedInsight.Gallery()})
        if request.GET.get('action') == 'delete':
            SavedInsight.SetAsInvisible(image_id)
            return render_to_response('gallery_images.html', {'gallery_images':SavedInsight.Gallery()})
    return render_to_response('gallery.html', template_data, context_instance=RequestContext(request))

def save_and_share(request):
    def write_image(image_data, file_name):
        import re
        imgstr = re.search(r'base64,(.*)', image_data).group(1)
        output = open(settings.MEDIA_ROOT + file_name, 'wb')
        output.write(imgstr.decode('base64'))
        output.close()


    data = request.POST['data']
    data = simplejson.loads(data)

    final_image_config = {'title':request.POST.get('title'), 'author':request.POST.get('author'), 'left':{}, 'right':{} }

    guid = data['guid']
    for side in ['left', 'right']:
        if data[side]:
            final_image_config[side] = { 'main_question':data[side]['main_question'], 'filters':[] }
            main_image_id = '%s_%s_main_chart.png' % (guid, side)
            final_image_config[side]['main_chart'] = main_image_id
            write_image(data[side]['main_chart'], main_image_id)
            for x in range(len(data[side]['filters'])):
                filter_image_id = '%s_%s_filter_image_%i.png' % (guid, side, x+1)
                final_image_config[side]['filters'].append({
                    'facet_name':data[side]['filters'][x]['facet_name'],
                    'facet_value':data[side]['filters'][x]['facet_value'] if 'facet_value' in data[side]['filters'][x] else None,
                    'display_name':data[side]['filters'][x]['display_name'],
                    'chart':filter_image_id
                })
                write_image(data[side]['filters'][x]['chart'], filter_image_id)

    import cairo
    width = 1024
    height = 756
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1024, 756)
    context = cairo.Context(surface)
    context.set_source_rgb(0.20, 0.22, 0.24)
    context.rectangle(0, 0, width, height)
    context.fill()
    context.set_source_rgb(0.22, 0.26, 0.31)
    context.rectangle(0,0, width, 100)
    context.fill()
    image_surface = cairo.ImageSurface.create_from_png(settings.MEDIA_ROOT + '../images/header_left.png')
    context.set_source_surface(image_surface)
    context.paint()
    image_surface = cairo.ImageSurface.create_from_png(settings.MEDIA_ROOT + '../images/header_right.png')
    context.set_source_surface(image_surface, 471, 0)
    context.paint()
    image_surface = cairo.ImageSurface.create_from_png(settings.MEDIA_ROOT + '../images/header_center.png')
    context.set_source_surface(image_surface, 417, 0)
    context.paint()

    #Title
    text = final_image_config['title']
    context.set_source_rgb(1.0, 1.0, 1.0)
    context.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    context.set_font_size(20)
    x, y, w, h = context.text_extents(text)[:4]
    context.move_to((width / 2) - (w / 2) - x, 135)
    context.show_text(text)

    #Author
    text = final_image_config['author']
    context.set_source_rgb(1.0, 1.0, 1.0)
    context.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    context.set_font_size(12)
    x, y, w, h = context.text_extents(text)[:4]
    context.move_to((width / 2) - (w / 2) - x, 165)
    context.show_text(text)

    for side in [('left', 0), ('right', 512)]:

        context.set_source_rgb(0.85,0.85,0.85)
        context.rectangle(6 + side[1], 180, 502, 565)
        context.fill()
        context.set_source_rgb(0.11, 0.13, 0.16)
        context.rectangle(7 + side[1], 181, 500, 563)
        context.fill()
        image_surface = cairo.ImageSurface.create_from_png(settings.MEDIA_ROOT + '../images/callout_dark_selected_small.png')
        context.set_source_surface(image_surface, 17 + side[1], 335)
        context.paint()
    
        #question
        if 'main_question' in final_image_config[side[0]]:
            context.set_font_size(8)
            context.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            context.set_source_rgb(1.0, 1.0, 1.0)
            text = final_image_config[side[0]]['main_question']
            text_pieces = text.split(' ')
            words_used = 0
            row = 0
            while words_used < len(text_pieces):
                w = a = 0
                while w < 120 and a <len(text_pieces):
                    t = ' '.join(text_pieces[words_used:words_used+a])
                    x, w, w, h = context.text_extents(t)[:4]
                    a+=1

                context.move_to(30 + side[1], 350 + (row * 12))
                context.show_text(' '.join(text_pieces[words_used:words_used+a-2]))
                words_used += a-2
                row += 1

        if 'main_chart' in final_image_config[side[0]]:
            image_surface = cairo.ImageSurface.create_from_png(settings.MEDIA_ROOT + final_image_config[side[0]]['main_chart'])
            context.set_source_surface(image_surface, 152 + side[1], 181)
            context.paint()

        #Author
        text = 'Filters'
        context.set_source_rgb(0.18, 0.19, 0.25)
        context.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        context.set_font_size(25)
        context.move_to(30 + side[1], 530)
        context.show_text(text)

        if 'filters' in final_image_config[side[0]]:
            for b in range(len(final_image_config[side[0]]['filters'])):
                context.set_font_size(10)
                context.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                context.set_source_rgb(1.0, 1.0, 1.0)
                text = final_image_config[side[0]]['filters'][b]['display_name']
                text_pieces = text.split(' ')
                words_used = 0
                row = 0
                while words_used <= len(text_pieces):
                    w = a = 0
                    while w < 120 and a <len(text_pieces):
                        t = ' '.join(text_pieces[words_used:words_used + a])
                        x, w, w, h = context.text_extents(t)[:4]
                        a += 1

                    left = 7 + 17 + (b*150) + 20 + side[1]
                    context.move_to(left, 550 + (row * 14))
                    context.show_text(' '.join(text_pieces[words_used:words_used + a-1]))
                    words_used += a-1
                    row += 1


                image_surface = cairo.ImageSurface.create_from_png(settings.MEDIA_ROOT + final_image_config[side[0]]['filters'][b]['chart'])
                left = 7 + 17 + (b*150) + side[1]
                context.set_source_surface(image_surface, left, 590)
                context.paint()
    

    string_io = StringIO.StringIO()
    surface.write_to_png(string_io)
    string_io.seek(0)
    image_path = settings.MEDIA_ROOT + '%s.png' % guid
    output = open(image_path, 'wb')
    output.write(string_io.read())
    output.close()
    image = Image.open(image_path)
    image.thumbnail((614, 453), Image.ANTIALIAS)
    image.save(image_path.replace('.png', '_medium.png'))
    image.thumbnail((200, 148), Image.ANTIALIAS)
    image.save(image_path.replace('.png', '_small.png'))
    SavedInsight.Create(guid, final_image_config['title'], final_image_config['author'], request.POST['data'])
    return redirect('/gallery/'+ guid)

def download(request, image_id):
    saved_insight = SavedInsight.objects.get(image_id=image_id)
    image = Image.open(settings.MEDIA_ROOT + image_id + '.png')
    response = HttpResponse(mimetype='image/png')
    file_name = ''.join([s for s in saved_insight.title if s.isalnum()]) or 'HumanFaceOfBigData_MetaLayer'
    response['Content-Disposition'] = 'attachment; filename=%s.png' % file_name
    image.save(response, 'png')
    return response

def email(request, image_id, email_address):
    if not email_re.match(email_address):
        return HttpResponse()
    saved_insight = SavedInsight.objects.get(image_id=image_id)
    image_data = open(settings.MEDIA_ROOT + image_id + '.png', 'rb')
    image_title = ''.join([s for s in saved_insight.title if s.isalnum()]) or 'HumanFaceOfBigData_MetaLayer'
    subject = 'Human Face of Big Data & MetaLayer - Insight: %s' % (saved_insight.title or 'Untitled')
    body = """
        Thank you for taking the time to explore the Human Face of Big Data project with MetaLayer! \n
        \n
        The insight you chose to download is attached to this email.\n
        \n
        \tThis insight is titled: %s\n
        \tAnd was created by: %s\n
        \n
        Thanks!
        """ % (saved_insight.title or 'Untitled', saved_insight.author or 'No Author')
    email = EmailMessage(subject, body, 'team@metalayer.com', [email_address], attachments=[(image_title + '.png', image_data.read(), 'image/png')])
    image_data.close()
    email.send()
    return HttpResponse()


def generate_color_pallet(number_needed, color='green'):
    if color == 'orange':
        start_rgb = (255, 146, 1)
        end_rgb = (193, 78, 23)
    elif color == 'blue':
        start_rgb = (0, 185, 255)
        end_rgb = (38, 81, 98)
    elif color == 'grey':
        return ['#00adee' for x in range(number_needed)]
    else:
        start_rgb = (216, 229, 39)
        end_rgb = (112, 120, 21)
    gaps = ((start_rgb[0] - end_rgb[0]) / number_needed,(start_rgb[1] - end_rgb[1]) / number_needed,(start_rgb[2] - end_rgb[2]) / number_needed)
    colors = []
    for x in range(number_needed):
        colors.append(((start_rgb[0] - (gaps[0] * x)), (start_rgb[1] - (gaps[1] * x)), (start_rgb[2] - (gaps[2] * x))))
    return ['#' + format((c[0]<<16)|(c[1]<<8)|c[2], '06x') for c in colors]


def data_push(request):
    if request.GET.get('password') != 'hfobd':
        return
    from hfobd.solrbridge.controllers import SolrController
    import csv
    lines = [l for l in csv.reader(open('/usr/local/metaLayer-humanfaceofbigdata/humanfaceofbigdata/assets/data/rich_export_02.csv', 'rb'))]
    #lines = [l for l in csv.reader(open('assets/data/rich_export_01.csv', 'rb'))]
    headers = lines[0]
    lines = lines[1:]
    SolrController.PushTabularData(headers, lines)
    from hfobd.solrbridge.models import FacetMapping
    for display_name in ['Worker', 'Time (seconds)', 'If I could live forever I would/would not?']:
        f = FacetMapping.objects.get(display_name=display_name)
        f.display_as_question = False
        f.save()

def globe(request, facet_name=None):
    if facet_name:
        facet_pivot = 'raw_coordinates_s,%s' % facet_name
        results = settings.SOLR.select('*:*', rows=0, facet='true', facet_pivot=facet_pivot, facet_limit=1000)
        pivot_data = {}
        for x_axis_field in results.facet_counts['facet_pivot'][facet_pivot]:
            for y_axis_field in x_axis_field['pivot']:
                facet_value = y_axis_field['value']
                if facet_value not in pivot_data.keys():
                    pivot_data[facet_value] = []
                pivot_data[facet_value].append({ 'label':x_axis_field['value'], 'value':y_axis_field['count']})

        return_data = { 'legend':[], 'data':[] }
        for x in range(len(pivot_data.keys())):
            key = pivot_data.keys()[x]
            color = x
            return_data['legend'].append({'color':color, 'label':key})
            for value in pivot_data[key]:
                return_data['data'].append('%s' % (float(value['label'].split(',')[0]) + x))
                return_data['data'].append('%s' % (float(value['label'].split(',')[1]) + x))
                return_data['data'].append((1.0/value['value'])/3)
                return_data['data'].append(color)

        return HttpResponse(simplejson.dumps(return_data), content_type='application/json')


    template_data = {
        'questions':FacetMapping.objects.filter(display_as_question=True),
    }
    return render_to_response('globe.html', template_data, context_instance=RequestContext(request))


#@csrf_exempt
#def get_graph_data(request):
#    facet_name = request.POST.get('facet_name')
#    filters = request.POST.get('filters')
#    if filters and filters != '[]':
#        filters = simplejson.loads(filters)
#        query = ' AND '.join('%s:%s' % (f['facet_name'], f['facet_value']) for f in filters)
#    else:
#        query = "*:*"
#    results = settings.SOLR.select(query, row=0, facet='true', facet_field=facet_name)
#    graph_dict = results.facet_counts['facet_fields'][facet_name]
#    graph_data = []
#    for key in graph_dict.keys():
#        graph_data.append({'label':key, 'value':graph_dict[key]})
#    graph_data = sorted(graph_data, key=lambda x: x['value'])
#    graph_data = graph_data[:10]
#    question_display_name = FacetMapping.objects.get(facet_name=facet_name).display_name
#    return JSONResponse({ 'graph_data':[{'key':question_display_name, 'values':graph_data}]})
#
#@csrf_exempt
#def get_graph_data2(request):
#    chart_area_id = request.POST.get('chart_area_id')
#    search_data = request.POST.get('search_data')
#    search_data = simplejson.loads(search_data)
#    questions = search_data['questions']
#    filters = search_data['filters']
#    return_data = { 'chart_area_id':chart_area_id, 'graph_data':[], 'filters':{} }
#    query = "*:*"
#    if len(questions) == 1:
#        return_data['graph_type'] = 'pie'
#        facet_names = [q['facet_name'] for q in questions]
#        facet_names += [f['facet_name'] for f in filters]
#        results = settings.SOLR.select(query, row=0, facet='true', facet_field=facet_names)
#        for question in questions:
#            facet_name = question['facet_name']
#            graph_dict = results.facet_counts['facet_fields'][facet_name]
#            graph_data = [{'label':key, 'value':int(100*(float(value)/sum(v for v in graph_dict.values())))} for key, value in graph_dict.items()]
#            graph_data = sorted(graph_data, key=lambda x: x['value'])
#            graph_data = graph_data[:10]
#            return_data['graph_data'].append({'key':question['display_name'], 'values':graph_data})
#            return_data['graph_colors'] = generate_color_pallet(len(graph_data))
#            for f in filters:
#                filter_facet_name = f['facet_name']
#                filter_graph_dict = results.facet_counts['facet_fields'][filter_facet_name]
#                filter_graph_data = [{'label':key, 'value':int(100*(float(value)/sum(v for v in filter_graph_dict.values())))} for key, value in filter_graph_dict.items()]
#                filter_graph_data = sorted(filter_graph_data, key=lambda x: x['value'])
#                filter_graph_data = filter_graph_data[:10]
#                return_data['filters'][filter_facet_name] = [{'key':f['display_name'], 'values':filter_graph_data }]
#
#
#
#    else:
#        facet_pivot = ','.join(q['facet_name'] for q in questions)
#        results = settings.SOLR.select(query, row=0, facet='true', facet_pivot=facet_pivot)
#        pivot_data = {}
#        for x_axis_field in results.facet_counts['facet_pivot'][facet_pivot]:
#            for y_axis_field in x_axis_field['pivot']:
#                facet_field = y_axis_field['field']
#                facet_field_display_name = [q['display_name'] for q in questions if q['facet_name'] == facet_field][0]
#                facet_value = y_axis_field['value']
#                facet_field_display_name += ': %s' % facet_value
#                if facet_field_display_name not in pivot_data.keys():
#                    pivot_data[facet_field_display_name] = []
#                pivot_data[facet_field_display_name].append({ 'label':x_axis_field['value'], 'value':y_axis_field['count']})
#        return_data['graph_data'] = [{'key':key.split(':')[-1].strip(), 'values':value} for key, value in pivot_data.items()]
##        colors = generate_color_pallet(len(return_data['graph_data']))
##        for x in range(return_data['graph_data']):
##            return_data['graph_data'][x]['color'] = colors[x]
#    return JSONResponse(return_data)