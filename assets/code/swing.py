import os
import csv
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
        "Select how obedient or independent you think children should be",
        "Would you kill another person if your life depended on it?"]
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
        "Select how obedient or independent you think children should be",
        "Would you kill another person if your life depended on it?"]
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

def all_by_demographic(demographic='areyoumaleorfemale_s', output_file=None):
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
        'lat',
        'lon',
        'How many generations currently live in your household?',
        "What's your Age?",
        "In general, I do/do not feel that life has been fair to me",
        "Select how obedient or independent you think children should be",
        "Would you kill another person if your life depended on it?"]
    all_facets = [f for f in FacetMapping.objects.filter(display_as_question=True) if f.display_name not in exclude]
    demographic_response = solr.select('*:*', facet='true', facet_field=demographic)
    demographic_values = [key for key in demographic_response.facet_counts['facet_fields'][demographic].keys()]
    full_output = {}
    for demographic_value in demographic_values:
        demographic_value_response = solr.select('%s:%s' % (demographic, demographic_value), facet='true', facet_field=[f.facet_name for f in all_facets])
        for facet_field in demographic_value_response.facet_counts['facet_fields'].keys():
            if facet_field not in full_output:
                full_output[facet_field] = {'question':[f.display_name for f in all_facets if f.facet_name == facet_field][0]}
            full_output[facet_field][demographic_value] = demographic_value_response.facet_counts['facet_fields'][facet_field]
    if not output_file:
        print full_output
        return
    with open(output_file, 'wb') as f:
#        csv_writer = csv.writer(csv_file)
#        all_lines = full_output.values()
#        csv_writer.writerow([''] + [l['question'] for l in all_lines])
#        for demographic_value in demographic_values:
#            csv_writer.writerow([demographic_value] + [l[demo]])
        cell_width = 30

        for group in question_split.keys():
            all_lines = []
            for key, value in full_output.items():
                if key in question_split[group]:
                    all_lines.append(value)
            f.write(group.upper() + '\n')
            f.write(''.join('=' for x in range(len(group))) + '\n\n')
            for line in all_lines:
                f.write('\t' + line['question'].upper() + '\n')
                f.write('\t' + ''.join('-' for x in range(len(line['question']))) + '\n')
                f.write('\t' + _pad('', cell_width))
                for key in line[demographic_values[0]].keys():
                    f.write('\t' + _pad(key, cell_width))
                f.write('\n')
                for demographic_value in demographic_values:
                    f.write('\t' + _pad(demographic_value, cell_width))
                    for key, value in line[demographic_value].items():
                        value = int(100 * float(value)/sum(line[demographic_value].values()))
                        f.write('\t' + _pad('%i%s' % (value, '%'), cell_width))
                    f.write('\n')
                    #f.write(demographic_value + ' >> ' + ' '.join('%s:%i' % (key, value) for key, value in line[demographic_value].items()) + '\n')
                f.write('\n\n')

def average(output_file=None):
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
        'lat',
        'lon',
        'How many generations currently live in your household?',
        "What's your Age?",
        "In general, I do/do not feel that life has been fair to me",
        "Select how obedient or independent you think children should be",
        "Would you kill another person if your life depended on it?"]
    all_facets = [f for f in FacetMapping.objects.filter(display_as_question=True) if f.display_name not in exclude]
    full_output = {}
    demographic_value_response = solr.select('*:*', facet='true', facet_field=[f.facet_name for f in all_facets])
    for facet_field in demographic_value_response.facet_counts['facet_fields'].keys():
        if facet_field not in full_output:
            full_output[facet_field] = {'question':[f.display_name for f in all_facets if f.facet_name == facet_field][0]}
        full_output[facet_field]['values'] = demographic_value_response.facet_counts['facet_fields'][facet_field]
    if not output_file:
        print full_output
        return
    with open(output_file, 'wb') as f:
        cell_width = 30

        for group in question_split.keys():
            all_lines = []
            for key, value in full_output.items():
                if key in question_split[group]:
                    all_lines.append(value)
            f.write(group.upper() + '\n')
            f.write(''.join('=' for x in range(len(group))) + '\n\n')
            for line in all_lines:
                f.write('\t' + line['question'].upper() + '\n')
                f.write('\t' + ''.join('-' for x in range(len(line['question']))) + '\n')
                f.write('\t' + _pad('', cell_width))
                for key in line['values'].keys():
                    f.write('\t' + _pad(key, cell_width))
                f.write('\n')
                f.write('\t' + _pad('everyone', cell_width))
                for key, value in line['values'].items():
                    value = int(100 * float(value)/sum(line['values'].values()))
                    f.write('\t' + _pad('%i%s' % (value, '%'), cell_width))
                f.write('\n')
                    #f.write(demographic_value + ' >> ' + ' '.join('%s:%i' % (key, value) for key, value in line[demographic_value].items()) + '\n')
                f.write('\n\n')


def ad_hoc_nny_magazine(output_file=None):
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
        'lat',
        'lon',
        'How many generations currently live in your household?',
        "What's your Age?",
        "In general, I do/do not feel that life has been fair to me",
        "Select how obedient or independent you think children should be",
        "Would you kill another person if your life depended on it?"]
    all_facets = [f for f in FacetMapping.objects.filter(display_as_question=True) if f.display_name not in exclude]
    full_output = {}
    demographic_value_response = solr.select('wheredoyoulivecityandstatecountry_s:"New York" OR wheredoyoulivecityandstatecountry_s:"New York New York United States" OR wheredoyoulivecityandstatecountry_s:"New.York  United.States" OR wheredoyoulivecityandstatecountry_s:"New York United States" OR wheredoyoulivecityandstatecountry_s:"New York City New York United States" OR wheredoyoulivecityandstatecountry_s:"New York New York USA"', facet='true', facet_field=[f.facet_name for f in all_facets])
    for facet_field in demographic_value_response.facet_counts['facet_fields'].keys():
        if facet_field not in full_output:
            full_output[facet_field] = {'question':[f.display_name for f in all_facets if f.facet_name == facet_field][0]}
        full_output[facet_field]['values'] = demographic_value_response.facet_counts['facet_fields'][facet_field]
    if not output_file:
        print full_output
        return
    with open(output_file, 'wb') as f:
        cell_width = 30

        for group in question_split.keys():
            all_lines = []
            for key, value in full_output.items():
                if key in question_split[group]:
                    all_lines.append(value)
            f.write(group.upper() + '\n')
            f.write(''.join('=' for x in range(len(group))) + '\n\n')
            for line in all_lines:
                f.write('\t' + line['question'].upper() + '\n')
                f.write('\t' + ''.join('-' for x in range(len(line['question']))) + '\n')
                f.write('\t' + _pad('', cell_width))
                for key in line['values'].keys():
                    f.write('\t' + _pad(key, cell_width))
                f.write('\n')
                f.write('\t' + _pad('everyone', cell_width))
                for key, value in line['values'].items():
                    value = int(100 * float(value)/sum(line['values'].values()))
                    f.write('\t' + _pad('%i%s' % (value, '%'), cell_width))
                f.write('\n')
                    #f.write(demographic_value + ' >> ' + ' '.join('%s:%i' % (key, value) for key, value in line[demographic_value].items()) + '\n')
                f.write('\n\n')


def _pad(value, length):
    while len(value) < length:
        value += ' '
    return value

question_split = {
    'Basic Demographics':[
        'areyoumaleorfemale_s',
        'howoldareyou_s',
        'wheredoyoulivecityandstatecountry_s',
        'country_s',
        ],
    'Health':[
        'ithinkthefollowingismostimportantforgoodhealthchooseone_s',
        'howmuchdoyouthinkaboutyourweight_s',
        'whatdoyoudotohelpcopewithstressmost_s',
        ],
    'Safety':[
        'selectwhereyoufeelsafest_s',
        'doyouknowthenamesofyourclosestneighbors_s',
        'howsafeorscaryisyourneighborhood_s',
        ],
    'Pets':[
        'didyougrowupwithapet_s',
        'mypetthinksofmeasitschooseone_s',
        'doyoukickyourpetoutoftheroombeforehavingsex_s',
        ],
    'Parents and Children':[
        'ificouldenhancemyunbornchildsdnainonlyonewayiwouldimprovetheirchooseone_s',
        'numberofgenerationslivinginyourhousehold_s',
        'howstrictorlenientwereyourparentswhenyouweregrowingup_s',
        'whoareyoumoresimilarto_s',
        'whereareyouinthebirthorderofyoursiblings_s',
        'iwouldorwouldnotsaythatoneofthemaingoalsinmylifehasbeentomakemyparentsproud_s',
        ],
    'Love and Marrage':[
        'haveyouexperiencedloveatfirstsight_s',
        'wouldyoumarrysomeonewithwhomyoucouldneverhavechildren_s',
        'doyouthinkitisacceptableforamarriedpersontohaveanaffair_s',
        'doyouthinkloveisnecessaryformarriage_s',
        'imarriedatxyearsold_s',
        'ificouldchangeonethingaboutmypartneritwouldbethefollowingpickone_s',
        'mycurrentrelationshipstatus_s',
        ],
    'Sleep':[
        'ifyouspendthedaybeinglazydoyoufeelgoodorbad_s',
        'iusuallywakeupinthefollowingway_s',
        'pickhowoftenyouhaveluciddreams_s',
        'pickhowoftenyourrememberyourdreamsduringtheday_s',
        'pickwhatyoumostlydreamabout_s',
        'iftherewereapillthateliminatedtheneedforsleepiwouldwouldnotnottakeit_s',
        'haveyousleptwalkedbefore_s',
        'doyounapregularly_s',
        'hourssleepeachnight_s',
        ],
    'Life':[
        'iftherewereafireatmyhomeiwouldtakethefollowingitemfirst_s',
        'ingeneraldoyoufeellifehasbeenfairtoyou_s',
        'howoptimisticorpessimisticareyou_s',
        'thefollowingwouldmakemylifebetterchooseone_s',
        'rankhowtrustworthyyouthinkpeopleare_s',
        'ithinksuccessfulpeoplemorelesshonestthantheaverageperson_s',
        'timespentaloneeachday_s',
        ],
    'Religion':[
        'whichclosesfitswhatyouthinkwillhappenwhenyoudie_s',
        ],
    'Other':[
        'selectwhereyouusuallygetyourinformationabouttheworldfrom_s',
        'whowouldyouvoteforpresidentoftheus_s',
        'numberoflanguagesspoken_s',
        ]
}