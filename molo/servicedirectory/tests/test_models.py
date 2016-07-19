from datetime import datetime, timedelta

from django.contrib.gis.geos import Point
from django.test import TestCase
from pytz import utc
from service_directory.api.models import Country, Organisation, Category,\
    Keyword, OrganisationIncorrectInformationReport, OrganisationRating, \
    KeywordCategory, OrganisationCategory, OrganisationKeyword


class CountryTestCase(TestCase):
    def setUp(self):
        country = Country.objects.create(
            name='South Africa',
            iso_code='ZA'
        )
        country.full_clean()  # force model validation to happen

    def test_query(self):
        countries = Country.objects.filter(name='South Africa')

        self.assertEqual(1, len(countries))
        self.assertEqual('South Africa', countries[0].name)
        self.assertEqual('South Africa', countries[0].__unicode__())

    def test_case_insensitivity(self):
        countries = Country.objects.filter(name='SOUTH AFRICA')
        self.assertEqual(1, len(countries))

        countries = Country.objects.filter(iso_code='za')
        self.assertEqual(1, len(countries))

    def test_update(self):
        countries = Country.objects.filter(name='South Africa')

        country = countries[0]
        country.iso_code = 'SA'
        country.save()

        country.refresh_from_db()

        self.assertEqual('SA', country.iso_code)


class CategoryTestCase(TestCase):
    def setUp(self):
        cat = Category.objects.create(name='Test Category')
        cat.full_clean()  # force model validation to happen

    def test_query(self):
        categories = Category.objects.filter(name='Test Category')

        self.assertEqual(1, len(categories))
        self.assertEqual('Test Category', categories[0].name)
        self.assertEqual('Test Category', categories[0].__unicode__())

    def test_case_insensitivity(self):
        categories = Category.objects.filter(name='TEST CATEGORY')
        self.assertEqual(1, len(categories))

    def test_update(self):
        categories = Category.objects.filter(name='Test Category')

        category = categories[0]
        category.name = 'Changed Category'
        category.save()

        category.refresh_from_db()

        self.assertEqual('Changed Category', category.name)


class KeywordTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category')
        self.category.full_clean()  # force model validation to happen

        keyword = Keyword.objects.create(name='test')
        keyword.full_clean()  # force model validation to happen

        kwc = KeywordCategory.objects.create(
            keyword=keyword, category=self.category
        )
        kwc.full_clean()  # force model validation to happen

    def test_query(self):
        keywords = Keyword.objects.filter(name='test')

        self.assertEqual(1, len(keywords))
        self.assertEqual('test', keywords[0].name)
        self.assertEqual('test', keywords[0].__unicode__())
        self.assertTrue(
            self.category.name in keywords[0].formatted_categories()
        )

    def test_case_insensitivity(self):
        keywords = Keyword.objects.filter(name='TEST')
        self.assertEqual(1, len(keywords))

    def test_update(self):
        keyword = Keyword.objects.filter(name='test').get()

        keyword.name = 'test changed'
        keyword.save()

        keyword.refresh_from_db()

        self.assertEqual('test changed', keyword.name)


class OrganisationTestCase(TestCase):
    def setUp(self):
        self.country = Country.objects.create(
            name='South Africa',
            iso_code='ZA'
        )
        self.country.full_clean()  # force model validation to happen

        self.category = Category.objects.create(name='Test Category')
        self.category.full_clean()  # force model validation to happen

        self.keyword = Keyword.objects.create(name='test')
        self.keyword.full_clean()  # force model validation to happen

        kwc = KeywordCategory.objects.create(
            keyword=self.keyword, category=self.category
        )
        kwc.full_clean()  # force model validation to happen

        org = Organisation.objects.create(
            name='Test Org',
            country=self.country,
            location=Point(18.505496, -33.891937, srid=4326)
        )
        org.full_clean()  # force model validation to happen

        oc = OrganisationCategory.objects.create(
            organisation=org, category=self.category
        )
        oc.full_clean()  # force model validation to happen

        ok = OrganisationKeyword.objects.create(
            organisation=org, keyword=self.keyword
        )
        ok.full_clean()  # force model validation to happen

    def test_query(self):
        organisations = Organisation.objects.filter(name='Test Org')

        self.assertEqual(1, len(organisations))
        self.assertEqual('Test Org', organisations[0].name)
        self.assertEqual('Test Org', organisations[0].__unicode__())

        self.assertTrue(
            'Test Category' in organisations[0].formatted_categories()
        )
        self.assertTrue('test' in organisations[0].formatted_keywords())

    def test_update(self):
        organisations = Organisation.objects.filter(name='Test Org')

        organisation = organisations[0]
        organisation.name = 'Changed Org'
        organisation.save()

        organisation.refresh_from_db()

        self.assertEqual('Changed Org', organisation.name)


class OrganisationIncorrectInformationReportTestCase(TestCase):
    def setUp(self):
        self.country = Country.objects.create(
            name='South Africa',
            iso_code='ZA'
        )
        self.country.full_clean()  # force model validation to happen

        self.category = Category.objects.create(name='Test Category')
        self.category.full_clean()  # force model validation to happen

        self.keyword = Keyword.objects.create(name='test')
        self.keyword.full_clean()  # force model validation to happen

        kwc = KeywordCategory.objects.create(
            keyword=self.keyword, category=self.category
        )
        kwc.full_clean()  # force model validation to happen

        self.organisation = Organisation.objects.create(
            name='Test Org',
            country=self.country,
            location=Point(18.505496, -33.891937, srid=4326)
        )
        self.organisation.full_clean()  # force model validation to happen

        oc = OrganisationCategory.objects.create(
            organisation=self.organisation, category=self.category
        )
        oc.full_clean()  # force model validation to happen

        ok = OrganisationKeyword.objects.create(
            organisation=self.organisation, keyword=self.keyword
        )
        ok.full_clean()  # force model validation to happen

        report = OrganisationIncorrectInformationReport.objects.create(
            organisation=self.organisation,
            contact_details=True
        )
        report.full_clean()  # force model validation to happen

    def test_query(self):
        reports = OrganisationIncorrectInformationReport.objects.filter(
            organisation=self.organisation
        )

        self.assertEqual(1, len(reports))
        self.assertTrue(reports[0].contact_details)
        self.assertIsNone(reports[0].address)
        self.assertIsNone(reports[0].trading_hours)
        self.assertIsNone(reports[0].other)
        self.assertEqual('', reports[0].other_detail)

        self.assertAlmostEqual(
            datetime.now(utc),
            reports[0].reported_at,
            delta=timedelta(seconds=10)
        )

    def test_update(self):
        report = OrganisationIncorrectInformationReport.objects.filter(
            organisation=self.organisation
        ).get()

        report.other = True
        report.other_detail = 'Test'
        report.save()

        report.refresh_from_db()

        self.assertTrue(report.other)
        self.assertEqual('Test', report.other_detail)


class OrganisationRatingTestCase(TestCase):
    def setUp(self):
        self.country = Country.objects.create(
            name='South Africa',
            iso_code='ZA'
        )
        self.country.full_clean()  # force model validation to happen

        self.category = Category.objects.create(name='Test Category')
        self.category.full_clean()  # force model validation to happen

        self.keyword = Keyword.objects.create(name='test')
        self.keyword.full_clean()  # force model validation to happen

        kwc = KeywordCategory.objects.create(
            keyword=self.keyword, category=self.category
        )
        kwc.full_clean()  # force model validation to happen

        self.organisation = Organisation.objects.create(
            name='Test Org',
            country=self.country,
            location=Point(18.505496, -33.891937, srid=4326)
        )
        self.organisation.full_clean()  # force model validation to happen

        oc = OrganisationCategory.objects.create(
            organisation=self.organisation, category=self.category
        )
        oc.full_clean()  # force model validation to happen

        ok = OrganisationKeyword.objects.create(
            organisation=self.organisation, keyword=self.keyword
        )
        ok.full_clean()  # force model validation to happen

        rating = OrganisationRating.objects.create(
            organisation=self.organisation,
            rating=OrganisationRating.AVERAGE
        )
        rating.full_clean()  # force model validation to happen

    def test_query(self):
        ratings = OrganisationRating.objects.filter(
            organisation=self.organisation
        )

        self.assertEqual(1, len(ratings))
        self.assertEqual(OrganisationRating.AVERAGE, ratings[0].rating)

        self.assertAlmostEqual(
            datetime.now(utc),
            ratings[0].rated_at,
            delta=timedelta(seconds=10)
        )

    def test_update(self):
        rating = OrganisationRating.objects.filter(
            organisation=self.organisation
        ).get()

        rating.rating = OrganisationRating.GOOD
        rating.save()

        rating.refresh_from_db()

        self.assertEqual(OrganisationRating.GOOD, rating.rating)
