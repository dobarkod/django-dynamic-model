from django.db import models
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.validators import RegexValidator
from .fields import JSONField
from django.core.exceptions import ValidationError
from django.core.cache import cache


class DynamicModel(models.Model):

    class Meta:
        abstract = True

    extra_fields = JSONField(editable=False, default="{}")

    def __init__(self, *args, **kwargs):
        self._schema = None
        super(DynamicModel, self).__init__(*args, **kwargs)
        self.get_schema()
        self._sync_with_schema()

    def _sync_with_schema(self):
        schema_extra_fields = self.get_extra_fields_names()
        clear_field = [field_name for field_name in self.extra_fields
            if field_name not in schema_extra_fields]
        new_field = [field_name for field_name in schema_extra_fields
            if field_name not in self.extra_fields]

        for el in clear_field:
            del self.extra_fields[el]
        for el in new_field:
            self.extra_fields[el] = None

    def get_extra_field_value(self, key):
        if key in self.extra_fields:
            return self.extra_fields[key]
        else:
            return None

    def get_extra_fields(self):
        _schema = self.get_schema()
        for field in _schema.fields.all():
            yield field.name, field.verbose_name, field.field_type, \
                field.required, self.get_extra_field_value(field.name)

    def get_extra_fields_names(self):
        return [name for name, verbose_name, field_type, required, value in self.get_extra_fields()]

    def get_schema(self):
        type_value = ''
        if self.get_schema_type_descriptor():
            type_value = getattr(self, self.get_schema_type_descriptor())
        return DynamicSchema.get_for_model(self, type_value)

    def get_schema_type_descriptor(self):
        return ''

    def __getattr__(self, attr_name):
        if attr_name in self.extra_fields:
            return self.extra_fields[attr_name]
        else:
            return getattr(super(DynamicModel, self), attr_name)

    def __setattr__(self, attr_name, value):
        if hasattr(self, 'extra_fields') and \
            attr_name not in [el.name for el in self._meta.fields] and \
            attr_name not in ['_schema'] and \
            attr_name in self.get_extra_fields_names():

            self.extra_fields[attr_name] = value

        super(DynamicModel, self).__setattr__(attr_name, value)


class DynamicForm(forms.ModelForm):
    field_mapping = [
        ('IntegerField', {'field': forms.IntegerField}),
        ('CharField', {'field': forms.CharField}),
        ('TextField', {'field': forms.CharField, 'widget': forms.Textarea}),
        ('EmailField', {'field': forms.EmailField}),
    ]

    def __init__(self, *args, **kwargs):
        super(DynamicForm, self).__init__(*args, **kwargs)

        if not isinstance(self.instance, DynamicModel):
            raise ValueError("DynamicForm.Meta.model must be inherited from DynamicModel")

        if self.instance and hasattr(self.instance, 'get_extra_fields'):
            for name, verbose_name, field_type, req, value in self.instance.get_extra_fields():
                field_mapping_case = dict(self.field_mapping)[field_type]
                self.fields[name] = field_mapping_case['field'](required=req,
                    widget=field_mapping_case.get('widget'),
                    initial=self.instance.get_extra_field_value(name),
                    label=verbose_name.capitalize() if verbose_name else \
                        " ".join(name.split("_")).capitalize())

    def save(self, force_insert=False, force_update=False, commit=True):
        m = super(DynamicForm, self).save(commit=False)

        extra_fields = {}

        extra_fields_names = [name for name, verbose_name, field_type, req, value \
            in self.instance.get_extra_fields()]

        for cleaned_key in self.cleaned_data.keys():
            if cleaned_key in extra_fields_names:
                extra_fields[cleaned_key] = self.cleaned_data[cleaned_key]

        m.extra_fields = extra_fields

        if commit:
            m.save()
        return m


class DynamicSchemaQuerySet(models.query.QuerySet):
    def delete(self):
        cache_el = None
        for el in self:
            cache_el = el.delete(renew=False)
        if cache_el:
            cache_el.renew_cache()


class DynamicSchemaManager(models.Manager):
    def get_query_set(self):
        return DynamicSchemaQuerySet(self.model, using=self._db)

    def get_for_model(self, model_class, type_value=''):
        cache_key = DynamicSchema.get_cache_key_static(model_class, type_value)
        cache_value = cache.get(cache_key)
        if cache_value is not None:
            return cache_value
        else:
            return DynamicSchema.renew_cache_static(model_class, type_value)


class DynamicSchema(models.Model):
    class Meta:
        unique_together = ('model', 'type_value')

    objects = DynamicSchemaManager()

    model = models.ForeignKey(ContentType)
    type_value = models.CharField(max_length=100, null=True, blank=True)

    def __unicode__(self):
        return "%s%s" % (self.model,
            " (%s)" % self.type_value if self.type_value else '')

    def add_field(self, name, type):
        return self.fields.create(schema=self, name=name, field_type=type)

    def remove_field(self, name):
        return self.fields.filter(name=name).delete()

    @classmethod
    def get_for_model(cls, model_class, type_value=''):
        return cls.objects.get_for_model(model_class, type_value)

    @classmethod
    def get_cache_key_static(cls, model_class, type_value):
        return "%s-%s-%s-%s" % ('DYNAMICMODEL_SCHEMA_CACHE_KEY',
            model_class._meta.app_label, model_class._meta.module_name,
            type_value)

    def get_cache_key(self):
        return self.get_cache_key_static(self.model.model_class(),
            self.type_value)

    @classmethod
    def renew_cache_static(cls, model_class, type_value):
        cache_key = cls.get_cache_key_static(model_class, type_value)

        if not cls.objects.filter(type_value=type_value,
            model=ContentType.objects.get_for_model(model_class)).exists():

            cls.objects.create(type_value=type_value,
                model=ContentType.objects.get_for_model(model_class))

        schema = cls.objects.prefetch_related('fields')\
            .get(
                type_value=type_value,
                model=ContentType.objects.get_for_model(model_class))

        cache.set(cache_key, schema)
        return schema

    def renew_cache(self):
        return self.renew_cache_static(self.model.model_class(),
            self.type_value)

    def save(self, *args, **kwargs):
        super(DynamicSchema, self).save(*args, **kwargs)
        self.renew_cache()

    def delete(self, *args, **kwargs):
        renew = kwargs.pop('renew', True)
        super(DynamicSchema, self).delete(*args, **kwargs)
        if renew:
            self.renew_cache()
        return self


class DynamicSchemaFieldQuerySet(models.query.QuerySet):
    def delete(self):
        cache_el = None
        for el in self:
            cache_el = el.delete(renew=False)
        if cache_el:
            cache_el.renew_cache()


class DynamicSchemaFieldManager(models.Manager):
    def get_query_set(self):
        return DynamicSchemaFieldQuerySet(self.model, using=self._db)


class DynamicSchemaField(models.Model):
    FIELD_TYPES = [
        ('IntegerField', 'Integer number field'),
        ('CharField', 'One line of text'),
        ('TextField', 'Multiline text input'),
        ('EmailField', 'Email'),
    ]

    class Meta:
        unique_together = ('schema', 'name')

    objects = DynamicSchemaFieldManager()

    schema = models.ForeignKey(DynamicSchema, related_name='fields')
    name = models.CharField(max_length=100, validators=[RegexValidator(r'^[\w]+$',
        message="Name should contain only alphanumeric characters and underscores.")])
    verbose_name = models.CharField(max_length=100, null=True, blank=True)
    field_type = models.CharField(max_length=100, choices=FIELD_TYPES)
    required = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.clean()
        super(DynamicSchemaField, self).save(*args, **kwargs)
        self.renew_cache()

    def delete(self, *args, **kwargs):
        renew = kwargs.pop('renew', True)
        super(DynamicSchemaField, self).delete(*args, **kwargs)
        if renew:
            self.renew_cache()
        return self

    def renew_cache(self):
        DynamicSchema.renew_cache_static(self.schema.model.model_class(),
            self.schema.type_value)

    def clean(self):

        if self.field_type not in dict(self.FIELD_TYPES).keys():
            raise ValueError("Wrong field_type")

        if not self.id:
            return

        old_model = DynamicSchemaField.objects.get(pk=self.id)

        fields = [f.name for f in DynamicSchemaField._meta.fields]
        fields.remove('verbose_name')

        for field_name in fields:
            if old_model.__dict__.get(field_name) != self.__dict__.get(field_name):
                raise ValidationError("%s value cannot be modified")

    def __unicode__(self):
        return "%s - %s" % (self.schema, self.name)
