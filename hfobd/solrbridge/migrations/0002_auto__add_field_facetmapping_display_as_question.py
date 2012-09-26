# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'FacetMapping.display_as_question'
        db.add_column('solrbridge_facetmapping', 'display_as_question',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'FacetMapping.display_as_question'
        db.delete_column('solrbridge_facetmapping', 'display_as_question')


    models = {
        'solrbridge.facetmapping': {
            'Meta': {'object_name': 'FacetMapping'},
            'display_as_question': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'facet_name': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['solrbridge']