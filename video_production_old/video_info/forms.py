# -*- coding:utf8 -*-
# author: Recker Mao

from django import forms

class VideoInfoForm(forms.Form):

    videoname = forms.CharField()
    videotype = forms.IntegerField()
    videofile = forms.FileField()
