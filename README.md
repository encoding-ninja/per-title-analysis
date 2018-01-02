# Per-Title Analysis
This a python package providing tools for optimizing your over-the-top bitrate ladder per each video you need to encode.

Documentation will improve over time!

Dependencies:
You need to have ffmpeg and ffprobe installed on the host which is running the script.

Example:
```
# -*- coding: utf8 -*-

from pertitleanalysis import per_title_analysis as pta

# create your static encoding ladder
profile_list = []
profile_list.append(pta.EncodingProfile(1920, 1080, 4500000, 2000000, 6000000, True))
profile_list.append(pta.EncodingProfile(1280, 720, 3400000, 1300000, 4500000, True))
profile_list.append(pta.EncodingProfile(960, 540, 2100000, 700000, 300000, True))
profile_list.append(pta.EncodingProfile(640, 360, 1100000, 300000, 2000000, True))
profile_list.append(pta.EncodingProfile(480, 270, 750000, 300000, 900000, False))
profile_list.append(pta.EncodingProfile(480, 270, 300000, 150000, 500000, True))
ladder = pta.EncodingLadder(profile_list)

# Create a new analysis provider 
analysis = pta.Analyzer("{{ your_input_file_path }}", ladder)

# Launch various analysis
analysis.process(1, 3, 2)
analysis.process(1, 7, 2)
analysis.process(10, 7, 2)

# Print results
print(analysis.get_json()) 
```