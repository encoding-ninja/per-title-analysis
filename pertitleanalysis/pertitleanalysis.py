# -*- coding: utf8 -*-

import os 
import json

from config import EncodingProfile, EncodingLadder
from task import Probe, CrfEncode

class PerTitleAnalysis:
    """This class defines a per title analysis.

    :param input_file_path: The input video file path
    :param encoding_ladder: An EncodingLadder object
    """

    def __init__(self, input_file_path, encoding_ladder):
        """Class constructor"""
        self.input_file_path = input_file_path
        self.encoding_ladder = encoding_ladder
        self.crf_value = 7 # TO DO: make crf_value as an input parameter
        self.idr_interval = 2 # in secondes - TO DO: make idr_interval as an input parameter
        self.number_of_parts = 3 # TO DO: make number_of_parts a parameter

        # init json result
        self.json = {}
        self.json['config'] = {}
        self.json['config']['overall_bitrate_ladder'] = self.encoding_ladder.get_overall_bitrate()
        self.json['config']['encoding_ladder'] = []
        for encoding_profile in self.encoding_ladder.encoding_profile_list:
            profile = {}
            profile['width'] = encoding_profile.width
            profile['height'] = encoding_profile.height
            profile['bitrate'] = encoding_profile.bitrate_default
            profile['constraints'] = {}
            profile['constraints']['bitrate_min'] = encoding_profile.bitrate_min
            profile['constraints']['bitrate_max'] = encoding_profile.bitrate_max
            profile['constraints']['required'] = encoding_profile.required
            self.json['config']['encoding_ladder'].append(profile)
        self.json['analysis'] = []

    def __str__(self):
        """Display the per title analysis informations"""
        return json.dumps(self.json)

    def process(self, method):
        """Do the necessary crf encodings and assessments

        :param method: Can be 'singlepart' or 'multipart'
        """
        # Start by probing the input video file
        input_probe = Probe(self.input_file_path)
        input_probe.execute()

        if method is "singlepart":
            self.number_of_parts = 1
            # Do a CRF encode for the input file
            crf_encode = CrfEncode(self.input_file_path, self.crf_value, self.idr_interval, 0, input_probe.duration)
            crf_encode.execute()

            # Get the Bitrate from the CRF encoded file
            crf_probe = Probe(crf_encode.output_file_path)
            crf_probe.execute()

            # Remove temporary CRF encoded file
            os.remove(crf_encode.output_file_path)

            # Set the optimal bitrate
            self.optimal_bitrate = crf_probe.bitrate
        
        elif method is "multipart":
            optimal_bitrate_list = []

            part_duration = input_probe.duration/self.number_of_parts

            for i in range(0,self.number_of_parts):
                part_start_time = i * part_duration

                # Do a CRF encode for the input file
                crf_encode = CrfEncode(self.input_file_path, self.crf_value, self.idr_interval, part_start_time, part_duration)
                crf_encode.execute()

                # Get the Bitrate from the CRF encoded file
                crf_probe = Probe(crf_encode.output_file_path)
                crf_probe.execute()

                # Remove temporary CRF encoded file
                os.remove(crf_encode.output_file_path)

                # Set the optimal bitrate
                optimal_bitrate_list.append(crf_probe.bitrate)
            
            # Set the optimal bitrate from the average of all crf encoded parts
            self.optimal_bitrate = sum(optimal_bitrate_list)/len(optimal_bitrate_list)

        # Common result formatting
        result = {}
        result['parameters'] = {}
        result['parameters']['method'] = method
        result['parameters']['crf_value'] = self.crf_value
        result['parameters']['idr_interval'] = self.idr_interval
        result['parameters']['number_of_parts'] = self.number_of_parts
        result['optimal_bitrate'] = self.optimal_bitrate
        result['profiles'] = []

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
                profile['bitrate'] = target_bitrate
                result['profiles'].append(profile)
            
        result['overall_bitrate_optimal'] = overall_bitrate_optimal
        result['overall_bitrate_savings'] = self.encoding_ladder.get_overall_bitrate() - overall_bitrate_optimal
        self.json['analysis'].append(result)
