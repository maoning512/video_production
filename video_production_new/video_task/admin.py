# -*- coding:utf8 -*-

from django.contrib import admin
from django import forms
from video_task.models import VideoTask


class VideoTaskForm(forms.ModelForm):

    taskid = forms.CharField()
    versionid = forms.ChoiceField(choices=[(1, '标清'), (2, '高清')])
    priority = forms.ChoiceField(choices=[(x,x) for x in range(10)])
    platform = forms.ChoiceField(choices=[(1, '主站'), (2, '移动端'), (4, 'ios'), (7, '全部')])
    srtfile = forms.CharField(required=False)
    logofile = forms.CharField(required=False)
    logopos = forms.CharField(required=False)
    status = forms.IntegerField(required=False)

    class Meta:
        forms.model = VideoTask


class VideoTaskAdmin(admin.ModelAdmin):
    
    list_display = ('taskid','status','filepath','getIp','createdtime','convlog','enclog','getResult')
    search_fields = ('taskid',)
    list_filter = ('status',)
    form = VideoTaskForm
    fields = ('taskid','filepath','platform','priority','callback','srtfile','logofile','versionid','crop','aid','logopos','ifps','status')

admin.site.register(VideoTask, VideoTaskAdmin)
