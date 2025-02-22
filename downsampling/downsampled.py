#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  9 16:32:55 2022

@author: genzel
"""
#import required modules
import os, sys, json
import numpy as np
import pandas as pd
import mdaio 
from scipy import signal
from scipy.signal import butter, lfilter
from timeit import default_timer as timer
from scipy.signal import butter, sosfilt, sosfreqz
import pathlib

#define function for creation of the butterworth filter
def butter_bandpass(lowcut, highcut, fs, order=5):
        nyq = 0.5 * fs #nyquist frequency
        low = lowcut / nyq
        high = highcut / nyq
        sos = butter(order, [low, high], analog=False, btype='band', output='sos')
        return sos

#define function that uses the butterworth filter on the data
def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
        sos = butter_bandpass(lowcut, highcut, fs, order=order)
        y = sosfilt(sos, data)
        return y


def main():
    fe = 30000  # sampling frequency
    fc1 = 1
    fc2 = 300

        #difine begininning and end (in hours) of the recording. 1hr for presleep, 4hrs per postsleep
    if sleep=='presleep':
        win=[0,1] 
    else:
        win=[0,4]
    for directory in list_dir: #loops over the file paths provided
        for filename in os.listdir(directory): #loops over the tetrode files
            f = os.path.join(directory, filename)
            # checking if it is a file
            extension = f[-4:]
            check = f[-14:]
            #print(os.path.isfile(f))
            if os.path.isfile(f):
                start = timer()
                if extension == '.mda' and check != 'timestamps.mda':

                    studyday = filename[25:33]
                    rec = mdaio.readmda(f)
                    rec = rec[:,fe * 3600 * win[0]: fe * 3600 * win[1]]
                    rec = np.transpose(rec).astype(int)
                    recording = pd.DataFrame()
                    for j in range(4):
                        recording1 = butter_bandpass_filter(rec[:, j], fc1, fc2, fe, order=6)
                        q=10
                        down1 = signal.decimate(recording1,q)
                        q=5
                        down1 = signal.decimate(down1,q)
                        ch1 = pd.DataFrame(down1)
                        recording = pd.concat([recording,ch1], axis=1)
                    recording.columns = ['wavech1','wavech2','wavech3','wavech4']
                    recording = recording.to_numpy()
                    recording = recording.transpose()

                    if not os.path.exists(directory+'/StudyDay'+str(studyday)+'/'):
                        os.makedirs(directory+'/StudyDay'+str(studyday)+'/')
                    mdaio.writemda16i(recording,directory+'/StudyDay'+str(studyday)+'/'+filename);
                end = timer()
                print(f'elapsed time: {end - start}')


a=open('files.txt')
b=a.read()
list=b.split()
list_dir=list[1:]
sleep=list[0]

if __name__ == '__main__':
    main()
    
