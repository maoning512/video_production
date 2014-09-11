#!/usr/bin/python
# -*- coding: utf8 -*-

'''
Created on 2014-07-08
Author: Ray
Brief:
    srt to ass, output utf8
usage:
    python mediaCodec_srt2ass.py -i test.srt -o output.ass

function:
(1)change srt to ass file
(2)check whether utf8 coded character set, if not changed to utf8;
(3)reorder the ass text with time;
(4)check the start and stop time, warning if not valid!
'''

import chardet
import codecs
import sys
import os
import re
from optparse import OptionParser
sys.path.append("..")
import mediabase

#error code
MEDIACODEC_SRT2ASS_OK               =  {"error_code": 0, "error_msg": "OK!" }
MEDIACODEC_SRT2ASS_INPUT_ERROR      =  {"error_code": 1, "error_msg": "input cmd error!" }
MEDIACODEC_SRT2ASS_INPUT_FILE_ERROR =  {"error_code": 2, "error_msg": "input file error!" }
MEDIACODEC_SRT2ASS_INPUT_NOTSUPPORT =  {"error_code": 3, "error_msg": "input file not support!" }

def srt2ass( input_name, output_name, logname ):
    ''''''
    mediabase.addlog(" python mediaCodec_srt2ass.py -i %s -o %s\n" % (input_name, output_name), logname)
    result_error_code = MEDIACODEC_SRT2ASS_OK

    #step1: check input
    if input_name != None:
        input_file = input_name
    else:
        print " python mediaCodec_srt2ass.py -i input -o output "
        mediabase.addlog("   need input file", logname)
        result_error_code = MEDIACODEC_SRT2ASS_INPUT_ERROR
        return result_error_code

    if output_name != None:
        output_file = output_name
    else:
        print " python mediaCodec_srt2ass.py -i input -o output "
        mediabase.addlog("   need output file", logname)
        result_error_code = MEDIACODEC_SRT2ASS_INPUT_ERROR
        return result_error_code

    if not os.path.isfile (input_name):
        mediabase.addlog("  input file not exist: %s" % input_name, logname )
        result_error_code = MEDIACODEC_SRT2ASS_INPUT_FILE_ERROR
        return result_error_code

    if ".ass" not in input_file and ".ASS" not in input_file and ".srt" not in input_file and ".SRT" not in input_file:
        mediabase.addlog("   input file not support: %s!" % input_file, logname)
        result_error_code = MEDIACODEC_SRT2ASS_INPUT_NOTSUPPORT
        return result_error_code

    mediabase.addlog("   Process start: %s" % input_name, logname )

    #step2: change to utf8
    try:
        fp_input  = open(input_file,"r")
    except:
        mediabase.addlog("open input file error!", logname)
        result_error_code = MEDIACODEC_SRT2ASS_INPUT_FILE_ERROR
        return result_error_code

    orig_content = fp_input.read()

    try:
        fp_input.close()
    except:
        mediabase.addlog("close input file error!", logname)
        result_error_code = MEDIACODEC_SRT2ASS_INPUT_FILE_ERROR
        return result_error_code

    detect_type = chardet.detect(orig_content)['encoding']
    mediabase.addlog( "   input code   : %s " % detect_type, logname )

    encode_type = ['GB2312', 'GBK', 'GB18030']
    if detect_type in encode_type:
        for i in range(0,3):
            tmp_type = encode_type[i]
            try:
                sub_origin = orig_content.decode( tmp_type )
                mediabase.addlog("   detect type  : %s OK!" % tmp_type, logname )
                break
            except:
                mediabase.addlog("   detect type  : %s not right!" % tmp_type, logname )
                if i < 2:
                    continue
                else:
                    mediabase.addlog("   input file not support!", logname)
                    result_error_code = MEDIACODEC_SRT2ASS_INPUT_NOTSUPPORT
                    return result_error_code
    else:
        try:
            sub_origin = orig_content.decode( chardet.detect(orig_content)['encoding'] )
        except:
            mediabase.addlog("   input file not support!", logname)
            result_error_code = MEDIACODEC_SRT2ASS_INPUT_NOTSUPPORT
            return result_error_code

    sub_utf8 = sub_origin.encode('utf8')

    if sub_utf8[:3] == codecs.BOM_UTF8:
        sub_utf8 = sub_utf8[3:]

    mediabase.addlog( "   output code  : %s " % chardet.detect(sub_utf8)['encoding'], logname )

    #step3: srt to ass
    #step3.1: if srt or ass, just copy
    if ".ass" not in input_file and ".ASS" not in input_file and ".srt" not in input_file and ".SRT" not in input_file:
        mediabase.addlog("   input file not support: %s!" % input_file, logname)
        result_error_code = MEDIACODEC_SRT2ASS_INPUT_NOTSUPPORT
        return result_error_code
    else:
        #step3.2: srt or ass
        #step3.2.1: generate header
        final_content = []
        final_content.append( "[Script Info]\n" )
        final_content.append( "ScriptType: v4.00+\n" )
        final_content.append( "Title:\n" )
        final_content.append( "Original Script:\n" )
        final_content.append( "Synch Point:0\n" )
        final_content.append( "Collisions:Normal\n" )
        final_content.append( "PlayResX:1280\n" )
        final_content.append( "PlayResY:720\n" )
        final_content.append( "\n" )
        final_content.append( "[V4+ Styles]\n" )
        final_content.append( "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n" )
        final_content.append( "Style: Default,Microsoft YaHei,50,&H00FFFFFF,&HF0000000,&H00000000,&HF0000000,-1,0,0,0,100,100,0,0.00,1,2,0,2,30,30,10,134\n" )
        final_content.append( "\n" )
        final_content.append( "[Events]\n" )
#        final_content.append( "Format: Layer, Start, End, Style, Actor, MarginL, MarginR, MarginV, Effect, Text\n" )
        final_content.append( "Format: Layer, Start, End, Style, Text\n" )

        sub_list = sub_utf8.splitlines()

        #step3.2.2: ass
        if ".ass" in input_file or ".ASS" in input_file:
            mediabase.addlog( "   input is ass: changed header and copy!", logname )

            #check every line
            ass_list = []
            srt_line_num = 0
            for line in sub_list:
                srt_line_num = srt_line_num + 1
                line = line.strip()

                if re.search(r'Dialogue:', line) and re.search(r'Default', line):
                    ass_list.append( line + '\n' );
                    split_text = re.split( ',', line )
                    time_start = split_text[1]
                    time_stop  = split_text[2]
                    if time_start > time_stop:
                        mediabase.addlog( "  sub_warning timecode line [%d]: %s " %( srt_line_num, line ), logname )

            #sort subtitle
            ass_list.sort()
            final_content = final_content + ass_list

        else:
            mediabase.addlog( "   input is srt: changed to ass!", logname )
            #step3.2.3: srt
            #change every line
            ass_list = []
            line_num = 0
            srt_line_num = 0
            line_content=''
            srt_idx = 0
            for line in sub_list:
                srt_line_num = srt_line_num + 1
                line = line.strip()

                if str(line).isdigit():
                    if srt_idx != 0:
                        ass_list.append( line_content + '\n' )
                        srt_idx = 0
                    line_content='Dialogue: 0,'
                    continue
                elif line.strip() == '':
                    continue
                elif "-->" in line and ":" in line:  #parse time code
                    line_num = line_num + 1
                    time_list = line.split("-->")
                    if "," in time_list[0] and "," in time_list[1]:
                        time_start_list = time_list[0].split(",")
                        time_stop_list = time_list[1].split(",")
                        time_start = time_start_list[0].strip()[1:] + '.' + time_start_list[1].strip()[:2]
                        time_stop  = time_stop_list[0].strip()[1:] + '.' + time_stop_list[1].strip()[:2]
                    else:
                        mediabase.addlog( "   cur line time code invalid: %s" % line, logname )
                        time_start = "0:00:00.00"
                        time_stop  = "0:00:00.00"

                    if time_start > time_stop:
                        mediabase.addlog( "  sub_warning timecode line [%d]: %s " %( line_num, line ), logname )

                    line_content = line_content + time_start + ',' + time_stop + ',Default,'
                else:  #add subtitle
                    if srt_idx > 0:
                        line_content = line_content + ' \N ' + line
                    else:
                        line_content = line_content + line
                    srt_idx = srt_idx + 1

            #add last subtitle
            if srt_idx != 0:
                ass_list.append( line_content + '\n' )

            #sort subtitle
            ass_list.sort()
            final_content = final_content + ass_list

        #step3.4: output
        try:
            fp_output  = open(output_file,"w")
        except:
            mediabase.addlog( "open output file error!", logname )
            result_error_code = MEDIACODEC_SRT2ASS_INPUT_FILE_ERROR
            return result_error_code

        for element in final_content:
            fp_output.write( element )

        try:
            fp_output.close()
        except:
            mediabase.addlog( "close input file error!", logname )
            result_error_code = MEDIACODEC_SRT2ASS_INPUT_FILE_ERROR
            return result_error_code

    mediabase.addlog( "   trans over!", logname )
    return result_error_code

def main():
    parser = OptionParser()
    parser.add_option("-i", "--in", type="string", dest="input", help="input srt file name")
    parser.add_option("-o", "--out", type="string", dest="output", help="output ass file name")

    (options, args) = parser.parse_args()

    #start call function
    test_logname = "srt2ass_log.txt"
    srt2ass_result = srt2ass( options.input, options.output, test_logname )
    print srt2ass_result
    print "ok!"

if __name__ == '__main__':
    main()

