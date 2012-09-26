# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FacetMapping'
        db.create_table('solrbridge_facetmapping', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=2048)),
            ('facet_name', self.gf('django.db.models.fields.CharField')(max_length=2048)),
        ))
        db.send_create_signal('solrbridge', ['FacetMapping'])


    def backwards(self, orm):
        # Deleting model 'FacetMapping'
        db.delete_table('solrbridge_facetmapping')


    models = {
        'solrbridge.facetmapping': {
            'Meta': {'object_name': 'FacetMapping'},
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'facet_name': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['solrbridge']