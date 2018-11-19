import cmath
import math
import sys
import enum
import numpy as np
import convert_data

FLUCTUATION_PADDING = 0.1 * math.pi
VARIATION_OF_FLUCTUATION_MIN = math.pi - FLUCTUATION_PADDING
VARIATION_OF_FLUCTUATION_MAX = math.pi + FLUCTUATION_PADDING

START_SIGNAL_PADDING = 0.2
VARIATION_OF_START_SIGNAL_MIN = 0.4 - START_SIGNAL_PADDING
VARIATION_OF_START_SIGNAL_MAX = 0.4 + START_SIGNAL_PADDING

BEGIN_CUT_OFF = 0.1
START_POINT = 0

#
# Signal State flows READY -> DOWN -> UP -> START
# 
#       ** -------  DOWN  ------  START  **
#           READY |______|  UP  |_______
#
class SignalState(enum.Enum):

    READY = 0
    DOWN = 1
    UP = 2
    START = 3

#
# Get start point(sample index) of signal
#
def detect_start(file_name, sample_rate):
    
    global START_POINT

    # Set source file's location
    src = np.fromfile(open('../result/' + file_name), dtype=np.complex64)
    cut_off_samples = (int)(BEGIN_CUT_OFF * sample_rate)
    
    # Set start_flag to READY
    # Set prev_amp using sample after cutting off 
    state = SignalState.READY
    prev_amp = abs(src[cut_off_samples])
    for i in range(cut_off_samples + 1, len(src)):
        amp = abs(src[i])      
        variation_of_amp = abs(amp - prev_amp)

        # If the variation of amplitude is larger than threshold 
        if (variation_of_amp > (VARIATION_OF_START_SIGNAL_MIN * amp) and \
            variation_of_amp < (VARIATION_OF_START_SIGNAL_MAX * amp)):
            # Check the signal's state and move it to next state
            if (state is SignalState.READY):
                state = SignalState.DOWN
            elif (state is SignalState.DOWN):
                state = SignalState.UP
            elif (state is SignalState.UP):
                state = SignalState.START 
        prev_amp = amp
        
        # If the state is START, then return start_point
        if (state is SignalState.START):
            START_POINT = i
    
    # Fail to detect start point
    # Set start point to cut off point
    START_POINT = cut_off_samples

#
# Make binary/csv/txt files to save amplitude
# File format: (file_name)_amp, (file_name)_amp.csv, (file_name)_amp.txt
#
def get_amp(file_name, sample_rate, get_period_sec):
    
    global START_POINT

    # Set source file's location
    src = np.fromfile(open('../result/' + file_name), dtype=np.complex64)
    
    # Get amplitude
    amp_list = []
    for i in range(START_POINT, len(src)):
        amp = abs(src[i])
        amp_list.append(amp)

    # Make binary file
    amp_list_np = np.asarray(amp_list, dtype=np.float32)
    amp_list_np.tofile('../result/' + file_name + '_amp')

    # Make csv, txt files
    convert_data.convert_bin2float(file_name + '_amp', sample_rate, get_period_sec)
     

#
# Make binary/csv/txt files to save [0, 2pi] phase
# File format: (file_name)_phase, (file_name)_phase.csv, (file_name)_phase.txt
#
def get_phase(file_name, sample_rate, get_period_sec):
    
    global START_POINT

    # Set source file's location
    src = np.fromfile(open('../result/' + file_name), dtype=np.complex64)
    
    # Save first sample and set it to prev_phase
    phase_list = []
    prev_phase = cmath.phase(src[START_POINT])
    if (prev_phase < 0):
        prev_phase += 2 * math.pi
    phase_list.append(prev_phase)

    # Get phase with range [0, 2pi]
    for i in range(START_POINT + 1, len(src)):
        phase = cmath.phase(src[i])
        if (phase < 0):
            phase += 2 * math.pi
        
        # Detect fluctuation caused by ON/OFF
        variation_of_phase = abs(phase - prev_phase)
        if (variation_of_phase > VARIATION_OF_FLUCTUATION_MIN and \
            variation_of_phase < VARIATION_OF_FLUCTUATION_MAX):
                phase -= math.pi
                if (phase < 0):
                    phase += 2 * math.pi

        phase_list.append(phase)
        prev_phase = phase

    # Make binary file
    phase_list_np = np.asarray(phase_list, dtype=np.float32)
    phase_list_np.tofile('../result/' + file_name + '_phase')

    # Make csv, txt files
    convert_data.convert_bin2float(file_name + '_phase', sample_rate, get_period_sec)

#
# Call get_amp & get_phase to get amplitude & phase
# 
def get_data(file_name, sample_rate, get_period_sec):
    
    global START_POINT

    detect_start(file_name, sample_rate)
    print(START_POINT)
    get_amp(file_name, sample_rate, get_period_sec)
    get_phase(file_name, sample_rate, get_period_sec)


if __name__ == '__main__':

    # Set parameter dynamically
    #file_name = sys.argv[1]
    #sample_rate = (float)(sys.argv[2])
    #get_period_sec = (float)(sys.argv[3])

    # Set parameter statically
    file_name = 'data'
    sample_rate = 2000000
    get_period_sec = 0.0001

    # Get Data
    get_data(file_name, sample_rate, get_period_sec)

