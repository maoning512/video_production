#!/usr/bin/python
# -*- coding: utf8 -*-

'''
Created on 2014-07-06
Author: Ray
Brief:
    scan audio volume
usage:
    python mediaCodec_audiogain.py -i test.mp4

function:
    return audio volume infomation

'''

import sys
import os
import commands, string
from optparse import OptionParser
sys.path.append("..")
import mediabase

DEBUG = 0

MEDIACODEC_AUDIO_VOLUME_TH = -20

#error code
MEDIACODEC_SCAN_VOLUME_OK               =  {"error_code": 0, "error_msg": "OK!" }
MEDIACODEC_SCAN_VOLUME_INPUT_ERROR      =  {"error_code": 1, "error_msg": "input cmd error!" }
MEDIACODEC_SCAN_VOLUME_INPUT_FILE_ERROR =  {"error_code": 2, "error_msg": "input file error!" }

def mediaCodec_scan_volume( ffmpeg_input, input_name, param, logname ):
    '''scan volume'''
    mediabase.addlog("python mediaCodec_audiogain.py -i %s" % input_name, logname)

    result_error_code = MEDIACODEC_SCAN_VOLUME_OK

    #step1: check input
    if input_name != None:
        input_file = input_name
    else:
        mediabase.addlog("need input file!\n", logname)
        result_error_code = MEDIACODEC_SCAN_VOLUME_INPUT_ERROR
        return result_error_code

    if not os.path.exists(ffmpeg_input):
        mediabase.addlog("  encoder does not exist", logname)
        result_error_code = MEDIACODEC_SCAN_VOLUME_INPUT_ERROR
        return result_error_code
    elif not os.path.exists(input_file):
        mediabase.addlog("  input file not exist:%s\n" % input_file, logname)
        result_error_code = MEDIACODEC_SCAN_VOLUME_INPUT_FILE_ERROR
        return result_error_code
    else:
        if param.has_key("aid") and param["aid"] != "":  #has audio map
            audio_map = str(param["aid"]).strip()
            scan_cmd = ffmpeg_input +  " -i %s -map 0:a:%s -af volumedetect -f null - " % ( input_file, audio_map )
            mediabase.addlog( "get audio volume info cmd:\n%s " % scan_cmd, logname )
            result = commands.getstatusoutput(scan_cmd)
            if result[0] != 0:
                mediabase.addlog( "call function error: %s\n " % scan_cmd, logname )
                result_error_code = MEDIACODEC_SCAN_VOLUME_INPUT_FILE_ERROR
                return result_error_code

            mean_volume_line = []
            max_volume_line = []
            log_line = result[1].splitlines()

            for line in log_line:
                if "volumedetect" in line and "mean_volume" in line:
                    mean_volume_line = line
                if "volumedetect" in line and "max_volume" in line:
                    max_volume_line = line

            if len(mean_volume_line) == 0:
                mediabase.addlog( "get audio volume error:mean!", logname )
                result_error_code = MEDIACODEC_SCAN_VOLUME_INPUT_FILE_ERROR
                mediabase.addlog( "get audio volume info:\n%s " % result_error_code, logname )
                return result_error_code
            if len(max_volume_line) == 0:
                mediabase.addlog( "get audio volume error:max! " )
                result_error_code = MEDIACODEC_SCAN_VOLUME_INPUT_FILE_ERROR
                mediabase.addlog( "get audio volume info:\n%s " % result_error_code, logname )
                return result_error_code

            if DEBUG:
                print mean_volume_line
                print max_volume_line
                print ""

            mean_list = mean_volume_line.split()
            max_list  = max_volume_line.split()

            if "mean_volume:" in mean_list:
                temp_db = mean_list[mean_list.index("mean_volume:") + 1].strip()
                if "-" in temp_db:
                    result_error_code["mean_db"] = -string.atof(temp_db.strip("-"))
                else:
                    result_error_code["mean_db"] = string.atof(temp_db.strip())

                if result_error_code.has_key("mean_db"):
                    result_error_code["adjust_db"] = str(MEDIACODEC_AUDIO_VOLUME_TH - result_error_code["mean_db"]) + "dB"
            if "max_volume:" in max_list:
                temp_db = max_list[max_list.index("max_volume:") + 1].strip()
                if "-" in temp_db:
                    result_error_code["max_db"] = -string.atof(temp_db.strip("-"))
                else:
                    result_error_code["max_db"] = string.atof(temp_db.strip())

    mediabase.addlog( "get audio volume info:\n%s " % result_error_code, logname )

    return result_error_code


def main():
    parser = OptionParser()
    parser.add_option("-i", "--in", type="string", dest="input", help="input file name")

    (options, args) = parser.parse_args()

    #start call function
    test_param = {'input': 'video.mp4', 'aid':"0", 'bitrate': 505000}
    test_logname = "audiogain_log.txt"

    scan_result = mediaCodec_scan_volume( mediabase.MEDIA_FFMPEG, options.input, test_param, test_logname )
    print scan_result
    print 'ok!'

if __name__ == '__main__':
    main()


