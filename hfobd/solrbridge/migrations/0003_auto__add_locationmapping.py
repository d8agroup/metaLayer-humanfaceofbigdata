# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LocationMapping'
        db.create_table('solrbridge_locationmapping', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('raw_location', self.gf('django.db.models.fields.TextField')()),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=2048)),
            ('raw_coordinates', self.gf('django.db.models.fields.CharField')(max_length=2048)),
        ))
        db.send_create_signal('solrbridge', ['LocationMapping'])


    def backwards(self, orm):
        # Deleting model 'LocationMapping'
        db.delete_table('solrbridge_locationmapping')


    models = {
        'solrbridge.facetmapping': {
            'Meta': {'object_name': 'FacetMapping'},
            'display_as_question': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'facet_name': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'solrbridge.locationmapping': {
            'Meta': {'object_name': 'LocationMapping'},
            'country': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'raw_coordinates': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'raw_location': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['solrbridge']