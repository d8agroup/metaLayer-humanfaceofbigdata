from django.db import models

class FacetMapping(models.Model):
    display_name = models.CharField(max_length=2048)
    facet_name = models.CharField(max_length=2048)

    @classmethod
    def CreateFromDisplayName(cls, display_name):
        facet_name = ''.join(c for c in display_name.lower() if c.isalnum()) + "_s"
        try:
            facet_mapping = FacetMapping.objects.get(facet_name=facet_name)
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
