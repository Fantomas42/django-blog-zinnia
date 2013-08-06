"""Fields for Zinnia admin"""
from __future__ import unicode_literals

from django import forms
from django.utils.encoding import smart_unicode


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
    def __init__(self, level_indicator='|--', *args, **kwargs):
        self.level_indicator = level_indicator
        super(MPTTModelMultipleChoiceField, self).__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        """Creates labels which represent the tree level of each node
        when generating option labels."""
        return '%s %s' % (self.level_indicator * getattr(
            obj, obj._mptt_meta.level_attr), smart_unicode(obj))

    def _get_choices(self):
        """Overriding _get_choices"""
        if hasattr(self, '_choices'):
            return self._choices
        return MPTTModelChoiceIterator(self)

    choices = property(_get_choices, forms.ChoiceField._set_choices)
