# -*- coding:utf8 -*-

from django.contrib import admin
from django import forms
from video_task.models import VideoTask


class VideoTaskForm(forms.ModelForm):

    taskid = forms.CharField()
    versionid = forms.ChoiceField(choices=[(1, '标清'), (2, '高清')])
    priority = forms.ChoiceField(choices=[(x,x) for x in range(10)])
    platform = forms.ChoiceField(choices=[(1, '主站'), (2, '移动端'), (4, 'ios'), (7, '全部')])

    class Meta:
        forms.model = VideoTask


class VideoTaskAdmin(admin.ModelAdmin):
    
    list_display = ('taskid','status','filepath','logUtil')
    form = VideoTaskForm
    fields = ('taskid','filepath','platform','priority','callback','srtfile','logofile','versionid','crop','aid','logopos','ifps')

admin.site.register(VideoTask, VideoTaskAdmin)
