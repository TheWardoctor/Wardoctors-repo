import xbmc,xbmcaddon,xbmcvfs,xbmcgui
import sys
which = sys.argv[1]

ADDON = xbmcaddon.Addon(id='script.tvguide.tardis')

if which == "commands":
    path = xbmc.translatePath('special://home/addons/script.tvguide.tardis/commands.txt')
elif which == "autoplaywith":
    path = xbmc.translatePath('special://home/addons/script.tvguide.tardis/resources/playwith/readme.txt')
f = xbmcvfs.File(path,"rb")
data = f.read()
dialog = xbmcgui.Dialog()
dialog.textviewer('Help', data)
