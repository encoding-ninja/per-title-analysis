# -*- coding: utf8 -*-

import json

class EncodingProfile:
    """This class defines an encoding profile.

    :param width: Video profile width
    :param height: Video profile height
    :param bitrate_default: Video profile bitrate default (in bits per second)
    :param bitrate_min: Video profile bitrate min constraint (in bits per second)
    :param bitrate_max: Video profile bitrate max constraint (in bits per second)
    :param required: The video profile is required and cannot be removed from the optimized encoding ladder
    """

    def __init__(self, width, height, bitrate_default, bitrate_min, bitrate_max, required):
        """Class constructor"""

        if width is None:
            raise ValueError
        else:
            self.width = int(width)
    
        if height is None:
            raise ValueError
        else:
            self.height = int(height)

        if bitrate_default is None:
            raise ValueError
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
        """Display the encoding profile informations"""
        return "{}x{}, bitrate_default={}, bitrate_min={}, bitrate_max={}, bitrate_factor={}, required={}".format(self.width, self.height, self.bitrate_default, self.bitrate_min, self.bitrate_max, self.bitrate_factor, self.required)
        
    def set_bitrate_factor(self, ladder_max_bitrate):
        """Set the bitrate factor from the max bitrate in the encoding ladder"""
        self.bitrate_factor = ladder_max_bitrate/self.bitrate_default

    def get_json(self):
        """Return object details in json"""
        profile = {}
        profile['width'] = self.width
        profile['height'] = self.height
        profile['bitrate'] = self.bitrate_default
        profile['constraints'] = {}
        profile['constraints']['bitrate_min'] = self.bitrate_min
        profile['constraints']['bitrate_max'] = self.bitrate_max
        profile['constraints']['required'] = self.required
        return json.dumps(profile)


class EncodingLadder:
    """This class defines an over-the-top encoding ladder.

    :param encoding_profile_list: A list of multiple encoding profiles
    """

    def __init__(self, encoding_profile_list):
        """Class constructor"""
        self.encoding_profile_list = encoding_profile_list
        self.calculate_bitrate_factors()

    def __str__(self):
        """Display the encoding ladder informations"""
        string = "{} encoding profiles\n".format(len(self.encoding_profile_list))
        for encoding_profile in self.encoding_profile_list:
            string += str(encoding_profile) + "\n"
        return string

    def get_max_bitrate(self):
        """Get the max bitrate in the ladder"""
        ladder_max_bitrate = 0
        for encoding_profile in self.encoding_profile_list:
            if encoding_profile.bitrate_default > ladder_max_bitrate:
                ladder_max_bitrate = encoding_profile.bitrate_default
        return ladder_max_bitrate

    def get_overall_bitrate(self):
        """Get the overall bitrate for the ladder"""
        ladder_overall_bitrate = 0
        for encoding_profile in self.encoding_profile_list:
            ladder_overall_bitrate += encoding_profile.bitrate_default
        return ladder_overall_bitrate

    def calculate_bitrate_factors(self):
        """Calculate the bitrate factor for each profile"""
        ladder_max_bitrate = self.get_max_bitrate()
        for encoding_profile in self.encoding_profile_list:
            encoding_profile.set_bitrate_factor(ladder_max_bitrate)

    def get_json(self):
        """Return object details in json"""
        ladder = {}
        ladder['overall_bitrate_ladder'] = self.get_overall_bitrate()
        ladder['encoding_profiles'] = []
        for encoding_profile in self.encoding_profile_list:
            ladder['encoding_profiles'].append(json.loads(encoding_profile.get_json()))
        return json.dumps(ladder)
    

