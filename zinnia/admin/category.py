"""CategoryAdmin for Zinnia"""
from django.contrib import admin
from django.core.urlresolvers import NoReverseMatch
from django.utils.translation import ugettext_lazy as _

from zinnia.admin.forms import CategoryAdminForm


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
