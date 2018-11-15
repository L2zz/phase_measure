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
        sample_unit = (int)(sample_rate * get_period_sec)
        avg += src[i]
        if ((i % sample_unit) == 0):
            if (i != 0):
                avg /= sample_unit
            time_pass = (float)(i / sample_rate)
            csv_wr.writerow([avg])
            txt_file.write('%5.3f(s)> %6.3f\n'%(time_pass, avg))
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

    for i in range(len(src)):
        sample_unit = (int)(sample_rate * get_period_sec)
        if((i % sample_unit) == 0):
            time_pass = (float)(i / sample_rate)
            real = np.real(src[i])
            imag = np.imag(src[i])
            csv_wr.writerow([real, imag])
            txt_file.write('%5.3f(s)> real: %6.3f \t\timag: %6.3f\n' \
                            %(time_pass, real, imag))

def get_degree(file_name):

    # Set source file's location
    src = open('../csv/' + file_name + '.csv', 'r', encoding='utf-8')
    rdr = csv.reader(src)

    # Set data file's location to save
    dest = open('../csv/' + file_name + '_deg.csv', 'w', newline='')
    wr = csv.writer(dest, delimiter=',')

    for line in rdr:
        wr.writerow([math.radians(line)])

    src.close()
    dest.close()

if __name__ == '__main__':

    # Set parameter dynamically
    file_name = sys.argv[1]
    # sample_rate = (float)(sys.argv[2])
    # get_period_sec = (float)(sys.argv[3])


    # Set parameter statically
    # file_name = ''
    sample_rate = 10000000
    get_period_sec = 0.001

    # Get datas
    # get_float_data(file_name, sample_rate, get_period_sec)
    get_complex_data(file_name, sample_rate, get_period_sec)
    get_degree(file_name)
    # get_float_data(file_name + '_amp', sample_rate, get_period_sec)
    # get_float_data(file_name + '_phase', sample_rate, get_period_sec)



