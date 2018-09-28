import re
from mock import patch

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import Site, Main, SiteSettings


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

        self.site = Site.objects.first()
        self.site.hostname = 'test.com',
        self.site.root_page = self.main
        self.site.save()

        self.site_settings = SiteSettings.for_site(self.site)
        self.site_settings.enable_service_directory = True
        self.site_settings. \
            default_service_directory_radius = 25
        self.site_settings. \
            enable_multi_category_service_directory_search = True
        self.site_settings.save()

    def test_home_view(self):
        data = {'categories[]': [1, 2], 'keywords[]': ['key1', 'key2']}
        response = self.client.get(
            reverse('molo.servicedirectory:home'), data=data)

        context = response.context_data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(context['categories'], [1, 2])
        self.assertTrue('keyword_list' in context.keys())
        self.assertEqual(context['keywords'], ['key1', 'key2'])

        self.assertEqual(
            response.context['ENABLE_SERVICE_DIRECTORY'],
            self.site_settings.enable_service_directory
        )

        multi_sel = 'SERVICE_DIRECTORY_MULTI_CATEGORY_SELECT'
        self.assertEqual(
            response.context[multi_sel],
            self.site_settings.
            enable_multi_category_service_directory_search
        )
        self.assertEqual(
            True,
            self.site_settings.
            enable_multi_category_service_directory_search
        )

        self.assertTrue(
            self.site_settings.enable_service_directory)

        self.assertTrue(
            self.site_settings.default_service_directory_radius)

        self.assertTrue(
            self.site_settings.
            enable_multi_category_service_directory_search)

        self.assertContains(response, 'Select Service Categories')

        self.assertContains(
            response, 'type="hidden" name="categories[]" value="1"')
        self.assertContains(
            response, 'type="hidden" name="categories[]" value="2"')
        self.assertTemplateUsed(
            response, 'servicedirectory/home.html')

    def test_location_search_view(self):
        data = {'categories[]': [1, 2], 'keywords[]': ['key1', 'key2']}
        response = self.client.get(
            reverse('molo.servicedirectory:location-search'), data=data)

        context = response.context_data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(context['categories'], [1, 2])
        self.assertEqual(context['keywords'], ['key1', 'key2'])

        self.assertContains(
            response, 'type="hidden" name="categories[]" value="1"')
        self.assertContains(
            response, 'type="hidden" name="categories[]" value="2"')
        self.assertContains(
            response, 'type="hidden" name="keywords[]" value="key1"')
        self.assertContains(
            response, 'type="hidden" name="keywords[]" value="key2"')

        self.assertTemplateUsed(
            response, 'servicedirectory/location_search.html')

    def test_location_results_view_missing_location(self):
        data = {
            'categories[]': [1, 2],
            'keywords[]': ['key1', 'key2']
        }
        response = self.client.get(
            reverse('molo.servicedirectory:location-results'),
            data=data
        )

        self.assertIn(
            reverse('molo.servicedirectory:location-search'),
            response.url,
        )
        self.assertIn(
            'Please select a location',
            response.cookies['messages'].value
        )

    def test_location_results_view(self):
        data = {
            'location': 'test',
            'categories[]': [1, 2],
            'keywords[]': ['key1', 'key2']
        }
        response = self.client.get(
            reverse('molo.servicedirectory:location-results'),
            data=data
        )

        context = response.context_data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(context['categories'], [1, 2])
        self.assertEqual(context['keywords'], ['key1', 'key2'])
        self.assertEqual(
            response.context['SERVICE_DIRECTORY_RADIUS'], 25)

        self.assertContains(
            response, 'type="hidden" name="categories[]" value="1"')
        self.assertContains(
            response, 'type="hidden" name="categories[]" value="2"')
        self.assertContains(
            response, 'type="hidden" name="keywords[]" value="key1"')
        self.assertContains(
            response, 'type="hidden" name="keywords[]" value="key2"')

        self.assertTemplateUsed(
            response, 'servicedirectory/location_results.html')

    def test_organisation_results_view_no_search_params(self):
        response = self.client.get(
            reverse('molo.servicedirectory:organisation-results')
        )
        self.assertIn(
            reverse('molo.servicedirectory:home'),
            response.url
        )
        self.assertIn(
            'Please select at least one category or service',
            response.cookies['messages'].value
        )

    def test_organisation_results_view(self):
        data = {
            'radius': 5,
            'categories[]': [1, 2],
            'keywords[]': ['key1', 'key2']
        }
        response = self.client.get(
            reverse('molo.servicedirectory:organisation-results'),
            data=data
        )

        context = response.context_data
        self.assertEqual(response.status_code, 200)

        self.assertEqual(context['categories'], [1, 2])
        self.assertEqual(context['keywords'], ['key1', 'key2'])
        self.assertEqual(
            response.context['SERVICE_DIRECTORY_RADIUS'], 5)

        self.assertContains(
            response, 'type="hidden" name="categories[]" value="1"')
        self.assertContains(
            response, 'type="hidden" name="categories[]" value="2"')
        self.assertContains(
            response, 'type="hidden" name="keywords[]" value="key1"')
        self.assertContains(
            response, 'type="hidden" name="keywords[]" value="key2"')

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

    def test_invalid_search_params(self):
        data = {
            'radius': 'abc',
            'categories[]': ['abc', 'xyz'],
            'keywords[]': ['key1', 'key2']
        }
        response = self.client.get(
            reverse('molo.servicedirectory:location-search'), data=data)

        context = response.context_data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(context['categories'], [])
        self.assertEqual(context['keywords'], ['key1', 'key2'])

        self.assertEqual(
            response.context['SERVICE_DIRECTORY_RADIUS'], 25)
        self.assertTemplateUsed(
            response, 'servicedirectory/location_search.html')
