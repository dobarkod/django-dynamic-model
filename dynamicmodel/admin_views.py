from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType

from dynamicmodel.models import DynamicSchema, DynamicSchemaField, DynamicModel

from .admin_forms import (DynamicSchemaFieldForm,
    DynamicSchemaDropdownFieldForm, DynamicSchemaBooleanFieldForm)

import json


def ajax_required(f):
    def wrap(request, *args, **kwargs):
            if not request.is_ajax():
                return HttpResponseBadRequest()
            return f(request, *args, **kwargs)
    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap


def json_response(data):
    return HttpResponse(json.dumps(data), content_type='application/json')


@ajax_required
@login_required
def dynamic_schema_field_list(request, schema_id):
    list = get_object_or_404(DynamicSchema, id=schema_id).fields.all()
    rendered_list = render_to_string(
        'admin/dynamicmodel/dynamicschema/partials/dynamic_schema_field_list.html', {
            'list': list
        })
    return json_response({'html': rendered_list})


@require_POST
@ajax_required
@login_required
def dynamic_schema_field_delete(request, field_id):
    get_object_or_404(DynamicSchemaField, id=field_id).delete()
    rendered_list = render_to_string(
        'admin/dynamicmodel/dynamicschema/partials/dynamic_schema_field_list.html', {
            'list': list
        })
    return json_response({'html': rendered_list})


@ajax_required
@login_required
def dynamic_schema_field_form(request, schema_id, field_type, field_id=None):

    schema = get_object_or_404(DynamicSchema, id=schema_id)
    success = False
    title = "Add new field - %s" % (
        dict(DynamicSchemaField.FIELD_TYPES).get(field_type))

    try:
        data = json.loads(request.body)
    except (KeyError, ValueError):
        data = None

    if field_id:
        instance = get_object_or_404(DynamicSchemaField, id=field_id,
            schema=schema)
        form_url = reverse('admin:dynamicmodel_dynamicschema_field_form_edit',
            args=[schema_id, field_type, field_id])
    else:
        instance = DynamicSchemaField(schema=schema, field_type=field_type)
        form_url = reverse('admin:dynamicmodel_dynamicschema_field_form_create',
            args=[schema_id, field_type])

    if field_type == 'Dropdown':
        form_class = DynamicSchemaDropdownFieldForm
    elif field_type == 'BooleanField':
        form_class = DynamicSchemaBooleanFieldForm
    else:
        form_class = DynamicSchemaFieldForm

    form = form_class(data, instance=instance)

    if form.is_valid():
        form.save()
        form = form_class()
        success = True

    rendered_form = render_to_string(
        'admin/dynamicmodel/dynamicschema/partials/dynamic_schema_field_form.html', {
            'title': title,
            'form': form,
            'form_url': form_url,
            'field_id': field_id,
        })

    return json_response({'html': rendered_form, 'success': success})


@login_required
def dynamic_schema_field_type_select(request):
    options = DynamicSchemaField.FIELD_TYPES
    rendered_select = render_to_string(
        'admin/dynamicmodel/dynamicschema/partials/dynamic_schema_field_type_select.html', {
            'options': options
        })
    return json_response({'html': rendered_select})


@login_required
@ajax_required
def dynamic_schema_model_type_values(request, ct_id):
    model = get_object_or_404(ContentType, id=ct_id).model_class()

    choices = []
    rendered_select = ''

    if issubclass(model, DynamicModel):
        choices = model.get_schema_type_choices()

    if choices:
        rendered_select = render_to_string(
            'admin/dynamicmodel/dynamicschema/partials/dynamic_schema_model_type_select.html', {
                'options': choices
            })

    return json_response({'html': rendered_select})
