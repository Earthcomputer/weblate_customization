
import re
from django import forms
from weblate.addons.forms import JSONCustomizeForm

def validate_no_gap(value):
    parts = value.split(';')
    for part in parts:
        part = part.strip()
        if len(part) == 0:
            raise forms.ValidationError('Cannot have empty group regex')
        try:
            re.compile(part)
        except re.error:
            raise forms.ValidationError(f'Invalid regex "{part}"')

class JSONCustomizeFormExt(JSONCustomizeForm):
    groups = forms.CharField(
        label='Groups', 
        help_text='Semicolon-separated list of groups. Each group is specified by a regex which must match at the start of the translation key, and each member of the same group has the same values from the regex\'s capture groups', 
        required=True, 
        initial='.*', 
        validators=[validate_no_gap]
    )
    filter_empty = forms.BooleanField(
        label='Filter empty translations',
        help_text='Filters out untranslated strings (empty translations) from the output json file',
        required=False,
        initial=True
    )
