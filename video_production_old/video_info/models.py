#-*- coding:utf8 -*-
#created by Recker on 2014/07/06

from django.db import models

class VideoInfo(models.Model):
    '''
    视频信息
    '''
    #taskid = models.CharField(u"任务id", max_length=64, null=True, db_index=True)
    #filepath = models.URLField(u"片源地址", max_length=255, null=True)
    #callback = models.URLField(u"回调地址", max_length=255, null=True)
    createdtime = models.DateTimeField(u"创建时间", auto_now=False, auto_now_add=True, db_index=True)
    mediainfo = models.TextField(u"视频扫描结果", null=True)
    status = models.IntegerField(u"任务状态", max_length=1, null=True, db_index=True)
    videofile = models.FileField(u"浏览文件", upload_to="%Y%m%d/")
    videoname = models.CharField(u"视频名称", max_length=128, null=True)
    videotype = models.IntegerField(u"视频类型", max_length=1, null=True)


    class Meta:
        db_table = "video_info"
        verbose_name = u"片源"
        verbose_name_plural = u"片源"


    def logUtil(self):
        return '<a href="baidu.com">打开</a>'

    logUtil.short_description = u"进度日志"
    logUtil.allow_tags = True

    def createTask(self):
        return '<a href="/admin/video_task/videotask/add/?filepath=>创建</a>'

    createTask.allow_tags = True
    createTask.short_description = u"转码任务"

    def strTime(self):
        return self.createdtime.strftime("%Y-%m-%d %H:%M:%S")
