# -*- coding: utf8 -*-
import per_title_analysis as pta
import sys

path=str(sys.argv[1])
print ("\nfile=",path)
crf_value=str(sys.argv[2])
print("crf = ",crf_value)
number_of_parts=int(sys.argv[3])
print("number_of_parts=",number_of_parts)
model=str(sys.argv[4])
print("model value 1 for True (linear), 0 for False (for each):", model, "\n\n")

# create your template encoding ladder
PROFILE_LIST = []                     #(self, width, height, bitrate_default, bitrate_min, bitrate_max, required, bitrate_steps_individual)
PROFILE_LIST.append(pta.EncodingProfile(1920, 1080, 4500000, 1000000, 6000000, True, 100000))
PROFILE_LIST.append(pta.EncodingProfile(1280, 720, 3400000, 800000, 5000000, True, 100000))
PROFILE_LIST.append(pta.EncodingProfile(960, 540, 2100000, 600000, 4000000, True, 100000))
PROFILE_LIST.append(pta.EncodingProfile(640, 360, 1100000, 300000, 3000000, True, 100000))
PROFILE_LIST.append(pta.EncodingProfile(480, 270, 750000, 200000, 2000000, False, 100000))
#PROFILE_LIST.append(pta.EncodingProfile(480, 270, 300000, 200000, 2000000, True, 100000))

LADDER = pta.EncodingLadder(PROFILE_LIST)


# Create a new Metric analysis provider
ANALYSIS = pta.CrfAnalyzer(path, LADDER)

# Launch various analysis (here crf)
if model==1:                    #model = linear (True) or for each (False)
    ANALYSIS.process(number_of_parts, 1920, 1080, crf_value, 2, True)
else:
    ANALYSIS.process(number_of_parts, 1920, 1080, crf_value, 2, False)
    ANALYSIS.process(number_of_parts, 1280, 720, crf_value, 2, False)
    ANALYSIS.process(number_of_parts, 960, 540, crf_value, 2, False)
    ANALYSIS.process(number_of_parts, 640, 360, crf_value, 2, False)
    ANALYSIS.process(number_of_parts, 480, 270, crf_value, 2, False)
