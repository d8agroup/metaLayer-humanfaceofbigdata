from hfobd.solrbridge.controllers import SolrController
import csv
lines = [l for l in csv.reader(open('assets/data/507.csv', 'rb'))]
headers = lines[0]
lines = lines[1]
SolrController.PushTabularData(headers, [lines])
from hfobd.solrbridge.models import FacetMapping
for display_name in ['Worker', 'Time (seconds)', 'If I could live forever I would/would not?']:
    f = FacetMapping.objects.get(display_name=display_name)
    f.display_as_question = False
    f.save()

