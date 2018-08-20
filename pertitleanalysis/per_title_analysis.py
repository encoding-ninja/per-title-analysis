# -*- coding: utf-8 -*-

#importation

from __future__ import division
from pylab import *
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sys
import os
import json
import datetime
import statistics

from task_providers import Probe, CrfEncode, CbrEncode, Metric


#class_1_création des profiles d'encodage ('ici on travaille à l'échelle d'un profil d'encodage)

class EncodingProfile(object):

    def __init__(self, width, height, bitrate_default, bitrate_min, bitrate_max, required, bitrate_steps_by_default):
        #call: PROFILE_LIST.append(pta.EncodingProfile(480, 270, 300000, 150000, 500000, True, 150000))

            self.width = int(width)
            self.height = int(height)
            self.bitrate_default = int(bitrate_default)
            self.bitrate_min = int(bitrate_min)
            self.bitrate_max = int(bitrate_max)
            self.bitrate_factor = None
            self.bitrate_steps_by_default = int(bitrate_steps_by_default)
            if required is not None:
                self.required = required
            else:
                self.required = True

    def set_bitrate_factor(self, ladder_max_bitrate): #fonction utilisée dans le calculate_bitrate_factors
        self.bitrate_factor = ladder_max_bitrate/self.bitrate_default
        #print('the bitrate factor for ',self.width, 'x', self.height, 'is:', self.bitrate_factor)



#class_2_création de l'échelle des profiles d'encodage (ici on travaille à l'échelle de la liste d'ensemble des profiles)

class EncodingLadder(object):

    def __init__(self, encoding_profile_list):
        #call: LADDER = pta.EncodingLadder(PROFILE_LIST)

        self.encoding_profile_list = encoding_profile_list
        self.calculate_bitrate_factors()
        #pour calculer le bitrate_factor on a besoin d'abord d'obtenir le bitrate_default max de la liste encoding_profile_list, ensuite on applique la fonction set_bitrate factor qui
        #pour chaque profile va déterminer le facteur par une simple division.

    def get_max_bitrate(self):
        #parcours la liste des débits dispo et ressort le max parmi les bitrate default !!
        ladder_max_bitrate = 0
        for encoding_profile in self.encoding_profile_list:
            if encoding_profile.bitrate_default > ladder_max_bitrate:
                ladder_max_bitrate = encoding_profile.bitrate_default
        return ladder_max_bitrate

    def get_overall_bitrate(self):

        ladder_overall_bitrate = 0
        for encoding_profile in self.encoding_profile_list:
            ladder_overall_bitrate += encoding_profile.bitrate_default
        return ladder_overall_bitrate

    def calculate_bitrate_factors(self): #cf plus haut !

        ladder_max_bitrate = self.get_max_bitrate()
        for encoding_profile in self.encoding_profile_list:
            encoding_profile.set_bitrate_factor(ladder_max_bitrate)


#class_3_préparation des opérations d'analyse, initialisation des variables

class Analyzer(object):

    def __init__(self, input_file_path, encoding_ladder):


        self.input_file_path = input_file_path
        self.encoding_ladder = encoding_ladder

        self.average_bitrate = None
        self.standard_deviation = None
        self.optimal_bitrate = None
        self.peak_bitrate = None



#class_4_analyse du débit oprimal pour une qualité constante définie, le number of part désigne le nombre de découpage réalisé sur la source pour pouvoir trouver au mieux pour optimiser le débit sur des cas complexes.

class CrfAnalyzer(Analyzer):
    #cette classe s'appuie grandement sur la classe prècèdente donc pas d'init !!! elle est appellé dans le fichier test.py juste deux fois


    def set_bitrate(self,number_of_parts):

        overall_bitrate_optimal = 0 #pour tous les profiles on va réaliser des opérations avec le facteur calculé pour en déduire les débit 'mode linéaire'
        for encoding_profile in self.encoding_ladder.encoding_profile_list:
            #print('encoding profile is : ',encoding_profile.bitrate_default)

            target_bitrate = int(self.optimal_bitrate/encoding_profile.bitrate_factor)
            #print ('target bitrate=',target_bitrate)
            remove_profile = False
            if target_bitrate < encoding_profile.bitrate_min and encoding_profile.required is False:
                remove_profile = True

            # if target_bitrate < encoding_profile.bitrate_min:
            #     target_bitrate = encoding_profile.bitrate_min
            #
            # if target_bitrate > encoding_profile.bitrate_max:
            #     target_bitrate = encoding_profile.bitrate_max

            if remove_profile is False:
                overall_bitrate_optimal += target_bitrate

                print('          ',encoding_profile.width,'x',encoding_profile.height,'                       ',target_bitrate*1e-3,'kbps                          linear',' / nbr part:',number_of_parts,'      ')




    def process(self, number_of_parts, width, height, crf_value, idr_interval, model):

        #première étape je commence par analyser le fichier d'origine
        input_probe = Probe(self.input_file_path) #appel nécessaire à la classe Probe, création d'un objet de type probe
        input_probe.execute()#application de la méthode execute de la classe probe

        crf_bitrate_list = [] #création d'une liste
        part_duration = input_probe.duration/number_of_parts #définition des varibles durée d'une partie à partir du probe
        idr_interval_frames =  idr_interval*input_probe.framerate #rcl: An IDR frame is a special type of I-frame in H.264. An IDR frame specifies that no frame after the IDR frame can reference any frame before it. This makes seeking the H.264 file easier and more responsive in the player.
        #comme j'ai une idr toutes les deux secondes alors connaissant le framerate je peux en déduire le nombre d'images entre deux idr


        for i in range(0,number_of_parts): #la on commence les choses sérieuses
            part_start_time = i*part_duration #on sélectionne le début des extraits à encoder

            crf_encode = CrfEncode(self.input_file_path, width, height, crf_value, idr_interval_frames, part_start_time, part_duration)
            crf_encode.execute() #pour chaque extrait on créé une instance de la classe crfencode et on appelle la methode execute()

            crf_probe = Probe(crf_encode.output_file_path)
            crf_probe.execute() #pour chaque extrait on fait un probe du fichier de sortie de l'encodage, on récupère les valeur grace à la methode execute du probe

            os.remove(crf_encode.output_file_path) # on supprime le fichier

            crf_bitrate_list.append(crf_probe.bitrate) #on ajoute dans la liste qu'on avait créé le bitrate trouvé grace au probe de l'output


        self.average_bitrate = statistics.mean(crf_bitrate_list)
        self.peak_bitrate = max(crf_bitrate_list)

        if number_of_parts > 1:
            self.standard_deviation = statistics.stdev(crf_bitrate_list)

            weight = 1
            weighted_bitrate_sum = 0
            weighted_bitrate_len = 0

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

            self.optimal_bitrate = weighted_bitrate_sum/weighted_bitrate_len

        else:
            self.optimal_bitrate = self.average_bitrate

        if not model:
            print('        ',width,'x',height,'                ',self.optimal_bitrate*1e-3,'kbps                       encode_for_each','/ nbr part:',number_of_parts,'      ')

        if model:
            self.set_bitrate(number_of_parts)


#class_5_en fonction de la métrique choisie

class MetricAnalyzer(Analyzer):

    def process(self, metric, limit_metric, bitrate_steps_by_default, idr_interval, steps_individual_bitrate_required):

        input_probe = Probe(self.input_file_path)
        input_probe.execute()

        part_start_time = 0
        part_duration = input_probe.duration
        idr_interval_frames =  idr_interval*input_probe.framerate
        metric = str(metric).strip().lower()

        #création listes bitrate pour graph 2
        optimal_bitrate_array = []
        default_bitrate_array = []

        print('\n********************************\n********Encoding Started********\n********************************\n')
        print('File Selected: ', os.path.basename(self.input_file_path))

#pour tous les profils on a le process

        for encoding_profile in self.encoding_ladder.encoding_profile_list:

            default_bitrate_array.append(encoding_profile.bitrate_default)

            profile = {}
            profile['width'] = encoding_profile.width
            profile['height'] = encoding_profile.height
            profile['cbr_encodings'] = []
            profile['optimal_bitrate'] = None

            if steps_individual_bitrate_required:
                bitrate_steps_by_default = encoding_profile.bitrate_steps_by_default
            print('\n\n                      __________________________________________')
            print('                          The bitrate_step is: ',bitrate_steps_by_default*10**(-3),'kbps')

            print('\n |||',encoding_profile.width, 'x', encoding_profile.height,'|||\n')
            last_metric_value = 0
            last_quality_step_ratio = 0
            bitrate_array = []
            quality_array = []


#pour chaque profile on a calcul de la qualité sur le range bitrare

            for bitrate in range(encoding_profile.bitrate_min, (encoding_profile.bitrate_max + bitrate_steps_by_default), bitrate_steps_by_default):
                # Do a CRF encode for the input file
                cbr_encode = CbrEncode(self.input_file_path, encoding_profile.width, encoding_profile.height, bitrate, idr_interval_frames, part_start_time, part_duration)
                cbr_encode.execute()
                print('cbr_encode -> in progress -> ->')

                # Get the Bitrate from the CRF encoded file
                metric_assessment = Metric(metric, cbr_encode.output_file_path, self.input_file_path, input_probe.width, input_probe.height)
                metric_assessment.execute()
                print('-> ->  probe       |>', bitrate*10**(-3),'kbps  |>',metric,' = ',metric_assessment.output_value, '\n')

                # Remove temporary CRF encoded file
                os.remove(cbr_encode.output_file_path)

                if last_metric_value is 0 :
                    # for first value, you cannot calculate acurate jump in quality from nothing
                    last_metric_value = metric_assessment.output_value
                    profile['optimal_bitrate'] = bitrate
                    quality_step_ratio = (metric_assessment.output_value)/bitrate # frist step from null to the starting bitrate
                else:
                    quality_step_ratio = (metric_assessment.output_value - last_metric_value)/bitrate_steps_by_default

                if quality_step_ratio >= (last_quality_step_ratio/2):
                    profile['optimal_bitrate'] = bitrate

                #if 'ssim' in metric:
                #    if metric_assessment.output_value >= (last_metric_value + 0.01):
                #        profile['optimal_bitrate'] = bitrate
                #elif 'psnr' in metric:
                #    if metric_assessment.output_value > last_metric_value:
                #        profile['optimal_bitrate'] = bitrate

                last_metric_value = metric_assessment.output_value
                last_quality_step_ratio = quality_step_ratio

                encoding = {}
                encoding['bitrate'] = bitrate
                bitrate_array.append(bitrate) #pour un profile on a trous les bitrate
                #print(bitrate_array)
                quality_array.append(metric_assessment.output_value) #pour un profile on a toutes les qualités
                #print(quality_array)
                encoding['metric_value'] = metric_assessment.output_value
                encoding['quality_step_ratio'] = quality_step_ratio
                profile['cbr_encodings'].append(encoding)


            profile['bitrate_savings'] = encoding_profile.bitrate_default - profile['optimal_bitrate']

            #**************graph matplotlib*************
            #initialisation
            diff_quality_array=0 #ordonnées
            diff_bitrate_array=1 #abscisses
            taux_accroissement=1

            #création de la courbe
            figure(1)
            plot(bitrate_array, quality_array, label=str(encoding_profile.width)+'x'+str(encoding_profile.height))
            xlabel('bitrate (bps)')
            ylabel("quality: "+str(metric).upper())
            title(os.path.basename(self.input_file_path))

            #calcul du taux d'accroissement et recherche du point idéal
            for j in range(0, len(quality_array)-1):
                diff_quality_array=quality_array[j+1]-quality_array[j]
                diff_bitrate_array=bitrate_array[j+1]-bitrate_array[j]

                #limited_evolution_metric=0.005 #à régler, autour 0.1 pour psnr avec 100000 en bitrate step et 0.05 avec 50000 en bitrate step et 0.005 pour ssim
                limited_evolution_metric=limit_metric

                taux_accroissement = diff_quality_array/diff_bitrate_array
                if taux_accroissement <= limited_evolution_metric/bitrate_steps_by_default:
                    #scatter(bitrate_array[j], quality_array[j],s=4) #j'ai trouvé le point
                    break

            #traitement des valeurs trouvées
            print ('\nI found the best values for ||--- ', str(encoding_profile.width)+'x'+str(encoding_profile.height),' ---|| >> ',metric,':',quality_array[j],'| bitrate = ',bitrate_array[j]*10**(-3),'kbps')
            optimal_bitrate_array.append(bitrate_array[j])


            #mise en forme graph for each profile
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
        newpath = '/home/labo/Documents/per_title_analysis/results/%s' % (name)
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        plt.savefig(newpath+"/%s-%s-%s-Per_Title.png" % (name, str(metric).strip().upper(), str(limited_evolution_metric)))

        #print(optimal_bitrate_array)
        #print(default_bitrate_array)
        bitrate_data = [list(i) for i in zip(optimal_bitrate_array, default_bitrate_array)]
        #print(bitrate_data)


        #graph2 computation*******************

        figure(2)
        columns = ('Dynamic (kbps)', 'Fix (kbps)')
        rows = ['%s' % resolution for resolution in ('1920 x 1080', '1280 x 720', '960 x 540', '640 x 360', '480 x 270')]

        ylabel("bitrate (bps)")
        title(os.path.basename(self.input_file_path))

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
        for row in range(n_rows+1): #ca s'arrette à n-1
            plt.bar(index, bitrate_data[n_rows-row], bar_width, bottom=y_offset, color=colors[row])
            y_offset = y_offset + bitrate_data[n_rows-row]
            #print('this is y_offset',y_offset)
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
