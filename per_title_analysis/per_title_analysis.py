# -*- coding: utf-8 -*-

#importation

from __future__ import division
from pylab import *
import sys
import os
import json
import datetime
import statistics
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from task_providers import Probe, CrfEncode, CbrEncode, Metric



class EncodingProfile(object):
    """This class defines an encoding profile"""


    def __init__(self, width, height, bitrate_default, bitrate_min, bitrate_max, required, bitrate_steps_individual):
        """EncodingProfile initialization

        :param width: Video profile width
        :type width: int
        :param height: Video profile height
        :type height: int
        :param bitrate_default: Video profile bitrate default (in bits per second)
        :type bitrate_default: int
        :param bitrate_min: Video profile bitrate min constraint (in bits per second)
        :type bitrate_min: int
        :param bitrate_max: Video profile bitrate max constraint (in bits per second)
        :type bitrate_max: int
        :param required: The video profile is required and cannot be removed from the optimized encoding ladder
        :type required: bool
        :param bitrate_steps_individual: Step Bitrate Range defined for each Video profile (in bits per second)
        :type bitrate_steps_individual: int
        """
        #call: PROFILE_LIST.append(pta.EncodingProfile(480, 270, 300000, 150000, 500000, True, 150000))


        if width is None:
            raise ValueError('The EncodingProfile.width value is required')
        else:
            self.width = int(width)

        if height is None:
            raise ValueError('The EncodingProfile.height value is required')
        else:
            self.height = int(height)

        if bitrate_default is None:
            raise ValueError('The EncodingProfile.bitrate_default value is required')
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

        if bitrate_steps_individual is None:
            self.bitrate_steps_individual = None
        else:
            self.bitrate_steps_individual = int(bitrate_steps_individual)

        if required is not None:
            self.required = required
        else:
            self.required = True

        self.bitrate_factor = None


    def __str__(self):
        """Display the encoding profile informations
        :return: human readable string describing an encoding profil object
        :rtype: str
        """
        return "{}x{}, bitrate_default={}, bitrate_min={}, bitrate_max={}, bitrate_steps_individual{}, bitrate_factor={}, required={}".format(self.width, self.height, self.bitrate_default, self.bitrate_min, self.bitrate_max, self.bitrate_steps_individual, self.bitrate_factor, self.required)


    def get_json(self):
            """Return object details in json
            :return: json object describing the encoding profile and the configured constraints
            :rtype: str
            """
            profile = {}
            profile['width'] = self.width
            profile['height'] = self.height
            profile['bitrate'] = self.bitrate_default
            profile['constraints'] = {}
            profile['constraints']['bitrate_min'] = self.bitrate_min
            profile['constraints']['bitrate_max'] = self.bitrate_max
            profile['constraints']['bitrate_factor'] = self.bitrate_factor
            profile['constraints']['required'] = self.required
            return json.dumps(profile)


    def set_bitrate_factor(self, ladder_max_bitrate):
        """Set the bitrate factor from the max bitrate in the encoding ladder"""
        self.bitrate_factor = ladder_max_bitrate/self.bitrate_default




class EncodingLadder(object):
    """This class defines an over-the-top encoding ladder template"""


    def __init__(self, encoding_profile_list):
        """EncodingLadder initialization

        :param encoding_profile_list: A list of multiple encoding profiles
        :type encoding_profile_list: per_title.EncodingProfile[]
        """
        #call: LADDER = pta.EncodingLadder(PROFILE_LIST)

        self.encoding_profile_list = encoding_profile_list
        self.calculate_bitrate_factors()


    def __str__(self):
        """Display the encoding ladder informations
        :return: human readable string describing the encoding ladder template
        :rtype: str
        """
        string = "{} encoding profiles\n".format(len(self.encoding_profile_list))
        for encoding_profile in self.encoding_profile_list:
            string += str(encoding_profile) + "\n"
        return string


    def get_json(self):
        """Return object details in json
        :return: json object describing the encoding ladder template
        :rtype: str
        """
        ladder = {}
        ladder['overall_bitrate_ladder'] = self.get_overall_bitrate()
        ladder['encoding_profiles'] = []
        for encoding_profile in self.encoding_profile_list:
            ladder['encoding_profiles'].append(json.loads(encoding_profile.get_json()))
        return json.dumps(ladder)


    def get_max_bitrate(self):
        """Get the max bitrate in the ladder
        :return: The maximum bitrate into the encoding laddder template
        :rtype: int
        """
        ladder_max_bitrate = 0
        for encoding_profile in self.encoding_profile_list:
            if encoding_profile.bitrate_default > ladder_max_bitrate:
                ladder_max_bitrate = encoding_profile.bitrate_default
        return ladder_max_bitrate

    def get_overall_bitrate(self):
        """Get the overall bitrate for the ladder
        :return: The sum of all bitrate profiles into the encoding laddder template
        :rtype: int
        """
        ladder_overall_bitrate = 0
        for encoding_profile in self.encoding_profile_list:
            ladder_overall_bitrate += encoding_profile.bitrate_default
        return ladder_overall_bitrate

    def calculate_bitrate_factors(self): #cf plus haut !
        """Calculate the bitrate factor for each profile"""
        ladder_max_bitrate = self.get_max_bitrate()
        for encoding_profile in self.encoding_profile_list:
            encoding_profile.set_bitrate_factor(ladder_max_bitrate)



class Analyzer(object):
    """This class defines a Per-Title Analyzer"""

    def __init__(self, input_file_path, encoding_ladder):
        """Analyzer initialization
        :param input_file_path: The input video file path
        :type input_file_path: str
        :param encoding_ladder: An EncodingLadder object
        :type encoding_ladder: per_title.EncodingLadder
        """
        self.input_file_path = input_file_path
        self.encoding_ladder = encoding_ladder

        self.average_bitrate = None
        self.standard_deviation = None
        self.optimal_bitrate = None
        self.peak_bitrate = None

        # init json result
        self.json = {}
        self.json['input_file_path'] = self.input_file_path
        self.json['template_encoding_ladder'] = json.loads(self.encoding_ladder.get_json())
        self.json['analyses'] = []


    def __str__(self):
        """Display the per title analysis informations
        :return: human readable string describing all analyzer configuration
        :rtype: str
        """
        string = "Per-Title Analysis for: {}\n".format(self.input_file_path)
        string += str(self.encoding_ladder)
        return string

    def get_json(self):
        """Return object details in json
        :return: json object describing all inputs configuration and output analyses
        :rtype: str
        """
        return json.dumps(self.json, indent=4, sort_keys=True)



class CrfAnalyzer(Analyzer):
    """This class defines a Per-Title Analyzer based on calculating the top bitrate wit CRF, then deducting the ladder"""


    def set_bitrate(self,number_of_parts):
        """In linear mode, optimal_bitrates are defined from the first analysis thanks to the bitrate_factor
        : print results in linear mode for CRF analyzer
        """

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

            print('          ',encoding_profile.width,'x',encoding_profile.height,'                       ',target_bitrate*1e-3,'kbps                          linear',' / nbr part:',number_of_parts,'      ')


    def process(self, number_of_parts, width, height, crf_value, idr_interval, model):
        """Do the necessary crf encodings and assessments
        :param number_of_parts: Number of part/segment for the analysis
        :type number_of_parts: int
        :param width: Width of the CRF encode
        :type width: int
        :param height: Height of the CRF encode
        :type height: int
        :param crf_value: Constant Rate Factor: this is a constant quality factor, see ffmpeg.org for more documentation on this parameter
        :type crf_value: int
        :param idr_interval: IDR interval in seconds
        :type idr_interval: int
        :param model: linear (True) or for each (False)
        :type model: bool
        """

        # Start by probing the input video file
        input_probe = Probe(self.input_file_path)
        input_probe.execute()

        crf_bitrate_list = []
        part_duration = input_probe.duration/number_of_parts
        idr_interval_frames =  idr_interval*input_probe.framerate #rcl: An IDR frame is a special type of I-frame in H.264. An IDR frame specifies that no frame after the IDR frame can reference any frame before it. This makes seeking the H.264 file easier and more responsive in the player.
        #As I have an IDR_FRAME every 2 seconds, I can find out the number of frame between two IDR using framerate !

        # Start Analysis
        for i in range(0,number_of_parts):
            part_start_time = i*part_duration #select extracts to encode

            # Do a CRF encode for the input file
            crf_encode = CrfEncode(self.input_file_path, width, height, crf_value, idr_interval_frames, part_start_time, part_duration)
            crf_encode.execute()

            # Get the Bitrate from the CRF encoded file
            crf_probe = Probe(crf_encode.output_file_path)
            crf_probe.execute()

            # Remove temporary CRF encoded file
            os.remove(crf_encode.output_file_path)

            # Set the crf bitrate
            crf_bitrate_list.append(crf_probe.bitrate)

        # Calculate the average bitrate for all CRF encodings
        self.average_bitrate = statistics.mean(crf_bitrate_list)
        self.peak_bitrate = max(crf_bitrate_list)

        if number_of_parts > 1:
            # Calculate the the standard deviation of crf bitrate values
            self.standard_deviation = statistics.stdev(crf_bitrate_list)

            weight = 1
            weighted_bitrate_sum = 0
            weighted_bitrate_len = 0

            # Giving weight for each bitrate based on the standard deviation
            for bitrate in crf_bitrate_list:
                if bitrate > (self.average_bitrate + self.standard_deviation):
                    weight = 4
                elif bitrate > (self.average_bitrate + self.standard_deviation/2):
                    weight = 2
                elif bitrate < (self.average_bitrate - self.standard_deviation/2):
                    weight = 0.5
                elif bitrate < (self.average_bitrate - self.standard_deviation):
                    weight = 0
                else:
                    weight = 1

                weighted_bitrate_sum += weight*bitrate
                weighted_bitrate_len += weight

            # Set the optimal bitrate from the weighted bitrate of all crf encoded parts
            self.optimal_bitrate = weighted_bitrate_sum/weighted_bitrate_len

        else:
            # Set the optimal bitrate from the only one crf result
            self.optimal_bitrate = self.average_bitrate

        if not model:
            print('        ',width,'x',height,'                ',self.optimal_bitrate*1e-3,'kbps                       encode_for_each','/ nbr part:',number_of_parts,'      ')

        if model:
            # We calculate optimal bitrate of the the remaining profiles using bitrate factor
            self.set_bitrate(number_of_parts)

        # Adding results to json
        result = {}
        result['processing_date'] = str(datetime.datetime.now())
        result['parameters'] = {}
        result['parameters']['method'] = "CRF"
        result['parameters']['width'] = width
        result['parameters']['height'] = height
        result['parameters']['crf_value'] = crf_value
        result['parameters']['idr_interval'] = idr_interval
        result['parameters']['number_of_parts'] = number_of_parts
        result['parameters']['part_duration'] = part_duration
        result['bitrate'] = {}
        result['bitrate']['optimal'] = self.optimal_bitrate
        result['bitrate']['average'] = self.average_bitrate
        result['bitrate']['peak'] = self.average_bitrate
        result['bitrate']['standard_deviation'] = self.standard_deviation
        result['optimized_encoding_ladder'] = {}
        if model == "True":
            result['optimized_encoding_ladder']['model'] = "linear"
        if model == "False":
            result['optimized_encoding_ladder']['model'] = "encode_for_each"

        self.json['analyses'].append(result)


class MetricAnalyzer(Analyzer):
    """This class defines a Per-Title Analyzer based on VQ Metric and Multiple bitrate encodes"""

    def process(self, metric, limit_metric, bitrate_steps_by_default, idr_interval, steps_individual_bitrate_required):
        """Do the necessary encodings and quality metric assessments
        :param metric: Supporting "ssim" or "psnr"
        :type metric: string
        :param limit_metric: limit value of "ssim" or "psnr" use to find optimal bitrate
        :type limit_metric: int
        :param bitrate_steps_by_default: Bitrate gap between every encoding, only use if steps_individual_bitrate_required is False
        :type bitrate_steps_by_default: int
        :param idr_interval: IDR interval in seconds
        :type idr_interval: int
        :param steps_individual_bitrate_required: The step is the same for each profile and cannot be set individually if False
        :type steps_individual_bitrate_required: bool
        """

        # Start by probing the input video file
        input_probe = Probe(self.input_file_path)
        input_probe.execute()

        part_start_time = 0
        part_duration = input_probe.duration
        idr_interval_frames =  idr_interval*input_probe.framerate
        metric = str(metric).strip().lower()

        #Create two lists for GRAPH 2
        optimal_bitrate_array = []
        default_bitrate_array = []

        print('\n********************************\n********Encoding Started********\n********************************\n')
        print('File Selected: ', os.path.basename(self.input_file_path))

        # Adding results to json
        json_ouput = {}
        json_ouput['processing_date'] = str(datetime.datetime.now())
        json_ouput['parameters'] = {}
        json_ouput['parameters']['method'] = "Metric"
        json_ouput['parameters']['metric'] = metric
        json_ouput['parameters']['bitrate_steps'] = bitrate_steps_by_default
        json_ouput['parameters']['idr_interval'] = idr_interval
        json_ouput['parameters']['number_of_parts'] = 1
        json_ouput['parameters']['part_duration'] = part_duration
        json_ouput['optimized_encoding_ladder'] = {}
        json_ouput['optimized_encoding_ladder']['encoding_profiles'] = []


        # Start Analysis
        for encoding_profile in self.encoding_ladder.encoding_profile_list:

            profile = {}
            profile['width'] = encoding_profile.width
            profile['height'] = encoding_profile.height
            profile['cbr_encodings'] = []
            profile['optimal_bitrate'] = None

            default_bitrate_array.append(encoding_profile.bitrate_default)

            if steps_individual_bitrate_required:
                bitrate_steps_by_default = encoding_profile.bitrate_steps_individual
            print('\n\n                      __________________________________________')
            print('                          The bitrate_step is: ',bitrate_steps_by_default*10**(-3),'kbps')
            print('\n |||',encoding_profile.width, 'x', encoding_profile.height,'|||\n')

            last_metric_value = 0
            last_quality_step_ratio = 0
            bitrate_array = []
            quality_array = []


            for bitrate in range(encoding_profile.bitrate_min, (encoding_profile.bitrate_max + bitrate_steps_by_default), bitrate_steps_by_default):
                # Do a CBR encode for the input file
                cbr_encode = CbrEncode(self.input_file_path, encoding_profile.width, encoding_profile.height, bitrate, idr_interval_frames, part_start_time, part_duration)
                cbr_encode.execute()
                print('cbr_encode -> in progress -> ->')

                # Get the Bitrate from the CBR encoded file
                metric_assessment = Metric(metric, cbr_encode.output_file_path, self.input_file_path, input_probe.width, input_probe.height)
                metric_assessment.execute()
                print('-> ->  probe       |>', bitrate*10**(-3),'kbps  |>',metric,' = ',metric_assessment.output_value, '\n')

                # Remove temporary CBR encoded file
                os.remove(cbr_encode.output_file_path)


                # OLD method to find optimal bitrate_min

                # if last_metric_value is 0 :
                #     # for first value, you cannot calculate acurate jump in quality from nothing
                #     last_metric_value = metric_assessment.output_value
                #     profile['optimal_bitrate'] = bitrate
                #     quality_step_ratio = (metric_assessment.output_value)/bitrate # first step from null to the starting bitrate
                # else:
                #     quality_step_ratio = (metric_assessment.output_value - last_metric_value)/bitrate_steps_by_default
                #
                # if quality_step_ratio >= (last_quality_step_ratio/2):
                #     profile['optimal_bitrate'] = bitrate

                # if 'ssim' in metric:
                #     if metric_assessment.output_value >= (last_metric_value + 0.01):
                #         profile['optimal_bitrate'] = bitrate
                # elif 'psnr' in metric:
                #     if metric_assessment.output_value > last_metric_value:
                #         profile['optimal_bitrate'] = bitrate

                # last_metric_value = metric_assessment.output_value
                # last_quality_step_ratio = quality_step_ratio

                # New method
                bitrate_array.append(bitrate) # All bitrate for one profile
                print(bitrate_array)
                quality_array.append(metric_assessment.output_value) #pour un profile on a toutes les qualités
                print(quality_array)


            #**************GRAPH 1 matplotlib*************
            # Initialize
            diff_bitrate_array=1 # X
            diff_quality_array=0 # Y
            taux_accroissement=1

            #Curve
            figure(1)
            plot(bitrate_array, quality_array, label=str(encoding_profile.width)+'x'+str(encoding_profile.height))
            xlabel('bitrate (bps)')
            ylabel("quality: "+str(metric).upper())
            title(str(self.input_file_path))

            # Rate of change and find out the optimal bitrate in the array
            for j in range(0, len(quality_array)-1):
                diff_quality_array=quality_array[j+1]-quality_array[j]
                diff_bitrate_array=bitrate_array[j+1]-bitrate_array[j]

                #limited_evolution_metric=0.005 -> indication: set arround 0.1 for psnr with a 100000 bps bitrate step and 0.05 with a 50000 bitrate step for ssim
                limited_evolution_metric=limit_metric

                taux_accroissement = diff_quality_array/diff_bitrate_array

                encoding = {}
                encoding['bitrate'] = bitrate_array[j]
                encoding['metric_value'] = quality_array[j]
                encoding['quality_step_ratio'] = taux_accroissement
                profile['cbr_encodings'].append(encoding)

                if taux_accroissement <= limited_evolution_metric/bitrate_steps_by_default:
                    #scatter(bitrate_array[j], quality_array[j]) # I found out the good point
                    break

            # Display good values !
            print ('\nI found the best values for ||--- ', str(encoding_profile.width)+'x'+str(encoding_profile.height),' ---|| >> ',metric,':',quality_array[j],'| bitrate = ',bitrate_array[j]*10**(-3),'kbps')
            optimal_bitrate_array.append(bitrate_array[j]) # use in GRAPH 2
            profile['optimal_bitrate'] = bitrate_array[j]
            profile['bitrate_savings'] = encoding_profile.bitrate_default - profile['optimal_bitrate']

            # Graph annotations
            annotation=str(bitrate_array[j]*1e-3)+' kbps'
            #plot([bitrate_array[j],bitrate_array[j]], [0, quality_array[j]], linestyle='--' )
            annotate(annotation, xy=(bitrate_array[j], quality_array[j]), xycoords='data', xytext=(+1, +20), textcoords='offset points', fontsize=8, arrowprops=dict(arrowstyle="->", connectionstyle="arc,rad=0.2"))
            #plot([0, bitrate_array[j]], [quality_array[j], quality_array[j]], linestyle='--' )
            scatter(bitrate_array[j], quality_array[j], s=7)
            grid()
            legend()
            draw()
            show(block=False)
            pause(0.001)


        #save graph1 and plot graph2
        name=str(os.path.basename(self.input_file_path))
        input("\n\n\nPress [enter] to continue, This will close the graphic and save the figure as ''file_name_metric_limit_metric.png'' !")
        newpath = str(os.getcwd())+"/results/%s" % (name)
        #newpath = '/home/labo/Documents/per_title_analysis/results/%s' % (name)
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        plt.savefig(newpath+"/%s-%s-%s-Per_Title.png" % (name, str(metric).strip().upper(), str(limited_evolution_metric)))

        bitrate_data = [list(i) for i in zip(optimal_bitrate_array, default_bitrate_array)]

        # GRAH 2 Computation
        figure(2)
        columns = ('Dynamic (kbps)', 'Fix (kbps)')
        rows = ['%s' % resolution for resolution in ('1920 x 1080', '1280 x 720', '960 x 540', '640 x 360', '480 x 270')]

        ylabel("bitrate (bps)")
        title(str(self.input_file_path))

        # Get some pastel shades for the colors
        colors = plt.cm.YlOrBr(np.linspace(0.35, 0.8, len(rows)))
        #size and positions
        n_rows = len(bitrate_data)-1
        index = np.arange(len(columns)) + 0.3
        bar_width = 0.5

        # Initialize the vertical-offset for the stacked bar chart.
        y_offset = np.zeros(len(columns))

        # Plot bars and create text labels for the table
        cell_text = []
        for row in range(n_rows+1): # until n_rows
            plt.bar(index, bitrate_data[n_rows-row], bar_width, bottom=y_offset, color=colors[row])
            y_offset = y_offset + bitrate_data[n_rows-row]
            print('this is y_offset',y_offset)
            cell_text.append(['%1.1f' % (x / 1000.0) for x in bitrate_data[n_rows-row]])
        # Reverse colors and text labels to display the last value at the top.
        colors = colors[::-1]
        cell_text.reverse()


        # Add a table at the bottom of the axes
        the_table = plt.table(cellText=cell_text,
                              rowLabels=rows,
                              rowColours=colors,
                              colLabels=columns,
                              loc='bottom')

        # Adjust layout to make room for the table:
        plt.subplots_adjust(left=0.5, bottom=0.2)

        #plt.ylabel("Loss in ${0}'s".format(value_increment))
        #plt.yticks(values * value_increment, ['%d' % val for val in values])
        plt.xticks([])
        #plt.title('Loss by Disaster')

        show(block=False)
        pause(0.001)
        print('\n\n->->\nloading graphic Histogram\n->->\n\n')
        input("Press [enter] to continue, This will close the graphic and save the figure as ''file_name_metric_limit_metric.png'' ")
        plt.savefig(newpath+"/%s-%s-%s-Per_Title_Histogram.png" % (name, str(metric).strip().upper(), str(limited_evolution_metric)))
        print('\n\n\n************ALL DONE********** !\n\n')
