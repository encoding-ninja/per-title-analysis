# Per-Title Analysis
This a python package providing tools for optimizing your over-the-top bitrate ladder per each video you need to encode.

Documentation will improve over time!

Dependencies:
You need to have ffmpeg and ffprobe installed on the host which is running the script.

Example:
```
# -*- coding: utf8 -*-

from pertitleanalysis import per_title_analysis as pta

# create your template encoding ladder
PROFILE_LIST = []
PROFILE_LIST.append(pta.EncodingProfile(1920, 1080, 4500000, 2000000, 6000000, True))
PROFILE_LIST.append(pta.EncodingProfile(1280, 720, 3400000, 1300000, 4500000, True))
PROFILE_LIST.append(pta.EncodingProfile(960, 540, 2100000, 700000, 300000, True))
PROFILE_LIST.append(pta.EncodingProfile(640, 360, 1100000, 300000, 2000000, True))
PROFILE_LIST.append(pta.EncodingProfile(480, 270, 750000, 300000, 900000, False))
PROFILE_LIST.append(pta.EncodingProfile(480, 270, 300000, 150000, 500000, True))
LADDER = pta.EncodingLadder(PROFILE_LIST)

# Create a new analysis provider 
ANALYSIS = pta.Analyzer("{{ your_input_file_path }}", LADDER)

# Launch various analysis
ANALYSIS.process(1, 7, 2) # 1 Segment, CRF 7, IDR 2s
ANALYSIS.process(10, 7, 2) # 1O Segments, CRF 7, IDR 2s

# Print results
print(ANALYSIS.get_json())
```