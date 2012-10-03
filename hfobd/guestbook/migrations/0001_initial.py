# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Guest'
        db.create_table('guestbook_guest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email_address', self.gf('django.db.models.fields.TextField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('guestbook', ['Guest'])


    def backwards(self, orm):
        # Deleting model 'Guest'
        db.delete_table('guestbook_guest')


    models = {
        'guestbook.guest': {
            'Meta': {'object_name': 'Guest'},
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'email_address': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['guestbook']