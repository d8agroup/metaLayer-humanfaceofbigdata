from hfobd.solrbridge.controllers import SolrController
import csv
import datetime
now = datetime.datetime.now()
start = 0
count = 1000000
lines = [l for l in csv.reader(open('/usr/local/metaLayer-humanfaceofbigdata/humanfaceofbigdata/assets/data/hfobd-all.csv', 'rb'))]
headers = lines[0]
lines = lines[start+1:count+start+1]
SolrController.PushTabularData(headers, lines)
print '************************'
print len(lines), 'items in', datetime.datetime.now() - now
print '************************'
from hfobd.solrbridge.models import FacetMapping
questions_to_hide = [
    'Worker',
    'lat',
    'lon',
    'Time (seconds)',
    'If I could live forever I would/would not?',
    "What's your Age?",
    "How much time do you spend alone each day?",
    "I usually average X hours sleep each night",
    "I was X years old when I got married",
    "How many languages do you speak fluently?",
    "How many generations currently live in your household?"]
for display_name in questions_to_hide:
    try:
        f = FacetMapping.objects.get(display_name=display_name)
        f.display_as_question = False
        f.save()
    except FacetMapping.DoesNotExist:
        continue

