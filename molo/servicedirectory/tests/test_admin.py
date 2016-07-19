from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.test import TestCase
from service_directory.api.models import Country, Organisation, Category, \
    Keyword, KeywordCategory, OrganisationCategory, OrganisationKeyword


class OrganisationModelFormTestCase(TestCase):
    SU_USERNAME = 'test'
    SU_PASSWORD = 'test'

    @classmethod
    def setUpTestData(cls):
        User.objects.create_superuser(
            cls.SU_USERNAME, 'test@test.com', cls.SU_PASSWORD
        )

        cls.country = Country.objects.create(
            name='South Africa',
            iso_code='ZA'
        )
        cls.country.full_clean()  # force model validation to happen

        cls.category = Category.objects.create(name='Test Category')
        cls.category.full_clean()  # force model validation to happen

        cls.keyword = Keyword.objects.create(name='test')
        cls.keyword.full_clean()  # force model validation to happen

        kwc = KeywordCategory.objects.create(
            keyword=cls.keyword, category=cls.category
        )
        kwc.full_clean()  # force model validation to happen

        cls.org_cbmh = Organisation.objects.create(
            name='Netcare Christiaan Barnard Memorial Hospital',
            country=cls.country,
            location=Point(18.418231, -33.921859, srid=4326)
        )
        cls.org_cbmh.full_clean()  # force model validation to happen

        oc = OrganisationCategory.objects.create(
            organisation=cls.org_cbmh, category=cls.category
        )
        oc.full_clean()  # force model validation to happen

        ok = OrganisationKeyword.objects.create(
            organisation=cls.org_cbmh, keyword=cls.keyword
        )
        ok.full_clean()  # force model validation to happen

        cls.api_url = '/admin/api/organisation/{0}/'.format(cls.org_cbmh.id)

    def setUp(self):
        self.client.login(username=self.SU_USERNAME, password=self.SU_PASSWORD)

    def get_post_payload_for_test_organisation(self):
        data = {
            'name': self.org_cbmh.name,
            'about': self.org_cbmh.about,
            'address': self.org_cbmh.address,
            'telephone': self.org_cbmh.telephone,
            'emergency_telephone': self.org_cbmh.emergency_telephone,
            'email': self.org_cbmh.email,
            'web': self.org_cbmh.web,
            'verified_as': self.org_cbmh.verified_as,
            'age_range_min': self.org_cbmh.age_range_min if
            self.org_cbmh.age_range_min else '',
            'age_range_max': self.org_cbmh.age_range_max if
            self.org_cbmh.age_range_max else '',
            'opening_hours': self.org_cbmh.opening_hours,
            'country': self.org_cbmh.country_id,
            'location': self.org_cbmh.location,
            'facility_code': self.org_cbmh.facility_code,

            # fields from OrganisationCategoryInlineModelAdmin
            'organisationcategory_set-TOTAL_FORMS': 1,
            'organisationcategory_set-INITIAL_FORMS': 0,
            'organisationcategory_set-MIN_NUM_FORMS': 0,
            'organisationcategory_set-MAX_NUM_FORMS': 1000,
            'organisationcategory_set-0-id': '',
            'organisationcategory_set-0-organisation': self.org_cbmh.id,
            'organisationcategory_set-0-category': '',
            'organisationcategory_set-__prefix__-id': '',
            'organisationcategory_set-__prefix__-organisation':
                self.org_cbmh.id,
            'organisationcategory_set-__prefix__-category': '',

            # fields from OrganisationKeywordInlineModelAdmin
            'organisationkeyword_set-TOTAL_FORMS': 1,
            'organisationkeyword_set-INITIAL_FORMS': 0,
            'organisationkeyword_set-MIN_NUM_FORMS': 0,
            'organisationkeyword_set-MAX_NUM_FORMS': 1000,
            'organisationkeyword_set-0-id': '',
            'organisationkeyword_set-0-organisation': self.org_cbmh.id,
            'organisationkeyword_set-0-keyword': '',
            'organisationkeyword_set-__prefix__-id': '',
            'organisationkeyword_set-__prefix__-organisation':
                self.org_cbmh.id,
            'organisationkeyword_set-__prefix__-keyword': '',
        }
        return data

    def test_location_coords_field_overrides_map_location(self):
        new_lat = -33.921124
        new_lng = 18.417313

        data = self.get_post_payload_for_test_organisation()
        data['location_coords'] = '{0},{1}'.format(new_lat, new_lng)

        response = self.client.post(self.api_url, data)

        # if the status_code is 200 then validation for one of the fields
        # probably failed - check the HTML response content
        self.assertEqual(302, response.status_code)
        self.assertTrue(
            response._headers['location'][1].endswith(
                '/admin/api/organisation/'
            )
        )

        org = Organisation.objects.get(pk=self.org_cbmh.id)
        self.assertEqual(new_lat, org.location.y)
        self.assertEqual(new_lng, org.location.x)

    def test_location_coords_field_validation(self):
        data = self.get_post_payload_for_test_organisation()
        data['location_coords'] = '123abc'

        response = self.client.post(self.api_url, data)

        self.assertContains(response, 'Invalid coordinates')

    def test_map_location_required_if_location_coords_field_empty(self):
        data = self.get_post_payload_for_test_organisation()
        del data['location']

        response = self.client.post(self.api_url, data)

        self.assertContains(response, 'No geometry value provided')

    def test_map_location_not_required_if_location_coords_supplied(self):
        new_lat = -33.921124
        new_lng = 18.417313

        data = self.get_post_payload_for_test_organisation()
        del data['location']
        data['location_coords'] = '{0},{1}'.format(new_lat, new_lng)

        response = self.client.post(self.api_url, data)

        # if the status_code is 200 then validation for one of the fields
        # probably failed - check the HTML response content
        self.assertEqual(302, response.status_code)
        self.assertTrue(
            response._headers['location'][1].endswith(
                '/admin/api/organisation/'
            )
        )
