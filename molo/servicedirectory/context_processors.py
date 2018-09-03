from django.conf import settings
from molo.core.models import SiteSettings


def enable_service_directory_context(request):
    site_settings = SiteSettings.for_site(request.site)
    enabled = site_settings.enable_service_directory
    ctx = dict(ENABLE_SERVICE_DIRECTORY=enabled)

    if enabled and 'servicedirectory' in request.path:
        radius = request.GET.get(
            'radius',
            site_settings.default_service_directory_radius
        )

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
            'SERVICE_DIRECTORY_RADIUS': int(radius),
            'SERVICE_DIRECTORY_RADIUS_OPTIONS': options,
        })

    return ctx