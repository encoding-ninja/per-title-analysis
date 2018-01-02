# per-title-analysis
Analysis provider for adapting your OTT bitrate ladder

Example:
```
# -*- coding: utf8 -*-
from pertitleanalysis import config, pertitleanalysis

# create your static encoding ladder
profile_list = []
profile_list.append(config.EncodingProfile(1920, 1080, 4500000, 2000000, 6000000, True))
profile_list.append(config.EncodingProfile(1280, 720, 3400000, 1300000, 4500000, True))
profile_list.append(config.EncodingProfile(960, 540, 2100000, 700000, 300000, True))
profile_list.append(config.EncodingProfile(640, 360, 1100000, 300000, 2000000, True))
profile_list.append(config.EncodingProfile(480, 270, 750000, 300000, 900000, False))
profile_list.append(config.EncodingProfile(480, 270, 150000, 150000, 150000, True))
ladder = config.EncodingLadder(profile_list)

# Create a new analysis provider 
analysis = pertitleanalysis.Provider(" {{ your_input_file_path }} ", ladder)

# Launch a singlepart analysis
analysis.process('singlepart')

# Launch a multipart analysis
analysis.process('multipart')

# Print results
print(analysis.get_json())
```