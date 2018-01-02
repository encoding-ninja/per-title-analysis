# -*- coding: utf8 -*-

import subprocess
import json
import os
import uuid

class Task:
    """This class defines a processing task.

    :param input_file_path: The input video file path
    """

    def __init__(self, input_file_path):
        """Class constructor"""
        self.input_file_path = input_file_path
        # TO DO: Check if file exists

    def process(self, command):
        """Launch subprocess for the task"""
        p = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        self.subprocess_pid = p.pid

        try:
            self.subprocess_out, self.subprocess_err = p.communicate()
        except:
            print(self.subprocess_err)
            # TO DO: error management


class Probe(Task):
    """This class defines a Probe task."""

    def __init__(self, input_file_path):
        """Class constructor"""
        super(Probe, self).__init__(input_file_path)

    def execute(self):
        """Using FFprobe to get input video file informations"""
        command = ['ffprobe',
                '-hide_banner',
                '-i', self.input_file_path,
                '-show_format', '-show_streams', 
                '-print_format', 'json']
        super(Probe, self).process(command)

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
            # TO DO: error management
            pass


class CrfEncode(Task):
    """This class defines a processing task.

    :param input_file_path: The input video file path
    :param crf_value: The CRF Encoding value for ffmpeg
    :param idr_interval: IDR Interval in images ('None' value is no fix IDR interval needed)
    :param part_start_time: Encode seek start time (in seconds)
    :param part_duration: Encode duration (in seconds)
    """

    def __init__(self, input_file_path, crf_value, idr_interval, part_start_time, part_duration):
        """Class constructor"""
        super(CrfEncode, self).__init__(input_file_path)

        self.crf_value = crf_value
        self.idr_interval = idr_interval
        self.part_start_time = part_start_time
        self.part_duration = part_duration

        # Generate a temporary file name for the task output
        self.output_file_path = os.path.join(os.path.dirname(self.input_file_path), 
                                             os.path.splitext(os.path.basename(self.input_file_path))[0] + "_"+uuid.uuid4().hex+".mp4")

    def execute(self):
        """Using FFmpeg to CRF encode"""
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
        super(CrfEncode, self).process(command)
