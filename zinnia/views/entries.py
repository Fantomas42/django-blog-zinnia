"""Views for Zinnia entries"""
from django.views.generic.date_based import object_detail

from zinnia.views.decorators import protect_entry


entry_detail = protect_entry(object_detail)
