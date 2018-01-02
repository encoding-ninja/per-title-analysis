# -*- coding: utf8 -*-

from __future__ import division
import os
import json
import datetime
import statistics

from .task_providers import Probe, CrfEncode


class EncodingProfile(object):
    """This class defines an encoding profile"""

    def __init__(self, width, height, bitrate_default, bitrate_min, bitrate_max, required):
        """EncodingProfile initialization
        
        :param width: Video profile width
        :type width: int
        :param height: Video profile height
        :type height: int
        :param bitrate_default: Video profile bitrate default (in bits per second)
        :type bitrate_default: int
        :param bitrate_min: Video profile bitrate min constraint (in bits per second)
        :type bitrate_min: int
        :param bitrate_max: Video profile bitrate max constraint (in bits per second)
        :type bitrate_max: int
        :param required: The video profile is required and cannot be removed from the optimized encoding ladder
        :type required: bool
        """

        if width is None:
            raise ValueError('The EncodingProfile.width value is required')
        else:
            self.width = int(width)
    
        if height is None:
            raise ValueError('The EncodingProfile.height value is required')
        else:
            self.height = int(height)

        if bitrate_default is None:
            raise ValueError('The EncodingProfile.bitrate_default value is required')
        else:
            self.bitrate_default = int(bitrate_default)
        
        if int(bitrate_min) <= self.bitrate_default:
            self.bitrate_min = int(bitrate_min)
        else:
            self.bitrate_min = self.bitrate_default

        if int(bitrate_max) >= self.bitrate_default:
            self.bitrate_max = int(bitrate_max)
        else:
            self.bitrate_max = self.bitrate_default

        if required is not None:
            self.required = required
        else:
            self.required = True

        self.bitrate_factor = None
    
    def __str__(self):
        """Display the encoding profile informations

        :return: human readable string describing an encoding profil object
        :rtype: str
        """
        return "{}x{}, bitrate_default={}, bitrate_min={}, bitrate_max={}, bitrate_factor={}, required={}".format(self.width, self.height, self.bitrate_default, self.bitrate_min, self.bitrate_max, self.bitrate_factor, self.required)

    def get_json(self):
        """Return object details in json

        :return: json object describing the encoding profile and the configured constraints
        :rtype: str
        """
        profile = {}
        profile['width'] = self.width
        profile['height'] = self.height
        profile['bitrate'] = self.bitrate_default
        profile['constraints'] = {}
        profile['constraints']['bitrate_min'] = self.bitrate_min
        profile['constraints']['bitrate_max'] = self.bitrate_max
        profile['constraints']['bitrate_factor'] = self.bitrate_factor
        profile['constraints']['required'] = self.required
        return json.dumps(profile)

    def set_bitrate_factor(self, ladder_max_bitrate):
        """Set the bitrate factor from the max bitrate in the encoding ladder"""
        self.bitrate_factor = ladder_max_bitrate/self.bitrate_default


class EncodingLadder(object):
    """This class defines an over-the-top encoding ladder template"""

    def __init__(self, encoding_profile_list):
        """EncodingLadder initialization

        :param encoding_profile_list: A list of multiple encoding profiles
        :type encoding_profile_list: per_title.EncodingProfile[]
        """
        self.encoding_profile_list = encoding_profile_list
        self.calculate_bitrate_factors()

    def __str__(self):
        """Display the encoding ladder informations

        :return: human readable string describing the encoding ladder template
        :rtype: str
        """
        string = "{} encoding profiles\n".format(len(self.encoding_profile_list))
        for encoding_profile in self.encoding_profile_list:
            string += str(encoding_profile) + "\n"
        return string
    
    def get_json(self):
        """Return object details in json
        
        :return: json object describing the encoding ladder template
        :rtype: str
        """
        ladder = {}
        ladder['overall_bitrate_ladder'] = self.get_overall_bitrate()
        ladder['encoding_profiles'] = []
        for encoding_profile in self.encoding_profile_list:
            ladder['encoding_profiles'].append(json.loads(encoding_profile.get_json()))
        return json.dumps(ladder)

    def get_max_bitrate(self):
        """Get the max bitrate in the ladder
        
        :return: The maximum bitrate into the encoding laddder template
        :rtype: int
        """
        ladder_max_bitrate = 0
        for encoding_profile in self.encoding_profile_list:
            if encoding_profile.bitrate_default > ladder_max_bitrate:
                ladder_max_bitrate = encoding_profile.bitrate_default
        return ladder_max_bitrate

    def get_overall_bitrate(self):
        """Get the overall bitrate for the ladder
        
        :return: The sum of all bitrate profiles into the encoding laddder template
        :rtype: int
        """
        ladder_overall_bitrate = 0
        for encoding_profile in self.encoding_profile_list:
            ladder_overall_bitrate += encoding_profile.bitrate_default
        return ladder_overall_bitrate

    def calculate_bitrate_factors(self):
        """Calculate the bitrate factor for each profile"""
        ladder_max_bitrate = self.get_max_bitrate()
        for encoding_profile in self.encoding_profile_list:
            encoding_profile.set_bitrate_factor(ladder_max_bitrate)


class Analyzer(object):
    """This class defines a Per-Title Analyzer"""

    def __init__(self, input_file_path, encoding_ladder):
        """Analyzer initialization

        :param input_file_path: The input video file path
        :type input_file_path: str
        :param encoding_ladder: An EncodingLadder object
        :type encoding_ladder: per_title.EncodingLadder
        """
        self.input_file_path = input_file_path
        self.encoding_ladder = encoding_ladder
        
        self.average_bitrate = None
        self.standard_deviation = None
        self.optimal_bitrate = None

        # init json result
        self.json = {}
        self.json['encoding_ladder'] = json.loads(self.encoding_ladder.get_json())
        self.json['analyses'] = []

    def __str__(self):
        """Display the per title analysis informations

        :return: human readable string describing all analyzer configuration
        :rtype: str
        """
        string = "Per-Title Analysis for: {}\n".format(self.input_file_path)
        string += str(self.encoding_ladder)
        return string

    def get_json(self):
        """Return object details in json

        :return: json object describing all inputs configuration and output analyses
        :rtype: str
        """
        return json.dumps(self.json, indent=4, sort_keys=True)

    def process(self, number_of_parts, crf_value, idr_interval):
        """Do the necessary crf encodings and assessments

        :param number_of_parts: Number of part/segment for the analysis
        :type number_of_parts: int
        :param crf_value: Constant Rate Factor: this is a constant quality factor, see ffmpeg.org for more documentation on this parameter
        :type crf_value: int
        :param idr_interval: IDR interval in seconds
        :type idr_interval: int
        """
        # Start by probing the input video file
        input_probe = Probe(self.input_file_path)
        input_probe.execute()

        crf_bitrate_list = []
        part_duration = input_probe.duration/number_of_parts
        idr_interval_frames =  idr_interval*input_probe.framerate

        for i in range(0,number_of_parts):
            part_start_time = i*part_duration

            # Do a CRF encode for the input file
            crf_encode = CrfEncode(self.input_file_path, crf_value, idr_interval_frames, part_start_time, part_duration)
            crf_encode.execute()

            # Get the Bitrate from the CRF encoded file
            crf_probe = Probe(crf_encode.output_file_path)
            crf_probe.execute()

            # Remove temporary CRF encoded file
            os.remove(crf_encode.output_file_path)

            # Set the crf bitrate
            crf_bitrate_list.append(crf_probe.bitrate)
            
        # Calculate the average bitrate for all CRF encodings
        self.average_bitrate = statistics.mean(crf_bitrate_list)

        if number_of_parts > 1:
            # Calculate the the standard deviation of crf bitrate values
            self.standard_deviation = statistics.stdev(crf_bitrate_list)

            weight = 1
            weighted_bitrate_sum = 0
            weighted_bitrate_len = 0

            for bitrate in crf_bitrate_list:
                if bitrate > (self.average_bitrate + 2*self.standard_deviation):
                    weight = 3
                elif bitrate > (self.average_bitrate + self.standard_deviation):
                    weight = 2
                elif bitrate < (self.average_bitrate - self.standard_deviation):
                    weight = 0.5
                elif bitrate < (self.average_bitrate - 2*self.standard_deviation):
                    weight = 0.25
                else:
                    weight = 1

                weighted_bitrate_sum += weight*bitrate
                weighted_bitrate_len += weight

            self.optimal_bitrate = weighted_bitrate_sum/weighted_bitrate_len

        else:
            # Set the optimal bitrate from the average of all crf encoded parts
            self.optimal_bitrate = self.average_bitrate

        # Adding results to json
        result = {}
        result['processing_date'] = str(datetime.datetime.now())
        result['parameters'] = {}
        result['parameters']['crf_value'] = crf_value
        result['parameters']['idr_interval'] = idr_interval
        result['parameters']['number_of_parts'] = number_of_parts
        result['parameters']['part_duration'] = part_duration
        result['optimal_bitrate'] = self.optimal_bitrate
        result['average_bitrate'] = self.average_bitrate
        result['standard_deviation'] = self.standard_deviation
        result['encoding_ladder'] = {}
        result['encoding_ladder']['encoding_profiles'] = []

        overall_bitrate_optimal = 0
        for encoding_profile in self.encoding_ladder.encoding_profile_list:

            target_bitrate = int(self.optimal_bitrate/encoding_profile.bitrate_factor)

            remove_profile = False
            if target_bitrate < encoding_profile.bitrate_min and encoding_profile.required is False:
                remove_profile = True
            
            if target_bitrate < encoding_profile.bitrate_min:
                target_bitrate = encoding_profile.bitrate_min

            if target_bitrate > encoding_profile.bitrate_max:
                target_bitrate = encoding_profile.bitrate_max

            if remove_profile is False:
                overall_bitrate_optimal += target_bitrate
                profile = {}
                profile['width'] = encoding_profile.width
                profile['height'] = encoding_profile.height
                profile['bitrate'] = target_bitrate
                profile['bitrate_savings'] = encoding_profile.bitrate_default - target_bitrate
                result['encoding_ladder']['encoding_profiles'].append(profile)
            
        result['encoding_ladder']['overall_bitrate_ladder'] = overall_bitrate_optimal
        result['encoding_ladder']['overall_bitrate_savings'] = self.encoding_ladder.get_overall_bitrate() - overall_bitrate_optimal
        self.json['analyses'].append(result)
