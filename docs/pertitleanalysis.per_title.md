Help on module pertitleanalysis.per_title in pertitleanalysis:

NAME
    pertitleanalysis.per_title - # -*- coding: utf8 -*-

FILE
    /Users/antoine/Github/per-title-analysis/pertitleanalysis/per_title.py

CLASSES
    __builtin__.object
        Analyzer
        EncodingLadder
        EncodingProfile
    
    class Analyzer(__builtin__.object)
     |  This class defines a Per-Title Analyzer
     |  
     |  Methods defined here:
     |  
     |  __init__(self, input_file_path, encoding_ladder)
     |      Analyzer initialization
     |      
     |      :param input_file_path: The input video file path
     |      :type input_file_path: str
     |      :param encoding_ladder: An EncodingLadder object
     |      :type encoding_ladder: per_title.EncodingLadder
     |  
     |  __str__(self)
     |      Display the per title analysis informations
     |      
     |      :return: human readable string describing all analyzer configuration
     |      :rtype: str
     |  
     |  get_json(self)
     |      Return object details in json
     |      
     |      :return: json object describing all inputs configuration and output analyses
     |      :rtype: str
     |  
     |  process(self, number_of_parts, crf_value, idr_interval)
     |      Do the necessary crf encodings and assessments
     |      
     |      :param number_of_parts: Number of part/segment for the analysis
     |      :type number_of_parts: int
     |      :param crf_value: Constant Rate Factor: this is a constant quality factor, see ffmpeg.org for more documentation on this parameter
     |      :type crf_value: int
     |      :param idr_interval: IDR interval in seconds
     |      :type idr_interval: int
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)
    
    class EncodingLadder(__builtin__.object)
     |  This class defines an over-the-top encoding ladder template
     |  
     |  Methods defined here:
     |  
     |  __init__(self, encoding_profile_list)
     |      EncodingLadder initialization
     |      
     |      :param encoding_profile_list: A list of multiple encoding profiles
     |      :type encoding_profile_list: per_title.EncodingProfile[]
     |  
     |  __str__(self)
     |      Display the encoding ladder informations
     |      
     |      :return: human readable string describing the encoding ladder template
     |      :rtype: str
     |  
     |  calculate_bitrate_factors(self)
     |      Calculate the bitrate factor for each profile
     |  
     |  get_json(self)
     |      Return object details in json
     |      
     |      :return: json object describing the encoding ladder template
     |      :rtype: str
     |  
     |  get_max_bitrate(self)
     |      Get the max bitrate in the ladder
     |      
     |      :return: The maximum bitrate into the encoding laddder template
     |      :rtype: int
     |  
     |  get_overall_bitrate(self)
     |      Get the overall bitrate for the ladder
     |      
     |      :return: The sum of all bitrate profiles into the encoding laddder template
     |      :rtype: int
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)
    
    class EncodingProfile(__builtin__.object)
     |  This class defines an encoding profile
     |  
     |  Methods defined here:
     |  
     |  __init__(self, width, height, bitrate_default, bitrate_min, bitrate_max, required)
     |      EncodingProfile initialization
     |      
     |      :param width: Video profile width
     |      :type width: int
     |      :param height: Video profile height
     |      :type height: int
     |      :param bitrate_default: Video profile bitrate default (in bits per second)
     |      :type bitrate_default: int
     |      :param bitrate_min: Video profile bitrate min constraint (in bits per second)
     |      :type bitrate_min: int
     |      :param bitrate_max: Video profile bitrate max constraint (in bits per second)
     |      :type bitrate_max: int
     |      :param required: The video profile is required and cannot be removed from the optimized encoding ladder
     |      :type required: bool
     |  
     |  __str__(self)
     |      Display the encoding profile informations
     |      
     |      :return: human readable string describing an encoding profil object
     |      :rtype: str
     |  
     |  get_json(self)
     |      Return object details in json
     |      
     |      :return: json object describing the encoding profile and the configured constraints
     |      :rtype: str
     |  
     |  set_bitrate_factor(self, ladder_max_bitrate)
     |      Set the bitrate factor from the max bitrate in the encoding ladder
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)


