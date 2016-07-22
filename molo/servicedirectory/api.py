import logging

from django.conf import settings
from django.contrib.gis.geos import Point
from django.db.models.query import Prefetch
from go_http import HttpApiSender
from molo.servicedirectory.haystack_elasticsearch_raw_query.\
    custom_elasticsearch import ConfigurableSearchQuerySet
from molo.servicedirectory.models import Keyword, Category, Organisation, \
    OrganisationIncorrectInformationReport, OrganisationRating


def get_home_page_categories_with_keywords():
    """
    Retrieve keywords grouped by category for the home page
    """
    filtered_keyword_queryset = Keyword.objects.filter(
        show_on_home_page=True
    )

    home_page_categories_with_keywords = Category.objects.filter(
        show_on_home_page=True
    ).prefetch_related(
        Prefetch(
            'keyword_set',
            queryset=filtered_keyword_queryset,
            to_attr='filtered_keywords'
        )
    )

    # exclude categories that don't have any keywords associated
    home_page_categories_with_keywords = [
        category for category in home_page_categories_with_keywords
        if category.filtered_keywords
    ]

    return home_page_categories_with_keywords


def get_keywords(categories=None):
    """
    List keywords, optionally filtering by one or more categories
    """
    keywords = Keyword.objects.all()

    if categories:
        keywords = keywords.filter(categories__name__in=categories)

        if keywords:
            # although this endpoint accepts a list of categories we only
            # send a tracking event for the first one as generally only one
            # will be supplied (and we don't want to block the response
            # because of a large number of tracking calls)
            # TODO: enable tracking
            pass
            # send_ga_tracking_event(
            #     self.request._request.path, 'View', 'KeywordsInCategory',
            #     category_list[0]
            # )

    return keywords


def search(search_term=None, location=None, place_name=None):
    """
    Search for organisations by search term and/or location.
    If location coordinates are supplied then results are ordered ascending
    by distance.
    """
    point = None

    if search_term:
        search_term = search_term.strip()

    if location:
        latlng = location.strip()
        lat, lng = latlng.split(',')
        lat = float(lat)
        lng = float(lng)
        point = Point(lng, lat, srid=4326)

    if place_name:
        place_name = place_name.strip()

    # TODO: enable tracking
    # send_ga_tracking_event(
    #     request._request.path,
    #     'Search',
    #     search_term or '',
    #     place_name or ''
    # )

    sqs = ConfigurableSearchQuerySet().models(Organisation)

    if search_term:
        query = {
            "match": {
                "text": {
                    "query": search_term,
                    "fuzziness": "AUTO"
                }
            }
        }
        sqs = sqs.custom_query(query)

    if point:
        sqs = sqs.distance('location', point).order_by('distance')

    # fetch all result objects and limit to 20 results
    sqs = sqs.load_all()[:20]

    # TODO: consider http://django-haystack.readthedocs.io/en/latest/
    # searchqueryset_api.html#RelatedSearchQuerySet.load_all_queryset
    # to prefetch the org keywords - currently this happens in the template

    organisation_distance_tuples = []
    try:
        organisation_distance_tuples = [
            (
                result.object,
                result.distance if hasattr(result, 'distance') else None
            )
            for result in sqs
        ]
    except AttributeError:
        logging.warn('The ElasticSearch index is likely out of sync with'
                     ' the database. You should run the `rebuild_index`'
                     ' management command.')

    for organisation, distance in organisation_distance_tuples:
        if distance is not None:
            organisation.distance = '{0:.2f}km'.format(distance.km)

    if organisation_distance_tuples:
        services = zip(*organisation_distance_tuples)[0]
        return services

    return []


def get_organisation(organisation_id):
    """
    Retrieve organisation details
    """
    # TODO: prefetch categories - currently this happens in the template
    organisation = Organisation.objects.get(pk=organisation_id)

    # TODO: enable tracking
    # send_ga_tracking_event(
    #     request._request.path,
    #     'View',
    #     'Organisation',
    #     organisation.name
    # )

    return organisation


def report_organisation(organisation_id, contact_details, address,
                        trading_hours, other, other_detail):
    """
    Report incorrect information for an organisation
    """
    organisation = Organisation.objects.get(pk=organisation_id)

    report = OrganisationIncorrectInformationReport.objects.create(
        organisation=organisation,
        contact_details=contact_details,
        address=address,
        trading_hours=trading_hours,
        other=other,
        other_detail=other_detail
    )

    # TODO: enable tracking
    # send_ga_tracking_event(
    #     request._request.path,
    #     'Feedback',
    #     'OrganisationIncorrectInformationReport',
    #     organisation.name
    # )

    return report


def rate_organisation(organisation_id, rating):
    """
    Rate the quality of an organisation
    """
    organisation = Organisation.objects.get(pk=organisation_id)

    rating = OrganisationRating.objects.create(
        organisation=organisation,
        rating=rating
    )

    # TODO: enable tracking
    # send_ga_tracking_event(
    #     request._request.path,
    #     'Feedback',
    #     'OrganisationRating',
    #     organisation.name
    # )

    return rating


def sms_organisation(cell_number, organisation_url, your_name=None):
    """
    Send an SMS to a supplied cell_number with a supplied organisation_url
    """
    analytics_label = ''
    result = False

    try:
        sender = HttpApiSender(
            settings.VUMI_GO_ACCOUNT_KEY,
            settings.VUMI_GO_CONVERSATION_KEY,
            settings.VUMI_GO_API_TOKEN,
            api_url=settings.VUMI_GO_API_URL
        )

        if your_name:
            message = '{0} has sent you a link: {1}'.format(
                your_name,
                organisation_url
            )
            analytics_label = 'send'
        else:
            message = 'You have sent yourself a link: {0}'.format(
                organisation_url
            )
            analytics_label = 'save'

        sender.send_text(cell_number, message)

        result = True
    except:
        logging.error("Failed to send SMS", exc_info=True)

    # TODO: enable tracking
    # send_ga_tracking_event(
    #     request._request.path,
    #     'SMS',
    #     request_serializer.validated_data['organisation_url'],
    #     analytics_label
    # )

    return result
