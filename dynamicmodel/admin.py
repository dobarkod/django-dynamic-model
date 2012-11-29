from django.contrib import admin
from dynamicmodel.models import DynamicSchemaField, DynamicSchema, DynamicModel
from django.contrib.contenttypes.models import ContentType


class DynamicSchemaFieldInline(admin.TabularInline):
    model = DynamicSchemaField
    extra = 1


class DynamicSchemaAdmin(admin.ModelAdmin):
    list_display = ['model', 'type_value']
    inlines = [
        DynamicSchemaFieldInline,
    ]

    def render_change_form(self, request, context, *args, **kwargs):

        dynamic_schema_content_type_ids = [el.id for el in \
            ContentType.objects.all()
            if issubclass(el.model_class(), DynamicModel)]

        context['adminform'].form.fields['model'].queryset = \
            ContentType.objects.filter(id__in=dynamic_schema_content_type_ids)

        return super(DynamicSchemaAdmin, self).render_change_form(
            request, context, args, kwargs)


admin.site.register(DynamicSchema, DynamicSchemaAdmin)
admin.site.register(ContentType)
