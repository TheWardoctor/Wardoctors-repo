#plugin.video.addons.ini.player 0.0.3 as a base
from xbmcswift2 import Plugin
from xbmcswift2 import actions
import xbmc,xbmcaddon,xbmcvfs,xbmcgui
import re
import requests
import random
from datetime import datetime,timedelta
import time
import HTMLParser
import xbmcplugin
import os
from types import *
import json

try: from main_ini import ADDONID
except ImportError: ADDONID = 'script.tvguide.tardis.skin.awesome'   # set this to your skin addonid
#
try: from main_ini import ADDONID_CORE
except ImportError: ADDONID_CORE  = 'script.tvguide.tardis'       # set this to your dest addonid
#
PLAYER_ADDONS_INI    = xbmc.translatePath(os.path.join('special://home', 'userdata', 'addon_data', ADDONID_CORE, 'addons.ini'))
PLAYER_CHANNELS_INI  = xbmc.translatePath(os.path.join('special://home', 'userdata', 'addon_data', ADDONID_CORE, 'channels.ini'))
PLAYER_CHANNELS_SET  = xbmc.translatePath(os.path.join('special://home', 'userdata', 'addon_data', ADDONID, '.storage', 'channels'))


plugin = Plugin()
big_list_view = False

def log2(v):
    xbmc.log(repr(v))

def log(v):
    xbmc.log(re.sub(',',',\n',repr(v)))

def get_icon_path(icon_name):
    addon_path = xbmcaddon.Addon().getAddonInfo("path")
    return os.path.join(addon_path, icon_name+".png")
    #return os.path.join(addon_path, 'resources', 'img', icon_name+".png")

def remove_formatting(label):
    label = re.sub(r"\[/?[BI]\]",'',label)
    label = re.sub(r"\[/?COLOR.*?\]",'',label)
    return label


@plugin.route('/addon/<id>')
def addon(id):
    addon = plugin.get_storage(id)
    items = []
    for name in sorted(addon):
        url = addon[name]
        items.append({'label': name,'path': url,'thumbnail':get_icon_path('icon'),'is_playable':True,})
    return items

@plugin.route('/add_channel')
def add_channel():
    channels = plugin.get_storage('channels')
    d = xbmcgui.Dialog()
    channel = d.input("Add Channel")
    if channel:
        channels[channel] = ""
    xbmc.executebuiltin('Container.Refresh')


@plugin.route('/remove_channel')
def remove_channel():
    channels = plugin.get_storage('channels')
    channel_list = sorted(channels)
    d = xbmcgui.Dialog()
    which = d.select("Remove Channel",channel_list)
    if which == -1:
        return
    channel = channel_list[which]
    del channels[channel]
    xbmc.executebuiltin('Container.Refresh')

@plugin.route('/remove_this_channel/<channel>')
def remove_this_channel(channel):
    channels = plugin.get_storage('channels')
    del channels[channel]
    xbmc.executebuiltin('Container.Refresh')

@plugin.route('/clear_channels')
def clear_channels():
    channels = plugin.get_storage('channels')
    channels.clear()
    xbmc.executebuiltin('Container.Refresh')

@plugin.route('/import_channels')
def import_channels():
    channels = plugin.get_storage('channels')
    #d = xbmcgui.Dialog()
    #filename = d.browse(1, 'Import Channels', 'files', '', False, False, 'special://home/')
    filename = PLAYER_CHANNELS_INI
    if not filename:
        return
    if filename.endswith('.ini'):
        lines = xbmcvfs.File(filename,'rb').read().splitlines()
        for line in lines:
            if not line.startswith('[') and not line.startswith('#') and "=" in line:
                channel_url = line.split('=',1)
                if len(channel_url) == 2:
                    name = channel_url[0]
                    channels[name] = ""
    xbmc.executebuiltin('Container.Refresh')



@plugin.route('/stream_search/<channel>')
def stream_search(channel):
    streams = {}
    filename = PLAYER_ADDONS_INI
    f = xbmcvfs.File(filename,"rb")
    lines = f.read().splitlines()
    for line in lines:
        if line.startswith('['):
            addon = line.strip('[]')
            if addon not in streams:
                streams[addon] = {}
        elif "=" in line:
            (name,url) = line.split('=',1)
            if url and addon is not None:
                streams[addon][url] = name
    channel_search = channel.lower().replace(' ','')
    stream_list = []
    for id in sorted(streams):
        files = streams[id]
        for f in sorted(files, key=lambda k: files[k]):
            label = files[f]
            label_search = label.lower().replace(' ','')
            if label_search in channel_search or channel_search in label_search:
                stream_list.append((id,f,label))
    labels = ["[%s] %s" % (x[0],x[2]) for x in stream_list]
    d = xbmcgui.Dialog()
    which = d.select(channel, labels)
    if which == -1:
        return
    stream_name = stream_list[which][2]
    stream_link = stream_list[which][1]
    plugin.set_resolved_url(stream_link)



@plugin.route('/export_channels')
def export_channels():
    channels = plugin.get_storage('channels')
    f = xbmcvfs.File('special://profile/addon_data/'+ADDONID+'/export.ini','wb')
    for channel in sorted(channels):
        url = plugin.url_for('stream_search',channel=channel)
        s = "%s=%s\n" % (channel,url)
        f.write(s)
    f.close()



@plugin.route('/channel_player')
def channel_player():
    channels = plugin.get_storage("channels")
    items = []
    for channel in sorted(channels):
        context_items = []
        context_items.append(("[COLOR yellow][B]%s[/B][/COLOR] " % 'Add Channel', 'XBMC.RunPlugin(%s)' % (plugin.url_for(add_channel))))
        context_items.append(("[COLOR yellow][B]%s[/B][/COLOR] " % 'Remove Channel', 'XBMC.RunPlugin(%s)' % (plugin.url_for(remove_this_channel, channel=channel))))
        context_items.append(("[COLOR yellow][B]%s[/B][/COLOR] " % 'Import Channels', 'XBMC.RunPlugin(%s)' % (plugin.url_for(import_channels))))
        context_items.append(("[COLOR yellow][B]%s[/B][/COLOR] " % 'Export Channels', 'XBMC.RunPlugin(%s)' % (plugin.url_for(export_channels))))
        context_items.append(("[COLOR yellow][B]%s[/B][/COLOR] " % 'Clear Channels', 'XBMC.RunPlugin(%s)' % (plugin.url_for(clear_channels))))
        items.append({'label': channel,'path': plugin.url_for('stream_search',channel=channel),'thumbnail':get_icon_path('icon'),'is_playable': True,'context_menu': context_items,})
    return items



###########################################
#### plugin.video.addons.ini.search channel
###########################################
@plugin.route('/searchthistitle/<what>')
def searchthistitle(what):
    if not what:
        return
    addons = plugin.get_storage("addons")
    #folder = plugin.get_setting("addons.folder")
    #file = plugin.get_setting("addons.file")
    #filename = os.path.join(folder,file)
    filename = PLAYER_ADDONS_INI
    f = xbmcvfs.File(filename,"rb")
    lines = f.read().splitlines()
    addon = None
    for line in lines:
        if line.startswith('['):
            a = line.strip('[]')
            addons[a] = a
            addon = plugin.get_storage(a)
            addon.clear()
        elif "=" in line:
            (name,url) = line.split('=',1)
            if url and addon is not None:
                addon[name] = url
    items = []
    for a in addons.keys():
        add = plugin.get_storage(a)
        log2(add.keys())
        exact = [x for x in add.keys() if x.lower() == what.lower()]
        log2(exact)
        partial = [x for x in add.keys() if what.lower() in x.lower()]
        ignore_space = [x for x in add.keys() if re.sub(' ','',what).lower() in re.sub(' ','',x).lower()]
        found = exact + partial
        for f in sorted(set(exact)):
            items.append({"label": "[COLOR green]%s [%s][/COLOR]" % (f,a),"path" : add[f],"is_playable" : True})
        for f in sorted(set(partial)-set(exact)):
            items.append({"label": "[COLOR orange]%s [%s][/COLOR]" % (f,a),"path" : add[f],"is_playable" : True})
        for f in sorted(set(ignore_space)-set(partial)-set(exact)):
            items.append({"label": "[COLOR red]%s [%s][/COLOR]" % (f,a),"path" : add[f],"is_playable" : True})
    return items
#
@plugin.route('/search_dialog')
def search_dialog():
    dialog = xbmcgui.Dialog()
    what = dialog.input("Search")
    if what:
        return searchthistitle(what)
# END Search ini for Channel




###########################################
#### Set tvgfs minimal skin settings
###########################################
@plugin.route('/skin_mod_settings')
def skin_mod_settings():
    #import skin; skin.applyskin()
    #
    SKINS = [["Awesome", "Awesome"]]
    names = [s[0] for s in SKINS]
    d = xbmcgui.Dialog()
    skin = d.select("Set Default Skin for  "+ADDONID_CORE, names)
    if skin > -1:
        tvgf = xbmcaddon.Addon("script.tvguide.tardis")
        if tvgf:
            tvgf.setSetting('skin.source', '2')
            tvgf.setSetting('skin.folder', 'special://home/addons/script.tvguide.tardis.skin.awesome/')
            tvgf.setSetting('skin.user', SKINS[skin][1])
            tvgf.setSetting('categories.background.color', '[COLOR ffb22222]firebrick[/COLOR]')
            tvgf.setSetting('epg.nofocus.color', '[COLOR ffffffff]white[/COLOR]')
            tvgf.setSetting('epg.focus.color', '[COLOR ffffffff]black[/COLOR]')
            tvgf.setSetting('timebar.color', '[COLOR ffffff00]yellow[/COLOR]')
            tvgf.setSetting('epg.video.pip', 'true')
            tvgf.setSetting('program.image.scale', 'false')
            tvgf.setSetting('program.background.image.source', '0')
            tvgf.setSetting('program.background.color', '[COLOR ff4682b4]steelblue[/COLOR]')
            tvgf.setSetting('program.background.flat', 'true')
            tvgf.setSetting('program.background.enabled', 'false')
            tvgf.setSetting('action.bar', 'true')
            d.ok('Done', 'Using skin "' + SKINS[skin][1] + '"  with  '+ADDONID_CORE)
        if not tvgf: d.ok('Error', 'Cannot set "' + SKINS[skin][1] + '"')


# Open as Program Addon (EPG)
@plugin.route('/guide')
def guide(): xbmc.executebuiltin('RunScript('+ADDONID_CORE+')')


# Menu open main addon settings
@plugin.route('/open_settings')
def open_settings():  xbmcaddon.Addon(id=ADDONID_CORE).openSettings();sys.exit(0)


@plugin.route('/main_iniplayer')
def main_iniplayer():
    # import channels.ini
    if not os.path.isfile(PLAYER_CHANNELS_SET):
        import_channels()
        xbmc.sleep(350)
    # import addons.ini
    addons = plugin.get_storage("addons")
    for a in addons.keys():
        add = plugin.get_storage(a)
        add.clear()
    addons.clear()
    name = PLAYER_ADDONS_INI
    f = xbmcvfs.File(name,"rb")
    lines = f.read().splitlines()
    addon = None
    for line in lines:
        if line.startswith('['):
            a = line.strip('[]')
            addons[a] = a
            addon = plugin.get_storage(a)
            addon.clear()
        elif "=" in line:
            (name,url) = line.split('=',1)
            if url and addon is not None:
                addon[name] = url.strip('@ ')
    #
    items = []
    context_items = []
    context_items.append(("[COLOR yellow][B]%s[/B][/COLOR] " % 'Add Channel', 'XBMC.RunPlugin(%s)' % (plugin.url_for(add_channel))))
    context_items.append(("[COLOR yellow][B]%s[/B][/COLOR] " % 'Remove Channel', 'XBMC.RunPlugin(%s)' % (plugin.url_for(remove_channel))))
    context_items.append(("[COLOR yellow][B]%s[/B][/COLOR] " % 'Import Channels', 'XBMC.RunPlugin(%s)' % (plugin.url_for(import_channels))))
    context_items.append(("[COLOR yellow][B]%s[/B][/COLOR] " % 'Export Channels', 'XBMC.RunPlugin(%s)' % (plugin.url_for(export_channels))))
    context_items.append(("[COLOR yellow][B]%s[/B][/COLOR] " % 'Clear Channels', 'XBMC.RunPlugin(%s)' % (plugin.url_for(clear_channels))))
    items.append({'label': '[COLOR yellow]Search[/COLOR]','path': plugin.url_for('search_dialog'),'thumbnail':get_icon_path('icon'),})
    items.append({'label': "[COLOR yellow]Channels[/COLOR]",'path': plugin.url_for('channel_player'),'thumbnail':get_icon_path('icon'),'context_menu': context_items,})
    for id in sorted(addons):
        items.append({'label': id,'path': plugin.url_for('addon',id=id),'thumbnail':get_icon_path('icon'),})
    return items




@plugin.route('/')
def index():
    items = []
    context_items = []
    items.append({'label': '[COLOR green]TV:[/COLOR]  Run  '+ADDONID_CORE+ ' EPG','path': plugin.url_for('guide'),'thumbnail':get_icon_path('icon'),})
    items.append({'label': '[COLOR green]SKIN:[/COLOR]  Set Skin for  '+ADDONID_CORE,'path': plugin.url_for('skin_mod_settings'),'thumbnail':get_icon_path('icon'),})
    items.append({'label': '[COLOR yellow]Search[/COLOR] addon.ini','path': plugin.url_for('search_dialog'),'thumbnail':get_icon_path('icon'),})
    items.append({'label': '[COLOR yellow]Play[/COLOR] addon.ini','path': plugin.url_for('main_iniplayer'),'thumbnail':get_icon_path('icon'),})
    items.append({'label': '[COLOR yellow]Open Settings[/COLOR]  '+ADDONID_CORE,'path': plugin.url_for('open_settings'),'thumbnail':get_icon_path('icon'),})
    return items

if __name__ == '__main__':
    plugin.run()
    