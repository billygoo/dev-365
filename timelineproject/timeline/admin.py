__author__ = 'billy-dev'

from django.contrib import admin
from timeline.models import *

admin.site.register(Message)
admin.site.register(Like)
admin.site.register(UserProfile)
