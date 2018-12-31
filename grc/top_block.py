#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Top Block
# Generated: Mon Dec 31 17:08:57 2018
##################################################

from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser


class top_block(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Top Block")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 200000

        ##################################################
        # Blocks
        ##################################################
        self.blocks_file_source_0_1_0 = blocks.file_source(gr.sizeof_gr_complex*1, '/home/l2zz/phase/result/data', False)
        self.blocks_file_source_0_0 = blocks.file_source(gr.sizeof_gr_complex*1, '/home/l2zz/phase/result/data', False)
        self.blocks_file_sink_1_1 = blocks.file_sink(gr.sizeof_float*1, '/home/l2zz/phase/result/data_amp', False)
        self.blocks_file_sink_1_1.set_unbuffered(False)
        self.blocks_file_sink_1_0 = blocks.file_sink(gr.sizeof_float*1, '/home/l2zz/phase/result/data_phase', False)
        self.blocks_file_sink_1_0.set_unbuffered(False)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)
        self.blocks_complex_to_arg_1_0 = blocks.complex_to_arg(1)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_complex_to_arg_1_0, 0), (self.blocks_file_sink_1_0, 0))    
        self.connect((self.blocks_complex_to_mag_0, 0), (self.blocks_file_sink_1_1, 0))    
        self.connect((self.blocks_file_source_0_0, 0), (self.blocks_complex_to_arg_1_0, 0))    
        self.connect((self.blocks_file_source_0_1_0, 0), (self.blocks_complex_to_mag_0, 0))    

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate


def main(top_block_cls=top_block, options=None):

    tb = top_block_cls()
    tb.start()
    try:
        raw_input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
