# -*- coding:utf8 -*-
# created by Recker on 2014/07/15

from django.db import models

class Worker(models.Model):
    '''
    工作集群
    '''
    ip = models.IPAddressField(db_index=True)
    status = models.IntegerField(max_length=1, db_index=True, default=0)
    info = models.TextField(null=True)

    class Meta:
        db_table = "video_schedule"
        verbose_name_plural = u"服务器列表"
        verbose_name = u"工作机"

class Schedule(object):
    '''
    调度器
    '''
    def __init__(self):
        pass
