# #!/usr/bin/env python
####################################################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
####################################################################################################
# Import From other Modules
####################################################################################################
import sys
import urllib
import xbmcplugin

####################################################################################################
# Import Variables
####################################################################################################
from resources.lib.const import *

####################################################################################################
# Import Modules
####################################################################################################
from resources.lib.common import __log, ReadXML, SoundCloud_Play, YouTubeChannel_Play, \
    YouTubePlaylist_Play, YouTubeUser_Play, Vimeo_Play
from resources.data.menus import MainMenu

####################################################################################################
# Get Paramaters
####################################################################################################
def get_params():
    param = []
    param_string = sys.argv[2]
    __log('Param String - '+str(param_string))
    if len(param_string) >= 2:
        params = sys.argv[2]
        cleaned_params = params.replace('?', '')
        if params[len(params)-1] == '/':
            params = params[0:len(params)-2]
        pairs_of_params = cleaned_params.split('&')
        __log('Pairs of Parama - '+str(pairs_of_params))
        param = {}
        for i in range(len(pairs_of_params)):
            split_params = {}
            split_params = pairs_of_params[i].split('=')
            if len(split_params) == 2:
                param[split_params[0]] = split_params[1]
    return param
params = get_params()
try:
    mode = int(params["mode"])
except:
    mode = None
try:
    name = urllib.unquote_plus(params["name"])
except:
    name = None
try:
    url = urllib.unquote_plus(params["url"])
except:
    url = None

####################################################################################################
# What to Do
####################################################################################################
__log('Mode - '+str(mode))
__log('Name - '+str(name))
__log('URL - '+str(url))
if mode == None or url == None or len(url) < 1: ReadXML('Menus/Video/Video_Main.xml')

####################################################################################################
# Playback Options
####################################################################################################
elif mode == 10: YouTubeUser_Play(url)
elif mode == 11: SoundCloud_Play(url)
elif mode == 12: YouTubePlaylist_Play(url)
elif mode == 13: Vimeo_Play(url)
elif mode == 14: YouTubeChannel_Play(url)

####################################################################################################
# Main Menu
####################################################################################################
MainMenu(mode)

xbmcplugin.endOfDirectory(int(sys.argv[1]))