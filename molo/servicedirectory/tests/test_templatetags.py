from django.test import TestCase, RequestFactory


from molo.core.tests.base import MoloTestCaseMixin
from molo.servicedirectory.templatetags import servicedirectory_tags


class TestTemplateTagsProcessors(MoloTestCaseMixin, TestCase):
    def test_url_params_tag(self):
        data = {
            'radius': 5,
            'place_id': 'abc',
            'search': '123',
            'category': 1,
            'location': 'test',
            'place_latlng': 'abc',
            'all_categories': True,
            'keywords[]': 'keyword',
            'categories[]': 'category',
            'place_formatted_address': 'formatted_address',
        }
        request = RequestFactory().get('/', data=data)
        str_params = servicedirectory_tags.url_params(request)
        self.assertTrue(str_params)

        for k, v in data.items():
            self.assertIn('&{}={}'.format(k, v), str_params)
