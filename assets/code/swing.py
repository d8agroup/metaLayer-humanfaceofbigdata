import os
from django.conf import settings
from hfobd.solrbridge.models import FacetMapping
solr = settings.SOLR

def two_facet_swing(min_swing = 10, max_swing = 19, output_file=None):
    if output_file:
        try:
            os.unlink(output_file)
        except Exception:
            pass
        f = open(output_file, 'wb')
        f.close()

    exclude = [
        'How many languages do you speak fluently?',
        'How much time do you spend alone each day?',
        'I usually average X hours sleep each night',
        'I was X years old when I got married',
        'Where do you live? (City and State/Country)',
        'lat',
        'lon',
        'How many generations currently live in your household?',
        "What's your Age?",
        "In general, I do/do not feel that life has been fair to me",
        "Select how obedient or independent you think children should be"]
    all_facets = [f for f in FacetMapping.objects.filter(display_as_question=True) if f.display_name not in exclude]
    for outer_facet in all_facets:
        outer_response = solr.select('*:*', rows=0, facet='true', facet_mincount=1, facet_field=outer_facet.facet_name)
        facet_values = outer_response.facet_counts['facet_fields'][outer_facet.facet_name]
        outer_response_data = [{'facet_name':key, 'percent':int(100*(float(value)/sum(v for v in facet_values.values())))} for key, value in facet_values.items()]
        outputs = []
        for inner_facet in all_facets:
            if inner_facet.facet_name == outer_facet.facet_name:
                continue
            pivot_key = '%s,%s' % (inner_facet.facet_name, outer_facet.facet_name)
            inner_response = solr.select('*:*', rows=0, facet='true', facet_mincount=1, facet_pivot=pivot_key)
            for pivot in inner_response.facet_counts['facet_pivot'][pivot_key]:
                for filter in pivot['pivot']:
                    try:
                        original_percent = [o['percent'] for o in outer_response_data if o['facet_name'] == filter['value']][0]
                    except IndexError:
                        continue
                    filter_percent = int(100*(float(filter['count'])/sum(f['count'] for f in pivot['pivot'])))
                    difference = original_percent - filter_percent
                    if ((-1*max_swing) < difference < (-1*min_swing)) or (min_swing > difference > max_swing):
                        original_question = outer_facet.display_name
                        original_answer = filter['value']
                        filter_question = [f.display_name for f in all_facets if f.facet_name == pivot['field']][0]
                        filter_answer = pivot['value']
                        output = '%s,%s,' % (original_question.replace(',', ' '), original_answer.replace(',',' '))
#                        while len(output) < 100:
#                            output += ' '
#                        output += ' >> %s : %s' % (filter_question, filter_answer)
                        output += '%s,%s,' % (filter_question.replace(',',' '), filter_answer.replace(',',' '))
#                        while len(output) < 200:
#                            output += ' '
#                        output += '%i%s swing (from %i%s to %i%s)' % ((-1*difference), '%', original_percent, '%', filter_percent, '%')
                        output += '%i,%i,%i' % ((-1*difference), original_percent, filter_percent)
                        outputs.append(output)
        if outputs:
            outputs = sorted(outputs)
            if output_file:
                with open('%s.wip' % output_file, 'a') as f:
                    f.writelines([o + '\n' for o in outputs])
            else:
                print ''
                for o in outputs:
                    print o
    if output_file:
        os.unlink(output_file)
        os.rename('%s.wip' % output_file, output_file)

def by_subject(subject_facet='areyoumaleorfemale_s', min_swing=1, max_swing=99, output_file=None):
    if output_file:
        try:
            os.unlink(output_file)
        except Exception:
            pass
        f = open(output_file, 'wb')
        f.close()

    exclude = [
        'How many languages do you speak fluently?',
        'How much time do you spend alone each day?',
        'I usually average X hours sleep each night',
        'I was X years old when I got married',
#        'Where do you live? (City and State/Country)',
        'lat',
        'lon',
        'How many generations currently live in your household?',
        "What's your Age?",
        "In general, I do/do not feel that life has been fair to me",
        "Select how obedient or independent you think children should be"]
    all_facets = [f for f in FacetMapping.objects.filter(display_as_question=True) if f.display_name not in exclude]
    for outer_facet in all_facets:
        outer_response = solr.select('*:*', rows=0, facet='true', facet_mincount=1, facet_field=outer_facet.facet_name)
        facet_values = outer_response.facet_counts['facet_fields'][outer_facet.facet_name]
        outer_response_data = [{'facet_name':key, 'percent':int(100*(float(value)/sum(v for v in facet_values.values())))} for key, value in facet_values.items()]
        outputs = []
        pivot_key = '%s,%s' % (subject_facet, outer_facet.facet_name)
        pivot_response = solr.select('*:*', rows=0, facet='true', facet_mincount=1, facet_pivot=pivot_key)
        for pivot in pivot_response.facet_counts['facet_pivot'][pivot_key]:
            for filter in pivot['pivot']:
                try:
                    original_percent = [o['percent'] for o in outer_response_data if o['facet_name'] == filter['value']][0]
                except IndexError:
                    continue
                filter_percent = int(100*(float(filter['count'])/sum(f['count'] for f in pivot['pivot'])))
                difference = original_percent - filter_percent
                if ((-1*max_swing) < difference < (-1*min_swing)) or (min_swing > difference > max_swing):
                    original_question = outer_facet.display_name
                    original_answer = filter['value']
                    filter_question = [f.display_name for f in all_facets if f.facet_name == pivot['field']][0]
                    filter_answer = pivot['value']
                    output = '%s : %s' % (original_question, original_answer)
                    while len(output) < 100:
                        output += ' '
                    output += ' >> %s : %s' % (filter_question, filter_answer)
                    while len(output) < 200:
                        output += ' '
                    output += '%i%s swing (from %i%s to %i%s)' % ((-1*difference), '%', original_percent, '%', filter_percent, '%')
                    outputs.append(output)
        if outputs:
            outputs = sorted(outputs)
            if output_file:
                with open('%s.wip' % output_file, 'a') as f:
                    f.writelines([o + '\n' for o in outputs])
            else:
                print ''
                for o in outputs:
                    print o
    if output_file:
        os.unlink(output_file)
        os.rename('%s.wip' % output_file, output_file)

