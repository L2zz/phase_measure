import bin_trans
import numpy as np
import math
import csv
import sys
import os

def set_src(file_dest, values, number_of_sample_list):
    
    src_list = []

    for ith_val in range(len(values)):
        for count in range(number_of_sample_list[ith_val]):
            src_list.append(values[ith_val])
   
    src_list_np = np.asarray(src_list, dtype=np.complex64)
    src_list_np.tofile('../result/' + file_dest)     


if __name__ == "__main__":

    #values = [0+1j, -1+0j, 0+-1j, 1+0j]
    values = [-1+0j, 0+-1j, 1+0j, 0+1j]
    #values = [0+-1j, 1+0j, 0+1j, -1+0j]
    #values = [1+0j, 0+1j, -1+0j, 0+-1j]
    number_of_sample_list = [100000, 100000, 100000, 100000]
    sample_rate = 2000000
    get_period_sec = 0.0001

    file_name = sys.argv[1]
    # sample_rate = (float)(sys.argv[1])
    # get_period_sec = (float)(sys.argv[2])

    set_src(file_name, values, number_of_sample_list)
    # bin2float.bin2float_data(file_name, sample_rate, get_period_sec)
