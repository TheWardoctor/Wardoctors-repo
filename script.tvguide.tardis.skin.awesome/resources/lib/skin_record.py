# Todo - grab name and channel and time as arg.  Set a little record icon in screen bottom left if recording
import xbmc, xbmcaddon, xbmcgui, xbmcplugin
import sys
import os
import sqlite3
import urllib
import json
import traceback
from subprocess import call
from subprocess import Popen
import time
timestr = time.strftime("%Y_%m%d__%H-%M")

try: from main_ini import ADDONID_CORE
except ImportError: ADDONID_CORE  = 'script.tvguide.tardis'       # set this to your dest addonid
ADDON_CORE    = xbmcaddon.Addon(id=ADDONID_CORE)

try: from main_ini import ADDONID
except ImportError: ADDONID = 'script.tvguide.tardis.skin.awesome'   # set this to your skin addonid
ADDON         = xbmcaddon.Addon(id=ADDONID)
#
addonPath     = xbmc.translatePath(os.path.join('special://home/addons', ADDONID))
basePath      = xbmc.translatePath(os.path.join('special://profile', 'addon_data', ADDONID))
ICON          = xbmc.translatePath(os.path.join('special://home/addons', ADDONID, 'icon.png'))
Zip_temp_path = xbmc.translatePath(os.path.join('special://profile', 'addon_data', ADDONID))
dialog        = xbmcgui.Dialog()
dp            = xbmcgui.DialogProgress()

################################################################################
#   ffmpeg record settings
################################################################################
# grab or set executable and save paths
ffmpegdir              = xbmc.translatePath(os.path.join('special://profile', 'addon_data', ADDONID, 'resources')) # default dir for max compatability
ffplay                 = xbmc.translatePath(os.path.join(ffmpegdir, 'ffplay.exe'))
rtmpdump               = xbmc.translatePath(os.path.join(ffmpegdir, 'rtmpdump.exe'))
ffmpeg                 = ADDON_CORE.getSetting('autoplaywiths.ffmpeg')
autoplaywiths_folder   = ADDON_CORE.getSetting('autoplaywiths.folder')
udp                    = "udp://localhost:1234"
#udp                   = "udp://localhost:1234?buffer_size=10000000"
rtp                    = "rtp://localhost:1234" # wip
#

url_ffmpegwindows = 'https://raw.githubusercontent.com/thismustbetheplace/_zips/master/_ffmpeg/ffmpeg_windows.zip'
url_ffmpegwindowsfile = 'ffmpeg_windows'

url_ffmpegandroid = 'https://github.com/WritingMinds/ffmpeg-android/releases/download/v0.3.4/prebuilt-binaries.zip'
url_ffmpegandroidfile = 'prebuilt-binaries'

#if xbmc.getCondVisibility('system.platform.windows'): url_ffmpeg = 'http://ffmpeg.zeranoe.com/builds/win32/static/ffmpeg-3.2.4-win32-static.zip'
#if xbmc.getCondVisibility('system.platform.windows'): url_ffmpeg = 'https://ffmpeg.zeranoe.com/builds/win64/static/ffmpeg-20170801-1193301-win64-static.zip'
#if xbmc.getCondVisibility('system.platform.android'): url_ffmpeg = 'https://github.com/WritingMinds/ffmpeg-android/releases/download/v0.3.4/prebuilt-binaries.zip'


# get name from playing or lastchannel in settings
start = timestr
streamUrl = 'none'
url = 'none'
channel = 'Channel'
player = xbmc.Player()
if player.isPlaying():
    url = player.getPlayingFile()
s = ADDON_CORE.getSetting('last.channel')
if s:
    (id, title, lineup, logo, streamUrl, visible, weight) = json.loads(s)
    channel = id
    ## or
    '''
    try:
        import utils
        (id, title, lineup, logo, streamUrl, visible, weight) = json.loads(s)
        lastChannel = utils.Channel(id, title, lineup, logo, streamUrl, visible, weight)
        channel = id
        #url = streamUrl
    except: pass
    '''
#
name = "PVR_%s_%s" % (channel,start)
name = name.encode("cp1252")
url = "%s" % (url)
try: url = url.encode("cp1252")
except: pass
#
'''
# search database  wip
path = xbmc.translatePath(os.path.join('special://profile', 'addon_data', ADDONID, 'source.db'))
try: conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
except Exception as detail:  xbmc.log("EXCEPTION:  %s" % detail, xbmc.LOGERROR)
c = conn.cursor()
c.execute('SELECT stream_url FROM custom_stream_url WHERE channel=?', [channel])
row = c.fetchone()
if row:
    url = row[0]
    ADDON_CORE.setSetting('playing.channel',channel)
    ADDON_CORE.setSetting('playing.start',start)
#
'''

#
#wip
################################################################################
#   Download needed files (ffmpeg rtmpdunp ffplay)
################################################################################
def ffmpegDL():
    # check if ffmpeg exists
    isffmpeg = ADDON_CORE.getSetting('autoplaywiths.ffmpeg')
    if not os.path.exists(isffmpeg):
        # make dirs
        #ffmpegdir   = xbmc.translatePath(os.path.join('special://profile', 'addon_data', ADDONID, 'resources'))
        if not os.path.exists(ffmpegdir):  os.makedirs(ffmpegdir)
        # set ffmpeg path
        if xbmc.getCondVisibility('system.platform.windows'):
            ADDON_CORE.setSetting('autoplaywiths.ffmpeg', xbmc.translatePath(os.path.join(ffmpegdir,'ffmpeg.exe')))
        if xbmc.getCondVisibility('system.platform.android'):
            ADDON_CORE.setSetting('autoplaywiths.ffmpeg', xbmc.translatePath(os.path.join(ffmpegdir,'ffmpeg')))

        # dl a pre built zip from a repo or from source
        ffmpeg = ADDON_CORE.getSetting('autoplaywiths.ffmpeg')
        if not os.path.exists(ffmpeg):
            # dl paths
            mainurl    = ADDON_CORE.getSetting('main.url')
            if mainurl:
                xbmcgui.Dialog().notification('ffmpeg dl', 'Builtin url', ICON, 1000, False)
                if xbmc.getCondVisibility('system.platform.windows'): url_ffmpeg = mainurl+'_ffmpeg/record_windows.zip'
                if xbmc.getCondVisibility('system.platform.android'): url_ffmpeg = mainurl+'_ffmpeg/record_android.zip'
                _downloader(url_ffmpeg, xbmc.translatePath(os.path.join(Zip_temp_path,'ffmpeg.zip')), 'ffmpeg DL BuiltIn')
                zipEXTRACT(xbmc.translatePath(os.path.join(Zip_temp_path,'ffmpeg.zip')), ffmpegdir)
                xbmc.executebuiltin("XBMC.Container.Refresh")
                try: os.remove(xbmc.translatePath(os.path.join(Zip_temp_path,'ffmpeg.zip')))
                except: pass
            #
            # if not built in use paths provided at top of this file
            if not mainurl:
                xbmcgui.Dialog().notification('ffmpeg dl', 'Actual url', ICON, 1000, False)
                if xbmc.getCondVisibility('system.platform.windows'):
                    url_ffmpeg = url_ffmpegwindows
                    url_ffmpegfile = url_ffmpegwindowsfile
                if xbmc.getCondVisibility('system.platform.android'):
                    url_ffmpeg = url_ffmpegandroid
                    url_ffmpeg = url_ffmpegandroidfile
                _downloader(url_ffmpeg, xbmc.translatePath(os.path.join(Zip_temp_path,'ffmpeg.zip')), 'ffmpeg DL Default')
                zipEXTRACT(xbmc.translatePath(os.path.join(Zip_temp_path,'ffmpeg.zip')), ffmpegdir)
                xbmc.executebuiltin("XBMC.Container.Refresh")
                try: os.remove(xbmc.translatePath(os.path.join(Zip_temp_path,'ffmpeg.zip')))
                except: pass
                #if not os.path.exists(ffmpeg):
                
                
                # copy
                if xbmc.getCondVisibility('system.platform.windows'):
                    if os.path.exists(xbmc.translatePath(os.path.join(ffmpegdir,url_ffmpegwindowsfile,'bin','ffmpeg.exe'))):
                        os.rename(xbmc.translatePath(os.path.join(ffmpegdir,url_ffmpegwindowsfile,'bin','ffmpeg.exe')), xbmc.translatePath(os.path.join(ffmpegdir,'ffmpeg.exe')))
                        os.rename(xbmc.translatePath(os.path.join(ffmpegdir,url_ffmpegwindowsfile,'bin','ffplay.exe')), xbmc.translatePath(os.path.join(ffmpegdir,'ffplay.exe')))
                        remove_dir(xbmc.translatePath(os.path.join(ffmpegdir,url_ffmpegwindowsfile)))
                #
                if xbmc.getCondVisibility('system.platform.android'):
                    if os.path.exists(xbmc.translatePath(os.path.join(ffmpegdir,url_ffmpegandroidfile,'armeabi-v7a','ffmpeg'))):
                        os.rename(xbmc.translatePath(os.path.join(ffmpegdir,url_ffmpegandroidfile,'armeabi-v7a','ffmpeg')), xbmc.translatePath(os.path.join(ffmpegdir,'ffmpeg')))
                        remove_dir(xbmc.translatePath(os.path.join(ffmpegdir,url_ffmpegandroidfile)))

        #
        #dialog.ok('ffmpeg.exe path', 'Enter ffmpeg path and record folder in settings.',  'Please enter one in settings under Program Schedule tab')
        #xbmcaddon.Addon(id=ADDONID_CORE).openSettings()
        #sys.exit(0)
        #
        #'''
        autoplaywiths_folder   = ADDON_CORE.getSetting('autoplaywiths.folder')
        if not autoplaywiths_folder:
            dialog.ok('Save Path', 'Enter where to save your recordings in settings.',  'Please enter one under Program Schedule tab')
            xbmcaddon.Addon(id=ADDONID_CORE).openSettings()
            xbmc.executebuiltin("XBMC.Container.Refresh")
            sys.exit(0)
        #'''




################################################################################
#   ffmpeg Menu
#https://trac.ffmpeg.org/wiki/Creating%20multiple%20outputs
#https://trac.ffmpeg.org/wiki/StreamingGuide
#https://github.com/WritingMinds/ffmpeg-android   # pre built binaries
################################################################################
def record_Menu():
    ffmpegDL()
    ffmpeg   = ADDON_CORE.getSetting('autoplaywiths.ffmpeg')
    if url == 'none': dialog.ok('No URL', 'Please start a channel first')
    choiceffmpeg = dialog.select('Record [COLOR yellow]'+channel+ '[/COLOR]  to '+autoplaywiths_folder+ ' url:'+url,
                                                    ['[COLOR red]Stop[/COLOR]  Recording [COLOR yellow]'+channel+'[/COLOR]', 
                                                    '[COLOR green]Start[/COLOR]  Recording  (Indefinite)',
                                                    '[COLOR green]Start[/COLOR]  Recording  (Indefinite with udp)',
                                                    'Switchplayer (Playercorefactory.xml)',
                                                    'Open PVR Folder '+autoplaywiths_folder,
                                                    'Play with VLC',
                                                    'Start and play on '+udp,
                                                    'Play '+udp,
                                                    'RTPDump '+rtp,
                                                    'Start Recording  (30  mins)',
                                                    'Start Recording  (60  mins)',
                                                    'Start Recording  (90  mins)',
                                                    'Start Recording  (120 mins)',
                                                    'Start Recording  (1 min)',
                                                    'Play with ffplay',
                                                    '(Re) Download ffmpeg'])
    if choiceffmpeg == 0: stop_ffmpeg()                # Exit ffmpeg via taskkill
    if choiceffmpeg == 1: record_ffmpeg('10000',udp,1) # Indefinite  you stop it manually
    if choiceffmpeg == 2: record_ffmpeg_udp('10000',udp,1) # Indefinite  you stop it manually with udp for 2 accounts on a pay server
    if choiceffmpeg == 3: xbmc.executebuiltin('Action(SwitchPlayer)')#core='SwitchPlayer';xbmc.executebuiltin('%s' % core)#xbmc.executebuiltin('Sendclick(%s)' % core)# playercorefactory switch
    if choiceffmpeg == 4: pvr_folder()                  # Open Recording Folder
    if choiceffmpeg == 5: play_vlc()                    # Record screen with ffmpeg
    if choiceffmpeg == 6: start_udp_ffmpeg(udp)         # Start UDP STream
    if choiceffmpeg == 7: play_udp_ffmpeg(udp)          # Play UDP Stream
    if choiceffmpeg == 8: rtmpdump()                    # wip rtmpdump
    if choiceffmpeg == 9: record_ffmpeg('1800',udp,1)   # 30 min 1800
    if choiceffmpeg == 10: record_ffmpeg('3600',udp,1)  # 60 min 3600 
    if choiceffmpeg == 11: record_ffmpeg('5400',udp,1)  # 90 min 5400
    if choiceffmpeg == 12: record_ffmpeg('7200',udp,1)  # 2 hours 7200
    if choiceffmpeg == 13: record_ffmpeg('60',udp,1)    # 1 minute
    if choiceffmpeg == 14: ffplay_play()                # Play with ffmpeg
    if choiceffmpeg == 15:
        if os.path.exists(ffmpeg):
            try: os.remove(ffmpeg)
            except: pass
        if os.path.exists(ffplay):
            try: os.remove(ffplay)
            except: pass
        ffmpegDL()
    
#wip
################################################################################
#   rtmpdump wip dummy
################################################################################
def rtmpdump():
    #if not xbmc.getCondVisibility('system.platform.windows'): dialog.ok('Wrong OS', 'Currently only works on Windows',  'WIP');sys.exit(0)
    player = xbmc.Player()
  
#wip
################################################################################
#   Play with ffplay
################################################################################
def ffplay_play():
    #if not xbmc.getCondVisibility('system.platform.windows'): dialog.ok('Wrong OS', 'Currently only works on Windows',  'WIP');sys.exit(0)
    ffplay = xbmc.translatePath(os.path.join('special://profile', 'addon_data', ADDONID, 'resources', 'ffplay.exe'))
    cmd = [ffplay, "-i", url]
    #p = Popen(cmd,shell=True) # has NO cmd window info prompt
    p = Popen(cmd,shell=False) # has cmd window info prompt
    player.stop()

#wip
################################################################################
#   Play with VLC
################################################################################
def play_vlc():
    #if not xbmc.getCondVisibility('system.platform.windows'): dialog.ok('Wrong OS', 'Currently only works on Windows',  'WIP');sys.exit(0)
    if url:
        if xbmc.getCondVisibility('system.platform.windows'):
            if os.path.exists('C:\Program Files\Videolan\VLC\VLC.exe'): vlc = 'C:\Program Files\Videolan\VLC\VLC.exe'
            if os.path.exists('C:\Program Files (x86)\Videolan\VLC\VLC.exe'): vlc = "C:\Program Files (x86)\Videolan\VLC\VLC.exe"
            cmd = [vlc, "--play-and-exit", "--video-on-top", "--fullscreen", url]
            if player.isPlaying():  player.stop()
            #p = Popen(cmd,shell=True) # has NO cmd window info prompt
            p = Popen(cmd,shell=False) # has cmd window info prompt
        
        if xbmc.getCondVisibility('system.platform.android'):
            #if os.path.exists('C:\Program Files\Videolan\VLC\VLC.exe'): vlc = 'C:\Program Files\Videolan\VLC\VLC.exe'
            if player.isPlaying():  player.stop()
            #xbmc.executebuiltin('XBMC.StartAndroidActivity("org.acestream","android.intent.action.VIEW","","'+chid+'")')
            #xbmc.executebuiltin('XBMC.StartAndroidActivity("ru.vidsoftware.acestreamcontroller.free","android.intent.action.VIEW","","'+chid+'")')



#
################################################################################
#   Open PVR save folder
################################################################################
def pvr_folder():
    autoplaywiths_folder   = ADDON_CORE.getSetting('autoplaywiths.folder')
    if not autoplaywiths_folder :
        dialog.ok('Save Path', 'Enter where to save your recordings in settings.',  'Please enter one under Program Schedule tab')
        xbmcaddon.Addon(id=ADDONID_CORE).openSettings()
        sys.exit(0)
    xbmc.executebuiltin('ActivateWindow(10025,%s,return)' % autoplaywiths_folder)

#
################################################################################
#   Stop Recording
################################################################################
def stop_ffmpeg():
    #if not xbmc.getCondVisibility('system.platform.windows'): dialog.ok('Wrong OS', 'Currently only works on Windows',  'WIP');sys.exit(0)
    xbmc.log(msg='##['+ADDONID+'] Stopping 3rd Party Player Playback or recording', level=xbmc.LOGNOTICE)
    if xbmc.getCondVisibility('system.platform.windows'):
        try: os.system('@ECHO off');os.system('TASKKILL /im ffmpeg.exe /f');os.system('TASKKILL /im ffplay.exe /f');os.system('TASKKILL /im rtmpdump.exe /f')
        except: pass
#
################################################################################
#   Play UDP with ffmpeg
################################################################################
def play_udp_ffmpeg(the_udp):
    #if not xbmc.getCondVisibility('system.platform.windows'): dialog.ok('Wrong OS', 'Currently only works on Windows',  'WIP');sys.exit(0)
    notify('UPD','Play '+the_udp,ICON)
    xbmc.log(msg='##['+ADDONID+'] Play '+the_udp, level=xbmc.LOGNOTICE)
    if xbmc.getCondVisibility('system.platform.windows'): xbmc.executebuiltin('PlayMedia(%s)' % the_udp)
#
################################################################################
#   Record with ffmpeg
################################################################################
def record_ffmpeg(seconds, the_udp, ffmpeg_string):
    #if not xbmc.getCondVisibility('system.platform.windows'): dialog.ok('Wrong OS', 'Currently only works on Windows',  'WIP');sys.exit(0)
    autoplaywiths_folder   = ADDON_CORE.getSetting('autoplaywiths.folder')
    if not autoplaywiths_folder :
        dialog.ok('Save Path', 'Enter where to save your recordings in settings.',  'Please enter one under Program Schedule tab')
        xbmcaddon.Addon(id=ADDONID_CORE).openSettings()
        sys.exit(0)
    if url: 
        ffmpeg = ADDON_CORE.getSetting('autoplaywiths.ffmpeg')
        filename = xbmc.translatePath(os.path.join(autoplaywiths_folder, "%s.ts" % name)) 
        xbmc.log(msg='##['+ADDONID+'] Start 3rd Party Player recording '+autoplaywiths_folder, level=xbmc.LOGNOTICE)
        #
        #cmd = [ffmpeg, "-y", "-i", url, "-c:v", "copy", "-c:a", "copy", "-t", str(seconds), "-f", "mpegts", "-map", "0:v", "-map", "0:a", filename]
        cmd = [ffmpeg, "-y", "-i", url, "-c:v", "copy", "-c:a", "copy", "-t", str(seconds), filename]
        #p = Popen(cmd,shell=True) # has NO cmd window info prompt
        p = Popen(cmd,shell=False) # has cmd window info prompt
        #xbmc.log(msg='##['+ADDONID+'] Start Record and Playback', level=xbmc.LOGNOTICE)
        #player.stop()
        notify('RECORD','Recording to '+autoplaywiths_folder,ICON)
        #time.sleep(5)
        #try: xbmc.executebuiltin('PlayMedia(%s)' % filename)
        #except: pass
        
        
#
################################################################################
#   Record with ffmpeg and udp for 2 account
################################################################################
def record_ffmpeg_udp(seconds, the_udp, ffmpeg_string):
    #if not xbmc.getCondVisibility('system.platform.windows'): dialog.ok('Wrong OS', 'Currently only works on Windows',  'WIP');sys.exit(0)
    autoplaywiths_folder   = ADDON_CORE.getSetting('autoplaywiths.folder')
    if not autoplaywiths_folder :
        dialog.ok('Save Path', 'Enter where to save your recordings in settings.',  'Please enter one under Program Schedule tab')
        xbmcaddon.Addon(id=ADDONID_CORE).openSettings()
        sys.exit(0)
    if url: 
        ffmpeg = ADDON_CORE.getSetting('autoplaywiths.ffmpeg')
        filename = xbmc.translatePath(os.path.join(autoplaywiths_folder, "%s.ts" % name)) 
        xbmc.log(msg='##['+ADDONID+'] Start 3rd Party Player recording '+autoplaywiths_folder, level=xbmc.LOGNOTICE)
        #
        cmd = [ffmpeg, "-y", "-i", url, "-c:v", "copy", "-c:a", "copy", "-t", str(seconds), "-f", "mpegts", "-map", "0:v", "-map", "0:a", filename]
        #p = Popen(cmd,shell=True) # has NO cmd window info prompt
        p = Popen(cmd,shell=False) # has cmd window info prompt
        xbmc.log(msg='##['+ADDONID+'] Start Record and Playback', level=xbmc.LOGNOTICE)
        player.stop()
        notify('RECORD','Recording to '+autoplaywiths_folder,ICON)
        time.sleep(5)
        try: xbmc.executebuiltin('PlayMedia(%s)' % filename)
        except: pass

################################################################################
#   Start a udp of current channel and play
################################################################################
# Works but crashes sometimes
def start_udp_ffmpeg(the_udp):
    ffmpeg = ADDON_CORE.getSetting('autoplaywiths.ffmpeg')
    if url:   
        xbmc.log(msg='##['+ADDONID+'] Start ffmpeg UDP '+the_udp, level=xbmc.LOGNOTICE)   
        notify('UDP','Start UDP to '+the_udp,ICON)
        cmd = [ffmpeg, "-y", "-re", "-i", url, "-c:v", "copy", "-c:a", "copy", "-f", "mpegts", "-map", "0:v", "-map", "0:a", the_udp]
        #p = Popen(cmd,shell=True) # has NO cmd window info prompt
        p = Popen(cmd,shell=False) # has cmd window info prompt
        player.stop()
        time.sleep(5)
        xbmc.executebuiltin('PlayMedia(%s)' % the_udp)




################################################# 
# Re-open guide
#################################################
def reopen():
    xbmc.executebuiltin('XBMC.ActivateWindow(home)')
    xbmc.sleep(350)
    #RUN = 'RunAddon('+ADDONID+')'
    RUN = 'RunScript('+ADDONID+')'
    xbmc.executebuiltin(RUN)
    '''
    import gui
    xbmc.executebuiltin('XBMC.ActivateWindow(home)')
    xbmc.sleep(350)
    w = gui.TVGuide()
    w.doModal()
    xbmc.sleep(350)
    del w
    '''
#


################################################# 
# Download file
#################################################
def _downloader(url, dest, desc, dp = None):
    xbmc.log(msg='##['+ADDONID+'] Download '+url, level=xbmc.LOGNOTICE)
    #import xbmcgui
    #import urllib
    #import time
    if os.path.exists(dest):
        yes = dialog.yesno('Already Exists', "Would you like to Redownload?")
        if not yes:
            return
    try: os.remove(dest)
    except: pass
    if not dp:
        dp = xbmcgui.DialogProgress()
        dp.create('Downloading','Downloading & Installing ffmpeg', ' ', ' ')
    #dp.update(0)
    start_time=time.time()
    try:
        urllib.urlretrieve(url, dest, lambda nb, bs, fs: _pbhook(nb, bs, fs, dp, start_time))
    except: pass
#     
def _pbhook(numblocks, blocksize, filesize, dp, start_time):
        try: 
            percent = min(numblocks * blocksize * 100 / filesize, 100) 
            currently_downloaded = float(numblocks) * blocksize / (1024 * 1024) 
            kbps_speed = numblocks * blocksize / (time.time() - start_time) 
            if kbps_speed > 0: 
                eta = (filesize - numblocks * blocksize) / kbps_speed 
            else: 
                eta = 0 
            kbps_speed = kbps_speed / 1024 
            total = float(filesize) / (1024 * 1024) 
            mbs = '%.02f MB of %.02f MB' % (currently_downloaded, total) 
            e = 'Speed: %.02f Kb/s ' % kbps_speed 
            e += 'ETA: %02d:%02d' % divmod(eta, 60) 
            dp.update(percent, mbs, e)
        except: 
            percent = 100 
            dp.update(percent)
        if dp.iscanceled():
            dp.close()
#
#
################################################# 
# extract zip
#################################################
def zipEXTRACT(zipFileSource, zipDestPath):
    xbmc.log(msg='##['+ADDONID+'] Extract '+zipFileSource, level=xbmc.LOGNOTICE)
    try:
        import zipfile
        zin = zipfile.ZipFile(zipFileSource, 'r')
        zin.extractall(zipDestPath)
    except: pass
    try:    
        if os.path.exists(zipFileSource):
            os.remove(zipFileSource)
    except: pass
#
################################################# 
# Notification #
#################################################
def notify(header,msg,icon_path):
    addons_notify = ADDON_CORE.getSetting('addons.notify') == 'true'
    if addons_notify:
        try:
            duration=1000
            ##xbmc.executebuiltin('XBMC.Notification(%s,%s, %s, %s)' % (header, msg, duration, icon_path))
            xbmcgui.Dialog().notification(header, msg, icon=icon_path, time=duration, sound=False)
        except: pass


###########################################
###########################################
# ARGUMENT MENU
###########################################
###########################################
if __name__ == '__main__':
    if len(sys.argv) > 1:
        mode = int(sys.argv[1])
        if mode == 1:  record_Menu()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
