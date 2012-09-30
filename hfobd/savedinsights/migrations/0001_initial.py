# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SavedInsight'
        db.create_table('savedinsights_savedinsight', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image_id', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('title', self.gf('django.db.models.fields.TextField')()),
            ('author', self.gf('django.db.models.fields.TextField')()),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('savedinsights', ['SavedInsight'])


    def backwards(self, orm):
        # Deleting model 'SavedInsight'
        db.delete_table('savedinsights_savedinsight')


    models = {
        'savedinsights.savedinsight': {
            'Meta': {'object_name': 'SavedInsight'},
            'author': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_id': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'title': ('django.db.models.fields.TextField', [], {}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['savedinsights']