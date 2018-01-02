# -*- coding: utf8 -*-

import os
import json
import subprocess
import uuid

class Task(object):
    """This class defines a processing task"""

    def __init__(self, input_file_path):
        """Task initialization
        
        :param input_file_path: The input video file path
        :type input_file_path: str
        """
        if os.path.isfile(input_file_path) is True:       
            self.input_file_path = input_file_path
        else:
            raise ValueError('Cannot access the file: {}'.format(input_file_path))

    def execute(self, command):
        """Launch a subprocess task

        :param command: Arguments array for the subprocess task
        :type command: str[]
        """
        p = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        self.subprocess_pid = p.pid

        try:
            self.subprocess_out, self.subprocess_err = p.communicate()
        except:
            print(self.subprocess_err)
            # TODO: error management


class Probe(Task):
    """This class defines a Probing task"""

    def __init__(self, input_file_path):
        """Probe initialization
        
        :param input_file_path: The input video file path
        :type input_file_path: str
        """
        Task.__init__(self, input_file_path)

    def execute(self):
        """Using FFprobe to get input video file informations"""
        command = ['ffprobe',
                '-hide_banner',
                '-i', self.input_file_path,
                '-show_format', '-show_streams', 
                '-print_format', 'json']
        Task.execute(self, command)

        # Parse output data
        try:
            data = json.loads(self.subprocess_out)
            for stream in data['streams']:
                if stream['codec_type'] == 'video':
                    self.width = int(stream['width'])
                    self.height = int(stream['height'])
                    self.bitrate = int(stream['bit_rate'])
                    self.duration = float(stream['duration'])
                    self.video_codec = stream['codec_name']
                    self.framerate = int(stream['r_frame_rate'].replace('/1',''))
        except:
            # TODO: error management
            pass


class CrfEncode(Task):
    """This class defines a CRF encoding task"""

    def __init__(self, input_file_path, crf_value, idr_interval, part_start_time, part_duration):
        """CrfEncode initialization
        
        :param input_file_path: The input video file path
        :type input_file_path: str
        :param crf_value: The CRF Encoding value for ffmpeg
        :type crf_value: int
        :param idr_interval: IDR Interval in frames ('None' value is no fix IDR interval needed)
        :type idr_interval: int
        :param part_start_time: Encode seek start time (in seconds)
        :type part_start_time: float
        :param part_duration: Encode duration (in seconds)
        :type part_duration: float
        """
        Task.__init__(self, input_file_path)

        self.crf_value = crf_value
        self.idr_interval = idr_interval
        self.part_start_time = part_start_time
        self.part_duration = part_duration

        # Generate a temporary file name for the task output
        self.output_file_path = os.path.join(os.path.dirname(self.input_file_path), 
                                             os.path.splitext(os.path.basename(self.input_file_path))[0] + "_"+uuid.uuid4().hex+".mp4")

    def execute(self):
        """Using FFmpeg to CRF Encode a file or part of a file"""
        command = ['ffmpeg',
                '-hide_banner', '-loglevel', 'quiet', '-nostats',
                '-ss', str(self.part_start_time),
                '-i', self.input_file_path,
                '-t', str(self.part_duration),
                '-preset', 'ultrafast', 
                '-an', '-deinterlace',
                '-crf', str(self.crf_value),
                '-pix_fmt', 'yuv420p',
                '-s', '384x216',
                '-y', self.output_file_path]
        Task.execute(self, command)
