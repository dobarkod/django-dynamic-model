from django import forms

from dynamicmodel.models import DynamicSchemaField


class DynamicSchemaFieldForm(forms.ModelForm):
    class Meta:
        model = DynamicSchemaField
        exclude = ['schema', 'field_type', 'extra']


class DynamicSchemaDropdownFieldForm(DynamicSchemaFieldForm):
    options = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super(DynamicSchemaDropdownFieldForm, self).__init__(*args, **kwargs)
        if self.instance and 'choices' in self.instance.extra:
            self.fields['options'].initial = \
                ",".join(dict(self.instance.extra['choices']).keys())

    def save(self, force_insert=False, force_update=False, commit=True):
        m = super(DynamicSchemaDropdownFieldForm, self).save(commit=False)

        choices = []
        for el in self.cleaned_data.get('options').split(','):
            stripped_el = el.strip()
            choices.append(stripped_el)

        m.extra = {
            'choices': choices
        }

        if commit:
            m.save()
        return m


class DynamicSchemaBooleanFieldForm(DynamicSchemaFieldForm):
    class Meta:
        model = DynamicSchemaField
        exclude = ['schema', 'field_type', 'extra', 'required']
