import get_data
import numpy as np
import cmath
import math
import sys

PADDING = 0.1 * math.pi
VARIATION_OF_FLUCTUATION_MIN = math.pi - PADDING
VARIATION_OF_FLUCTUATION_MAX = math.pi + PADDING

def detect_start():
    
    return start_point;


def get_phase(file_name, sample_rate, get_period_sec):
    
    src = np.fromfile(open('../result/' + file_name), dtype=np.float32)
     
    #start_point = detect_start()
    start_point = 0
    dump_list = []
    
    #
    # Save first sample and set it to prev_phase
    # prev_phase: variable to save previous phase
    #
    prev_phase = src[start_point]
    if (prev_phase < 0):
        prev_phase += 2 * math.pi
    dump_list.append(prev_phase)

    # Get phase with range [0, 2pi]
    for i in range(start_point + 1, len(src)):
        phase = src[i]
        if (phase < 0):
            phase += 2 * math.pi
        
        # Detect fluctuation caused by ON/OFF
        variation_of_phase = abs(phase - prev_phase)
        if (variation_of_phase > VARIATION_OF_FLUCTUATION_MIN and \
            variation_of_phase < VARIATION_OF_FLUCTUATION_MAX):
                phase -= math.pi
                if (phase < 0):
                    phase += 2 * math.pi

        dump_list.append(phase)
        prev_phase = phase

    dump_list_np = np.asarray(dump_list, dtype=np.float32)
    dump_list_np.tofile('../result/' + file_name + '_modi')

    get_data.get_float_data(file_name + '_modi', sample_rate, get_period_sec)
    

if __name__ == '__main__':

    # Set parameter dynamically
    file_name = sys.argv[1]
    #sample_rate = (float)(sys.argv[2])
    #get_period_sec = (float)(sys.argv[3])

    # Set parameter statically
    #file_name = ''
    sample_rate = 2000000
    get_period_sec = 0.0001

    # Get Phase
    get_phase(file_name, sample_rate, get_period_sec)

