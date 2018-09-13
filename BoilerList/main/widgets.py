from django.forms.widgets import SelectMultiple, CheckboxSelectMultiple
from django.utils.html import format_html, html_safe
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.forms.utils import flatatt

from main.models import *

# widget for displaying checkboxes for categories by group
class CategorySelect(CheckboxSelectMultiple):
    input_type = None  # Subclasses must define this.

    def render(self, name, value, attrs=None):

        if value:
            selected_categories = Category.objects.filter(id__in = value)
        else:
            selected_categories = []

        context = {
            'category_groups':CategoryGroup.objects.all(),
            'selected_categories':selected_categories
            }
        return mark_safe(render_to_string('widgets/category_select.html', context))
