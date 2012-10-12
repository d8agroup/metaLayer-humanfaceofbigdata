from hfobd.solrbridge.controllers import SolrController
import csv
lines = [l for l in csv.reader(open('assets/data/rich_export_02.csv', 'rb'))]
headers = lines[0]
lines = lines[1:]
SolrController.PushTabularData(headers, lines)
from hfobd.solrbridge.models import FacetMapping
questions_to_hide = [
    'Worker',
    'Time (seconds)',
    'If I could live forever I would/would not?',
    "What's your Age?",
    "How much time do you spend alone each day?",
    "I usually average X hours sleep each night",
    "I was X years old when I got married",
    "How many languages do you speak fluently?",
    "How many generations currently live in your household?"]
for display_name in questions_to_hide:
    f = FacetMapping.objects.get(display_name=display_name)
    f.display_as_question = False
    f.save()

