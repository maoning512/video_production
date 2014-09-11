#-*- coding:utf8 -*-
#created by Recker on 2014/07/06

from django.db import models

class VideoInfo(models.Model):
    '''
    视频信息
    '''
    taskid = models.CharField(u"任务id", max_length=64, null=True, db_index=True)
    filepath = models.CharField(u"片源地址", max_length=255, null=True)
    callback = models.URLField(u"回调地址", max_length=255, null=True)
    createdtime = models.DateTimeField(u"创建时间", auto_now=False, auto_now_add=True, db_index=True)
    mediainfo = models.TextField(u"视频扫描结果", null=True)
    status = models.IntegerField(u"任务状态", max_length=1, null=True, db_index=True)
    ip = models.IPAddressField(null=True)

    class Meta:
        db_table = "video_info"
        verbose_name = u"片源"
        verbose_name_plural = u"片源"

    def getIp(self):
        if self.status and not self.ip:
            ip = "42.62.69.10"
        else:
            ip = self.ip
        return ip

    getIp.short_description = "转码机地址"


    def logUtil(self):
        ip = "42.62.69.10" if not self.ip else self.ip
        return '<a href="http://%s:8000/%s_1.log" target="_blank">open</a>'%(ip, self.taskid)

    logUtil.short_description = "进度日志"
    logUtil.allow_tags = True

    def getResult(self):
        return '<a href="/videoInfoSearch/?taskId=%s" target="_blank">open</a>'%self.taskid

    getResult.short_description = "获取视频信息"
    getResult.allow_tags = True

    def createTask(self):
        return '<a href="/admin/video_task/videotask/add/?filepath=" target="_blank">open</a>'

    createTask.allow_tags = True
    createTask.short_description = "转码任务"

    def rebootTask(self):
        result = '<a href="/videoInfoReboot/?taskId=%s" target="_blank">reboot</a>'%self.taskid if (self.status > 0 and self.status != 100) else "wait"
        return result

    rebootTask.allow_tags = True
    rebootTask.short_description = "操作"
