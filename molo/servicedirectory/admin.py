from admin_import_export import CountryResource, OrganisationResource, \
    CategoryResource, KeywordResource, \
    OrganisationIncorrectInformationReportResource, OrganisationRatingResource
from admin_model_forms import OrganisationModelForm
from django.contrib import admin
from import_export.admin import ImportExportMixin, ExportMixin
from leaflet.admin import LeafletGeoAdmin
from models import Country, Organisation, Category, Keyword, \
    OrganisationIncorrectInformationReport, OrganisationRating, \
    KeywordCategory, OrganisationCategory, OrganisationKeyword


class CountryModelAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'iso_code')
    resource_class = CountryResource


class CategoryModelAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'show_on_home_page')
    resource_class = CategoryResource


class KeywordCategoryInlineModelAdmin(admin.TabularInline):
    model = KeywordCategory
    extra = 1


class KeywordModelAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'formatted_categories', 'show_on_home_page')
    resource_class = KeywordResource
    inlines = (KeywordCategoryInlineModelAdmin,)


class OrganisationCategoryInlineModelAdmin(admin.TabularInline):
    model = OrganisationCategory
    extra = 1


class OrganisationKeywordInlineModelAdmin(admin.TabularInline):
    model = OrganisationKeyword
    extra = 1


class OrganisationModelAdmin(ImportExportMixin, LeafletGeoAdmin):
    form = OrganisationModelForm
    list_display = ('name', 'country')
    resource_class = OrganisationResource
    inlines = (OrganisationCategoryInlineModelAdmin,
               OrganisationKeywordInlineModelAdmin)


class OrganisationIncorrectInformationReportModelAdmin(ExportMixin,
                                                       admin.ModelAdmin):
    """
    We disallow adding, modifying or deleting
    OrganisationIncorrectInformationReport instances as these should only be
    created through the API and not modified afterwards.
    Currently this is the easiest way to have a 'read-only' model in admin.
    """
    actions = None

    readonly_fields = ('organisation', 'reported_at', 'contact_details',
                       'address', 'trading_hours', 'other', 'other_detail')

    list_display = ('organisation', 'reported_at')

    list_filter = ('organisation', 'reported_at')

    resource_class = OrganisationIncorrectInformationReportResource

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class OrganisationRatingModelAdmin(ExportMixin, admin.ModelAdmin):
    """
    We disallow adding, modifying or deleting OrganisationRating instances as
    these should only be created through the API and not modified afterwards.
    Currently this is the easiest way to have a 'read-only' model in admin.
    """
    actions = None

    readonly_fields = ('organisation', 'rated_at', 'rating')

    list_display = ('organisation', 'rating', 'rated_at')

    list_filter = ('organisation', 'rating', 'rated_at')

    resource_class = OrganisationRatingResource

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# Register your models here.
admin.site.register(Country, CountryModelAdmin)
admin.site.register(Organisation, OrganisationModelAdmin)
admin.site.register(Category, CategoryModelAdmin)
admin.site.register(Keyword, KeywordModelAdmin)
admin.site.register(
    OrganisationIncorrectInformationReport,
    OrganisationIncorrectInformationReportModelAdmin
)
admin.site.register(OrganisationRating, OrganisationRatingModelAdmin)
