# -*- coding: utf8 -*-
import per_title_analysis as pta
import sys

path=str(sys.argv[1])
metric=str(sys.argv[2])
limit_metric_value=float(sys.argv[3])
print('\nmetric:', metric)
print('limit metric =', limit_metric_value)

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
ANALYSIS = pta.MetricAnalyzer(path, LADDER)

# Launch various analysis (here ssim or psnr)
                #(self, metric, limit_metric, bitrate_steps_by_default, idr_interval, steps_individual_bitrate_required)
ANALYSIS.process(metric, limit_metric_value, 4000000, 2, True)
