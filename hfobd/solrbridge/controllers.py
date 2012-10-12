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

        additional_mapped_fields = [
            {
                'original_field':"What's your Age?",
                'mapped_field':"Age",
                'function':lambda age: SolrController._MapAge(age)
            },
            {
                'original_field':"How much time do you spend alone each day?",
                'mapped_field':"Time spent alone each day",
                'function':lambda t: SolrController._MapTimeAlone(t)
            },
            {
                'original_field':"I usually average X hours sleep each night",
                'mapped_field':"Hours sleep each night",
                'function':lambda s: SolrController._MapSleep(s)
            },
            {
                'original_field':"I was X years old when I got married",
                'mapped_field':"I married at X years old",
                'function':lambda a: SolrController._MapMarried(a)
            },
            {
                'original_field':"How many languages do you speak fluently?",
                'mapped_field':'Languages spoken',
                'function':lambda l: SolrController._MapLanguages(l)
            },
            {
                'original_field':"How many generations currently live in your household?",
                'mapped_field':'Number of generations living in your household',
                'function':lambda g: SolrController._MapGenerations(g)
            }
        ]

        headers = [FacetMapping.CreateFromDisplayName(h).facet_name for h in headers]
        for additional_header in additional_mapped_fields:
            additional_header['mapped_facet_name'] = FacetMapping.CreateFromDisplayName(additional_header['mapped_field']).facet_name
            additional_header['original_facet_name'] = FacetMapping.CreateFromDisplayName(additional_header['original_field']).facet_name

        for row in rows:
            solr_object = { 'id':id(row), 'timestamp_dt':datetime.datetime.now().replace(tzinfo=pytz.UTC) }
            for x in range(len(row)):
                try:
                    if row[x]:
                        solr_object[headers[x]] = row[x].encode('ascii', 'ignore')
                        for additional_mapping in additional_mapped_fields:
                            if headers[x] != additional_mapping['original_facet_name']:
                                continue
                            mapped_value = additional_mapping['function'](row[x])
                            if not mapped_value:
                                continue
                            solr_object[additional_mapping['mapped_facet_name']] = mapped_value
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
                settings.SOLR.add(solr_object)
            except Exception as e:
                logger.error('Error posting content to solr')
                logger.debug('Error posting content to solr - exception: %s  content:%s' % (e, solr_object))
        settings.SOLR.commit()

    @classmethod
    def _MapAge(cls, age):
        try:
            age = int(age)
            if age <=20: return 'Under 20'
            if age < 31: return '21 - 30'
            if age < 40: return '31 - 40'
            if age < 51: return '41 - 50'
            return 'Over 50'
        except Exception:
            return None

    @classmethod
    def _MapTimeAlone(cls, t):
        try:
            t = int(t)
            if t < 1: return '0 hours'
            if t < 3: return 'Up to 3 hours'
            if t < 6: return 'Up to 6 hours'
            if t < 12: return 'Up to 12 hours'
            if t < 18: return 'Up to 18 hours'
            return 'Over 18 hours'
        except Exception:
            return None

    @classmethod
    def _MapSleep(cls, s):
        try:
            s = int(s)
            if s < 4: return 'Less than 4 hours'
            if s < 7: return '4 - 6 hours'
            if s < 9: return '6 - 8 hours'
            return 'More than 8 hours'
        except Exception:
            return None

    @classmethod
    def _MapMarried(cls, a):
        try:
            a = int(a)
            if not a: return "I'm not married"
            if a <=20: return 'Under 20'
            if a < 31: return '21 - 30'
            if a < 40: return '31 - 40'
            if a < 51: return '41 - 50'
            return 'Over 50'
        except Exception:
            return None

    @classmethod
    def _MapLanguages(cls, l):
        try:
            l = int(l)
            if l < 2: return 'Only 1'
            if l < 4: return '2 - 3'
            return '4 or more'
        except Exception:
            return None

    @classmethod
    def _MapGenerations(cls, g):
        try:
            g = int(g)
            if not g: return '0'
            if g < 2: return '1'
            if g < 3: return '2'
            if g < 4: return '3'
            return '4 or more'
        except Exception:
            return None