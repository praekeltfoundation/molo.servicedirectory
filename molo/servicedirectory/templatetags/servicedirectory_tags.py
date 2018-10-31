from django import template

register = template.Library()


@register.simple_tag
def url_params(request):
    params = ''
    attrs = [
        'radius',
        'place_id',
        'search',
        'category',
        'location',
        'place_latlng',
        'all_categories',
        'place_formatted_address',
        'keywords[]',
        'categories[]',
    ]
    for attr in attrs:
        if '[]' in attr:
            vals = request.GET.getlist(attr, [])
            for val in vals:
                params += '&{}={}'.format(attr, val)
        else:
            params += '&{}={}'.format(
                attr, request.GET.get(attr, '')
            )

    return params
