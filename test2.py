# -*- coding: utf-8 -*-
"""
Created on Mon May 25 16:04:07 2015

@author: luan
"""

from mpegCodec import codec

vdName = '/home/luan/Dropbox/workspace/sublime_projects/TCC_shared/mpeg_versions/videos/akiyo_cif.mp4'
#vdName = './outputs/akiyo_cif.txt'

mpeg = codec.Encoder(vdName, search=1)
mpeg.run()

#mpeg = codec.Decoder(vdName)
#mpeg.run()