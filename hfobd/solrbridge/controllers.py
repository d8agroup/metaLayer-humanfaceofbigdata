import datetime
import pytz
from hfobd.solrbridge.models import FacetMapping, LocationMapping
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
                try:
                    solr_object[headers[x]] = row[x].encode('ascii', 'ignore')
                except Exception as e:
                    logger.error('Error encoding content')
                    logger.debug('Error encoding content - exception: %s  content:%s' % (e, solr_object))
            try:
                index = headers.index('wheredoyoulivecityandstatecountry_s')
                if index > -1:
                    raw_location = row[index]
                    if raw_location:
                        location_mapping = LocationMapping.GetForRawLocation(raw_location)
                        if location_mapping:
                            solr_object['country_s'] = location_mapping.country
                            solr_object['raw_coordinates_s'] = location_mapping.raw_coordinates
            except Exception as e:
                logger.error('Error location sniffing')
                logger.debug('Error location sniffing - exception: %s  content:%s' % (e, solr_object))
            try:
                settings.SOLR.add(solr_object, commit=True)
            except Exception as e:
                logger.error('Error posting content to solr')
                logger.debug('Error posting content to solr - exception: %s  content:%s' % (e, solr_object))

