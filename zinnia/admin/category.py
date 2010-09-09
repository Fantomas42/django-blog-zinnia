"""CategoryAdmin for Zinnia"""
from django import forms
from django.contrib import admin
from django.core.urlresolvers import NoReverseMatch
from django.utils.translation import ugettext, ugettext_lazy as _

from mptt.forms import TreeNodeChoiceField

from zinnia.models import Category


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

class CategoryAdmin(admin.ModelAdmin):
    form = CategoryAdminForm
    fields = ('title', 'parent', 'description', 'slug')
    list_display = ('title', 'slug', 'get_tree_path', 'description')
    prepopulated_fields = {'slug': ('title', )}
    search_fields = ('title', 'description')
    list_filter = ('parent',)

    def get_tree_path(self, category):
        try:
            return '<a href="%s" target="blank">/%s/</a>' % \
                   (category.get_absolute_url(), category.tree_path)
        except NoReverseMatch:
            return '/%s/' % category.tree_path
    get_tree_path.allow_tags = True
    get_tree_path.short_description = _('tree path')
