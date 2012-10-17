from urllib import urlencode
from urllib2 import Request, urlopen
from django.db import models
from django.utils import simplejson as json

class FacetMapping(models.Model):
    display_name = models.CharField(max_length=2048)
    facet_name = models.CharField(max_length=2048)
    display_as_question = models.BooleanField(default=True)

    @classmethod
    def CreateFromDisplayName(cls, display_name):
        facet_name = ''.join(c for c in display_name.lower() if c.isalnum()) + "_s"
        try:
            facet_mapping = FacetMapping.objects.get(display_name=display_name)
        except FacetMapping.DoesNotExist:
            facet_mapping = FacetMapping(display_name=display_name, facet_name=facet_name)
            facet_mapping.save()
        return facet_mapping

    @classmethod
    def GetDisplayName(cls, facet_name):
        try:
            return FacetMapping.objects.get(facet_name=facet_name).display_name
        except FacetMapping.DoesNotExist:
            return facet_name

class LocationMapping(models.Model):
    raw_location = models.TextField()
    country = models.CharField(max_length=2048)
    raw_coordinates = models.CharField(max_length=2048)

    @classmethod
    def GetForRawLocation(cls, raw_location):
        raw_location = raw_location.lower()
        raw_location_parts = raw_location.split(' ')
        raw_location_parts = [''.join([p for p in part if p.isalnum()]) for part in raw_location_parts]
        raw_location = ' '.join(raw_location_parts)

        try:
            location_mapping = LocationMapping.objects.get(raw_location=raw_location)
        except LocationMapping.DoesNotExist:
            location_getter = LocationGetter(raw_location)
            locations = location_getter.run()
            country = sorted(locations['locations'], key=lambda x: len(x), reverse=True)[0] if locations['locations'] else None
            if country:
                country = country.replace('(Country)', '').strip(' ')
            raw_coordinates = locations['points'][0] if locations['points'] else None
            location_mapping = LocationMapping(
                raw_location = raw_location,
                country = country,
                raw_coordinates = raw_coordinates)
            location_mapping.save()
        return location_mapping




class LocationGetter():
    def __init__(self, content):
        self.content = content
        self.result = None

    def run(self):
        text = self.content
        try:
            text = text.encode('ascii', 'ignore')
            url = 'http://wherein.yahooapis.com/v1/document'
            post_data = urlencode({ 'documentContent':text, 'documentType':'text/plain', 'outputType':'json', 'appid':'123'})
            request = Request(url, post_data)
            response = urlopen(request)
            response = json.loads(response.read())
            result = self._map_location(response)
            return result
        except Exception as e:
            return None

    def _map_location(self, response):
        def countries(a,v,p):
            if isinstance(a, dict):
                if 'type' in a and a['type'] == 'Country':
                    if 'name' in a and a['name'] not in v:
                        v.append(a['name'].encode('ascii', 'ignore'))
                    if 'centroid' in a:
                        latlong = '%s,%s' % (a['centroid']['latitude'], a['centroid']['longitude'])
                        if latlong not in p:
                            p.append(latlong)
                for key in a.keys():
                    countries(a[key], v, p)
            elif isinstance(a, list):
                for b in a:
                    countries(b, v, p)
            else:
                return
        def places(a,v,p):
            if isinstance(a, dict):
                if 'type' in a and a['type'] != 'Country':
                    if 'centroid' in a:
                        latlong = '%s,%s' % (a['centroid']['latitude'], a['centroid']['longitude'])
                        if latlong not in p:
                            p.append(latlong)
                for key in a.keys():
                    places(a[key], v, p)
            elif isinstance(a, list):
                for b in a:
                    places(b, v, p)
            else:
                return

        if not isinstance(response['document'], dict):
            return False
        names = []
        locations = []

        countries(response, names, locations)
        places(response, names, locations)

        return {'locations':names, 'points':locations}



