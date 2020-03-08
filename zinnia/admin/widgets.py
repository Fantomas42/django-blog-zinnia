"""Widgets for Zinnia admin"""
import json
from itertools import chain

from django.contrib.admin import widgets
from django.contrib.staticfiles.storage import staticfiles_storage
from django.forms import Media
from django.utils.encoding import force_str
from django.utils.safestring import mark_safe

from tagging.models import Tag

from zinnia.models import Entry


class MPTTFilteredSelectMultiple(widgets.FilteredSelectMultiple):
    """
    MPTT version of FilteredSelectMultiple.
    """
    option_inherits_attrs = True

    def __init__(self, verbose_name, is_stacked=False, attrs=None, choices=()):
        """
        Initializes the widget directly not stacked.
        """
        super(MPTTFilteredSelectMultiple, self).__init__(
            verbose_name, is_stacked, attrs, choices)

    def optgroups(self, name, value, attrs=None):
        """Return a list of optgroups for this widget."""
        groups = []
        has_selected = False
        if attrs is None:
            attrs = {}

        for index, (option_value, option_label, sort_fields) in enumerate(
                chain(self.choices)):

            # Set tree attributes
            attrs['data-tree-id'] = sort_fields[0]
            attrs['data-left-value'] = sort_fields[1]

            subgroup = []
            subindex = None
            choices = [(option_value, option_label)]
            groups.append((None, subgroup, index))

            for subvalue, sublabel in choices:
                selected = (
                    force_str(subvalue) in value and
                    (has_selected is False or self.allow_multiple_selected)
                )
                if selected is True and has_selected is False:
                    has_selected = True
                subgroup.append(self.create_option(
                    name, subvalue, sublabel, selected, index,
                    subindex=subindex, attrs=attrs,
                ))

        return groups

    @property
    def media(self):
        """
        MPTTFilteredSelectMultiple's Media.
        """
        js = ['admin/js/core.js',
              'zinnia/admin/mptt/js/mptt_m2m_selectbox.js',
              'admin/js/SelectFilter2.js']
        return Media(js=[staticfiles_storage.url(path) for path in js])


class TagAutoComplete(widgets.AdminTextInputWidget):
    """
    Tag widget with autocompletion based on select2.
    """

    def get_tags(self):
        """
        Returns the list of tags to auto-complete.
        """
        return [tag.name for tag in
                Tag.objects.usage_for_model(Entry)]

    def render(self, name, value, attrs=None, renderer=None):
        """
        Render the default widget and initialize select2.
        """
        output = [super(TagAutoComplete, self).render(name, value, attrs)]
        output.append('<script type="text/javascript">')
        output.append('(function($) {')
        output.append('  $(document).ready(function() {')
        output.append('    $("#id_%s").select2({' % name)
        output.append('       width: "element",')
        output.append('       maximumInputLength: 50,')
        output.append('       tokenSeparators: [",", " "],')
        output.append('       tags: %s' % json.dumps(self.get_tags()))
        output.append('     });')
        output.append('    });')
        output.append('}(django.jQuery));')
        output.append('</script>')
        return mark_safe('\n'.join(output))

    @property
    def media(self):
        """
        TagAutoComplete's Media.
        """
        def static(path):
            return staticfiles_storage.url(
                'zinnia/admin/select2/%s' % path)
        return Media(
            css={'all': (static('css/select2.css'),)},
            js=(static('js/select2.js'),)
        )


class MiniTextarea(widgets.AdminTextareaWidget):
    """
    Vertically shorter version of the admin textarea widget.
    """
    rows = 2

    def __init__(self, attrs=None):
        super(MiniTextarea, self).__init__(
            {'rows': self.rows})
