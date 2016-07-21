from django.db.models.query import Prefetch
from molo.servicedirectory.models import Keyword, Category


def get_home_page_categories_with_keywords():
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
