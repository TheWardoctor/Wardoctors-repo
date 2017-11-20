# -*- coding: utf-8 -*-
#
#      Copyright (C) 2012 Tommy Winther
#      http://tommy.winther.nu
#
#      Modified for FTV Guide (09/2014 onwards)
#      by Thomas Geppert [bluezed] - bluezed.apps@gmail.com
#
#      Modified for Stargate Guide (2016)
#      by wardoctor - wardoctor@tardisbuilds.com
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this Program; see the file LICENSE.txt.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#

import sys
import xbmc,xbmcaddon,xbmcvfs
import os
import stat

ADDON = xbmcaddon.Addon(id='script.stargate.guide')

'''
ffmpeg = ADDON.getSetting('autoplaywiths.ffmpeg')
if ffmpeg:
    try:
        st = os.stat(ffmpeg)
        os.chmod(ffmpeg, st.st_mode | stat.S_IEXEC)
    except:
        pass
'''

if len(sys.argv) > 1:
    category = sys.argv[1]
    if category:
        ADDON.setSetting('category',category)

if len(sys.argv) > 2:
    source = ADDON.getSetting('source.source')
    new_source = sys.argv[2]
    if new_source != source:
        ADDON.setSetting('source.source',new_source)

channel = ""
if len(sys.argv) > 3:
    channel = sys.argv[3]
ADDON.setSetting('channel.arg',channel)

assets = [
('special://profile/addon_data/script.stargate.guide/backgrounds/sunburst.png','http://163.172.46.122/files/masterbeta/art/sunburst.png'),
('special://profile/addon_data/script.stargate.guide/backgrounds/charcoal.png','http://163.172.46.122/files/masterbeta/art/charcoal.png'),
]
if ADDON.getAddonInfo('id').endswith('fullscreen'):
    for (dst,src) in assets:
        if not xbmcvfs.exists(dst):
            xbmcvfs.copy(src,dst)

xbmcvfs.copy('special://home/addons/script.stargate.guide/resources/actions.json','special://profile/addon_data/script.stargate.guide/actions.json')

try:
    import gui
    w = gui.TVGuide()
    w.doModal()
    del w

except:
    import sys
    import traceback as tb
    (etype, value, traceback) = sys.exc_info()
    tb.print_exception(etype, value, traceback)