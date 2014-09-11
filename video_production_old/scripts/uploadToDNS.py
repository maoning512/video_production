#!/usr/bin/python 
# -*- coding:utf8 -*- 
# created by Recker on 2014/07/15

import time
import commands
import os
from copy import deepcopy


#def plog(content, LOGNAME, type="INFO"):
#    f = open(LOGNAME, "a+")
#    t = "[%s]: %s: "%(time.strftime("%Y-%m-%d %H:%M:%S"), type)
#    print >>f, t, content
#    f.close()
#
#def runcmd(cmd):
#    res = commands.getstatusoutput(cmd)
#    plog()
#    return res[0]

class runCmd(object):
    '''
    日志对象
    cmd运行对象
    '''
    def __init__(self, logfile):
        self.logfile = logfile
        self.log = self._log
        self.shell = self._cmd

    def _log(self, content, type='INFO'):
        f = open(self.logfile, "a+")
        t = "[%s]: %s: "%(time.strftime("%Y-%m-%d %H:%M:%S"), type)
        print >>f, t, content
        f.close()

    def _cmd(self, cmd):
        res = commands.getstatusoutput(cmd)
        self._log(cmd+ "|"+ str(res))
        return res[0]

class UploadToDNS(object):
    
    def __init__(self, output, dns, rc):
        self.datedir = time.strftime("%Y%m%d") + "/"
        self.output = output
        self.dns = dns + self.datedir 
        self.mp4 = deepcopy(output.get("mobile_out",[]))
        self.f4v = deepcopy(output.get("f4v_out",[]))
        self.hls = deepcopy(output.get("hls_out",{}))
        self.pic = deepcopy(output.get("pic_out",[]))
        self.upload_video = self._upload_video
        self.upload_pic = self._upload_pic
        self.rc = rc

    def _upload_pic(self):
        urlprefix = self.dns
        self.output['pic_out'] = []
        result = 0
        for input in self.pic:
            cmd = "/bin/cp %s %s"%(input['pic'], self.dns)
            if self.rc.shell(cmd):
                result = 51
            self.output['pic_out'].append({'name':urlprefix + os.path.basename(input['pic']), 'dur':''})
        return result, self.output

    def _upload_video(self):
        #urlprefix = os.path.join(self.dns.split(':')[0], "videos", self.datedir)
        urlprefix = self.dns
        self.output['mobile_out'] = []
        self.output['f4v_out'] = []
        result = 0
        for input in self.mp4:
            cmd = "/bin/cp %s %s"%(input['name'], self.dns)
            if self.rc.shell(cmd):
                result = 51
            self.output['mobile_out'].append({'name':urlprefix + os.path.basename(input['name']), 'dur':input['dur']})
        for input in self.f4v:
            cmd = "/bin/cp %s %s"%(input['name'], self.dns)
            if self.rc.shell(cmd):
                result = 51
            self.output['f4v_out'].append({'name':urlprefix + os.path.basename(input['name']), 'dur':input['dur']})
        if self.hls:
            cmd = "/bin/cp %s %s"%(self.hls['hls_m3u8'], self.dns)
            if self.rc.shell(cmd):
                result = 51
            cmd = "/bin/cp %s/*.ts %s"%(os.path.dirname(self.hls['hls_m3u8']), self.dns)
            if self.rc.shell(cmd):
                result = 51
            self.output['hls_out']['hls_m3u8'] = urlprefix + os.path.basename(self.hls['hls_m3u8'])

        return result, self.output

'''
 {u'error_code': 0, u'data': {u'mobile_out': [{u'dur': u'00:00:05.11', u'name': u'/root/workspace/tmp/1_2/encode/c4ca4238a0b923820dcc509a6f75849b.mp4'}], u'f4v_out': [{u'dur': u'00:00:04.97', u'name':
 u'/root/workspace/tmp/1_2/encode/c4ca4238a0b923820dcc509a6f75849b_0.f4v'}], u'hls_out': {u'hls_m3u8': u'/root/workspace/tmp/1_2/encode/c4ca4238a0b923820dcc509a6f75849b.m3u8', u'hls_dur':
 u'00:00:05.11', u'ts_num': u'2'}}, u'error_msg': u'ok'}
'''
