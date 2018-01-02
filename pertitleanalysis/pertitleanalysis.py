# -*- coding: utf8 -*-

import os 

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

    def __str__(self):
        """Display the per title analysis informations"""
        string = "Per-Title Analysis for: {}\n".format(self.input_file_path)
        string += str(self.encoding_ladder)
        return string

    def process(self):
        """Do the necessary crf encodings and assessments"""
        # Start by probing the input video file
        input_probe = Probe(self.input_file_path)
        input_probe.execute()

        # Do a CRF encode for the input file
        crf_encode = CrfEncode(self.input_file_path, self.crf_value, self.idr_interval, None, None)
        crf_encode.execute()

        # Get the Bitrate from the CRF encoded file
        crf_probe = Probe(crf_encode.output_file_path)
        crf_probe.execute()

        # Remove temporary CRF encoded file
        os.remove(crf_encode.output_file_path)

        # Set the optimal bitrate
        self.optimal_bitrate = crf_probe.bitrate

    def get_optimized_ladder(self):
        """Get the optimized encoding ladder"""
        print("Raw optimisation for the encoding ladder:")
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
                print("{}x{}, bitrate={}".format(encoding_profile.width, encoding_profile.height, target_bitrate))
