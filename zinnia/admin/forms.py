"""Forms for Zinnia admin"""
from django import forms
from django.db.models import ManyToOneRel
from django.db.models import ManyToManyRel
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper

from mptt.forms import TreeNodeChoiceField

from zinnia.models.entry import Entry
from zinnia.models.category import Category
from zinnia.admin.widgets import MiniTextarea
from zinnia.admin.widgets import TagAutoComplete
from zinnia.admin.widgets import MPTTFilteredSelectMultiple
from zinnia.admin.fields import MPTTModelMultipleChoiceField


class CategoryAdminForm(forms.ModelForm):
    """
    Form for Category's Admin.
    """
    parent = TreeNodeChoiceField(
        label=_('Parent category'),
        level_indicator='|--', required=False,
        empty_label=_('No parent category'),
        queryset=Category.objects.all())

    def __init__(self, *args, **kwargs):
        super(CategoryAdminForm, self).__init__(*args, **kwargs)
        rel = ManyToOneRel(Category._meta.get_field('tree_id'),
                           Category, 'id')
        self.fields['parent'].widget = RelatedFieldWidgetWrapper(
            self.fields['parent'].widget, rel, self.admin_site)

    def clean_parent(self):
        """
        Check if category parent is not selfish.
        """
        data = self.cleaned_data['parent']
        if data == self.instance:
            raise forms.ValidationError(
                _('A category cannot be parent of itself.'),
                code='self_parenting')
        return data

    class Meta:
        """
        CategoryAdminForm's Meta.
        """
        model = Category
        fields = forms.ALL_FIELDS


class EntryAdminForm(forms.ModelForm):
    """
    Form for Entry's Admin.
    """
    categories = MPTTModelMultipleChoiceField(
        label=_('Categories'), required=False,
        queryset=Category.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('categories'), False,
                                          attrs={'rows': '10'}))

    def __init__(self, *args, **kwargs):
        super(EntryAdminForm, self).__init__(*args, **kwargs)
        rel = ManyToManyRel(Category, 'id')
        self.fields['categories'].widget = RelatedFieldWidgetWrapper(
            self.fields['categories'].widget, rel, self.admin_site)

    class Meta:
        """
        EntryAdminForm's Meta.
        """
        model = Entry
        fields = forms.ALL_FIELDS
        widgets = {
            'tags': TagAutoComplete,
            'subtitle': MiniTextarea,
            'caption': MiniTextarea,
            'excerpt': MiniTextarea,
        }
