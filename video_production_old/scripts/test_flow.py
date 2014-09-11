#!/usr/bin/python -w
# -*- coding:utf8 -*-

import sys
import re
import os
import json
import hashlib
import mediabase
import mediaCodec_flow
import mediaCodec_service
from optparse import OptionParser

class parse:
    '''parse data'''

    def __init__(self):
        '''init'''
        self.param = {}
        self.param["logpath"]    = "/home/ray/data/tmp/"                           # log file path
        self.param["tmppath"]    = "/home/ray/data/tmp/"                           # transcoe tmp file path
        self.param["outpath"]    = "/home/ray/data/tmp/"                           # output clip path

    def parse_media_param(self, vid, task_id, platform, filename, srtname, logoname):
        '''parse media input param'''
        #business
        self.param["queuefile"]   = filename                                       # input file full path
        self.param["srtfile"]     = srtname                                        # srt path
        self.param["logofile"]    = logoname                                       # logo file
        self.param["vid"]         = vid                                            # video id                : numb
        self.param["task_id"]     = task_id                                        # task_id                 : numb
        self.param["platform"]    = platform                                       # platform                : numb
        self.param["version_id"]  = "3"                                            # stream version_Id(0,1,2,3): string
        #crop: out_width:out_height:crop_left:crop_rigit
        self.param["crop"]        = "0:0:0:0"                                      # crop size               : string
        self.param["aid"]         = "0"                                            # audio id                : string
        #logo_pos: logo_size_width:logo_size_height:logo_right_side:logo_bot_side
        self.param["logo_pos"]    = "0:0:0:0"                                      # logo pos                : string
        self.param["ifps"]        = "25"                                           # output fps              : string
        self.param["enc_log"]     = self.param["logpath"] + self.md5Str(str(self.param["task_id"])) + mediabase.MEDIA_ENC_LOG    #encode log
        self.param["flow_log"]    = self.param["logpath"] + self.md5Str(str(self.param["task_id"])) + mediabase.MEDIA_FLOW_LOG  #flow log

        self.param["logo_pos"]    = "500:150:5:5"                                   # logo pos                : string
        self.param["pic_time"]    = "0;1;3;5;7;"                                      # cut time                : string
        self.param["pic_format"]  = "2"                                             # format(0:png,1:jpg)     : string
        self.param["dimension"]   = "480x320"                                       # pic size                : string

        return self.param

    def md5Str(self,string):
        '''string md5'''
        md5 = hashlib.md5()
        md5.update(string)
        return md5.hexdigest()

###################################################################################################
#main function start
parser = OptionParser()
parser.add_option('--input', action='store', dest='input', type='string', help='input src file')
parser.add_option('--in_srt', action='store', dest='in_srt', type='string', help='input srt file')
parser.add_option('--in_logo', action='store', dest='in_logo', type='string', help='input logo file')

(options, args) = parser.parse_args(sys.argv)

print 'Usage python test_flow.py --input=file --in_srt=in.srt --in_logo=in.jpg'

if options.input == None:
    print 'Please input the src file'
    print 'Usage python test_flow.py --input=file --in_srt=in.srt --in_logo=in.jpg'
    sys.exit(1)
else:
    input_name = options.input

if options.in_srt == None:
    print 'no srt file'
    print 'Usage python test_flow.py --input=file --in_srt=in.srt --in_logo=in.jpg'
    input_srt = ""
else:
    input_srt = options.in_srt

if options.in_logo == None:
    print 'no logo file'
    print 'Usage python test_flow.py --input=file --in_srt=in.srt --in_logo=in.jpg'
    input_logo = ""
else:
    input_logo = options.in_logo

def main():
    testdata = parse()
    testPara = testdata.parse_media_param(1000, 2000, mediabase.ALL_PLATFORM, input_name, input_srt, input_logo) #vid, task_id
    testJson = json.dumps(testPara)
    outinfo = json.loads(mediaCodec_flow.transcode(testJson))
    print ""
    print outinfo
    if outinfo["error_code"]:
        print "transcode failed: %s" % outinfo["error_code"]
    else:
        print "transcode succeed: %s" % outinfo["error_code"]

    print "transcode over!"
    exit(0)

if __name__ == '__main__':
    main()

'''
all param value:
cmd_str = {
    #step1: need input
    #path
    'logpath': '/home/ray/data/tmp/',
    'tmppath': '/home/ray/data/tmp/',
    'outpath': '/home/ray/data/tmp/',
    #input param
    'queuefile': '/data/tmp/0.mp4',
    'srtfile': '/data1/tmp/in.srt',
    'logofile': '/data1/tmp/in.jpg',
    'vid': 0,                                    #numb
    'task_id': 0,                                #numb
    'platform': 0,                               #numb
    'version_id': "0",                           #string
    'crop': "0:0:0:0",                           #string
    'aid': "0",                                  #string
    'logo_pos': '0:0:0:0',                       #string
    'ifps': '25',                                #string
    'enclog': '/data1/tmp/2000.enclog',
    'ffmpeglog': '/data1/tmp/2000.ffmpeglog',

    #step2: caculate
    "category": "movie"
    "date": ""
    "basemp4": "_base.mp4"    #video base mp4
    "output_mp4": ".mp4"      #output mp4
    "output_m3u8": ".m3u8"    #output m3u8
    "output_hls": "_hls_"     #output m3u8
    "passtmp":"_pass"         #2pass tmp
    "slice_base": "_"         #slice

    "tmp_log": ""

    "assfile": "_final.ass"  # ass path
    "vfps": ""
    "cuttime": "00:06:00"

    "aaclevel": ""
    "achannel": ""
    "asample": ""
    "abitrate": ""

    "height": ""
    "vbitrate": ""
    "vfps": ""
    "x264opt": ""
    "width": ""

    "input_w": ""
    "input_h": ""

    "hls_dur": ""
    "mp4_dur": ""
}
'''
