from django.test import TestCase, RequestFactory

from molo.core.models import SiteSettings, Site
from molo.core.tests.base import MoloTestCaseMixin
from molo.servicedirectory.context_processors \
    import enable_service_directory_context


class TestContextProcessors(MoloTestCaseMixin, TestCase):

    def test_enable_service_directory_context(self):
        self.mk_root()
        site = Site.objects.create(
            hostname='hostname', site_name='sitename',
            root_page_id=self.root.pk,
            is_default_site=True
        )
        site_setting = SiteSettings.objects.create(
            site=site,
            enable_service_directory=True,
            default_service_directory_radius=25,
            enable_multi_category_service_directory_search=True,
        )
        factory = RequestFactory()
        request = factory.get('/customer/details')
        request.GET = {'search': 'test'}
        request.path = 'servicedirectory/'
        ctx = enable_service_directory_context(request)
        self.assertEqual(
            ctx, {
                'SERVICE_DIRECTORY_RADIUS':
                    site_setting.default_service_directory_radius,
                'ENABLE_SERVICE_DIRECTORY': True,
                'SERVICE_DIRECTORY_MULTI_CATEGORY_SELECT': True,
                'SERVICE_DIRECTORY_RADIUS_OPTIONS': (
                    (5, '5 KM'), (10, '10 KM'), (15, '15 KM'),
                    (20, '20 KM'), (25, '25 KM'), (30, '30 KM'),
                    (50, '50 KM'), (100, '100 KM'), (200, '200 KM'),
                    (500, '500 KM'), (1000, '1000 KM'), (None, 'Show All')
                )
            })

        # Check when service directory is not enabled
        site_setting.enable_service_directory = False
        site_setting.save()
        ctx = enable_service_directory_context(request)
        self.assertEqual(ctx, {'ENABLE_SERVICE_DIRECTORY': False})
