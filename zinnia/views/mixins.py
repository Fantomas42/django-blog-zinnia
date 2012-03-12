class EntryQuerysetTemplatesMixin(object):
    """Return a custom template name for views
    returning a queryset of Entry filtered by another model."""
    model_type = None
    model_name = None

    def get_model_type(self):
        return self.model_type

    def get_model_name(self):
        return self.model_name

    def get_template_names(self):
        model_type = self.get_model_type()
        model_name = self.get_model_name()

        templates = [
            'zinnia/%s/%s/entry_list.html' % (model_type, model_name),
            'zinnia/%s/%s_entry_list.html' % (model_type, model_name),
            'zinnia/%s/entry_list.html' % model_type,
            'zinnia/entry_list.html'
        ]

        if self.template_name is not None:
            templates.insert(0,self.template_name)

        if 'template_name' in self.kwargs:
            templates.insert(0,self.kwargs['template_name'])

        return templates