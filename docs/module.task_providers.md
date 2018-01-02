Help on module pertitleanalysis.task_providers in pertitleanalysis:

NAME
    pertitleanalysis.task_providers - # -*- coding: utf8 -*-

FILE
    /Users/antoine/Github/per-title-analysis/pertitleanalysis/task_providers.py

CLASSES
    __builtin__.object
        Task
            CrfEncode
            Probe
    
    class CrfEncode(Task)
     |  This class defines a CRF encoding task
     |  
     |  Method resolution order:
     |      CrfEncode
     |      Task
     |      __builtin__.object
     |  
     |  Methods defined here:
     |  
     |  __init__(self, input_file_path, crf_value, idr_interval, part_start_time, part_duration)
     |      CrfEncode initialization
     |      
     |      :param input_file_path: The input video file path
     |      :type input_file_path: str
     |      :param crf_value: The CRF Encoding value for ffmpeg
     |      :type crf_value: int
     |      :param idr_interval: IDR Interval in frames ('None' value is no fix IDR interval needed)
     |      :type idr_interval: int
     |      :param part_start_time: Encode seek start time (in seconds)
     |      :type part_start_time: float
     |      :param part_duration: Encode duration (in seconds)
     |      :type part_duration: float
     |  
     |  execute(self)
     |      Using FFmpeg to CRF Encode a file or part of a file
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from Task:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)
    
    class Probe(Task)
     |  This class defines a Probing task
     |  
     |  Method resolution order:
     |      Probe
     |      Task
     |      __builtin__.object
     |  
     |  Methods defined here:
     |  
     |  __init__(self, input_file_path)
     |      Probe initialization
     |      
     |      :param input_file_path: The input video file path
     |      :type input_file_path: str
     |  
     |  execute(self)
     |      Using FFprobe to get input video file informations
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from Task:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)
    
    class Task(__builtin__.object)
     |  This class defines a processing task
     |  
     |  Methods defined here:
     |  
     |  __init__(self, input_file_path)
     |      Task initialization
     |      
     |      :param input_file_path: The input video file path
     |      :type input_file_path: str
     |  
     |  execute(self, command)
     |      Launch a subprocess task
     |      
     |      :param command: Arguments array for the subprocess task
     |      :type command: str[]
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)


