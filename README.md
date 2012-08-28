# django-dynamic-model

[![Build Status](https://secure.travis-ci.org/dobarkod/django-dynamic-model.png?branch=master)](http://travis-ci.org/dobarkod/django-dynamic-model)

Django Dynamic Model provides models which can be modified (fields added,
or removed) at runtime, from the code, without changing SQL database schema.

The dynamic fields can coexist with regular fields, can be picked up
and used by model forms, and can be accessed in the usual `object.field`
fashion in the code and templates.

The dynamic models aren't schemaless: valid fields are defined using
`DynamicSchema` and `DynamicSchemaField` models.

Here's a quick example:

    from dynamicmodel import DynamicModel, DynamicSchema, DynamicForm

    class MyModel(DynamicModel):
        name = models.CharField(max_length=100)  # regular field

    schema = DynamicSchema.get_for_model(MyModel)
    schema.add_field(name='nickname', type='CharField')
    schema.add_field(name='age', type='IntegerField')

    m1 = MyModel(name='John Doe')
    print m1.nickname # None
    m1.nickname = 'JD'
    m1.age = 21

    m1.save()

    class MyForm(DynamicForm):
        class Meta:
            model = MyModel

    form = MyForm({'field': 'foo'}, instance=m1)
    form.save()

## Installation

Install via pip directly from GitHub:

    pip install -e git+ssh://github.com/dobarkod/django-dynamic-model/tree/master

## Tests and docs

Documentation is sparse at the moment. Look at the tests for examples how
to use it (beyond the quick example above).

## Warning

Caveat emptor: This is beta software; the API will change a lot, and it may
still have serious bugs that will eat your data! All bug reports, fixes,
suggestions or pull requests are welcome.

## License

Copyright (C) 2012. GoodCode; Bundles JSONField copyright (c) 2012 Brad Jasper

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
