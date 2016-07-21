import logging

from django.contrib.gis.geos import Point
from django.db.models.query import Prefetch
from molo.servicedirectory.haystack_elasticsearch_raw_query.\
    custom_elasticsearch import ConfigurableSearchQuerySet
from molo.servicedirectory.models import Keyword, Category, Organisation


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
