# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DynamicSchema'
        db.create_table('dynamicmodel_dynamicschema', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('model', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('type_value', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('dynamicmodel', ['DynamicSchema'])

        # Adding unique constraint on 'DynamicSchema', fields ['model', 'type_value']
        db.create_unique('dynamicmodel_dynamicschema', ['model_id', 'type_value'])

        # Adding model 'DynamicSchemaField'
        db.create_table('dynamicmodel_dynamicschemafield', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('schema', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fields', to=orm['dynamicmodel.DynamicSchema'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('verbose_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('field_type', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('dynamicmodel', ['DynamicSchemaField'])

        # Adding unique constraint on 'DynamicSchemaField', fields ['schema', 'name']
        db.create_unique('dynamicmodel_dynamicschemafield', ['schema_id', 'name'])


    def backwards(self, orm):
        # Removing unique constraint on 'DynamicSchemaField', fields ['schema', 'name']
        db.delete_unique('dynamicmodel_dynamicschemafield', ['schema_id', 'name'])

        # Removing unique constraint on 'DynamicSchema', fields ['model', 'type_value']
        db.delete_unique('dynamicmodel_dynamicschema', ['model_id', 'type_value'])

        # Deleting model 'DynamicSchema'
        db.delete_table('dynamicmodel_dynamicschema')

        # Deleting model 'DynamicSchemaField'
        db.delete_table('dynamicmodel_dynamicschemafield')


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
            'field_type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'schema': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fields'", 'to': "orm['dynamicmodel.DynamicSchema']"}),
            'verbose_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['dynamicmodel']