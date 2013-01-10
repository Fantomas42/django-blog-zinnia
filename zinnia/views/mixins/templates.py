"""Template mixins for Zinnia views"""
from django.utils import timezone
from django.core.exceptions import ImproperlyConfigured
from django.views.generic.base import TemplateResponseMixin


class EntryQuerysetTemplateResponseMixin(TemplateResponseMixin):
    """Return a custom template name for views returning
    a queryset of Entry filtered by another model."""
    model_type = None
    model_name = None

    def get_model_type(self):
        """Return the model type for templates"""
        if self.model_type is None:
            raise ImproperlyConfigured(
                u"%s requires either a definition of "
                "'model_type' or an implementation of 'get_model_type()'" %
                self.__class__.__name__)
        return self.model_type

    def get_model_name(self):
        """Return the model name for templates"""
        if self.model_name is None:
            raise ImproperlyConfigured(
                u"%s requires either a definition of "
                "'model_name' or an implementation of 'get_model_name()'" %
                self.__class__.__name__)
        return self.model_name

    def get_template_names(self):
        """Return a list of template names to be used for the view"""
        model_type = self.get_model_type()
        model_name = self.get_model_name()

        templates = [
            'zinnia/%s/%s/entry_list.html' % (model_type, model_name),
            'zinnia/%s/%s_entry_list.html' % (model_type, model_name),
            'zinnia/%s/entry_list.html' % model_type,
            'zinnia/entry_list.html']

        if self.template_name is not None:
            templates.insert(0, self.template_name)

        return templates


class EntryQuerysetArchiveTemplateResponseMixin(TemplateResponseMixin):
    """Return a custom template name for the archive views based
    on the type of the archives and the value of the date."""
    template_name_suffix = '_archive'

    def get_archive_part_value(self, part):
        """Method for accessing to the value of
        self.get_year(), self.get_month(), etc methods
        if they exists.
        """
        try:
            return getattr(self, 'get_%s' % part)()
        except AttributeError:
            return None

    def get_default_base_template_names(self):
        """Return a list of default base templates used
        to build the full list of templates."""
        return ['entry%s.html' % self.template_name_suffix]

    def get_template_names(self):
        """Return a list of template names to be used for the view"""
        year = self.get_archive_part_value('year')
        week = self.get_archive_part_value('week')
        month = self.get_archive_part_value('month')
        day = self.get_archive_part_value('day')

        templates = []
        path = 'zinnia/archives'
        template_names = self.get_default_base_template_names()
        for template_name in template_names:
            templates.extend([template_name,
                              'zinnia/%s' % template_name,
                              '%s/%s' % (path, template_name)])
        if year:
            for template_name in template_names:
                templates.append(
                    '%s/%s/%s' % (path, year, template_name))
        if week:
            for template_name in template_names:
                templates.extend([
                    '%s/week/%s/%s' % (path, week, template_name),
                    '%s/%s/week/%s/%s' % (path, year, week, template_name)])
        if month:
            for template_name in template_names:
                templates.extend([
                    '%s/month/%s/%s' % (path, month, template_name),
                    '%s/%s/month/%s/%s' % (path, year, month, template_name)])
        if day:
            for template_name in template_names:
                templates.extend([
                    '%s/day/%s/%s' % (path, day, template_name),
                    '%s/%s/day/%s/%s' % (path, year, day, template_name),
                    '%s/month/%s/day/%s/%s' % (path, month, day,
                                               template_name),
                    '%s/%s/%s/%s/%s' % (path, year, month, day,
                                        template_name)])

        if self.template_name is not None:
            templates.append(self.template_name)

        templates.reverse()
        return templates


class EntryArchiveTemplateResponseMixin(
        EntryQuerysetArchiveTemplateResponseMixin):
    """Same as EntryQuerysetArchivetemplateResponseMixin
    but use the template defined in the Entry instance
    as the base template name."""

    def get_default_base_template_names(self):
        """Return the Entry.template value"""
        return [self.object.detail_template,
                '%s.html' % self.object.slug,
                '%s_%s' % (self.object.slug, self.object.detail_template)]


class EntryQuerysetArchiveTodayTemplateResponseMixin(
        EntryQuerysetArchiveTemplateResponseMixin):
    """Same as EntryQuerysetArchivetemplateResponseMixin
    but use the current date of the day when getting
    archive part values"""
    today = None

    def get_archive_part_value(self, part):
        """Return archive part for today"""
        parts_dict = {'year': '%Y',
                      'month': self.month_format,
                      'week': self.week_format,
                      'day': '%d'}
        if self.today is None:
            self.today = timezone.localtime(timezone.now()).date()
        return self.today.strftime(parts_dict[part])
