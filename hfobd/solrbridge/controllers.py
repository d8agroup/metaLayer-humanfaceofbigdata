import datetime
import pytz
from hfobd.solrbridge.models import FacetMapping
from django.conf import settings
from hashlib import md5
import logging
logger = logging.getLogger(__name__)

class SolrController(object):
    @classmethod
    def PushTabularData(cls, headers, rows):
        def id(row):
            return md5(''.join(r for r in row)).hexdigest()
        headers = [FacetMapping.CreateFromDisplayName(h).facet_name for h in headers]
        for row in rows:
            solr_object = { 'id':id(row), 'timestamp_dt':datetime.datetime.now().replace(tzinfo=pytz.UTC) }
            for x in range(len(row)):
                solr_object[headers[x]] = row[x].encode('ascii', 'ignore')
            try:
                settings.SOLR.add(solr_object)
            except Exception as e:
                logger.error('Error posting content to solr')
                logger.debug('Error posting content to solr - exception: %s  content:%s' % (e, solr_object))
        settings.SOLR.commit()



