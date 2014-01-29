"""Widgets for Zinnia admin"""
from itertools import chain

from django.utils.html import escape
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text
from django.contrib.admin import widgets
from django.contrib.staticfiles.storage import staticfiles_storage


class MPTTFilteredSelectMultiple(widgets.FilteredSelectMultiple):
    """
    MPTT version of FilteredSelectMultiple.
    """

    def render_option(self, selected_choices, option_value,
                      option_label, sort_fields):
        """
        Overrides the render_option method to handle
        the sort_fields argument.
        """
        option_value = force_text(option_value)
        option_label = escape(force_text(option_label)).encode('utf-8')

        if option_value in selected_choices:
            selected_html = mark_safe(' selected="selected"')
        else:
            selected_html = ''
        return format_html(
            '<option value="{1}"{2} data-tree-id="{3}"'
            ' data-left-value="{4}">{0}</option>',
            option_label, option_value, selected_html,
            sort_fields[0], sort_fields[1]).decode('utf-8')

    def render_options(self, choices, selected_choices):
        """
        This is copy'n'pasted from django.forms.widgets Select(Widget)
        change to the for loop and render_option so they will unpack
        and use our extra tuple of mptt sort fields (if you pass in
        some default choices for this field, make sure they have the
        extra tuple too!).
        """
        selected_choices = set(force_text(v) for v in selected_choices)
        output = []
        for option_value, option_label, sort_fields in chain(
                self.choices, choices):
            output.append(self.render_option(
                selected_choices, option_value,
                option_label, sort_fields))
        return '\n'.join(output)

    class Media:
        """
        MPTTFilteredSelectMultiple's Media.
        """
        js = (staticfiles_storage.url('admin/js/core.js'),
              staticfiles_storage.url('zinnia/js/mptt_m2m_selectbox.js'),
              staticfiles_storage.url('admin/js/SelectFilter2.js'))
