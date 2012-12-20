"""Widgets for Zinnia admin"""
from itertools import chain

from django import forms
from django.conf import settings
from django.contrib.admin import widgets
from django.utils.html import escape
from django.utils.html import conditional_escape
from django.utils.encoding import smart_unicode
from django.utils.encoding import force_unicode


class TreeNodeChoiceField(forms.ModelChoiceField):
    """Duplicating the TreeNodeChoiceField bundled in django-mptt
    to avoid conflict with the TreeNodeChoiceField bundled in django-cms..."""
    def __init__(self, level_indicator=u'|--', *args, **kwargs):
        self.level_indicator = level_indicator
        if kwargs.get('required', True) and not 'empty_label' in kwargs:
            kwargs['empty_label'] = None
        super(TreeNodeChoiceField, self).__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        """Creates labels which represent the tree level of each node
        when generating option labels."""
        return u'%s %s' % (self.level_indicator * getattr(
            obj, obj._mptt_meta.level_attr), smart_unicode(obj))


class MPTTModelChoiceIterator(forms.models.ModelChoiceIterator):
    """MPTT version of ModelChoiceIterator"""
    def choice(self, obj):
        """Overriding choice method"""
        tree_id = getattr(obj, self.queryset.model._mptt_meta.tree_id_attr, 0)
        left = getattr(obj, self.queryset.model._mptt_meta.left_attr, 0)
        return super(MPTTModelChoiceIterator,
                     self).choice(obj) + ((tree_id, left),)


class MPTTModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    """MPTT version of ModelMultipleChoiceField"""
    def __init__(self, level_indicator=u'|--', *args, **kwargs):
        self.level_indicator = level_indicator
        super(MPTTModelMultipleChoiceField, self).__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        """Creates labels which represent the tree level of each node
        when generating option labels."""
        return u'%s %s' % (self.level_indicator * getattr(
            obj, obj._mptt_meta.level_attr), smart_unicode(obj))

    def _get_choices(self):
        """Overriding _get_choices"""
        if hasattr(self, '_choices'):
            return self._choices
        return MPTTModelChoiceIterator(self)

    choices = property(_get_choices, forms.ChoiceField._set_choices)


class MPTTFilteredSelectMultiple(widgets.FilteredSelectMultiple):
    """MPTT version of FilteredSelectMultiple"""
    def __init__(self, verbose_name, is_stacked, attrs=None, choices=()):
        super(MPTTFilteredSelectMultiple, self).__init__(
            verbose_name, is_stacked, attrs, choices)

    def render_options(self, choices, selected_choices):
        """
        This is copy'n'pasted from django.forms.widgets Select(Widget)
        change to the for loop and render_option so they will unpack
        and use our extra tuple of mptt sort fields (if you pass in
        some default choices for this field, make sure they have the
        extra tuple too!)
        """
        def render_option(option_value, option_label, sort_fields):
            """Inner scope render_option"""
            option_value = force_unicode(option_value)
            selected_html = (option_value in selected_choices) and \
                u' selected="selected"' or ''
            return u'<option value="%s" data-tree-id="%s" ' \
                   'data-left-value="%s"%s>%s</option>' % (
                       escape(option_value),
                       sort_fields[0], sort_fields[1], selected_html,
                       conditional_escape(force_unicode(option_label)))
        # Normalize to strings.
        selected_choices = set([force_unicode(v) for v in selected_choices])
        output = []
        for option_value, option_label, sort_fields in chain(
                self.choices, choices):
            if isinstance(option_label, (list, tuple)):
                output.append(u'<optgroup label="%s">' % escape(
                    force_unicode(option_value)))
                for option in option_label:
                    output.append(render_option(*option))
                output.append(u'</optgroup>')
            else:
                output.append(render_option(option_value, option_label,
                                            sort_fields))
        return u'\n'.join(output)

    class Media:
        """MPTTFilteredSelectMultiple's Media"""
        js = (settings.STATIC_URL + 'admin/js/core.js',
              settings.STATIC_URL + 'zinnia/js/mptt_m2m_selectbox.js',
              settings.STATIC_URL + 'admin/js/SelectFilter2.js',)
