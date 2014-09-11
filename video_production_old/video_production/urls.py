from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'video_production.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^videoInfoCreate/','video_info.views.home'),
    url(r'^videoInfoSearch/','video_info.views.search'),
    url(r'^videoTaskCreate/','video_task.views.home'),
    url(r'^videoTaskSearch/','video_task.views.search'),
    url(r'^videoPreview/','video_preview.views.preview'),
    url(r'^videoInfoList/','video_info.views.list'),
    url(r'^videoCutImageCreate/','video_pic.views.home'),
    url(r'^videoCutImageSearch/','video_pic.views.search'),
)
