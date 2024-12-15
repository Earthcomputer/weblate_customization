
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
    groups = forms.CharField(label='Groups', help_text='Semicolon-separated list of regexes of groups, within which to not add a gap', required=True, initial='.*', validators=[validate_no_gap])
