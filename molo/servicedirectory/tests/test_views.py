import re
from mock import patch

from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory
from django.contrib.contenttypes.models import ContentType

from molo.core.models import Site, Main
from molo.core.tests.base import MoloTestCaseMixin
from molo.servicedirectory.views import get_service_directory_api_username


class MockSiteSettings(object):
    def __init__(self):
        self.service_directory_api_username = None


class MockOrganisation(object):
    pk = 1


def mock_make_request_to_servicedirectory_api(return_value):

    class MyMock(object):
        def read(self):
            url = return_value.get_full_url()
            # in case id's is required by url reversing
            if re.search('organisation/\d+/', url):
                return '{"id": 1}'
            return '{}'
    return MyMock()


@patch(
    'six.moves.urllib.request.urlopen',
    new=mock_make_request_to_servicedirectory_api
)
class TestViews(TestCase, MoloTestCaseMixin):
    def setUp(self):

        self.mk_root()
        main_content_type, created = ContentType.objects.get_or_create(
            model='main', app_label='core')

        # Create a new homepage
        self.main = Main.objects.create(
            title='title',
            slug='title',
            content_type=main_content_type,
            path='00010001',
            depth=2,
            numchild=0,
            url_path='/home/',
        )
        self.main.save_revision().publish()
        self.main.save()
        self.site = Site.objects.create(
            hostname='test.com',
            root_page=self.main
        )
        self.request = RequestFactory()

    @patch('molo.core.models.SiteSettings.for_site')
    def test_service_directory_api_username_returns_settings(self, site_patch):
        site_patch.return_value = MockSiteSettings()
        request = RequestFactory()
        request.site = None
        self.assertEqual(
            get_service_directory_api_username(request),
            'root',
        )

    def test_home_view(self):
        response = self.client.get(reverse('molo.servicedirectory:home'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, 'servicedirectory/home.html')

    def test_location_search_view(self):
        data = {}
        response = self.client.get(reverse('molo.servicedirectory:location-search'), data=data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, 'servicedirectory/location_search.html')

    def test_location_results_view(self):
        data = {}
        response = self.client.get(
            reverse('molo.servicedirectory:location-results'),
            data=data
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, 'servicedirectory/location_results.html')

    def test_organisation_results_view(self):
        data = {}
        response = self.client.get(
            reverse('molo.servicedirectory:organisation-results'),
            data=data
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, 'servicedirectory/organisation_results.html')

    def test_organisation_detail_view(self):
        org = MockOrganisation()
        data = {}
        response = self.client.get(
            reverse(
                'molo.servicedirectory:organisation-detail',
                kwargs=dict(organisation_id=org.pk,)),
            data=data
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, 'servicedirectory/organisation_detail.html')

    def test_organisation_report_view(self):
        org = MockOrganisation()
        data = {}
        response = self.client.get(
            reverse(
                'molo.servicedirectory:organisation-report',
                kwargs=dict(organisation_id=org.pk, )),
            data=data
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, 'servicedirectory/organisation_report.html')
