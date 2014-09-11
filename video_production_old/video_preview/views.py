# -*- coding:utf8 -*-

from django.shortcuts import render
from django.http import HttpResponse

def preview(request):
	params = request.REQUEST
	video_uri = params.get("video_uri","")
	html = '''<html><body><video src="%s" controls="controls"></video><p>%s</p></body></html>'''%(video_uri, video_uri)
	return HttpResponse(html)
