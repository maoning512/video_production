#!/usr/bin/python -w
# -*- coding:utf8 -*-
'''
Created on 2014-07-05

@author: Ray
'''

import os, sys
import string
import commands
import mediaCodec_service
import mediabase
import json
sys.path.append("encode_tools")
import mediaCodec_audiogain
import mediaCodec_srt2ass
import mediaCodec_scan_param

def transcode(test_json):
    '''transcode flow'''
    outinfo = {}
    outinfo["error_code"] = mediabase.SUCCESS
    outinfo["error_msg"] = "ok"
    outdata = {}

    param = json.loads(test_json)
    logname = param["flow_log"]

    mediabase.addlog("=================================================================", logname)
    mediabase.addlog("======================= task start ==============================", logname)
    mediabase.addlog("=================================================================", logname)

    #step1: check input file and parse
    mediabase.addlog("step1: check input file and parse", logname)
    #step1.1: check input file
    #input video
    if not os.path.exists(param["queuefile"] ):
        mediabase.addlog("the input file %s is not exist" % param["queuefile"], logname)
        error_code = mediabase.ERROR_INPUT_NOEXIST
        outinfo["error_code"] = error_code
        outinfo["error_msg"] = "the input video file is not exist"
        return json.dumps(outinfo)

    #input srt
    if param["srtfile"] != "":
        if not os.path.exists(param["srtfile"] ):
            mediabase.addlog("the input file %s is not exist" % param["srtfile"], logname)
            error_code = mediabase.ERROR_INPUT_NOEXIST
            outinfo["error_code"] = error_code
            outinfo["error_msg"] = "the input srt file is not exist"
            return json.dumps(outinfo)

    #input logo
    if param["logofile"] != "":
        #if exist
        if not os.path.exists(param["logofile"] ):
            mediabase.addlog("the input file %s is not exist" % param["logofile"], logname)
            error_code = mediabase.ERROR_INPUT_NOEXIST
            outinfo["error_code"] = error_code
            outinfo["error_msg"] = "the input logo file is not exist"
            return json.dumps(outinfo)

        #check if jpg
        cmd_str = "file %s" % param["logofile"]
        result = commands.getstatusoutput(cmd_str)
        if result[0] != 0:
            error_code = mediabase.ERROR_INPUT_PARAM_VALID
            outinfo["error_code"] = error_code
            outinfo["error_msg"] = "the input logo file is error"
            return json.dumps(outinfo)
        else:
            logo_string = result[1]
            if "jpg" not in param["logofile"].lower() and "png" not in param["logofile"].lower():
                mediabase.addlog("the input file %s is not support" % param["logofile"], logname)
                error_code = mediabase.ERROR_INPUT_PARAM_VALID
                outinfo["error_code"] = error_code
                outinfo["error_msg"] = "the input logo file is not support: should 'jpg/png'"
                return json.dumps(outinfo)

        #check pos
        if param.has_key("logo_pos"):
            if param["logo_pos"] == "" or param["logo_pos"] == "0:0:0:0":
                mediabase.addlog("the input logo pos %s is not support" % param["logo_pos"], logname)
                error_code = mediabase.ERROR_INPUT_PARAM_VALID
                outinfo["error_code"] = error_code
                outinfo["error_msg"] = "the input logo pos not valid[width:height:right:top]!"
                return json.dumps(outinfo)
            else:
                logo_pos_list = param["logo_pos"].split(":")
                if int(logo_pos_list[0]) == 0 or int(logo_pos_list[1]) == 0:
                    mediabase.addlog("the input logo pos %s is not support" % param["logo_pos"], logname)
                    error_code = mediabase.ERROR_INPUT_PARAM_VALID
                    outinfo["error_code"] = error_code
                    outinfo["error_msg"] = "the input logo pos not valid[width:height:right:top]!"
                    return json.dumps(outinfo)

    #input crop
    if param.has_key("crop"):
        if param["crop"] == "":
            mediabase.addlog("the input crop %s is not support" % param["crop"], logname)
            error_code = mediabase.ERROR_INPUT_PARAM_VALID
            outinfo["error_code"] = error_code
            outinfo["error_msg"] = "the input crop not valid!"
            return json.dumps(outinfo)

    #input fps
    if param.has_key("ifps"):
        tmp_fps = param["ifps"]
        tmp_fps = tmp_fps.replace('.','')
        if tmp_fps.isdigit() and not param["ifps"].count('.') > 1:
            fps_num = string.atof(param["ifps"])
            if fps_num < 5 or fps_num > 30:
                mediabase.addlog("the input ifps %s is not support" % param["ifps"], logname)
                error_code = mediabase.ERROR_INPUT_PARAM_VALID
                outinfo["error_code"] = error_code
                outinfo["error_msg"] = "the input ifps not valid[15-30]!"
                return json.dumps(outinfo)
        else:
            mediabase.addlog("the input ifps %s is not support" % param["ifps"], logname)
            error_code = mediabase.ERROR_INPUT_PARAM_VALID
            outinfo["error_code"] = error_code
            outinfo["error_msg"] = "the input ifps not valid!"
            return json.dumps(outinfo)

    #input version_id
    if param["version_id"] != "0" and param["version_id"] != "1" and param["version_id"] != "2" and param["version_id"] != "3":
        error_code = mediabase.ERROR_INPUT_VERSION_ID
        outinfo["error_code"] = error_code
        outinfo["error_msg"] = "the input version id not support,should '0','1','2','3'!"
        return json.dumps(outinfo)

    #get encode_video, encode_pic flag
    encode_pic_flag = 0
    if param["version_id"] == "3":
        encode_pic_flag = 1

    #step1.2: parse
    transcode = mediaCodec_service.Cservice(param)
    transcode.mediaCodec_parse_task_param(mediabase.MEDIA_XMLFILE)
    mediabase.addlog("step1: ok!", logname)

    #step1.3: if encode pic,encode and return
    if encode_pic_flag == 1:
        mediabase.addlog("step1.3: start encode pic", logname)
        result = transcode.mediaCodec_encode_pic(logname)
        if result["error_code"] != 0:
            mediabase.addlog("encode pic error!", logname)
            outinfo["error_code"] = mediabase.ERROR_ENCODE_PIC_ERROR
            outinfo["error_msg"] = "encode pic error"
            return json.dumps(outinfo)

        if result.has_key("data"):
            outdata["pic_out"] = result["data"]
        outinfo["data"] = outdata
        mediabase.addlog("step1.3: ok!", logname)

        mediabase.addlog("=================================================================", logname)
        mediabase.addlog("======================= task over ==============================", logname)
        mediabase.addlog("=================================================================", logname)
        return json.dumps(outinfo)

    #step2: if has subtitle, output ass
    mediabase.addlog("step2: srt to ass", logname)
    if param.has_key("srtfile") and param["srtfile"] != "" and param.has_key("assfile") and param["assfile"] != "":
        sub_info = mediaCodec_srt2ass.srt2ass( param["srtfile"], param["assfile"], logname )
        mediabase.addlog("subtitle info: %s" % sub_info, logname)
        if sub_info['error_code'] != 0:
            mediabase.addlog("the srt file %s is not support" % param["srtfile"], logname)
            outinfo["error_code"] = mediabase.ERROR_SUBTITLE_NOT_SUPPORT
            outinfo["error_msg"] = "the input subtitle not support"
            return json.dumps(outinfo)
        else:
            param["assfile"] = ""
    else:
        param["assfile"] = ""
    mediabase.addlog("step2: ok!", logname)

    #step3: get encode param
    mediabase.addlog("step3: get param", logname)
    ret = transcode.mediaCodec_parse_task_param( mediabase.MEDIA_XMLFILE )
    if ret != 0:
        mediabase.addlog("parse param error!", logname)
        outinfo["error_code"] = mediabase.ERROR_PARSE_PARAM
        outinfo["error_msg"] = "parse param error"
        return json.dumps(outinfo)
    mediabase.addlog("parse param: %s!" % param, logname)
    mediabase.addlog("step3: ok!", logname)

    #step4: get audio volume static
    mediabase.addlog("step4: audiogain", logname)
    if param.has_key("aid") and param["aid"] != "":  #has audio
        volume_info = mediaCodec_audiogain.mediaCodec_scan_volume(mediabase.MEDIA_FFMPEG, param["queuefile"], param, logname)
        mediabase.addlog("audio volume info: %s" % volume_info, logname)
        if volume_info["error_code"]:
            mediabase.addlog("mediaCodec_scan_volume: %s error!" % param["queuefile"], logname)
            error_code = mediabase.ERROR_AUDIO_SCAN_ERROR
            outinfo["error_code"] = error_code
            outinfo["error_msg"] = "scan audio volume error!"
            return json.dumps(outinfo)
        else:
            if volume_info.has_key("adjust_db"):
                param["adjust_db"] = volume_info["adjust_db"]
            else:
                param["adjust_db"] = "0dB"
    else:
        param["adjust_db"] = "0dB"
    mediabase.addlog("step4: ok!", logname)

    #step5: start 1 pass
    mediabase.addlog("step5: 1 pass", logname)
    command_pass1 = transcode.mediaCodec_ffmpeg_encode_cmd( 1, logname )
    if command_pass1 == "":
        error_code = mediabase.ERROR_GET_PASS1_CMD
        outinfo["error_code"] = error_code
        outinfo["error_msg"] = "the get pass1 command line error!"
        return json.dumps(outinfo)

    ret = mediabase.run_cmd( command_pass1, logname )
    if ret != 0:
        error_code = mediabase.ERROR_TRANSCODE_PASS1
        outinfo["error_code"] = error_code
        outinfo["error_msg"] = "encode pass1 error"
        return json.dumps(outinfo)
    mediabase.addlog("step5: ok!", logname)

    #step6: start 2 pass
    mediabase.addlog("step6: 2 pass", logname)
    command_pass2 = transcode.mediaCodec_ffmpeg_encode_cmd( 2, logname )
    if command_pass1 == "":
        error_code = mediabase.ERROR_GET_PASS2_CMD
        outinfo["error_code"] = error_code
        outinfo["error_msg"] = "the get pass2 command line error!"
        return json.dumps(outinfo)

    ret = mediabase.run_cmd( command_pass2, logname )
    if ret != 0:
        error_code = mediabase.ERROR_TRANSCODE_PASS2
        outinfo["error_code"] = error_code
        outinfo["error_msg"] = "encode pass2 error"
        return json.dumps(outinfo)
    mediabase.addlog("step6: ok!", logname)

    #step7: get output dur
    mediabase.addlog("step7: get dur", logname)
    ret = transcode.mediaCodec_getdur( param["basemp4"], logname )
    if ret != "NULL":
        param["base_dur"] = ret
    else:
        error_code = mediabase.ERROR_OUTPUT_DURATION
        outinfo["error_code"] = error_code
        outinfo["error_msg"] = "get output duration error"
        return json.dumps(outinfo)
    mediabase.addlog("step7: ok!", logname)

    #step8: mobile, mov fast start mp4
    mobiledata = []
    mediabase.addlog("step8: mov fast start", logname)
    if param["platform"] & mediabase.MOBILE_PLATFORM:
        ret = transcode.mediaCodec_mp4_movflag( logname )
        if ret != 0:
            error_code = mediabase.ERROR_MOV_FAST_START
            outinfo["error_code"] = error_code
            outinfo["error_msg"] = "mov fast start error"
            return json.dumps(outinfo)
        else:
            mobile_member = {}
            mobile_member["name"] = param["output_mp4"]
            mobile_member["dur"] = param["mp4_dur"]
            mobiledata.append( mobile_member )
    outdata["mobile_out"] = mobiledata
    mediabase.addlog("step8: ok!", logname)

    #step9: hls, get m3u8
    hlsdata = {}
    mediabase.addlog("step9: get m3u8", logname)
    if param["platform"] & mediabase.HLS_PLATFORM:
        ret = transcode.mediaCodec_mp42hls( logname )
        if ret != 0:
            error_code = mediabase.ERROR_MP4_TO_M3U8
            outinfo["error_code"] = error_code
            outinfo["error_msg"] = "mp4 to m3u8 error"
            return json.dumps(outinfo)
        else:
            hlsdata["hls_m3u8"] = param["output_m3u8"]
            hlsdata["hls_dur"] = param["hls_dur"]
            ts_num = transcode.mediaCodec_hls_num( logname )
            if ts_num == 0:
                error_code = mediabase.ERROR_M3U8_IS_NULL
                outinfo["error_code"] = error_code
                outinfo["error_msg"] = "m3u8 has no ts error"
                return json.dumps(outinfo)
            hlsdata["ts_num"] = str(ts_num)
    outdata["hls_out"] = hlsdata
    mediabase.addlog("step9: ok!", logname)

    #step10: web, cut mp4 and meta f4v
    #step10.1: cut mp4
    f4vdata = []
    mediabase.addlog("step10: cut flow", logname)
    if param["platform"] & mediabase.WEB_PLATFORM:
        #step10.1: cut mp4
        mediabase.addlog("step10.1: cut mp4", logname)
        ret = transcode.mediaCodec_cut( logname )
        if ret != 0:
            error_code = mediabase.ERROR_MP4_MEDIA_CUT
            outinfo["error_code"] = error_code
            outinfo["error_msg"] = "mp4 cut to slice error"
            return json.dumps(outinfo)

        #step10.2: flv and f4v
        mediabase.addlog("step10.2: mp4 to flv", logname)
        ret = transcode.mediaCodec_mp42flv( logname )
        if ret != 0:
            error_code = mediabase.ERROR_MP4_TO_FLV
            outinfo["error_code"] = error_code
            outinfo["error_msg"] = "slice mp4 to flv error"
            return json.dumps(outinfo)

        mediabase.addlog("step10.3: flv to f4v", logname)
        ret = transcode.mediaCodec_flv2f4v( logname )
        if ret != 0:
            error_code = mediabase.ERROR_MP4_TO_FLV
            outinfo["error_code"] = error_code
            outinfo["error_msg"] = "slice flv to f4v error"
            return json.dumps(outinfo)

        mediabase.addlog("step10.4: dur and output", logname)
        mediabase.addlog("video has %d slice" % param["f4v_num"] , logname)
        for i in range (0, param["f4v_num"] ):
            f4v_member = {}
            index_dur = str(i) + "_dur"
            f4v_member["name"] = param["slice_base"] + str(i) + ".f4v"
            if os.path.exists(f4v_member["name"]):
                mediabase.addlog("get slice f4v dur: %d" % i, logname)
                if param.has_key(index_dur):
                    f4v_member["dur"] = param[index_dur]
                    mediabase.addlog("dur: %s" % param[index_dur], logname)
                else:
                    error_code = mediabase.ERROR_OUTPUT_DURATION
                    outinfo["error_code"] = error_code
                    outinfo["error_msg"] = "get slice f4v dur error!"
                    return json.dumps(outinfo)
            else:
                error_code = mediabase.ERROR_FLV_TO_F4V
                outinfo["error_code"] = error_code
                outinfo["error_msg"] = "flv to f4v error!"
                return json.dumps(outinfo)
            f4vdata.append(f4v_member)
    outdata["f4v_out"] = f4vdata
    mediabase.addlog("step10: ok!", logname)

    outinfo["data"] = outdata

    mediabase.addlog("=================================================================", logname)
    mediabase.addlog("======================= task over ==============================", logname)
    mediabase.addlog("=================================================================", logname)

    return json.dumps(outinfo)
