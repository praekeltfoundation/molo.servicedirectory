from django.test import TestCase, RequestFactory

from mock import patch

from molo.servicedirectory.views import get_service_directory_api_username


class MockSiteSettings(object):
    def __init__(self):
        self.service_directory_api_username = None


class TestViews(TestCase):
    @patch('molo.core.models.SiteSettings.for_site')
    def test_service_directory_api_username_returns_settings(self, site_patch):
        site_patch.return_value = MockSiteSettings()
        request = RequestFactory()
        request.site = None
        self.assertEqual(
            get_service_directory_api_username(request),
            'root',
        )
