# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'DynamicSchemaField.extra'
        db.add_column('dynamicmodel_dynamicschemafield', 'extra',
                      self.gf('dynamicmodel.fields.JSONField')(default='{}'),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'DynamicSchemaField.extra'
        db.delete_column('dynamicmodel_dynamicschemafield', 'extra')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'dynamicmodel.dynamicschema': {
            'Meta': {'unique_together': "(('model', 'type_value'),)", 'object_name': 'DynamicSchema'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'type_value': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'dynamicmodel.dynamicschemafield': {
            'Meta': {'unique_together': "(('schema', 'name'),)", 'object_name': 'DynamicSchemaField'},
            'extra': ('dynamicmodel.fields.JSONField', [], {'default': "'{}'"}),
            'field_type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'schema': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fields'", 'to': "orm['dynamicmodel.DynamicSchema']"}),
            'verbose_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['dynamicmodel']