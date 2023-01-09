#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Radio
# GNU Radio version: 3.10.4.0

from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import soapy




class radio(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Radio", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.volume = volume = 5
        self.freq = freq = 95.7e6
        self.fm_sample = fm_sample = 500e3
        self.audio_rate = audio_rate = 30e6

        ##################################################
        # Blocks
        ##################################################
        self.soapy_hackrf_source_0 = None
        dev = 'driver=hackrf'
        stream_args = ''
        tune_args = ['']
        settings = ['']

        self.soapy_hackrf_source_0 = soapy.source(dev, "fc32", 1, '',
                                  stream_args, tune_args, settings)
        self.soapy_hackrf_source_0.set_sample_rate(0, audio_rate)
        self.soapy_hackrf_source_0.set_bandwidth(0, 0)
        self.soapy_hackrf_source_0.set_frequency(0, freq)
        self.soapy_hackrf_source_0.set_gain(0, 'AMP', False)
        self.soapy_hackrf_source_0.set_gain(0, 'LNA', min(max(16, 0.0), 40.0))
        self.soapy_hackrf_source_0.set_gain(0, 'VGA', min(max(16, 0.0), 62.0))
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
                interpolation=(int(audio_rate/1000)),
                decimation=(int(fm_sample/10000)),
                taps=[],
                fractional_bw=0)
        self.low_pass_filter_0 = filter.fir_filter_ccf(
            (int(audio_rate / fm_sample)),
            firdes.low_pass(
                1,
                audio_rate,
                100e3,
                10e3,
                window.WIN_BLACKMAN,
                6.76))
        self.blocks_multiply_xx_0 = blocks.multiply_vff(1)
        self.audio_sink_0 = audio.sink(int(audio_rate), '', True)
        self.analog_wfm_rcv_0 = analog.wfm_rcv(
        	quad_rate=fm_sample,
        	audio_decimation=10,
        )
        self.analog_const_source_x_0 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, volume)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_const_source_x_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.analog_wfm_rcv_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.audio_sink_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.analog_wfm_rcv_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.soapy_hackrf_source_0, 0), (self.low_pass_filter_0, 0))


    def get_volume(self):
        return self.volume

    def set_volume(self, volume):
        self.volume = volume
        self.analog_const_source_x_0.set_offset(self.volume)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.soapy_hackrf_source_0.set_frequency(0, self.freq)

    def get_fm_sample(self):
        return self.fm_sample

    def set_fm_sample(self, fm_sample):
        self.fm_sample = fm_sample

    def get_audio_rate(self):
        return self.audio_rate

    def set_audio_rate(self, audio_rate):
        self.audio_rate = audio_rate
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.audio_rate, 100e3, 10e3, window.WIN_BLACKMAN, 6.76))
        self.soapy_hackrf_source_0.set_sample_rate(0, self.audio_rate)




def main(top_block_cls=radio, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
