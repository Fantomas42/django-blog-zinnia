# -*- coding: utf-8 -*-
"""Import Media to Zinnia command module"""
import re, sys
from django.conf import settings
from django.utils.encoding import smart_str
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.core.management.base import LabelCommand
from optparse import make_option

from tagging.models import Tag

from zinnia import __version__
from zinnia.settings import PROTOCOL
from zinnia.models import Entry
from zinnia.models import Category
from BeautifulSoup import BeautifulSoup
import urllib 
from urlparse import urlparse, urljoin

class Command(LabelCommand):
    help = 'Copy images from other servers to the local server'
    label = 'media-type'
    args = ''   
    src_url = None
    image_paths = []
    
    option_list = LabelCommand.option_list + (

        make_option('--download_dir', dest='download_directory',
                    help=''), 
                    
        make_option('--src_url', dest='src_url',
                    help=''),
                    
        make_option('--domain', dest='domain',
                    help='Domain for relative paths, must include protocol e.g. http://www.marketcircle.com'),
                    
        )
        
    def __init__(self, **options):
        """Init the Command and add custom styles"""
        super(Command, self).__init__()
        self.style.TITLE = self.style.SQL_FIELD
        self.style.STEP = self.style.SQL_COLTYPE
        self.style.ITEM = self.style.HTTP_INFO      
     
    def write_out(self, message, verbosity_level=1):
        """Convenient method for outputing"""
        if self.verbosity and self.verbosity >= verbosity_level:
            sys.stdout.write(smart_str(message))
            sys.stdout.flush()
            
    def handle_label(self, media_type, **options):
        if not media_type == 'img':
            raise Exception('Unknown media tag %s' % (media_type,))
            
        self.verbosity = int(options.get('verbosity', 1))

        download_dir = options.get('download_directory') 
        self.src_url = options.get('src_url')
        if not download_dir:
            try:
                download_dir = settings.ZINNIA_CONTENT_MEDIA_DIR
            except:
                raise Exception('No suitable download directory found. Please define ZINNIA_CONTENT_MEDIA_DIR in your settings or pass a download dir as an argument')
        
        self.write_out(self.style.STEP('- Searching for media files in entries\n\n'))
        
        for entry in Entry.objects.all():
            
            soup = BeautifulSoup(entry.content)
            images = soup.findAll('img')
            for image in images:
                img_src = image['src']
                if ((self.src_url and img_src.startswith(self.src_url)) or not self.src_url) and not img_src.startswith(settings.ZINNIA_CONTENT_MEDIA_URL):
                    self.image_paths.append(image['src'])
                    
                        
        
    
        for path in self.image_paths:
            self.write_out(self.style.STEP("Downloading %s\n" % (path,)))
            url = urlparse(path)
            if len(url.netloc) ==0 :
                # Relative
                src_url = urljoin(options.get('domain'), url.path)   
            else:
                src_url = url.geturl()                
                #src_url = ''
                
            
            filename = ''
            try:
                fn_regex = re.compile('^.*/([^/]*\..*)$')
                filename = fn_regex.match(src_url).groups()[0]
                urllib.urlretrieve(src_url, '%s%s' % (download_dir, filename))
            except:
                self.write_out(self.style.TITLE('Error downloading: %s\n\n'%(src_url,)))   
                
            for entry in Entry.objects.filter(content__contains=path):
                new_url =settings.ZINNIA_CONTENT_MEDIA_URL+filename
                self.write_out(self.style.TITLE('Changeing urls from %s to %s in article %s:\n'%(path, new_url, entry.title)))
                content_string = entry.content 
                entry.content = content_string.replace(path,new_url)
                entry.save()
                