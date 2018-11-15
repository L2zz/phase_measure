import numpy as np 
import math
import csv
import sys

def get_float_data(file_name, sample_rate, get_period_sec):
    
    # Set source file's location
    src = np.fromfile(open('../result/' + file_name), dtype=np.float32)

    # Set data file's location to save
    csv_file = open('../csv/' + file_name + '.csv', 'w', newline='')
    csv_wr = csv.writer(csv_file, delimiter=',')

    txt_file = open('../txt/' + file_name + '.txt', 'w')
    
    avg = 0.0
    for i in range(len(src)):
        
        # sample_unit: number of samples in period
        sample_unit = (int)(sample_rate * get_period_sec)
        
        # shift range [-pi, pi] to [0, 2pi]
        if (src[i] > 0):
            instant = src[i]
        else:
            instant = src[i] + 2 * math.pi
        
        #instant = src[i]
        avg += instant
        
        if ((i % sample_unit) == 0):
            if (i != 0):
                avg /= sample_unit
            time_pass = (float)(i / sample_rate)
            
            csv_wr.writerow([instant, avg])
            txt_file.write('%5.4f(s)> instant: %6.3f\n'%(time_pass, instant))
            txt_file.write('%5.4f(s)> avg: %10.3f\n\n'%(time_pass, avg))
            avg = 0.0
    
    csv_file.close()
    txt_file.close()


def get_complex_data(file_name, sample_rate, get_period_sec):

    # Set source file's location
    src = np.fromfile(open('../result/' + file_name), dtype=np.complex64)

    # Set  data file's location to save
    csv_file = open('../csv/' + file_name + '.csv', 'w', newline='')
    csv_wr = csv.writer(csv_file, delimiter=',')

    txt_file = open('../txt/' + file_name + '.txt', 'w')

    real_avg = 0.0
    imag_avg = 0.0
    for i in range(len(src)):
        
        # sample_unit: number of samples in period
        sample_unit = (int)(sample_rate * get_period_sec)
        real = np.real(src[i])
        imag = np.imag(src[i])
        real_avg += real
        imag_avg += imag

        if((i % sample_unit) == 0):
            if (i != 0):
                real_avg /= sample_unit
                imag_avg /= sample_unit
            
            time_pass = (float)(i / sample_rate)
            
            csv_wr.writerow([real, imag, real_avg, imag_avg])
            txt_file.write('%5.3f(s)> real: %10.3f \t\timag: %6.3f\n' \
                            %(time_pass, real, imag))
            txt_file.write('%5.3f(s)> real_avg: %6.3f \t\timag_avg: %6.3f\n\n' \
                            %(time_pass, real_avg, imag_avg))
            real_avg = 0.0
            imag_avg = 0.0

    csv_file.close()
    txt_file.close()


def get_degree(file_name):

    # Set source file's location
    src = open('../csv/' + file_name + '_phase.csv', 'r', encoding='utf-8')
    rdr = csv.reader(src)

    # Set data file's location to save
    dest = open('../csv/' + file_name + '_deg.csv', 'w', newline='')
    wr = csv.writer(dest, delimiter=',')

    r_dest = open('../csv/' + file_name + '_rldeg.csv', 'w', newline='')
    rwr = csv.writer(r_dest, delimiter=',')
    
    # To get vartiation of degree
    prev_instant_deg = 0.0
    prev_avg_deg = 0.0
    for line in rdr:
        instant = float(line[0])
        avg = float(line[1])
        instant_deg = math.degrees(instant)
        avg_deg = math.degrees(avg)
        
        wr.writerow([instant_deg, avg_deg])
        rwr.writerow([instant_deg - prev_instant_deg, avg_deg - prev_avg_deg])
        prev_instant_deg = instant_deg
        prev_avg_deg = avg_deg

    src.close()
    dest.close()
    r_dest.close()


if __name__ == '__main__':

    # Set parameter dynamically
    file_name = sys.argv[1]
    #sample_rate = (float)(sys.argv[2])
    #get_period_sec = (float)(sys.argv[3])


    # Set parameter statically
    #file_name = ''
    sample_rate = 2000000
    get_period_sec = 0.0001

    # Get datas
    #get_complex_data(file_name, sample_rate, get_period_sec)
    #get_float_data(file_name + '_phase', sample_rate, get_period_sec)
    #get_degree(file_name)
    get_complex_data('11.15_test/' + file_name, sample_rate, get_period_sec)
    get_float_data('11.15_test/' + file_name + '_phase', sample_rate, get_period_sec)
    get_degree('11.15_test/' + file_name)


