from django import forms 
from django.contrib import admin
from video_info.models import VideoInfo

class VideoInfoForm(forms.ModelForm):

    taskid = forms.CharField()

    class Meta:
        forms.model = VideoInfo

class VideoInfoAdmin(admin.ModelAdmin):
    
    list_display = ('status','videofile','mediainfo','logUtil','createTask')
    form = VideoInfoForm
    fields = ('filepath', 'videofile')


admin.site.register(VideoInfo, VideoInfoAdmin)
