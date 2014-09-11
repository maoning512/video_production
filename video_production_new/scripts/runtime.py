#!/usr/bin/python
# -*- coding:utf8 -*-
# created by Recker on 2014/07/07

import json, commands, os, sys
import traceback
from encode_tools.mediaCodec_scan_param import mediaCodec_scan_param
from mediaCodec_flow import transcode
from django.db import connection
from uploadToDNS import UploadToDNS, runCmd
from optparse import OptionParser
from django import db

VIDEO_TMP_DIR = "/opt/workspace/tmp/"
TOOLS_DIR = "/usr/local/mediaCodec/"
TOOLS = ['qt-faststart', 'ffmpeg', 'ffprobe', 'mediacut', 'yamdi']
LOG_DIR = "/opt/workspace/log/"

class Task(object):
    '''
    任务类
    '''
    def __init__(self, task_id, task_type):
        self.warnings = ""
        if Task._check_args(task_id, task_type):
             self.warnings = "parameters error [taskId:%s, taskType:%s]"%(task_id, task_type)
        self.taskid = task_id
        self.tasktype = task_type
        self.rc = runCmd(LOGNAME)
        self.tmpath = VIDEO_TMP_DIR+ self.taskid+ "_"+ str(self.tasktype)+ "/"
        self._init_workspace() #创建临时工作目录
        self.obj = self._get_models()
        if not self.obj:
            self.warnings = "unknown taskId %s"%self.taskid
        self.download = self._download
        self.startprocess = self._video_info if self.tasktype == 1 else self._video_task
        self.end = self._del_workspace

    def _init_workspace(self):
        '''
        创建临时工作目录
        '''
        self.rc.log("===================mission start============================")
        cmd = "mkdir -p %s"%self.tmpath
        res = commands.getstatusoutput(cmd)
        self.rc.log(cmd+ "|"+ str(res))

    def _del_workspace(self):
        '''
        移除临时工作目录，仅当任务成功后
        '''
        cmd = "rm -rf %s"%self.tmpath
        res = commands.getstatusoutput(cmd)
        self.rc.log(cmd+ "|"+ str(res))

    @staticmethod
    def _check_args(task_id, task_type):
        '''
        验证参数
        '''
        if not task_id or not task_type in [1, 2]:
            return True 
        else:
            return False 

    def _get_models(self):
        if self.tasktype == 1:
            try:
                return VideoInfo.objects.get(taskid=self.taskid)
            except:
                return False
        elif self.tasktype == 2:
            try:
                return VideoTask.objects.get(taskid=self.taskid)
            except:
                return False
        elif self.tasktype == 3:
            try:
                return VideoPic.objects.get(taskid=self.taskid)
            except:
                return False
        else:
            return False

    def _download(self):
        '''
        下载片源
        '''
        if os.path.exists(self.tmpath+ self.taskid+ ".video"):
            self.rc.log(self.tmpath+ self.taskid+ ".video has exists!")
            return 0 
        #下载视频文件
        if self.obj.filepath.startswith("http://"):
            cmd = "wget  -T 360 -q -O %s%s %s"%(self.tmpath, self.taskid+ ".video", self.obj.filepath)
        else:
            cmd = "/bin/cp %s %s%s"%(self.obj.filepath, self.tmpath, self.taskid+ ".video")
        res = commands.getstatusoutput(cmd)
        self.rc.log(cmd+ "|"+ str(res))

    def _download_srt_logo(self):
        '''
        下载字幕以及水印
        仅在视频转码中使用
        '''
        #self._transcode_info_to_dict()
        self.srtpath = ""
        self.logopath = ""
        if self.obj.srtfile:
            self.srtpath = self.tmpath+ self.taskid+ ".srt"
            if self.obj.srtfile.startswith("http://"):
                cmd = "wget  -T 360 -q -O %s %s"%(self.srtpath, self.obj.srtfile)
            else:
                cmd = "/bin/cp %s %s"%(self.obj.srtfile, self.srtpath)
            res = commands.getstatusoutput(cmd)
            self.rc.log(cmd+ "|"+ str(res))
        if self.obj.logofile:
            self.logopath = self.tmpath+ self.taskid+ ".png"
            if self.obj.logofile.startswith("http://"):
                cmd = "wget  -T 360 -q -O %s %s"%(self.logopath, self.obj.logofile)
            else:
                cmd = "/bin/cp %s %s"%(self.obj.logofile, self.logopath)
            res = commands.getstatusoutput(cmd)
            self.rc.log(cmd+ "|"+ str(res))

    def _video_info(self):
        '''
        调用视频信息扫描工具
        '''
        res = mediaCodec_scan_param(TOOLS_DIR+ 'ffprobe', self.tmpath+ self.taskid+ ".video", 1, LOGNAME)
        self.rc.log(res)
        self.obj.status = res['error_code']
        self.obj.mediainfo = res['error_msg'] if res['error_code'] else res['data']
        self.obj.save()
        self.rc.log(connection.queries[-1])

    def _video_pic(self):
        '''
        调度截图工具
        '''
        self.encode_tmp_path = self.tmpath + "encode/"
        self._init_encode_tmp_dir()
        self._create_pic_data()
        try:
            res = trnasocde(json.dumps(self.pic))
            res = json.loads(res)
            if not res['error_code']:
                uploader = UploadToDNS(res['data'], URI, self.rc)
                res['error_code'], res['data'] = uploader.upload_pic()
            self.rc.log(res)
            db.close_connection()
            resinfo = res['error_msg'] if res['error_code'] else res['data']
            VideoPic.objects.filter(taskid=self.taskid).update(status=res['error_code'], mediainfo=resinfo)
            self.rc.log(connection.queries[-1])
        except Exception, e:
            VideoPic.objects.filter(taskid=self.taskid).update(status=52, mediainfo=str(e))
            traceback.print_exc()

    def _video_task(self):
        '''
        调用视频编解码工具
        '''
        #创建编码子目录
        self.encode_tmp_path = self.tmpath + "encode/"
        self._init_encode_tmp_dir()
        self._download_srt_logo()
        self._create_transcode_data()
        try:
            res = transcode(json.dumps(self.transcode))
            res = json.loads(res)
            if not res['error_code']:
                uploader = UploadToDNS(res['data'], URI, self.rc)
                res['error_code'], res['data'] = uploader.upload_video()
            self.rc.log(res)
            db.close_connection()
            resinfo = res['error_msg'] if res['error_code'] else res['data']
            VideoTask.objects.filter(taskid=self.taskid).update(status = res['error_code'], mediainfo = resinfo)
            self.rc.log(connection.queries[-1])
        except Exception, e:
            VideoTask.objects.filter(taskid=self.taskid).update(status = 52, mediainfo = str(e))
            traceback.print_exc()

    def _create_transcode_data(self):
        self.transcode = {"queuefile":self.tmpath+ self.taskid+ ".video",
                "srtfile":self.srtpath, #
                "logofile":self.logopath,
                "tmppath":self.encode_tmp_path,
                "logpath":self.encode_tmp_path,
                "outpath":self.encode_tmp_path,
                "vid":TASKID,
                "task_id":TASKID,
                "platform":self.obj.platform,
                "version_id":str(self.obj.versionid),
                "crop":self.obj.crop,  #需要加判断
                "aid":str(self.obj.aid),  #
                "logo_pos":self.obj.logopos,
                "ifps":str(self.obj.ifps),
                "enc_log":"%s%s_enc.log"%(LOG_DIR, TASKID),
                "flow_log":"%s%s_flow.log"%(LOG_DIR, TASKID),
                }
        self.rc.log(self.transcode)

    def _create_pic_data(self):
        self.pic = {
            "queuefile":self.tmpath+ slef.taskid+ ".video",
            "tmppath":self.encode_tmp_path,
            "logpath":self.encode_tmp_path,
            "outpath":self.encode_tmp_path,
            "vid":TASKID,
            "task_id":TASKID,
            "version_id":3,
            "enc_log":"%s%s_enc.log"%(LOG_DIR, TASKID),
            "flow_log":"%s%s_flow.log"%(LOG_DIR, TASKID),
            "cut_time":self.obj.cuttimes,
            "pic_format":self.obj.pictureformat,
            "dimension":self.obj.dimension,
        }
        self.rc.log(self.transcode)
    


    def _init_encode_tmp_dir(self):
        cmd = "mkdir -p %s"%(self.encode_tmp_path)
        res = commands.getstatusoutput(cmd)
        self.rc.log(cmd+ "|"+ str(res))


def check_workspace():
    '''
    检查工作目录
    检查编码工具
    '''
    cmd = "mkdir -p %s && mkdir -p %s && mkdir -p %s"%(VIDEO_TMP_DIR, TOOLS_DIR, LOG_DIR)
    commands.getstatusoutput(cmd)
    for tool in TOOLS:
        if not os.path.exists(TOOLS_DIR+tool):
            commands.getoutput("cp %s %s"%(tool, TOOLS_DIR))
    commands.getoutput("chmod 755 -R %s"%TOOLS_DIR)
    

if __name__ == "__main__":
    '''
    input: taskid tasktype

    检查工作环境
    载入框架环境
    获取任务id以及任务类型
    初始化日志环境
    '''
    parser = OptionParser()
    parser.add_option("-i", "--task", type="string", dest="taskid", help="input taskid")
    parser.add_option("-t", "--type", type="string", dest="tasktype", help="input tasktype")
    (options, args) = parser.parse_args()
    try:
        check_workspace()
    except Exception, e:
        print e
        sys.exit()
    sys.path.append('/root/workspace/video_production/')
    os.environ['DJANGO_SETTINGS_MODULE'] = 'video_production.settings'
    try:
        #引入django models
        from video_info.models import VideoInfo
        from video_task.models import VideoTask
        from video_pic.models import VideoPic
        from video_production import settings
    except Exception, e:
        print e
        sys.exit()
    #接受传递参数
    global TASKID
    global TASKTYPE
    global URI
    global LOGNAME
    TASKID = options.taskid 
    TASKTYPE = options.tasktype
    LOGNAME = LOG_DIR+ str(TASKID)+ "_"+ str(TASKTYPE)+ ".log"
    URI = settings.VIDEO_URI
    #创建任务对象
    task = Task(TASKID, int(TASKTYPE))
    task.download() #下载片源
    task.startprocess() #开始任务处理
    task.end() #结束任务流程
