#!/usr/bin/python
# -*- coding:utf8 -*-
import sys
import os
import re
import string
import commands
import hashlib
import mediabase
import json
import datetime
from xml.dom import minidom
sys.path.append("encode_tools")
import mediaCodec_scan_param

class Cservice:
    '''split business logic'''

    def __init__(self,param):
        '''init'''
        self.param  = {}
        self.param  = param

    def mediaCodec_parse_task_param( self, xmlfile ):
        '''get task param'''
        #step1: has init
        ret = 0
        '''
        #set in input
        self.param["logpath"]    = "/home/ray/data/tmp/"                           # log file path
        self.param["tmppath"]    = "/home/ray/data/tmp/"                           # transcoe tmp file path
        self.param["outpath"]    = "/home/ray/data/tmp/"                           # output clip path

        self.param["queuefile"]   = filename                                       # input file full path
        self.param["srtfile"]     = self.param["srtroot"] + "input.srt"            # srt path
        self.param["logofile"]    = "temp.jpg"                                     # logo file
        self.param["vid"]         = vid                                            # video id                : numb
        self.param["task_id"]     = task_id                                        # task_id                 : numb
        self.param["platform"]    = platform                                       # platform                : numb
        self.param["version_id"]  = "0"                                            # stream version_Id(0,1,2): string
        self.param["crop"]        = "0:0:0:0"                                      # crop size               : string
        self.param["aid"]         = "0"                                            # audio id                : string
        self.param["logo_pos"]    = "0:0:0:0"                                      # logo pos                : string
        self.param["ifps"]        = "25"                                           # output fps              : string
        '''
        #step2: set output file name and log name
        self.media_path_Param()
        '''
        self.param["category"]   = "movie"
        self.param["date"] = datetime.datetime.now().strftime("%Y%m%d")
        self.param["basemp4"] = self.param["tmppath"] + self.md5Str(str(self.param["task_id"])) + mediabase.ENC_BASE_MP4 #video base mp4
        self.param["output_mp4"] = self.param["outpath"] + self.md5Str(str(self.param["task_id"])) + ".mp4"   #output mp4
        self.param["output_m3u8"] = self.param["outpath"] + self.md5Str(str(self.param["task_id"])) + mediabase.ENC_OUT_M3U8 #output m3u8
        self.param["output_hls"] = self.param["outpath"] + self.md5Str(str(self.param["task_id"])) + "_hls_"  #output m3u8
        self.param["passtmp"] = self.param["tmppath"] + self.md5Str(str(self.param["task_id"])) + "_pass"     #2pass tmp

        #split video
        self.param["slice_base"] = self.param["outpath"] + self.md5Str(str(self.param["task_id"])) + "_"      #slice
        #log name
        self.param["tmp_log"] = self.param["logpath"] + self.md5Str(str(self.param["task_id"])) + mediabase.MEDIA_TEMP_LOG  #temp log

        if self.param.has_key("srtfile") and self.param["srtfile"] != "":
            self.param["assfile"] = self.param["tmppath"] + self.md5Str(str(self.param["task_id"])) + mediabase.ENC_ASS_NAME  # ass path
        '''

        self.mediaCodec_parseXml(xmlfile, self.param["category"], self.param["version_id"])

        #step3: parse config and rewrite param
        if self.param["version_id"] != "3":
            self.mediaCodec_parseXml(xmlfile, self.param["category"], self.param["version_id"])

        if self.param.has_key("ifps") and self.param.has_key("vfps"):
            if float( self.param["ifps"] ) < float( self.param["vfps"] ):
                self.param["vfps"] = self.param["ifps"]

        self.param["cuttime"] = mediabase.CUT_TIME

        ret = self.mediaCodec_get_video_param( self.param["flow_log"] )

        '''
        self.param["aaclevel"]  = self.mediaCodec_xmlValue(self.mediaCodec_xmlElement(node,"aaclevel")[0],0)
        self.param["achannel"]  = self.mediaCodec_xmlValue(self.mediaCodec_xmlElement(node,"ac")[0],0)
        self.param["asample"]   = self.mediaCodec_xmlValue(self.mediaCodec_xmlElement(node,"ar")[0],0)
        self.param["abitrate"]  = self.mediaCodec_xmlValue(self.mediaCodec_xmlElement(node,"ab")[0],0)

        self.param["height"]  = self.mediaCodec_xmlValue(self.mediaCodec_xmlElement(node,"height")[0],0)
        self.param["vbitrate"]  = self.mediaCodec_xmlValue(self.mediaCodec_xmlElement(node,"vb")[0],0)
        self.param["vfps"]  = self.mediaCodec_xmlValue(self.mediaCodec_xmlElement(node,"fps")[0],0)
        self.param["x264opt"]  = self.mediaCodec_xmlValue(self.mediaCodec_xmlElement(node,"x264opt")[0],0)
        self.param["width"]  = self.mediaCodec_xmlValue(self.mediaCodec_xmlElement(node,"width")[0],0)             #not used now
        '''
        return ret

    def media_path_Param(self):
        '''get file name'''
        self.param["category"]   = "movie"
        self.param["date"] = datetime.datetime.now().strftime("%Y%m%d")

        #creat outpath
        if not os.path.exists(self.param["logpath"]):
            os.system("mkdir -p %s" % self.param["logpath"])
        if not os.path.exists(self.param["tmppath"]):
            os.system("mkdir -p %s" % self.param["tmppath"])
        if not os.path.exists(self.param["outpath"]):
            os.system("mkdir -p %s" % self.param["outpath"])

        #vtcoder param
        self.param["basemp4"] = self.param["tmppath"] + self.md5Str(str(self.param["task_id"])) + mediabase.ENC_BASE_MP4 #video base mp4
        self.param["output_mp4"] = self.param["outpath"] + self.md5Str(str(self.param["task_id"])) + ".mp4"   #output mp4
        self.param["output_m3u8"] = self.param["outpath"] + self.md5Str(str(self.param["task_id"])) + mediabase.ENC_OUT_M3U8 #output m3u8
        self.param["output_hls"] = self.param["outpath"] + self.md5Str(str(self.param["task_id"])) + "_hls_"  #output m3u8
        self.param["passtmp"] = self.param["tmppath"] + self.md5Str(str(self.param["task_id"])) + "_pass"     #2pass tmp
        #split video
        self.param["slice_base"] = self.param["outpath"] + self.md5Str(str(self.param["task_id"])) + "_"      #slice
        #log name
        self.param["tmp_log"] = self.param["logpath"] + self.md5Str(str(self.param["task_id"])) + mediabase.MEDIA_TEMP_LOG  #temp log

        if self.param.has_key("srtfile") and self.param["srtfile"] != "":
            self.param["assfile"] = self.param["tmppath"] + self.md5Str(str(self.param["task_id"])) + mediabase.ENC_ASS_NAME  # ass path

        #pic group name
        self.param["output_pic"] = self.param["outpath"] + self.md5Str(str(self.param["task_id"])) + "_pic_"  #output m3u8

    def mediaCodec_parseXml(self, xmlfilename, category, enc_level):
        '''parse config xml'''
        root  = self.mediaCodec_xmlParse(xmlfilename)
        nodes = self.mediaCodec_xmlElement(root,"channel")

        for node in nodes :
            if self.mediaCodec_xmlAttribute(node,"name") == category:
                nodes = self.mediaCodec_xmlElement(node,"version")
                for node in nodes :
                    if self.mediaCodec_xmlAttribute(node,"id") == enc_level:
                        self.param["aaclevel"] = self.mediaCodec_xmlValue(self.mediaCodec_xmlElement(node,"aaclevel")[0],0)
                        self.param["achannel"] = self.mediaCodec_xmlValue(self.mediaCodec_xmlElement(node,"ac")[0],0)
                        self.param["asample"] = self.mediaCodec_xmlValue(self.mediaCodec_xmlElement(node,"ar")[0],0)
                        self.param["abitrate"] = self.mediaCodec_xmlValue(self.mediaCodec_xmlElement(node,"ab")[0],0)

                        self.param["height"] = self.mediaCodec_xmlValue(self.mediaCodec_xmlElement(node,"height")[0],0)
                        self.param["vbitrate"] = self.mediaCodec_xmlValue(self.mediaCodec_xmlElement(node,"vb")[0],0)
                        self.param["vfps"] = self.mediaCodec_xmlValue(self.mediaCodec_xmlElement(node,"fps")[0],0)
                        self.param["x264opt"] = self.mediaCodec_xmlValue(self.mediaCodec_xmlElement(node,"x264opt")[0],0)
                        self.param["width"] = self.mediaCodec_xmlValue(self.mediaCodec_xmlElement(node,"width")[0],0)             #not used now

    def mediaCodec_xmlParse(self,filename):
        '''xml constructor'''
        doc  = minidom.parse(filename)
        root = doc.documentElement
        return root

    def mediaCodec_xmlElement(self,node,name):
        if node :
            return node.getElementsByTagName(name)
        else:
            return ""

    def mediaCodec_xmlAttribute(self,node,attribute):
        try :
            if node :
                return node.getAttribute(attribute)
            else :
                return ""
        except:
            return ""

    def mediaCodec_xmlValue(self,node,index=0):
        try:
            if node :
                return node.childNodes[index].nodeValue
            else :
                return ""
        except:
            return ""

    def mediaCodec_get_video_param(self, logname):
        '''scan input video'''
        ret = 0
        scan_result = mediaCodec_scan_param.mediaCodec_scan_param( mediabase.MEDIA_FFPROBE,
                      self.param["queuefile"], 0, logname)
        if scan_result['error_code'] != 0:
            mediabase.addlog("scan input video [%s] error" % self.param["queuefile"], logname)
            ret = 1
            return ret
        else:
            video_info = scan_result["data"]

            if video_info.has_key("Video"):
                self.param["input_w"] = video_info["Video"]["0"]["width"]
                self.param["input_h"] = video_info["Video"]["0"]["height"]
            else:
                ret = 1
                return ret
        return ret

    def mediaCodec_ffmpeg_encode_cmd(self, passtype, logname):
        ''' '''
        cmd_str = ""

        if passtype != 1 and passtype != 2:
            mediabase.addlog( " encode pass not valid! ", logname )
            return cmd_str

        cmd_str += mediabase.MEDIA_FFMPEG + " -i " + self.param["queuefile"]

        #get subtitle and scale param
        if self.param.has_key("input_w") and self.param.has_key("input_h"):
            input_width = int(self.param["input_w"])
            input_height = int(self.param["input_h"])
        else:
            mediabase.addlog( " no source width and height! ", logname )
            cmd_str = ""
            return cmd_str

        crop_cmd = ""
        if self.param.has_key("crop"):
            crop_list = self.param["crop"].split(":")
            if string.atoi(crop_list[0]) > 0 or string.atoi(crop_list[1]) > 0 \
                   or string.atoi(crop_list[2]) > 0 or string.atoi(crop_list[3]) > 0:
                if not (input_width == string.atoi(crop_list[0]) and input_height == string.atoi(crop_list[1])):
                    crop_width = int(crop_list[0])
                    crop_height = int(crop_list[1])
                    crop_cmd = ",crop=" + self.param["crop"]
                else:
                    crop_width = int(input_width)
                    crop_height = int(input_height)
            else:
                crop_width = int(input_width)
                crop_height = int(input_height)
        else:
            crop_width = int(input_width)
            crop_height = int(input_height)

        if self.param.has_key("logofile") and self.param["logofile"] != "":
            logo_percent = int(mediabase.LOGO_SIZEP)
            #get logo cmd_line, just crop,scale,and add sub, logo
            video_filter_cmd = " -vf 'movie=%s,scale=-1:%s[logo];" \
                               % ( self.param["logofile"], str(int(crop_height/logo_percent)) )
            video_filter_cmd += "[in]idet,yadif=0:-1:1" + crop_cmd
            if self.param.has_key("assfile") and self.param["assfile"] != "":
                video_filter_cmd += ",ass=%s" % ( self.param["assfile"] )

            logo_list = self.param["logo_pos"].split(":")
            #width, height, right_side, top_side
            #(1)width+right_side < crop_width
            #(2)height+top_side < crop_height
            if int(logo_list[0]) + int(logo_list[2]) > crop_width or \
               int(logo_list[1]) + int(logo_list[3]) > crop_height:
                mediabase.addlog( " the log position is not right:%s! " % ( self.param["logo_pos"] ), logname )
                cmd_str = ""
                return cmd_str

            #overlay is top_left pos
            video_filter_cmd += "[normal];[normal][logo]overlay=main_w-%d:%d" \
                                % ( int(int(logo_list[0])*crop_height/logo_percent/int(logo_list[1])) \
                                    + int(logo_list[2]), int(logo_list[3]) )

            if int(self.param["height"]) <= crop_height:
                cmd_height = int(self.param["height"])
                cmd_height = cmd_height / 16 * 16
                video_filter_cmd += ",scale=trunc((oh*a*sar+8)/16)*16:" + str(cmd_height)
            else:
                cmd_height = crop_height
                cmd_height = cmd_height / 16 * 16
                video_filter_cmd += ",scale=trunc((oh*a*sar+8)/16)*16:" + str(cmd_height)

            video_filter_cmd += "'"
        else:
            #get no logo cmd_line, just crop, add sub, scale
            video_filter_cmd = " -vf 'idet,yadif=0:-1:1" + crop_cmd

            if self.param.has_key("assfile") and self.param["assfile"] != "":
                video_filter_cmd += ",ass=%s" % ( self.param["assfile"] )

            if int(self.param["height"]) <= crop_height:
                cmd_height = int(self.param["height"])
                cmd_height = cmd_height / 16 * 16
                video_filter_cmd += ",scale=trunc((oh*a*sar+8)/16)*16:" + str(cmd_height)
            else:
                cmd_height = crop_height
                cmd_height = cmd_height / 16 * 16
                video_filter_cmd += ",scale=trunc((oh*a*sar+8)/16)*16:" + str(cmd_height)

            video_filter_cmd += "'"

        cmd_str += video_filter_cmd
        if self.param["aid"] != "":
            cmd_str += " -map 0:v -map 0:a:%s " % self.param["aid"]                        #map
        else:
            cmd_str += " -map 0:v "

        #video encode
        cmd_str += " -vcodec libx264 -r %s -b:v %s -pix_fmt yuv420p " % \
                    ( self.param["vfps"], self.param["vbitrate"] )                     #vcodec param
        cmd_str += " -x264opts %s" % ( self.param["x264opt"] )                         #x264 param
        cmd_str += ":keyint=%d " % ( int(float(self.param["vfps"]))*10 )               #video gop

        if passtype == 2:
            cmd_str += " -pass 2 -passlogfile %s " % self.param["passtmp"]
        else:
            cmd_str += " -pass 1 -passlogfile %s " % self.param["passtmp"]

        #audio encode
        if self.param["aid"] != "":
            #audiogain
            if self.param.has_key("adjust_db") and self.param["adjust_db"] != "0dB":
                cmd_str += " -af volume=%s " % self.param["adjust_db"]

            #audio encode
            cmd_str += " -acodec libfdk_aac -profile:a %s -ar %s -b:a %s -ac %s -strict -2 " % \
                       ( self.param["aaclevel"], self.param["asample"], self.param["abitrate"],
                         self.param["achannel"] )               #video gop
        else:
            cmd_str += " -an "

        #output
        if passtype == 2:
            cmd_str += " -y %s 2>>%s 1>&2 " % ( self.param["basemp4"], self.param["enc_log"] )
        else:
            cmd_str += " -f mp4 -y /dev/null 2>%s 1>&2 " % ( self.param["enc_log"] )

        return cmd_str


    def mediaCodec_encode_pic(self, logname):
        '''encode pic'''

        result_pic = {}
        result_pic["error_code"] = 0

        #step1.1: get duration
        file_dur = 0
        scan_result = mediaCodec_scan_param.mediaCodec_scan_param( mediabase.MEDIA_FFPROBE,
                      self.param["queuefile"] , 0, logname)
        if scan_result['error_code'] != 0:
            mediabase.addlog("encode pic: scan input video [%s] error" % self.param["queuefile"], logname)
            result_pic["error_code"] = 1
            return result_pic
        else:
            video_info = scan_result["data"]

            if video_info.has_key("duration"):
                file_dur = int(video_info["duration"]) / 1000
            else:
                mediabase.addlog("encode pic:scan video no duration [%s] error" % self.param["queuefile"], logname)
                result_pic["error_code"] = 1
                return result_pic

        #step1: cut time
        if len(self.param["pic_time"]) != 0:
            pic_time_list = self.param["pic_time"].split(";")
        else:
            mediabase.addlog("input pic time error[%s]!" % (self.param["pic_time"]), logname)
            result_pic["error_code"] = 1
            return result_pic

        #step2: format if not valid use default jpg
        if self.param["pic_format"] != "1" and self.param["pic_format"] != "2":
            self.param["pic_format"] = "2"

        #step3: get default dimension
        pic_dimension = "480x320"
        if len(self.param["dimension"]) != 0:
            pic_dimension_list = self.param["dimension"].split("x")
            if len(pic_dimension_list) != 2 or self.param["dimension"].count('.') > 0:
                mediabase.addlog("input dimension error[%s]!" % ( self.param["dimension"] ), logname)
                result_pic["error_code"] = 1
                return result_pic
            else:
                if pic_dimension_list[0].isdigit() and pic_dimension_list[1].isdigit():
                    pic_dimension = self.param["dimension"]
        else:
            mediabase.addlog("input dimension error[%s]!" % ( self.param["dimension"] ), logname)
            result_pic["error_code"] = 1
            return result_pic

        pic_list = []
        idx = -1
        for i in range( 0, len(pic_time_list) ):
            if pic_time_list[i] == "" or pic_time_list[i].count('.') > 0 or not pic_time_list[i].isdigit():
                continue
            if int(pic_time_list[i]) < 0 or int(pic_time_list[i]) > file_dur:
                continue
            idx = idx + 1
            pic_elem = {}
            if self.param["pic_format"] == "1":
                pic_name = self.param["output_pic"] + str(idx) + ".png"
            else:
                pic_name = self.param["output_pic"] + str(idx) + ".jpg"

            cmd_str = ""
            cmd_str += mediabase.MEDIA_FFMPEG + " -ss %s -i %s " % (pic_time_list[i], self.param["queuefile"])
            cmd_str += " -vframes 1 -f image2 -s %s -y %s " % ( pic_dimension, pic_name)
            cmd_str += " 2>>%s 1>&2" % ( self.param["tmp_log"] )

            ret = mediabase.run_cmd( cmd_str, logname )
            if ret != 0:
                mediabase.addlog("get pic error[%s]!" % ( pic_time_list[i] ), logname)
                result_pic["error_code"] = 1
                return result_pic

            pic_elem["time"] = pic_time_list[i]
            pic_elem["pic"] = pic_name
            pic_list.append(pic_elem)

        result_pic["data"] = pic_list
        return result_pic

    def mediaCodec_mp4_movflag(self, logname):
        '''mp4 to flv'''
        ret = 0
        cmd_str = ""
        cmd_str += mediabase.MEDIA_QTFAST + " %s  %s " % ( self.param["basemp4"] , self.param["output_mp4"] )
        cmd_str += " 2>>%s 1>&2" % ( self.param["tmp_log"] )
        ret = mediabase.run_cmd( cmd_str, logname )
        if ret != 0:
            mediabase.addlog("mp4 mov flag error!", logname)
            return ret
        duration = self.mediaCodec_getdur(self.param["output_mp4"], logname)
        if duration != "NULL":
            self.param["mp4_dur"] = duration
        else:
            mediabase.addlog("get mp4 duration error!", logname)
            ret = 1
            return ret

        return ret

    def mediaCodec_mp42hls(self, logname):
        '''mp4 to hls'''
        ret = 0
        cmd_str = ""
        split_time = "10"

        if self.param["aid"] != "":
            audiocmd = " -acodec copy -map 0:a "
        else:
            audiocmd = " -an "

        cmd_str += mediabase.MEDIA_FFMPEG + " -i %s " % ( self.param["basemp4"] )
        cmd_str += " -vcodec copy -bsf h264_mp4toannexb -map 0:v %s -flags -global_header " % ( audiocmd )
        cmd_str += " -f segment -segment_time %s -segment_list %s " % ( split_time, self.param["output_m3u8"] )
        cmd_str += " -segment_format mpegts %s" % ( self.param["output_hls"] )
        cmd_str += "%04d.ts"
        cmd_str += " 2>>%s 1>&2" % ( self.param["tmp_log"] )
        ret = mediabase.run_cmd( cmd_str, logname )
        self.param["hls_dur"] = self.param["base_dur"]
        return ret

    def mediaCodec_hls_num(self, logname):
        '''get m3u8'''
        ret = 0
        m3u8_name = self.param["output_m3u8"]
        cmd_str = " cat %s | grep '.ts'" % m3u8_name
        result = commands.getstatusoutput(cmd_str)
        if result[0] != 0:
           ret = 0
           return ret
        else:
           ts_line = result[1].splitlines()
           ret = len(ts_line)
           return ret

    def mediaCodec_cut(self, logname):
        '''cut mp4'''
        if mediabase.NEW_CUT_TOOLS:
            cmd_str = ""
            cut_list = self.param["cuttime"].split(":")
            if not cut_list[0].isdigit() or not cut_list[1].isdigit() or not cut_list[2].isdigit():
                ret = 1
                return ret
            cut_time = str(int(cut_list[0])*3600 + int(cut_list[1])*60 + int(cut_list[2]))
            filename = self.param["slice_base"] + "%d.mp4"
            if self.param["aid"] != "":
                cmd_str += mediabase.MEDIA_CUT + " -i %s -vcodec copy -acodec copy  -map 0 -f segment -segment_format mp4 " % ( self.param["basemp4"] )
            else:
                cmd_str += mediabase.MEDIA_CUT + " -i %s -vcodec copy -an -map 0 -f segment -segment_format mp4 " % ( self.param["basemp4"] )
            cmd_str += " -segment_time %s -y %s " % (cut_time, filename)
            cmd_str += " 2>>%s 1>&2" % ( self.param["tmp_log"] )
            ret = mediabase.run_cmd( cmd_str, logname )
        else:
            cmd_str = ""
            filename = self.param["slice_base"] + "%d.mp4"
            cmd_str += mediabase.MEDIA_CUT + " -i %s -t %s %s " % (self.param["basemp4"], self.param["cuttime"], filename)
            cmd_str += " 2>>%s 1>&2" % ( self.param["tmp_log"] )
            ret = mediabase.run_cmd( cmd_str, logname )
            return ret


        return ret

    def mediaCodec_mp42flv(self, logname):
        '''mp4 to flv'''
        ret = 0
        for i in range(0,100):
            cmd_str = ""
            in_file_mp4 = self.param["slice_base"] + str(i) + ".mp4"
            out_file_flv = self.param["slice_base"] + str(i) + ".flv"
            #if slice exist
            if os.path.exists(in_file_mp4):
                if self.param["aid"] != "":
                    cmd_str += mediabase.MEDIA_FFMPEG + " -i " + in_file_mp4 + " -f flv -vcodec copy -acodec copy -y "
                else:
                    cmd_str += mediabase.MEDIA_FFMPEG + " -i " + in_file_mp4 + " -f flv -vcodec copy -an -y "
                cmd_str += out_file_flv
                cmd_str += " 2>>%s 1>&2" % ( self.param["tmp_log"] )
                ret = mediabase.run_cmd( cmd_str, logname )
                if ret != 0:
                    mediabase.addlog("slice[%d] mp4 to flv error!" % i, logname)
                    return ret
            else:
                #if not exist break
                break
        return ret

    def mediaCodec_flv2f4v(self, logname):
        '''mp4 to flv'''
        ret = 0
        for i in range(0,100):
            cmd_str = ""
            in_file_flv = self.param["slice_base"] + str(i) + ".flv"
            out_file_f4v = self.param["slice_base"] + str(i) + ".f4v"
            #if slice exist
            if os.path.exists(in_file_flv):
                cmd_str += mediabase.MEDIA_YAMDI + " -i " + in_file_flv + " -o " + out_file_f4v
                cmd_str += " -c 'mediaCodec tools' 2>>%s 1>&2 " % ( self.param["tmp_log"] )
                ret = mediabase.run_cmd( cmd_str, logname )
                if ret != 0:
                    mediabase.addlog("slice[%d] flv add meta to f4v error!" % i, logname)
                    return ret
                self.param["f4v_num"] = i + 1
                duration = self.mediaCodec_getdur(out_file_f4v, logname)
                if duration != "NULL":
                    index = str(i) + "_dur"
                    self.param[index] = duration
                else:
                    mediabase.addlog("get f4v duration error!", logname)
                    ret = 1
                    return ret
            else:
                #if not exist break
                break

        return ret

    def mediaCodec_getdur(self, input_file, logname):
        '''get output dur'''
        scan_result = mediaCodec_scan_param.mediaCodec_scan_param( mediabase.MEDIA_FFPROBE,
                      input_file, 0, logname)
        if scan_result['error_code'] != 0:
            mediabase.addlog("scan input video [%s] error" % input_file, logname)
            out_dur = "NULL"
            return out_dur
        else:
            video_info = scan_result["data"]

            if video_info.has_key("Video"):
                video_dur = video_info["Video"]["0"]["duration"]
            else:
                mediabase.addlog("scan video no duration [%s] error" % input_file, logname)
                out_dur = "NULL"
                return out_dur
            if video_info.has_key("Audio"):
                audio_dur = video_info["Audio"]["0"]["duration"]
            else:
                mediabase.addlog("scan audio no duration [%s] error" % input_file, logname)
                out_dur = "NULL"
                return out_dur

            if abs(int(video_dur) - int(audio_dur))/1000 > int(video_dur)/1000/5: #video and audio len_diff big than 1/5
                mediabase.addlog("scan video and audio diff len [%s] error" % input_file, logname)
                out_dur = "NULL"
                return out_dur

        scan_cmd = mediabase.MEDIA_FFMPEG +  " -i %s 2>&1 | grep Duration" % ( input_file )
        mediabase.addlog("run cmd:%s" % scan_cmd, logname)
        result = commands.getstatusoutput(scan_cmd)
        if result[0] != 0:
            mediabase.addlog( "call function error: %s " % scan_cmd, logname )
            out_dur = "NULL"
            return out_dur

        log_line = result[1].splitlines()
        log_list = log_line[0].split()
        if "Duration" not in log_list[0]:
            out_dur = "NULL"
            return out_dur
        else:
            out_dur = log_list[1].strip(",")
            return out_dur

    def md5sum(self,file):
        '''file md5'''
        md5 = hashlib.md5()
        md5string = ''
        try:
            filehandle = open(file,"r")
            md5.update(filehandle.read())
            md5string  = md5.hexdigest()
            filehandle.close
        except Exception,e:
            print e
        return md5string

    def md5Str(self,string):
        '''string md5'''
        md5 = hashlib.md5()
        md5.update(string)
        return md5.hexdigest()

