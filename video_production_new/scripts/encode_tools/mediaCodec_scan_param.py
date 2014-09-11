#!/usr/bin/python
# -*- coding: utf8 -*-

'''
Created on 2014-07-09
Author: Ray
Brief:
    scan video info
usage:
    python mediaCodec_scan_param.py -i test.mp4

function:
    return video infomation

'''

import sys
import os
import commands, string
import logging
from optparse import OptionParser

DEBUG = 0
FFPROBE_SCAN = '/usr/local/mediaCodec/ffprobe'

#error code
MEDIACODEC_SCAN_PARAM_OK               =  {"error_code": 0, "error_msg": "OK!" }
MEDIACODEC_SCAN_PARAM_INPUT_ERROR      =  {"error_code": 1, "error_msg": "input cmd error!" }
MEDIACODEC_SCAN_PARAM_INPUT_FILE_ERROR =  {"error_code": 2, "error_msg": "input file error!" }

def addlog(info,logname):
    logger  = logging.getLogger()
    handler = logging.FileHandler(logname)
    logger.addHandler(handler)
    formatter = logging.Formatter('[%(asctime)s]: %(levelname)s: %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.setLevel(logging.NOTSET)
    logger.info(info)
    logger.removeHandler(handler)

def mediaCodec_time_code_change( full_time ):
    time_int, ms = full_time.split(".")
    time_list = time_int.split(":")
    time_ms = (int(time_list[0]) * 3600 + int(time_list[1]) * 60 + int(time_list[2])) * 1000 + int(ms)*10
    return str(time_ms)


def mediaCodec_scan_param( ffprobe_input, input_name, crop_flag, logname ):
    ''''''
    addlog(" python mediaCodec_scan_param.py -i %s\n" % input_name, logname)

    out_info = {}
    result_error_code = MEDIACODEC_SCAN_PARAM_OK

    #step1: check input
    if input_name != None:
        input_file = input_name
    else:
        addlog("   need input file", logname)
        result_error_code = MEDIACODEC_SCAN_PARAM_INPUT_ERROR
        return result_error_code

    if not os.path.exists(ffprobe_input):
        addlog("   encoder does not exist", logname)
        result_error_code = MEDIACODEC_SCAN_PARAM_INPUT_ERROR
        return result_error_code
    elif not os.path.exists(input_file):
        addlog("   input file not exist:%s\n" % input_file, logname)
        result_error_code = MEDIACODEC_SCAN_PARAM_INPUT_FILE_ERROR
        return result_error_code
    else:
        if crop_flag:
            scan_cmd = ffprobe_input +  " -i %s -show_streams -show_crop_detect" % ( input_file )
        else:
            scan_cmd = ffprobe_input +  " -i %s -show_streams" % ( input_file )

        addlog(" run cmd:%s" % scan_cmd, logname)
        result = commands.getstatusoutput(scan_cmd)
        if result[0] != 0:
            addlog( " call function error: %s " % scan_cmd, logname )
            result_error_code = MEDIACODEC_SCAN_PARAM_INPUT_FILE_ERROR
            addlog( " get video info:\n%s " % result_error_code, logname )
            return result_error_code

        get_info = []
        log_line = result[1].splitlines()

        get_info_flag = 0
        for line in log_line:
            if "mediaCodec-ffmpeg scan" not in line and get_info_flag == 0:
                continue
            get_info_flag = 1
            if " + " in line:
                get_info.append(line)

        if len(get_info) == 0:
            addlog( " get video info error:all! ", logname )
            result_error_code = MEDIACODEC_SCAN_PARAM_INPUT_FILE_ERROR
            addlog( " get video info:\n%s " % result_error_code, logname )
            return result_error_code

        if DEBUG:
            for line in get_info:
                print line
            print ""

        #get file info
        out_info['file_size'] = os.path.getsize(input_name)
        out_info['input'] = get_info[0].split()[2].strip()
        duration_tmp = get_info[1].split()[2].strip()
        out_info['duration'] = mediaCodec_time_code_change(duration_tmp)

        ffprobe_bitrate = int(get_info[2].split()[2].strip())*1000
        if ffprobe_bitrate == 0:
            ffprobe_dur = int(out_info['duration'])/1000
            if ffprobe_dur != 0:
                out_info['bitrate'] = out_info['file_size'] / ffprobe_dur
            else:
                out_info['bitrate'] = ffprobe_bitrate
        else:
            out_info['bitrate'] = ffprobe_bitrate

        out_info['bitrate'] = int(get_info[2].split()[2].strip())*1000

        #get video info
        video_multi = []
        video_info = []
        get_info_flag = 0
        for line in get_info:
            if "video tracks start" not in line and get_info_flag == 0:
                continue
            get_info_flag = 1
            if "Stream_id:" in line:
                video_info.append(line)
            if "video tracks end" in line:
                break

        if len(video_info) == 0:
            addlog( " get video info error: no video! ", logname )
            result_error_code = MEDIACODEC_SCAN_PARAM_INPUT_FILE_ERROR
            addlog( " get video info:\n%s " % result_error_code, logname )
            return result_error_code

        for i in range(0, len(video_info)):
            video_out = {}
            video_list = video_info[i].split()
            if 'Stream_id:' in video_list:
                video_out['no'] = int(video_list[video_list.index('Stream_id:') - 1].strip(':')) - 1
            if 'codec_name:' in video_list:
                video_out['codec_name'] = video_list[video_list.index('codec_name:') + 1].strip(',')
            if 'size:' in video_list:
                width, height = video_list[video_list.index('size:') + 1].strip(',').split('x')
                video_out['width'] = int(width)
                video_out['height'] = int(height)
            if 'play_aspect:' in video_list:
                video_out['display_aspect_ratio'] = video_list[video_list.index('play_aspect:') + 1].strip(',')

            if 'bitrate:' in video_list:
                video_out['bit_rate'] = int(video_list[video_list.index('bitrate:') + 1].strip(','))*1000
            if 'fps:' in video_list:
                frame_rate = str(video_list[video_list.index('fps:') + 1].strip(','))
                if '.' in frame_rate:
                    video_out['avg_frame_rate'] = string.atof(frame_rate)
                else:
                    video_out['avg_frame_rate'] = string.atoi(frame_rate)
            if 'dur:' in video_list:
                duration_tmp = video_list[video_list.index('dur:') + 1].strip(',')
                video_out['duration'] = mediaCodec_time_code_change(duration_tmp)
            if 'crop:' in video_list:
                if len(out_info['duration']) > 0 and int(out_info['duration']) > 30000:
                    crop_list = video_list[video_list.index('crop:') + 1].strip(',').split(":")
                    if int(crop_list[0]) < video_out['width']*2/3 or int(crop_list[1]) < video_out['height']*2/3:
                        video_out['v_crop'] = '0:0:0:0'
                    else:
                        video_out['v_crop'] = video_list[video_list.index('crop:') + 1].strip(',')
                else:
                    video_out['v_crop'] = '0:0:0:0'

            #get max resolution
            if video_out.has_key('width') and video_out.has_key('height'):
                input_area = video_out['width'] * video_out['height']
                # -(240P)- 150,000 -(320P)- 260,000 -(480P)- 650,000 -(720P)- 1,500,000 -(1080P)-
                if input_area < 260000 :
                    video_out['max_resolution'] = '320P'
                elif input_area < 650000 :
                    video_out['max_resolution'] = '480P'
                else:
                    video_out['max_resolution'] = '720P'
            else:
                video_out['max_resolution'] = '480P'

            #check video info
            #video_out['display_aspect_ratio'] =
            #bitrate
            if video_out.has_key('bit_rate') and video_out['bit_rate'] == 0:
                video_out['bit_rate'] = out_info['bitrate']
            #duration
            if video_out.has_key('duration'):
                dur = video_out['duration'].replace(":","" ).replace("0","").replace(".","")
                if dur == "" :
                    video_out['duration'] = out_info['duration']

            video_multi.append( video_out )

        #get audio info
        audio_multi = []
        audio_info = []
        get_info_flag = 0
        for line in get_info:
            if "audio tracks start" not in line and get_info_flag == 0:
                continue
            get_info_flag = 1
            if "Stream_id:" in line:
                audio_info.append(line)
            if "audio tracks end" in line:
                break

        if len(audio_info) == 0:
            addlog( " no audio streams!", logname )

        for i in range(0, len(audio_info)):
            audio_out = {}
            audio_list = audio_info[i].split()
            if 'Stream_id:' in audio_list:
                audio_out['no'] = int(audio_list[audio_list.index('Stream_id:') - 1].strip(':')) - 1
            if 'codec_name:' in audio_list:
                audio_out['codec_name'] = audio_list[audio_list.index('codec_name:') + 1].strip(',')
            if 'sample_rate:' in audio_list:
                audio_out['sample_rate'] = int(audio_list[audio_list.index('sample_rate:') + 1])
            if 'bitrate:' in audio_list:
                audio_out['bit_rate'] = int(audio_list[audio_list.index('bitrate:') + 1].strip(','))*1000

            if 'dur:' in audio_list:
                duration_tmp = audio_list[audio_list.index('dur:') + 1].strip(',')
                audio_out['duration'] = mediaCodec_time_code_change(duration_tmp)
            if 'channels:' in audio_list:
                audio_out['channels'] = int(audio_list[audio_list.index('channels:') + 1].strip(','))
            if 'language:' in audio_list:
                audio_out['language'] = str(audio_list[audio_list.index('language:') + 1].strip(','))

            #check audio info
            #duration
            if audio_out.has_key('duration'):
                dur = audio_out['duration'].replace(":","" ).replace("0","").replace(".","")
                if dur == "" :
                    audio_out['duration'] = out_info['duration']

            audio_multi.append( audio_out )

        #get sub info
        sub_multi = []
        sub_info = []
        get_info_flag = 0
        for line in get_info:
            if "sub tracks start" not in line and get_info_flag == 0:
                continue
            get_info_flag = 1
            if "Stream_id:" in line:
                sub_info.append(line)
            if "sub tracks end" in line:
                break

        for i in range(0, len(sub_info)):
            sub_out = {}
            sub_list = sub_info[i].split()
            if 'Stream_id:' in sub_list:
                sub_out['no'] = int(sub_list[sub_list.index('Stream_id:') - 1].strip(':')) - 1
            if 'codec_name:' in sub_list:
                sub_out['codec_name'] = sub_list[sub_list.index('codec_name:') + 1].strip(',')
            if 'width:' in sub_list:
                sub_out['width'] = int(sub_list[sub_list.index('width:') + 1].strip(','))
            if 'height:' in sub_list:
                sub_out['height'] = int(sub_list[sub_list.index('height:') + 1].strip(','))
            if 'language:' in sub_list:
                sub_out['language'] = str(sub_list[sub_list.index('language:') + 1].strip(','))
            sub_multi.append( sub_out )

            #check sub info
            #width, height
            if sub_out.has_key('width'):
                if sub_out['width'] == 0 and len(video_multi):
                    sub_out['width'] = video_multi[0]['width']
            if sub_out.has_key('height'):
                if sub_out['height'] == 0 and len(video_multi):
                    sub_out['height'] = video_multi[0]['height']

        if 0:
            if len(video_multi):
                out_info['Video'] = video_multi[0]
            if len(audio_multi):
                out_info['Audio'] = audio_multi[0]
            if len(sub_multi):
                for i in range(0, len(sub_multi)):
                    if sub_multi[i].has_key('language'):
                        if "chi" in sub_multi[i]['language'].lower() or "chb" in sub_multi[i]['language'].lower() or \
                           "zho" in sub_multi[i]['language'].lower() or "zht" in sub_multi[i]['language'].lower():
                            out_info['Subtitle'] = sub_multi[i]
                            break
                if not out_info.has_key('Subtitle'):
                    out_info['Subtitle'] = sub_multi[0]

        else:
            video_dic = {}
            audio_dic = {}
            sub_dic = {}
            for i in range(0, len( video_multi )):
                video_dic[str(i)] = video_multi[i]
            for i in range(0, len( audio_multi )):
                if audio_multi[i].has_key('channels') and audio_multi[i]['channels'] != 0:
                    audio_dic[str(i)] = audio_multi[i]
            for i in range(0, len( sub_multi )):
                sub_dic[str(i)] = sub_multi[i]

            if len(video_dic) == 0:
                result_error_code = MEDIACODEC_SCAN_PARAM_INPUT_FILE_ERROR
                addlog( " get video info error(no video):\n%s " % result_error_code, logname )
                return result_error_code

            if len(audio_dic) == 0:
                result_error_code = MEDIACODEC_SCAN_PARAM_INPUT_FILE_ERROR
                addlog( " get video info error(no audio):\n%s " % result_error_code, logname )
                return result_error_code

            if len(video_dic):
                out_info['Video'] = video_dic
            if len(audio_dic):
                out_info['Audio'] = audio_dic
            if len(sub_dic):
                out_info['Subtitle'] = sub_dic

    result_error_code["data"] = out_info
    addlog( " get video info:\n%s " % result_error_code, logname )

    return result_error_code

def main():
    parser = OptionParser()
    parser.add_option("-i", "--in", type="string", dest="input", help="input srt file name")
    (options, args) = parser.parse_args()

    #start call function
    crop_flag = 1
    test_logname = "mediainfo.txt"
    scan_result = mediaCodec_scan_param( FFPROBE_SCAN, options.input, crop_flag, test_logname )
    print scan_result
    print 'ok!'

if __name__ == '__main__':
    main()


'''
{
    'data': {
        'file_size': 36850212864,                                     // number
        'duration': '14000000',                                       // string  ms
        'input': '/data/00600.m2ts',                                  // string
        'bitrate': 39696000,                                          // number
        'Video':
            {'no': 0,                                                 // number
             'height': 1080,                                          // number
             'width': 1920,                                           // number
             'display_aspect_ratio': '16:9',                          // string
             'codec_name': 'h264',                                    // string
             'v_crop': '0:0:0:0',                                     // string
             'bit_rate': 39696000,                                    // number   bit_rate
             'duration': ':14000000',                                 // string   duration  ms
             'avg_frame_rate': 23.976,                                // number   avg_frame_rate
             'max_resolution':'720P'                                  // string
            },
        'Audio':
            {'no': 0,                                                 // number
             'duration': '14000000',                                  // string   duration ms
             'bit_rate': 1536000,                                     // number
             'sample_rate': 48000,                                    // number
             'codec_name': 'dts',                                     // string
             'channels': 6                                            // number   channels
            }
        'Subtitle':
            {'width': 1920,                                           // number
             'height': 1080,                                          // number
             'codec_name': 'hdmv_pgs_subtitle',                       // string
             'no': 0                                                  // number
            },
             },
    'error_code': 0,                                                  // number
    'error_msg': 'OK!'                                                // string
}
'''

