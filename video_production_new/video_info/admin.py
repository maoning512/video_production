from django import forms 
from django.contrib import admin
from video_info.models import VideoInfo

class VideoInfoForm(forms.ModelForm):

    taskid = forms.CharField()

    class Meta:
        forms.model = VideoInfo

class VideoInfoAdmin(admin.ModelAdmin):
    
    list_display = ('taskid','status','filepath','getIp','createdtime','mediainfo','logUtil','getResult','rebootTask')
    search_fields = ('taskid',)
    list_filter = ('status',)
    form = VideoInfoForm
    fields = ('taskid','filepath','callback')


admin.site.register(VideoInfo, VideoInfoAdmin)
