'''
Created on 2014-07-05

@author: Ray
'''
import os, sys
import logging

#common tools
#exe files
MEDIA_FFMPEG = '/usr/local/mediaCodec/ffmpeg'
MEDIA_FFPROBE = '/usr/local/mediaCodec/ffprobe'
MEDIA_QTFAST = '/usr/local/mediaCodec/qt-faststart'
MEDIA_CUT = '/usr/local/mediaCodec/mediacut'
MEDIA_YAMDI = '/usr/local/mediaCodec/yamdi'
MEDIA_XMLFILE = 'mediaCodec_config.xml'

#platform
WEB_PLATFORM = 1
MOBILE_PLATFORM = 2
HLS_PLATFORM = 4
ALL_PLATFORM = 7

NEW_CUT_TOOLS = 1
CUT_TIME = "10:00:00"
LOGO_SIZEP = "10"

#add log file
def addlog(info,logname):
    logger  = logging.getLogger()
    handler = logging.FileHandler(logname)
    logger.addHandler(handler)
    formatter = logging.Formatter('[%(asctime)s]: %(levelname)s: %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.setLevel(logging.NOTSET)
    logger.info(info)
    logger.removeHandler(handler)

#run cmd function
def run_cmd(cmd, logname):
    addlog( "run cmd: %s\n" % cmd, logname )
    try:
        result = os.system(cmd)
        if result:
            addlog( "run function fail: %s\n" % cmd, logname )
            return result
    except:
        result = 123456
        addlog( "run function exception: %s\n" % cmd, logname )
        sys.exit(-1)
    return result

#error information
SUCCESS = 0                                            #success
ERROR_INPUT_NOEXIST = 1                                #input file do not exist
ERROR_INPUT_VERSION_ID = 2                             #version id not support, only 3 streams now
ERROR_SUBTITLE_NOT_SUPPORT = 3                         #input subtitle not support
ERROR_AUDIO_SCAN_ERROR = 4                             #scan audio volume error
ERROR_GET_PASS1_CMD = 5                                #get pass 1 command line error
ERROR_TRANSCODE_PASS1 = 6                              #run pass 1 command line error
ERROR_GET_PASS2_CMD = 7                                #get pass 2 command line error
ERROR_TRANSCODE_PASS2 = 8                              #run pass 1 command line error
ERROR_MOV_FAST_START = 9                               #move the mp4 start error
ERROR_MP4_TO_M3U8 = 10                                 #mp4 to m3u8 errror
ERROR_MP4_MEDIA_CUT = 11                               #mp4 cut to slice error
ERROR_MP4_TO_FLV = 12                                  #slice mp4 to flv error
ERROR_FLV_TO_F4V = 13                                  #slice flv to f4v error
ERROR_OUTPUT_DURATION = 14                             #output duration get error
ERROR_PARSE_PARAM = 15                                 #scan input error
ERROR_M3U8_IS_NULL = 16                                #m3u8 has no ts
ERROR_INPUT_PARAM_VALID = 17                           #input param is not valid
ERROR_ENCODE_PIC_ERROR = 18                            #encode pic error


#temp file name
ENC_BASE_MP4       = '_base.mp4'
ENC_ASS_NAME       = '_final.ass'
ENC_OUT_M3U8       = '.m3u8'

#log file name
MEDIA_ENC_LOG        = '_enclog.log'
MEDIA_FLOW_LOG       = '_flowlog.log'
MEDIA_TEMP_LOG       = '_temp.log'

