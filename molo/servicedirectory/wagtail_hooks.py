from wagtailmodeladmin.options import ModelAdmin, ModelAdminGroup, \
    wagtailmodeladmin_register
from .models import Country, Category, Keyword, Organisation, \
    OrganisationIncorrectInformationReport, OrganisationRating


class CountryModelAdmin(ModelAdmin):
    model = Country
    menu_label = 'Countries'
    menu_icon = 'doc-full-inverse'


class CategoryModelAdmin(ModelAdmin):
    model = Category
    menu_label = 'Categories'
    menu_icon = 'doc-full-inverse'


class KeywordModelAdmin(ModelAdmin):
    model = Keyword
    menu_label = 'Keywords'
    menu_icon = 'doc-full-inverse'


class OrganisationModelAdmin(ModelAdmin):
    model = Organisation
    menu_label = 'Organisations'
    menu_icon = 'doc-full-inverse'


class OrganisationIncorrectInformationReportModelAdmin(ModelAdmin):
    model = OrganisationIncorrectInformationReport
    menu_label = 'Organisations - Incorrect Information Reports'
    menu_icon = 'doc-full-inverse'


class OrganisationRatingModelAdmin(ModelAdmin):
    model = OrganisationRating
    menu_label = 'Organisations - Ratings'
    menu_icon = 'doc-full-inverse'


class ServiceDirectoryModelAdminGroup(ModelAdminGroup):
    menu_label = 'Service Directory'
    menu_icon = 'folder-open-inverse'
    items = (CountryModelAdmin,
             CategoryModelAdmin,
             KeywordModelAdmin,
             OrganisationModelAdmin,
             OrganisationIncorrectInformationReportModelAdmin,
             OrganisationRatingModelAdmin)


wagtailmodeladmin_register(ServiceDirectoryModelAdminGroup)
