from django import forms
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from service_directory.api.models import Organisation


class OrganisationModelForm(forms.ModelForm):
    location_coords = forms.CharField(
        required=False,
        label='Location coordinates',
        help_text='Enter coordinates as latitude,longitude.'
        ' Note that entering coordinates here overrides any location set via'
        ' the map.'
    )

    class Meta:
        model = Organisation
        fields = ('name', 'about', 'address', 'telephone',
                  'emergency_telephone', 'email', 'web', 'verified_as',
                  'age_range_min', 'age_range_max', 'opening_hours',
                  'country', 'location', 'location_coords', 'categories',
                  'keywords', 'facility_code')

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=None,
                 empty_permitted=False, instance=None):
        if instance:
            initial = initial or {}
            initial['location_coords'] = instance.location_coords

        super(OrganisationModelForm, self).__init__(data, files, auto_id,
                                                    prefix, initial,
                                                    error_class, label_suffix,
                                                    empty_permitted, instance)

    def clean_location_coords(self):
        location_coords = self.cleaned_data.get('location_coords')
        if location_coords:
            try:
                lat, lng = location_coords.split(',')
                lat = float(lat)
                lng = float(lng)
                point = Point(lng, lat, srid=4326)
            except ValueError:
                raise ValidationError(
                    "Invalid coordinates. Coordinates must be comma-separated"
                    " latitude,longitude decimals, eg: -33.921124,18.417313"
                )

            return point
        return location_coords

    def clean(self):
        super(OrganisationModelForm, self).clean()

        location_coords = self.cleaned_data.get('location_coords')

        # only override location if location_coords is a valid Point and does
        # not match the current location
        if isinstance(location_coords, Point) and \
                location_coords != self.instance.location:

            self.cleaned_data['location'] = self.cleaned_data.get(
                'location_coords'
            )

            # if location_coords is a valid Point then we can ignore errors
            # about the location field (eg: 'Delete all Features' is used to
            # remove the map marker but valid coordinates are entered into
            # the location_coords field)
            if self.has_error('location'):
                del self.errors['location']
