"""Forms for Zinnia admin"""
from django import forms
from django.utils.translation import ugettext, ugettext_lazy as _

from mptt.forms import TreeNodeChoiceField

from zinnia.models import Entry
from zinnia.models import Category
from zinnia.admin.widgets import MPTTFilteredSelectMultiple
from zinnia.admin.widgets import MPTTModelMultipleChoiceField


class CategoryAdminForm(forms.ModelForm):
    parent = TreeNodeChoiceField(label=_('parent category').capitalize(),
                                 required=False,
                                 empty_label=_('No parent category'),
                                 queryset=Category.tree.all(),
                                 level_indicator=u'|--')

    def clean_parent(self):
        data = self.cleaned_data['parent']
        if data == self.instance:
            raise forms.ValidationError(_('A category cannot be parent of itself.'))
        return data
    
    class Meta:
        model = Category

class EntryAdminForm(forms.ModelForm):
    categories = MPTTModelMultipleChoiceField(
        Category.objects.all(),
        widget = MPTTFilteredSelectMultiple(_('categories'), False,
                                            attrs={'rows': '10'}))
    
    class Meta:
        model = Entry

                    
