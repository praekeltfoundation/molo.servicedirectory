from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.utils.encoding import force_text
from import_export import fields as import_export_fields
from import_export import resources
from import_export.widgets import ManyToManyWidget, ForeignKeyWidget, Widget
from models import Category, Keyword, Country, Organisation, \
    OrganisationIncorrectInformationReport, OrganisationRating


# We're defining our own Field and ModelResource classes here to handle
# ManyToManyFields with a manually specified intermediate table ('through'
# attribute).
# Source: https://github.com/django-import-export/django-import-export/
# issues/151#issuecomment-59472728
class ManyToManyIntermediateModelCapableField(import_export_fields.Field):
    def is_m2m_with_intermediate_model(self, obj):
        field = obj._meta.get_field(self.attribute)
        return field.many_to_many and not field.rel.through._meta.auto_created

    def get_intermediate_model(self, obj):
        field = obj._meta.get_field(self.attribute)
        IntermediateModel = field.rel.through
        from_field_name = field.m2m_field_name()
        to_field_name = field.rel.to.__name__.lower()
        return IntermediateModel, from_field_name, to_field_name

    def remove_old_intermediates(self, obj, related_objects,
                                 IntermediateModel, from_field_name,
                                 to_field_name):

        imported_ids = set(ro.pk for ro in related_objects)
        current_related_objects = getattr(obj, self.attribute).all()

        for cro in current_related_objects:
            if cro.pk not in imported_ids:
                queryset = IntermediateModel.objects.filter(**{
                    from_field_name: obj,
                    to_field_name: cro
                })
                queryset.delete()

    def ensure_current_intermediates(self, obj, related_objects,
                                     IntermediateModel, from_field_name,
                                     to_field_name):

        for ro in related_objects:
            attributes = {
                from_field_name: obj,
                to_field_name: ro
            }
            IntermediateModel.objects.get_or_create(**attributes)

    def update_intermediates(self, obj, related_objects):
        IntermediateModel, from_field_name, to_field_name = \
            self.get_intermediate_model(obj)

        self.remove_old_intermediates(obj, related_objects, IntermediateModel,
                                      from_field_name, to_field_name)

        self.ensure_current_intermediates(obj, related_objects,
                                          IntermediateModel, from_field_name,
                                          to_field_name)

    def save(self, obj, data):
        """
        Cleans this field value and assign it to provided object.
        """
        if not self.readonly:
            attrs = self.attribute.split('__')
            for attr in attrs[:-1]:
                obj = getattr(obj, attr, None)

            if self.is_m2m_with_intermediate_model(obj):
                self.update_intermediates(obj, self.clean(data))
            else:
                setattr(obj, attrs[-1], self.clean(data))


# We're explicitly defining our ManyToManyFields on our resource classes
# because we want to export names rather than IDs, so we don't need to use
# this ModelResource class. You can use this class if you want to have support
# for ManyToManyFields with a manually specified intermediate table and you
# don't care for explicitly defining your ManyToManyFields on your resource
# classes.
class CustomModelResource(resources.ModelResource):
    @classmethod
    def field_from_django_field(self, field_name, django_field, readonly):
        """
        Returns a Resource Field instance for the given Django model field.
        """

        FieldWidget = self.widget_from_django_field(django_field)
        widget_kwargs = self.widget_kwargs_for_field(field_name)
        field = ManyToManyIntermediateModelCapableField(
            attribute=field_name,
            column_name=field_name,
            widget=FieldWidget(**widget_kwargs),
            readonly=readonly,
            default=django_field.default,
        )
        return field


class PointWidget(Widget):
    def clean(self, value):
        try:
            lat, lng = value.split(',')
            lat = float(lat)
            lng = float(lng)
            point = Point(lng, lat, srid=4326)
        except ValueError:
            raise ValidationError(
                'Invalid coordinates. Coordinates must be comma-separated'
                ' latitude,longitude decimals, eg: "-33.921124,18.417313"'
            )

        return point

    def render(self, value):
        return force_text('{0},{1}'.format(value.y, value.x))


class CountryResource(resources.ModelResource):
    class Meta:
        model = Country
        import_id_fields = ('name',)
        fields = ('name', 'iso_code',)
        skip_unchanged = True
        report_skipped = True


class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        import_id_fields = ('name',)
        fields = ('name', 'show_on_home_page',)
        skip_unchanged = True
        report_skipped = True


class KeywordResource(resources.ModelResource):
    def import_obj(self, obj, data, dry_run):
        keyword_category_names_set = set(
            data.get('categories', u'').split(',')
        )

        db_categories = Category.objects.filter(
            name__in=keyword_category_names_set
        )

        db_categories_set = set(
            [db_category.name for db_category in db_categories]
        )

        if keyword_category_names_set != db_categories_set:
            missing_categories = keyword_category_names_set.difference(
                db_categories_set
            )
            raise ValidationError(
                u"Keyword '{0}' is being imported with "
                u"Categories that are missing and "
                u"need to be imported/created: {1}".format(
                    data.get('name', u''), missing_categories)
            )

        return super(KeywordResource, self).import_obj(obj, data, dry_run)

    categories = ManyToManyIntermediateModelCapableField(
        attribute='categories',
        column_name='categories',
        widget=ManyToManyWidget(
            Category,
            field='name'
        ))

    class Meta:
        model = Keyword
        import_id_fields = ('name',)
        fields = ('name', 'categories', 'show_on_home_page',)
        skip_unchanged = True
        report_skipped = True


class OrganisationResource(resources.ModelResource):
    def import_obj(self, obj, data, dry_run):
        # check countries
        organisation_country_names_set = set(
            data.get('country', u'').split(',')
        )

        db_countries = Country.objects.filter(
            name__in=organisation_country_names_set
        )

        db_countries_set = set(
            [db_country.name for db_country in db_countries]
        )

        if organisation_country_names_set != db_countries_set:
            missing_countries = organisation_country_names_set.difference(
                db_countries_set
            )
            raise ValidationError(
                u"Organisation '{0}' is being imported with "
                u"Countries that are missing and "
                u"need to be imported/created: {1}".format(
                    data.get('name', u''), missing_countries)
            )

        # check categories
        organisation_category_names_set = set(
            data.get('categories', u'').split(',')
        )

        db_categories = Category.objects.filter(
            name__in=organisation_category_names_set
        )

        db_categories_set = set(
            [db_category.name for db_category in db_categories]
        )

        if organisation_category_names_set != db_categories_set:
            missing_categories = organisation_category_names_set.difference(
                db_categories_set
            )
            raise ValidationError(
                u"Organisation '{0}' is being imported with "
                u"Categories that are missing and "
                u"need to be imported/created: {1}".format(
                    data.get('name', u''), missing_categories)
            )

        # check keywords
        organisation_keyword_names_set = set(
            data.get('keywords', u'').split(',')
        )

        db_keywords = Keyword.objects.filter(
            name__in=organisation_keyword_names_set
        )

        db_keywords_set = set(
            [db_keyword.name for db_keyword in db_keywords]
        )

        if organisation_keyword_names_set != db_keywords_set:
            missing_keywords = organisation_keyword_names_set.difference(
                db_keywords_set
            )
            raise ValidationError(
                u"Organisation '{0}' is being imported with "
                u"Keywords that are missing and "
                u"need to be imported/created: {1}".format(
                    data.get('name', u''), missing_keywords)
            )

        return super(OrganisationResource, self).import_obj(obj, data, dry_run)

    country = import_export_fields.Field(
        attribute='country',
        column_name='country',
        widget=ForeignKeyWidget(
            Country,
            field='name'
        ))

    location = import_export_fields.Field(
        attribute='location',
        column_name='location',
        widget=PointWidget()
    )

    categories = ManyToManyIntermediateModelCapableField(
        attribute='categories',
        column_name='categories',
        widget=ManyToManyWidget(
            Category,
            field='name'
        ))

    keywords = ManyToManyIntermediateModelCapableField(
        attribute='keywords',
        column_name='keywords',
        widget=ManyToManyWidget(
            Keyword,
            field='name'
        ))

    class Meta:
        model = Organisation
        import_id_fields = ('name',)
        export_order = ('id', 'name', 'about', 'address', 'telephone',
                        'emergency_telephone', 'email', 'web', 'verified_as',
                        'age_range_min', 'age_range_max', 'opening_hours',
                        'country', 'location', 'categories', 'keywords',
                        'facility_code')
        skip_unchanged = True
        report_skipped = True


class OrganisationIncorrectInformationReportResource(resources.ModelResource):
    organisation = import_export_fields.Field(
        attribute='organisation__name', column_name='organisation'
    )

    class Meta:
        model = OrganisationIncorrectInformationReport

        fields = ('organisation', 'contact_details', 'address',
                  'trading_hours', 'other', 'other_detail', 'reported_at')

        export_order = ('organisation', 'contact_details', 'address',
                        'trading_hours', 'other', 'other_detail',
                        'reported_at')


class OrganisationRatingResource(resources.ModelResource):
    organisation = import_export_fields.Field(
        attribute='organisation__name', column_name='organisation'
    )

    class Meta:
        model = OrganisationRating
        fields = ('organisation', 'rating', 'rated_at')
        export_order = ('organisation', 'rating', 'rated_at')
