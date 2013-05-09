from django.contrib.contenttypes.models import ContentType
from django.contrib import admin
from django.conf.urls import patterns, url
from django.conf import settings

from dynamicmodel.models import DynamicSchema, DynamicModel, DynamicSchemaField


class DynamicSchemaAdmin(admin.ModelAdmin):
    list_display = ['model', 'type_value']

    def get_urls(self):
        urls = super(DynamicSchemaAdmin, self).get_urls()
        custom_urls = patterns('dynamicmodel.admin_views',
            url(r'^ct/(?P<ct_id>\d+)/choices/$',
                'dynamic_schema_model_type_values',
                name='dynamicmodel_dynamicschema_model_type_values'),
            url(r'^(?P<schema_id>\d+)/field_list/$',
                'dynamic_schema_field_list',
                name='dynamicmodel_dynamicschema_field_list'),
            url(r'^/field/(?P<field_id>\d+)/delete/$',
                'dynamic_schema_field_delete',
                name='dynamicmodel_dynamicschema_field_delete'),
            url(r'^field_type_select/$',
                'dynamic_schema_field_type_select',
                name='dynamicmodel_dynamicschema_field_type_select'),
            url(r'^(?P<schema_id>\d+)/forms/(?P<field_type>%s)/$' %
                ("|".join(dict(DynamicSchemaField.FIELD_TYPES).keys())),
                'dynamic_schema_field_form',
                name='dynamicmodel_dynamicschema_field_form_create'),
            url(r'^(?P<schema_id>\d+)/forms/(?P<field_type>%s)/(?P<field_id>\d+)/$' %
                ("|".join(dict(DynamicSchemaField.FIELD_TYPES).keys())),
                'dynamic_schema_field_form',
                name='dynamicmodel_dynamicschema_field_form_edit'),
        )
        return custom_urls + urls

    def render_change_form(self, request, context, *args, **kwargs):

        dynamic_schema_content_type_ids = [el.id for el in
            ContentType.objects.all()
            if el.model_class() and issubclass(el.model_class(), DynamicModel)]

        context['adminform'].form.fields['model'].queryset = \
            ContentType.objects.filter(id__in=dynamic_schema_content_type_ids)

        return super(DynamicSchemaAdmin, self).render_change_form(
            request, context, args, kwargs)


if getattr(settings, 'DYNAMICMODEL_USE_DEFAULT_ADMIN', True):
    admin.site.register(DynamicSchema, DynamicSchemaAdmin)
