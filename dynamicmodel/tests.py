"""
Tests for DynamicModel, DynamicModelWithSchema and DynamicForm
"""

from django.test import TestCase
from .models import DynamicModel, DynamicForm, DynamicSchema, \
    DynamicSchemaField
from django.db import models, connection
from django.core.exceptions import ValidationError

from django.core.cache import cache


class TestModel(DynamicModel):

    TYPE = (
        ('email', 'Email item'),
        ('contact', 'Contact item'),
    )

    type = models.CharField(max_length=100, choices=TYPE, editable=False)
    about = models.CharField(max_length=100, default='about value')

    @classmethod
    def get_schema_type_descriptor(cls):
        return 'type'


class TestForm(DynamicForm):

    class Meta:
        model = TestModel


class M2MModel(models.Model):

    testmodels = models.ManyToManyField(TestModel)


class FalseModel(models.Model):

    TYPE = (
        ('email', 'Email item'),
        ('contact', 'Contact item'),
    )

    type = models.CharField(max_length=100, choices=TYPE, editable=False)
    about = models.CharField(max_length=100, default='about value')

    @classmethod
    def get_schema_type_descriptor(cls):
        return 'type'


class FalseForm(DynamicForm):

    class Meta:
        model = FalseModel


class TypelessModel(DynamicModel):

    about = models.CharField(max_length=100, default='about value')


class TypelessForm(DynamicForm):

    class Meta:
        model = TypelessModel


# testing DynamicModel
class DynamicModelTest(TestCase):

    def clear(self):
        cache.clear()
        M2MModel.objects.all().delete()
        TestModel.objects.all().delete()
        FalseModel.objects.all().delete()
        TypelessModel.objects.all().delete()
        DynamicSchema.objects.all().delete()
        DynamicSchemaField.objects.all().delete()

    def setUp(self):
        self.clear()

    def test_extra_fields_nonvalid_json(self):
        model = TestModel()
        self.assertRaises(ValueError, setattr, model, 'extra_fields', 'a')

    def test_extra_fields_valid_json(self):
        model = TestModel()
        model.extra_fields = '{}'

    def test_extra_fields_db_save(self):

        model = TestModel()
        DynamicSchemaField.objects.create(schema=model.get_schema(),
            name='experiment', field_type='CharField')

        self.ex_val = "experimental value"
        model.experiment = self.ex_val
        model.save()
        model_db_id = model.id

        new_model = TestModel.objects.get(pk=model_db_id)
        self.assertEqual(self.ex_val, new_model.experiment)

    def test_get_nonexistent_attr(self):

        model = TestModel()
        self.assertRaises(AttributeError, getattr, model, "attribute_that_does_not_exist")

    def test_dyn_attr_in_extra_fields(self):

        model = TestModel()
        DynamicSchemaField.objects.create(schema=model.get_schema(),
            name='experiment', field_type='CharField')

        self.ex_val = "experimental value"
        model.experiment = self.ex_val
        model.save()
        model_db_id = model.id

        new_model = TestModel.objects.get(pk=model_db_id)
        self.assertEqual(new_model.extra_fields['experiment'],
            new_model.experiment)

    def test_dyn_attr_changes_extra_fields(self):

        model = TestModel()
        DynamicSchemaField.objects.create(schema=model.get_schema(), name='experiment2',
            field_type='CharField')

        model.experiment2 = "experiment2 value"
        self.assertEqual(model.extra_fields['experiment2'],
            model.experiment2)

    def test_accept_schema_attr(self):

        model = TestModel()
        DynamicSchemaField.objects.create(schema=model.get_schema(), name='schema',
            field_type='CharField')

        model.schema = "schema value changed"
        self.assertEqual(model.extra_fields['schema'], model.schema)

    def test_underscore_schema_attr_fail(self):

        model = TestModel()
        # this dyn field has no effect because _schema is reserved attr
        DynamicSchemaField.objects.create(schema=model.get_schema(), name='_schema',
            field_type='CharField')

        model._schema = "schema value changed"
        self.assertNotEqual(model.get_extra_field_value('_schema'), model._schema)

    def test_extend_ignore_attrs(self):

        model = TestModel()

        model.schema = "schema value"
        self.assertNotIn('schema', model.extra_fields)

        model.schema_custom_ignore = "schema_custom_ignore value"
        self.assertNotIn('schema_custom_ignore', model.extra_fields)

        self.assertTrue(hasattr(model, '_meta'))
        model._meta = model._meta
        self.assertNotIn('_meta', model.extra_fields)

        model.about = "about text"
        self.assertNotIn('about', model.extra_fields)

    def test_rename(self):

        model = TestModel()

        DynamicSchemaField.objects.create(schema=model.get_schema(),
            name='old_field', field_type='CharField')

        model.old_field = "old field value"

        dsf = DynamicSchemaField.objects.get(schema=model.get_schema(),
            name='old_field', field_type='CharField')
        dsf.name = 'new_field'

        self.assertRaises(ValidationError, dsf.save)

    def test_delete_schema_field(self):

        model = TestModel()

        f1 = DynamicSchemaField.objects.create(schema=model.get_schema(),
            name='field_one', field_type='CharField')
        DynamicSchemaField.objects.create(schema=model.get_schema(),
            name='field_two', field_type='CharField')

        model.field_one = "field one"
        model.field_two = "field two"
        model.save()

        f1.delete()

        fresh_model = TestModel.objects.get(pk=model.id)

        # attr 'field_one' does not exist anymore because related
        # db entry was deleted
        self.assertFalse(hasattr(fresh_model, 'field_one'))
        # attr 'field_two' still exists
        self.assertTrue(hasattr(fresh_model, 'field_two'))

    def test_manually_create_schema_typeless(self):
        schema = DynamicSchema.get_for_model(TypelessModel)
        schema.add_field(name='field', type='CharField')

        m1 = TypelessModel()
        m1.field = 'foo'
        m1.save()
        m2 = TypelessModel.objects.get(id=m1.id)
        self.assertEqual(m2.field, 'foo')

    def test_manually_create_schema_typed(self):
        schema = DynamicSchema.get_for_model(TestModel, type_value='foo')
        schema.add_field(name='field', type='CharField')

        m1 = TestModel.objects.create(type='foo')
        m1.field = 'foo'
        m1.save()
        m2 = TestModel.objects.get(id=m1.id)
        self.assertEqual(m2.field, 'foo')

        m3 = TestModel.objects.create(type='bar')
        m3.field = 'foo'
        m3.save()
        m4 = TestModel.objects.get(id=m3.id)
        self.assertFalse(hasattr(m4, 'field'))

    def test_schema_add_remove_field(self):
        schema = DynamicSchema.get_for_model(TypelessModel)
        schema.add_field(name='field', type='CharField')

        m1 = TypelessModel.objects.create()
        self.assertTrue(hasattr(m1, 'field'))

        schema.remove_field(name='field')
        m2 = TypelessModel.objects.get(id=m1.id)
        m2 = TypelessModel.objects.create()
        self.assertFalse(hasattr(m2, 'field'))


class DynamicModelCachingTest(TestCase):

    def clear(self):
        cache.clear()
        M2MModel.objects.all().delete()
        TestModel.objects.all().delete()
        FalseModel.objects.all().delete()
        TypelessModel.objects.all().delete()
        DynamicSchema.objects.all().delete()
        DynamicSchemaField.objects.all().delete()

    def setUp(self):
        self.clear()

    def test_num_of_queries_on_related(self):
        with self.settings(DEBUG=True):
            m2m = M2MModel.objects.create()
            DynamicSchemaField.objects.create(
                schema=DynamicSchema.get_for_model(TestModel), name='email',
                field_type='EmailField')
            m2m.testmodels.add(
                TestModel.objects.create(about='one'),
                TestModel.objects.create(about='two'),
                TestModel.objects.create(about='three'),
                TestModel.objects.create(about='four'),
                TestModel.objects.create(about='five'),
                TestModel.objects.create(about='six'),
            )
            start_q_num = len(connection.queries)
            [(el.about, el.email) for el in m2m.testmodels.all()]
            end_q_num = len(connection.queries)
            self.assertEqual(end_q_num - start_q_num, 1)

    def test_num_of_queries_on_related_with_dependency(self):
        """ integration test
        test cache functionality in more complex environment """

        with self.settings(DEBUG=True):
            schema = DynamicSchema.get_for_model(TestModel)
            schema.add_field("field", "IntegerField")
            start_q_num = len(connection.queries)
            self.assertEqual(
                DynamicSchema.get_for_model(TestModel).fields.all()[0].name,
                "field")
            end_q_num = len(connection.queries)
            self.assertEqual(end_q_num - start_q_num, 0)

            schema = DynamicSchema.get_for_model(TestModel)
            schema.remove_field("field")
            start_q_num = len(connection.queries)
            self.assertEqual(
                DynamicSchema.get_for_model(TestModel).fields.count(), 0)
            end_q_num = len(connection.queries)
            self.assertEqual(end_q_num - start_q_num, 0)

            m2m = M2MModel.objects.create()
            DynamicSchemaField.objects.create(
                schema=DynamicSchema.get_for_model(TestModel), name='email',
                field_type='EmailField')
            m2m.testmodels.add(
                TestModel.objects.create(about='one'),
                TestModel.objects.create(about='two'),
                TestModel.objects.create(about='three'),
                TestModel.objects.create(about='four'),
                TestModel.objects.create(about='five'),
                TestModel.objects.create(about='six'),
            )
            start_q_num = len(connection.queries)
            [(el.about, el.email) for el in m2m.testmodels.all()]
            end_q_num = len(connection.queries)
            self.assertEqual(end_q_num - start_q_num, 1)

    def test_second_schema_fetching_doesnt_hit_db(self):
        with self.settings(DEBUG=True):
            DynamicSchema.get_for_model(TestModel)
            start_q_num = len(connection.queries)
            DynamicSchema.get_for_model(TestModel)
            end_q_num = len(connection.queries)
            self.assertEqual(end_q_num - start_q_num, 0)

    def test_cache_updated_after_adding_schema_field(self):
        with self.settings(DEBUG=True):
            schema = DynamicSchema.get_for_model(TestModel)
            schema.add_field("field", "IntegerField")
            start_q_num = len(connection.queries)
            self.assertEqual(
                DynamicSchema.get_for_model(TestModel).fields.all()[0].name,
                "field")
            end_q_num = len(connection.queries)
            self.assertEqual(end_q_num - start_q_num, 0)

    def test_cache_updated_after_removing_schema_field(self):
        with self.settings(DEBUG=True):
            schema = DynamicSchema.get_for_model(TestModel)
            schema.add_field("field", "IntegerField")
            schema.remove_field("field")
            start_q_num = len(connection.queries)
            self.assertEqual(
                DynamicSchema.get_for_model(TestModel).fields.count(), 0)
            end_q_num = len(connection.queries)
            self.assertEqual(end_q_num - start_q_num, 0)

    def test_delete_schema_qs_clears_cache(self):
        with self.settings(DEBUG=True):
            DynamicSchema.get_for_model(TestModel)
            self.assertIsNotNone(
                cache.get(DynamicSchema.get_cache_key_static(TestModel, '')))
            DynamicSchema.objects.all().delete()
            self.assertIsNone(
                cache.get(DynamicSchema.get_cache_key_static(TestModel, '')))

    def test_delete_schema_qs_with_diff_types_clears_cache(self):
        with self.settings(DEBUG=True):

            DynamicSchema.get_for_model(TestModel)
            DynamicSchema.get_for_model(TestModel, 'some_value')

            # there is cached value
            self.assertIsNotNone(
                cache.get(DynamicSchema.get_cache_key_static(TestModel, '')))
            self.assertIsNotNone(
                cache.get(DynamicSchema.get_cache_key_static(TestModel,
                    'some_value')))

            DynamicSchema.objects.all().delete()

            # there is no cached value
            self.assertIsNone(
                cache.get(DynamicSchema.get_cache_key_static(TestModel, '')))
            self.assertIsNone(
                cache.get(DynamicSchema.get_cache_key_static(TestModel,
                    'some_value')))

    def test_delete_schema_clears_cache(self):
        with self.settings(DEBUG=True):
            schema = DynamicSchema.get_for_model(TestModel)
            self.assertIsNotNone(
                cache.get(DynamicSchema.get_cache_key_static(TestModel, '')))
            schema.delete()
            self.assertIsNone(
                cache.get(DynamicSchema.get_cache_key_static(TestModel, '')))


# testing DynamicModel and DynamicForm
class DynamicFormTest(TestCase):

    def clear(self):
        cache.clear()
        M2MModel.objects.all().delete()
        TestModel.objects.all().delete()
        FalseModel.objects.all().delete()
        TypelessModel.objects.all().delete()
        DynamicSchema.objects.all().delete()
        DynamicSchemaField.objects.all().delete()

    def setUp(self):
        """prepare DynamicFormTest environment"""
        self.clear()

    def test_accept_any_extra_field(self):

        model = TestModel()
        DynamicSchemaField.objects.create(schema=model.get_schema(), name='email',
            field_type='EmailField')

        form = TestForm({
            'about': 'about change',
            'fail_field': 'fail field',
            'email': 'a@a.com',
        }, instance=model)

        form.is_valid()
        self.assertFalse(form['about'].errors)
        self.assertFalse(form['email'].errors)

    def test_validate_schema_fields(self):

        model = TestModel()
        DynamicSchemaField.objects.create(schema=model.get_schema(), name='email',
            field_type='EmailField')

        # should fail with invalid email value
        form_invalid = TestForm({
            'about': 'about change',
            'email': 'wrong email',
        }, instance=model)

        form_invalid.is_valid()
        self.assertFalse(form_invalid['about'].errors)
        self.assertTrue(form_invalid['email'].errors)

        # should pass with valid email value
        form = TestForm({
            'about': 'about change',
            'email': 'a@a.com',
        }, instance=model)

        form.is_valid()
        self.assertFalse(form['about'].errors)
        self.assertFalse(form['email'].errors)

    def test_validate_schema_fields_typeless(self):
        """Test form validation on dynamicmodel that has no
        get_schema_type_descriptor method declared
        """
        model = TypelessModel()
        DynamicSchemaField.objects.create(schema=model.get_schema(), name='email',
            field_type='EmailField')

        # should fail with invalid email value
        form_invalid = TypelessForm({
            'about': 'about change',
            'email': 'wrong email',
        }, instance=model)

        form_invalid.is_valid()
        self.assertFalse(form_invalid['about'].errors)
        self.assertTrue(form_invalid['email'].errors)

        # should pass with valid email value
        form = TypelessForm({
            'about': 'about change',
            'email': 'a@a.com',
        }, instance=model)

        form.is_valid()
        self.assertFalse(form['about'].errors)
        self.assertFalse(form['email'].errors)

    def test_form_with_type(self):

        # init schema fields
        info_model = TestModel(type='info')
        DynamicSchemaField.objects.create(schema=info_model.get_schema(), name='info',
            field_type='TextField')
        DynamicSchemaField.objects.create(schema=info_model.get_schema(), name='more_info',
            field_type='TextField', required=False)

        # should pass with info value set and
        # more_info empty (more_info not required)
        info_form = TestForm({
            'about': 'about change',
            'info': 'some info text',
            'more_info': '',
        }, instance=info_model)

        self.assertTrue(info_form.is_valid())

    def test_form_create(self):

        model = TestModel()
        DynamicSchemaField.objects.create(schema=model.get_schema(), name='email',
            field_type='EmailField')

        form = TestForm({
            'about': 'about change',
            'email': 'a@a.com',
        }, model)

        model_from_form = form.save()

        model_from_db = TestModel.objects.get(pk=model_from_form.id)

        self.assertEqual(model_from_form.extra_fields,
            model_from_db.extra_fields)

    def test_false_form(self):

        self.assertRaises(ValueError, FalseForm)
