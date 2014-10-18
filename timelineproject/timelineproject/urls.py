from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from timeline.views import *

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'timelineproject.views.home', name='home'),
    # url(r'^timelineproject/', include('timelineproject.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # timeline app
    url(r'^api/timeline/$', timeline_view),
    url(r'^api/timeline/create/$', message_create_view),
    url(r'^api/timeline/(?P<num>\d+)/$', message_view),
    url(r'^api/timeline/(?P<num>\d+)/delete/$', message_delete_view),
    url(r'^api/timeline/(?P<num>\d+)/like/$', like_view),
    url(r'^api/timeline/find/$', find_view),


    url(r'^api/user/(?P<method>create)/$', user_view),
    url(r'^api/user/(?P<method>update)/$', user_view),
    url(r'^api/user/(?P<method>list)/$', user_view),
    url(r'^api/user/name/$', name_view),
    url(r'^api/user/checkpassword/$', checkpassword_view),
    url(r'^api/user/setpassword/$', setpassword_view),

    url(r'^api/profile/$', profile_view),
    url(r'^api/profile/(?P<username>\w+)/$', profile_view),
)
