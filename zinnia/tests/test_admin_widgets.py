"""Test cases for Zinnia's admin widgets"""
from django.test import TestCase
from django.test.utils import override_settings

from zinnia.admin.widgets import MPTTFilteredSelectMultiple
from zinnia.admin.widgets import MiniTextarea
from zinnia.admin.widgets import TagAutoComplete
from zinnia.models.entry import Entry
from zinnia.signals import disconnect_entry_signals


class MPTTFilteredSelectMultipleTestCase(TestCase):
    maxDiff = None

    def test_optgroups(self):
        choices = [
            (1, 'Category 1', (1, 1)),
            (2, '|-- Category 2', (1, 2))
        ]

        widget = MPTTFilteredSelectMultiple(
            'test', False, choices=choices)

        optgroups = widget.optgroups('toto', '1')
        self.assertEqual(
            optgroups,
            [
                (
                    None, [
                        {
                            'index': '0',
                            'name': 'toto',
                            'template_name':
                            'django/forms/widgets/select_option.html',
                            'type': 'select',
                            'selected': True,
                            'attrs': {
                                'selected': True,
                                'data-tree-id': 1,
                                'data-left-value': 1
                            },
                            'value': 1,
                            'label': 'Category 1',
                            'wrap_label': True
                        }
                    ], 0
                ), (
                    None, [
                        {
                            'index': '1',
                            'name': 'toto',
                            'template_name':
                            'django/forms/widgets/select_option.html',
                            'type': 'select',
                            'selected': False,
                            'attrs': {
                                'data-tree-id': 1,
                                'data-left-value': 2
                            },
                            'value': 2,
                            'label': '|-- Category 2',
                            'wrap_label': True
                        }
                    ], 1
                )
            ]
        )

        optgroups = widget.optgroups('toto', ['2'])
        self.assertEqual(
            optgroups,
            [
                (
                    None, [
                        {
                            'index': '0',
                            'name': 'toto',
                            'template_name':
                            'django/forms/widgets/select_option.html',
                            'type': 'select',
                            'selected': False,
                            'attrs': {
                                'data-tree-id': 1,
                                'data-left-value': 1
                            },
                            'value': 1,
                            'label': 'Category 1',
                            'wrap_label': True
                        }
                    ], 0
                ), (
                    None, [
                        {
                            'index': '1',
                            'name': 'toto',
                            'template_name':
                            'django/forms/widgets/select_option.html',
                            'type': 'select',
                            'selected': True,
                            'attrs': {
                                'selected': True,
                                'data-tree-id': 1,
                                'data-left-value': 2
                            },
                            'value': 2,
                            'label': '|-- Category 2',
                            'wrap_label': True
                        }
                    ], 1
                )
            ]
        )

        optgroups = widget.optgroups('toto', '1', {'attribute': 'value'})
        self.assertEqual(
            optgroups,
            [
                (
                    None, [
                        {
                            'index': '0',
                            'name': 'toto',
                            'template_name':
                            'django/forms/widgets/select_option.html',
                            'type': 'select',
                            'selected': True,
                            'attrs': {
                                'selected': True,
                                'attribute': 'value',
                                'data-tree-id': 1,
                                'data-left-value': 1
                            },
                            'value': 1,
                            'label': 'Category 1',
                            'wrap_label': True
                        }
                    ], 0
                ), (
                    None, [
                        {
                            'index': '1',
                            'name': 'toto',
                            'template_name':
                            'django/forms/widgets/select_option.html',
                            'type': 'select',
                            'selected': False,
                            'attrs': {
                                'attribute': 'value',
                                'data-tree-id': 1,
                                'data-left-value': 2
                            },
                            'value': 2,
                            'label': '|-- Category 2',
                            'wrap_label': True
                        }
                    ], 1
                )
            ]
        )

    @override_settings(STATIC_URL='/s/')
    def test_media(self):
        medias = MPTTFilteredSelectMultiple('test', False).media
        self.assertEqual(medias._css, {})
        self.assertEqual(medias._js, [
            '/s/admin/js/core.js',
            '/s/zinnia/admin/mptt/js/mptt_m2m_selectbox.js',
            '/s/admin/js/SelectFilter2.js'])


class TagAutoCompleteTestCase(TestCase):

    def setUp(self):
        disconnect_entry_signals()

    def test_get_tags(self):
        widget = TagAutoComplete()
        self.assertEqual(
            widget.get_tags(),
            [])

        params = {'title': 'My entry',
                  'tags': 'zinnia, test',
                  'slug': 'my-entry'}
        Entry.objects.create(**params)
        self.assertEqual(
            widget.get_tags(),
            ['test', 'zinnia'])

    def test_render(self):
        widget = TagAutoComplete()
        params = {'title': 'My entry',
                  'tags': 'zinnia, test',
                  'slug': 'my-entry'}
        Entry.objects.create(**params)
        self.assertHTMLEqual(
            widget.render('tag', 'test,'),
            '<input class="vTextField" name="tag" type="text" value="test," />'
            '\n<script type="text/javascript">\n(function($) {'
            '\n  $(document).ready(function() {'
            '\n    $("#id_tag").select2({'
            '\n       width: "element",'
            '\n       maximumInputLength: 50,'
            '\n       tokenSeparators: [",", " "],'
            '\n       tags: ["test", "zinnia"]'
            '\n     });\n    });'
            '\n}(django.jQuery));\n</script>')

    def test_render_tag_with_apostrophe(self):
        widget = TagAutoComplete()
        params = {'title': 'My entry',
                  'tags': "zinnia, test, apos'trophe",
                  'slug': 'my-entry'}
        Entry.objects.create(**params)
        self.maxDiff = None
        self.assertHTMLEqual(
            widget.render('tag', 'test,'),
            '<input class="vTextField" name="tag" type="text" value="test," />'
            '\n<script type="text/javascript">\n(function($) {'
            '\n  $(document).ready(function() {'
            '\n    $("#id_tag").select2({'
            '\n       width: "element",'
            '\n       maximumInputLength: 50,'
            '\n       tokenSeparators: [",", " "],'
            '\n       tags: ["apos\'trophe", "test", "zinnia"]'
            '\n     });\n    });'
            '\n}(django.jQuery));\n</script>')

    @override_settings(STATIC_URL='/s/')
    def test_media(self):
        medias = TagAutoComplete().media
        self.assertEqual(
            medias._css,
            {'all': ['/s/zinnia/admin/select2/css/select2.css']}
        )
        self.assertEqual(
            medias._js,
            ['/s/zinnia/admin/select2/js/select2.js']
        )


class MiniTextareaTestCase(TestCase):

    def test_render(self):
        widget = MiniTextarea()
        self.assertHTMLEqual(
            widget.render('field', 'value'),
            '<textarea class="vLargeTextField" '
            'cols="40" name="field" rows="2">'
            '\r\nvalue</textarea>')
