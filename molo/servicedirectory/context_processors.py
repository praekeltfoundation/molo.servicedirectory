from django.conf import settings
from django.utils.six import string_types
from molo.core.models import SiteSettings
from wagtail.core.models import Site


def enable_service_directory_context(request):
    site = Site.find_for_request(request)
    site_settings = SiteSettings.for_site(site)
    enabled = site_settings.enable_service_directory
    ctx = dict(ENABLE_SERVICE_DIRECTORY=enabled)

    if enabled:
        radius = request.GET.get(
            'radius',
            site_settings.default_service_directory_radius
        )

        if isinstance(radius, string_types) and radius.isdigit():
            radius = int(radius)

        if radius and not isinstance(radius, int):
            radius = site_settings.default_service_directory_radius

        multi_category_select = site_settings. \
            enable_multi_category_service_directory_search

        options = getattr(
            settings,
            'SERVICE_DIRECTORY_RADIUS_OPTIONS', (
                (5, '5 KM'), (10, '10 KM'), (15, '15 KM'),
                (20, '20 KM'), (25, '25 KM'), (30, '30 KM'),
                (50, '50 KM'), (100, '100 KM'), (200, '200 KM'),
                (500, '500 KM'), (1000, '1000 KM'), (None, 'Show All')
            )
        )

        ctx.update({
            'SERVICE_DIRECTORY_RADIUS': radius,
            'SERVICE_DIRECTORY_RADIUS_OPTIONS': options,
            'SERVICE_DIRECTORY_MULTI_CATEGORY_SELECT': multi_category_select,
        })

    return ctx
