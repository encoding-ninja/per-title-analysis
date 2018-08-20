# -*- coding: utf-8 -*-

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

        self.subprocess_pid = None
        self.subprocess_out = None
        self.subprocess_err = None

    def execute(self, command):
        """Launch a subprocess task

        :param command: Arguments array for the subprocess task
        :type command: str[]
        """
        proc = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        self.subprocess_pid = proc.pid

        try:
            self.subprocess_out, self.subprocess_err = proc.communicate()
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

        self.width = None
        self.height = None
        self.bitrate = None
        self.duration = None
        self.video_codec = None
        self.framerate = None

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
            response = self.subprocess_out
            data = json.loads(response.decode('utf-8'))
            for stream in data['streams']:
                if stream['codec_type'] == 'video':
                    self.width = int(stream['width'])
                    #print('the probe',self.width)
                    self.height = int(stream['height'])
                    self.duration = float(stream['duration'])
                    self.video_codec = stream['codec_name']
                    self.framerate = int(stream['r_frame_rate'].replace('/1','')) #c'est quoi ce replace
                    self.bitrate = float(stream['bit_rate'])  #error
                    self.video_codec = stream['codec_name']
                    self.framerate = int(stream['r_frame_rate'].replace('/1','')) #c'est quoi ce replace
        except:

             # TODO: error management
             pass


class CrfEncode(Task):
    """This class defines a CRF encoding task"""

    def __init__(self, input_file_path, width, height, crf_value, idr_interval, part_start_time, part_duration):
        """CrfEncode initialization

        :param input_file_path: The input video file path
        :type input_file_path: str
        :param width: Width of the CRF encode
        :type width: int
        :param height: Height of the CRF encode
        :type height: int
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

        self.definition = str(width)+'x'+str(height)
        self.crf_value = crf_value
        self.idr_interval = idr_interval
        self.part_start_time = part_start_time
        self.part_duration = part_duration

        # Generate a temporary file name for the task output
        self.output_file_path = os.path.join(os.path.dirname(self.input_file_path),
                                             os.path.splitext(os.path.basename(self.input_file_path))[0] + "_"+uuid.uuid4().hex+".mp4")
        # print(self.output_file_path)
        # print(self.part_start_time)
        # print(self.input_file_path)
        # print(self.part_duration)
        # print(self.crf_value)
        # print(self.definition)
        # print(self.idr_interval)

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
                '-s', self.definition,
                '-x264opts', 'keyint=' + str(self.idr_interval),
                '-y', self.output_file_path]
        Task.execute(self, command)


class CbrEncode(Task):
    """This class defines a CBR encoding task"""

    def __init__(self, input_file_path, width, height, cbr_value, idr_interval, part_start_time, part_duration):
        """CrfEncode initialization

        :param input_file_path: The input video file path
        :type input_file_path: str
        :param width: Width of the CBR encode
        :type width: int
        :param height: Height of the CBR encode
        :type height: int
        :param cbr_value: The CBR Encoding value for ffmpeg
        :type cbr_value: int
        :param idr_interval: IDR Interval in frames ('None' value is no fix IDR interval needed)
        :type idr_interval: int
        :param part_start_time: Encode seek start time (in seconds)
        :type part_start_time: float
        :param part_duration: Encode duration (in seconds)
        :type part_duration: float
        """
        Task.__init__(self, input_file_path)

        self.definition = str(width)+'x'+str(height)
        self.cbr_value = cbr_value
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
                '-c:v', 'libx264',
                '-an', '-deinterlace',
                '-b:v', str(self.cbr_value),
                '-pix_fmt', 'yuv420p',
                '-s', self.definition,
                '-x264opts', 'keyint=' + str(self.idr_interval),
                '-y', self.output_file_path]
        Task.execute(self, command)


class Metric(Task):
    """This class defines a Probing task"""

    def __init__(self, metric, input_file_path, ref_file_path, ref_width, ref_height):
        """Probe initialization

        :param metric: Supporting "ssim" or "psnr"
        :type metric: string
        :param input_file_path: The input video file path, the one to be analyzed
        :type input_file_path: str
        :param ref_file_path: The reference video file path
        :type ref_file_path: str

        """
        Task.__init__(self, input_file_path)

        if os.path.isfile(ref_file_path) is True:
            self.ref_file_path = ref_file_path
            self.ref_width = ref_width
            self.ref_height = ref_height
        else:
            raise ValueError('Cannot access the file: {}'.format(ref_file_path))

        available_metrics = ['ssim', 'psnr']
        self.metric = str(metric).strip().lower()
        if self.metric not in available_metrics:
            raise ValueError('Available metrics are "ssim" and "psnr", does not include: {}'.format(metric))

        self.output_value = None

    def execute(self):
        """Using FFmpeg to process metric assessments"""
        command = ['ffmpeg',
                '-hide_banner',
                '-i', self.input_file_path,
                '-i', self.ref_file_path,
                '-lavfi', '[0]scale='+str(self.ref_width)+':'+str(self.ref_height)+'[scaled];[scaled][1]'+str(self.metric)+'=stats_file=-',
                '-f', 'null', '-']
        Task.execute(self, command)

        # Parse output data
        try:
            data = self.subprocess_err.splitlines()
            for line in data:
                line = str(line)
                if 'Parsed_ssim' in line:
                    self.output_value = float(line.split('All:')[1].split('(')[0].strip())
                elif 'Parsed_psnr' in line:
                    self.output_value = float(line.split('average:')[1].split('min:')[0].strip())

        except:
            # TODO: error management
            pass
