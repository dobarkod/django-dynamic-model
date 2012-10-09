
# website: https://github.com/bradjasper/django-jsonfield
# git access: https://github.com/bradjasper/django-jsonfield.git
# commit: c605674b02e4a1c79b20d685bc4688d846531671


# Copyright (c) 2012 Brad Jasper

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import simplejson as json
from django.utils.translation import ugettext_lazy as _

from django.forms.fields import Field
from django.forms.util import ValidationError as FormValidationError


class JSONFormField(Field):
    def clean(self, value):

        if not value and not self.required:
            return None

        value = super(JSONFormField, self).clean(value)

        if isinstance(value, basestring):
            try:
                json.loads(value)
            except ValueError:
                raise FormValidationError(_("Enter valid JSON"))
        return value


class JSONFieldBase(object):

    # Used so to_python() is called
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.dump_kwargs = kwargs.pop('dump_kwargs', {'cls': DjangoJSONEncoder})
        self.load_kwargs = kwargs.pop('load_kwargs', {})

        super(JSONFieldBase, self).__init__(*args, **kwargs)

    def to_python(self, value):
        """Convert string value to JSON"""
        if isinstance(value, basestring):
            try:
                return json.loads(value, **self.load_kwargs)
            except ValueError:
                raise ValueError("%s field got non-valid JSON" % self.name)
        return value

    def get_db_prep_value(self, value, connection, prepared=False):
        """Convert JSON object to a string"""

        if isinstance(value, basestring):
            return value
        return json.dumps(value, **self.dump_kwargs)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

    def value_from_object(self, obj):
        return json.dumps(super(JSONFieldBase, self).value_from_object(obj))

    def formfield(self, **kwargs):

        if "form_class" not in kwargs:
            kwargs["form_class"] = JSONFormField

        field = super(JSONFieldBase, self).formfield(**kwargs)

        if not field.help_text:
            field.help_text = "Enter valid JSON"

        return field


class JSONField(JSONFieldBase, models.TextField):
    """JSONField is a generic textfield that serializes/unserializes JSON objects"""


class JSONCharField(JSONFieldBase, models.CharField):
    """JSONCharField is a generic textfield that serializes/unserializes JSON objects,
    stored in the database like a CharField, which enables it to be used
    e.g. in unique keys"""


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^dynamicmodel\.fields\.(JSONField|JSONCharField)"])
except ImportError:
    pass
