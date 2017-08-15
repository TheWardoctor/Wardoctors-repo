# This script allows for extra scripts assigned to buttons for custom per skin creator functions to share ideas
import xbmc, xbmcaddon, xbmcgui, xbmcplugin
import sys
import os
#path_exec_file = os.getcwd() + '\\guideTypes.py'  #test this command

try: from main_ini import ADDONID_CORE
except ImportError: ADDONID_CORE  = 'script.tvguide.tardis'       # set this to your dest addonid
ADDON_CORE    = xbmcaddon.Addon(id=ADDONID_CORE)

try: from main_ini import ADDONID
except ImportError: ADDONID = 'script.tvguide.tardis.skin.awesome'   # set this to your skin addonid
ADDON         = xbmcaddon.Addon(id=ADDONID)

addonPath     = xbmc.translatePath(os.path.join('special://home', 'addons', ADDONID))
coreaddonPath = xbmc.translatePath(os.path.join('special://home', 'addons', ADDONID_CORE))
basePath      = xbmc.translatePath(os.path.join('special://home', 'addon_data', ADDONID_CORE))
ICON          = xbmc.translatePath(os.path.join('special://home', 'addons', ADDONID_CORE, 'icon.png'))
temp_path     = xbmc.translatePath(os.path.join('special://home', 'addons', 'packages'))
dialog        = xbmcgui.Dialog()
dp            = xbmcgui.DialogProgress()


#################################################
# (Hopefully) Detect Skin
#################################################
skinPath = ''
# Ours - user set custom skin like script.tvguide.tardis.skin.awesome to script.tvguide.tardis
if ADDON_CORE.getSetting('skin.source') == '2':
    skin_folder = ADDON_CORE.getSetting('skin.folder')
    skin_user   = ADDON_CORE.getSetting('skin.user')
    skinPath    = xbmc.translatePath(os.path.join(skin_folder, 'resources' , 'skins', skin_user))
# Yours - inside user_data  resources\skins\yourskinname
if ADDON_CORE.getSetting('skin.source') == '1':
    skin_user   = ADDON_CORE.getSetting('skin.user')
    skinPath    = xbmc.translatePath(os.path.join(basePath, 'resources' , 'skins', skin_user))
# Folder -  A Built in skin
if ADDON_CORE.getSetting('skin.source') == '0':
    skin_user   = ADDON_CORE.getSetting('skin')
    skinPath    = xbmc.translatePath(os.path.join(addonPath, 'resources' , 'skins', skin_user))
#
if not os.path.exists(skinPath):
    xbmcgui.Dialog().notification('Error', 'Skin Not Detected', ICON, 1000, False)
    sys.exit(0)
flipmenu = 'script-tvguide-menu.xml'
flipmain = 'script-tvguide-main.xml'
flipvod = 'script-tvguide-vod-tv.xml'
#dialog.ok(ADDONID_CORE, ADDONID, skinPath, skin_user)  # For testing




#################################################
# Flip skin reverse description and videowindow co-ordinates
#################################################
def _skinvideowindow_toggle(Clean_File, rezsize):
     Clean_Name = xbmc.translatePath(os.path.join(skinPath, rezsize, Clean_File))
     if not os.path.exists(Clean_Name): return
     tmpFile = xbmc.translatePath(os.path.join(temp_path,'tmp.xml'))
     if os.path.exists(tmpFile): os.remove(tmpFile)
     xbmc.log(msg='##['+ADDONID+'] '+Clean_Name, level=xbmc.LOGNOTICE)
     try:    os.rename(Clean_Name, tmpFile)
     except: pass
     s=open(tmpFile).read()
     if rezsize == '720p':
         ## Description Flip
         # flip3 720p main
         if '<posx>20.5</posx>' in s:  s=s.replace('<posx>20.5</posx>','<posx>360.5</posx>')
         else:  s=s.replace('<posx>360.5</posx>','<posx>20.5</posx>')# extra 30 for timebar at top
         # flip4 720p menu
         if '<posx>920.5</posx>' in s:  s=s.replace('<posx>920.5</posx>','<posx>-360.5</posx>')
         else:  s=s.replace('<posx>-360.5</posx>','<posx>920.5</posx>')# extra 30 for timebar at top
     #
     if rezsize == '1080i':
         ## Description Flip
         # flip3 1080p main
         if '<posx>31</posx>' in s:  s=s.replace('<posx>31</posx>','<posx>541</posx>')
         else:  s=s.replace('<posx>541</posx>','<posx>31</posx>')# extra 30 for timebar at top
         # flip4 1080p menu
         if '<posx>1381</posx>' in s:  s=s.replace('<posx>1381</posx>','<posx>-541</posx>')
         else:  s=s.replace('<posx>-541</posx>','<posx>1381</posx>')# extra 30 for timebar at top
     #
     f=open(Clean_Name,'a')
     f.write(s)
     f.close()
     if os.path.exists(tmpFile): os.remove(tmpFile)



#################################################
# Flip skin description co-ordinates
#################################################
def _skinflip_toggle(Clean_File, rezsize):
     Clean_Name = xbmc.translatePath(os.path.join(skinPath, rezsize, Clean_File))
     if not os.path.exists(Clean_Name): return
     tmpFile = xbmc.translatePath(os.path.join(temp_path,'tmp.xml'))
     if os.path.exists(tmpFile): os.remove(tmpFile)
     xbmc.log(msg='##['+ADDONID+'] '+Clean_Name, level=xbmc.LOGNOTICE)
     try:    os.rename(Clean_Name, tmpFile)
     except: pass
     s=open(tmpFile).read()
     if rezsize == '720p':
         ## Description Flip
         # flip1 720p main
         if '<posy>240.5</posy>' in s:  s=s.replace('<posy>240.5</posy>','<posy>30.5</posy>')
         else:  s=s.replace('<posy>30.5</posy>','<posy>240.5</posy>')# extra 30 for timebar at top
         # flip2 720p menu
         if '<posy>0.5</posy>' in s:  s=s.replace('<posy>0.5</posy>','<posy>475.5</posy>')
         else:  s=s.replace('<posy>475.5</posy>','<posy>0.5</posy>')# extra 30 for timebar at top
     #
     if rezsize == '1080i':
         ## Description Flip
         # flip1 1080p main
         if '<posy>361</posy>' in s:  s=s.replace('<posy>361</posy>','<posy>46</posy>')
         else:  s=s.replace('<posy>46</posy>','<posy>361</posy>')
         # flip2 1080p menu
         if '<posy>1</posy>' in s:  s=s.replace('<posy>1</posy>','<posy>713</posy>')
         else:  s=s.replace('<posy>713</posy>','<posy>1</posy>')
     #
     f=open(Clean_Name,'a')
     f.write(s)
     f.close()
     if os.path.exists(tmpFile): os.remove(tmpFile)



################################################# 
# Toggle 1080i #
#################################################
def _toggle_1080():
    disabled_1080 = xbmc.translatePath(os.path.join(skinPath, '1080i-'))
    enabled_1080  = xbmc.translatePath(os.path.join(skinPath, '1080i'))
    xbmc.executebuiltin('XBMC.ActivateWindow(home)')
    xbmc.sleep(350)
    if os.path.exists(xbmc.translatePath(os.path.join(enabled_1080, flipmenu))):
        xbmcgui.Dialog().notification('Toggle', 'Disable 1080', ICON, 1000, False)
        os.rename(enabled_1080, disabled_1080)
    else:
        xbmcgui.Dialog().notification('Toggle', 'Enable 1080', ICON, 1000, False)
        os.rename(disabled_1080, enabled_1080)
#




################################################# 
# Choose menu style of popup menu #
#################################################
def _vodstyle_menu():
    choicevodstyle = dialog.select('VOD menu style',
                                    ['Awesome (Videoplayer Background)',
                                    'Default Style'])
    if choicevodstyle == 0:  _menu_overwrite('replace_mod_vod.xml', 'script-tvguide-vod-tv.xml')
    if choicevodstyle == 1:  _menu_overwrite('replace_default_vod.xml', 'script-tvguide-vod-tv.xml')
#

################################################# 
# Choose menu style of popup menu #
#################################################
def _popupstyle_menu():
    choicepopupstyle = dialog.select('Popup menu style',
                                    ['Awesome (Videoplayer Background)',
                                    'Default Style'])
    if choicepopupstyle == 0:  _menu_overwrite('replace_mod_menu.xml', 'script-tvguide-menu.xml')
    if choicepopupstyle == 1:  _menu_overwrite('replace_default_menu.xml', 'script-tvguide-menu.xml')
#
################################################# 
# Overwrite xml with chosen one
#################################################
def _menu_overwrite(SourceFile, Destfile):
    FileToDo = xbmc.translatePath(os.path.join(skinPath, '720p' , SourceFile))
    DestFile = xbmc.translatePath(os.path.join(skinPath, '720p' , Destfile))
    if os.path.exists(FileToDo):
        try:
            s=open(FileToDo).read()
            f=open(DestFile,'w')
            f.write(s)
            f.close()
            s.close()
            #reopen()
        except: pass
    #
    FileToDo = xbmc.translatePath(os.path.join(skinPath, '1080i' , SourceFile))
    DestFile = xbmc.translatePath(os.path.join(skinPath, '1080i' , Destfile))
    if os.path.exists(FileToDo):
        try:
            s=open(FileToDo).read()
            f=open(DestFile,'w')
            f.write(s)
            f.close()
            s.close()
            #reopen()
        except: pass
    #reopen()



################################################# 
# Re-open guide
#################################################
def _reopen():
    xbmc.executebuiltin('XBMC.ActivateWindow(home)')
    xbmc.sleep(350)
    #RUN = 'RunAddon('+ADDONID+')'
    RUN = 'RunScript('+ADDONID_CORE+')'
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
# logos toggle
#################################################
def _logos_toggle():
    if ADDON_CORE.getSetting('logos.enabled') == 'false':
        ADDON_CORE.setSetting('logos.enabled', 'true')
    elif ADDON_CORE.getSetting('logos.enabled') == 'true':
        ADDON_CORE.setSetting('logos.enabled', 'false')
    _reopen()
    #xbmc.executebuiltin('XBMC.ReloadSkin()')
    #xbmc.executebuiltin('XBMC.Action(reloadkeymaps)') #? 
#


#################################################
# pip toggle
#################################################
def _pip_toggle():
    if ADDON_CORE.getSetting('epg.video.pip') == 'false':
        ADDON_CORE.setSetting('epg.video.pip', 'true')
    elif ADDON_CORE.getSetting('epg.video.pip') == 'true':
        ADDON_CORE.setSetting('epg.video.pip', 'false')
    _reopen()
#

################################################# 
# Remove directory
#################################################
def _remove_dir(path):
    dflist = os.listdir(path)
    for itm in dflist:
         _path = os.path.join(path, itm)
         if os.path.isfile(_path):
             try:
                 os.remove(_path)
             except: pass
         else:
             try:
                 remove_dir(_path)
             except: pass
    os.rmdir(path)
    #
    if os.path.exists(path):
        try: os.remove(path)
        except: pass
#


###########################################
###########################################
# ARGUMENT MENU
###########################################
###########################################
if __name__ == '__main__':
    #if not len(sys.argv) > 1: xbmcgui.Dialog().notification('Skin', 'skin.py with no args', ICON, 1000, False)
    if len(sys.argv) > 1:
        mode = int(sys.argv[1])
        
        #  streamsetup
        #skin.py, 20 Refresh subs
        
        #  main xml
        #skin.py, 1  Reopen guide above logos
        #skin.py, 3  Logos
        #skin.py, 21 Lookups
        #skin.py, 22 Search ini
        #skin.py, 23 Play ini
        #skin.py, 30 Record
        
        # menu xml
        #skin.py, 2  Pip Toggle
        #skin.py, 4  Help
        #skin.py, 5  Open As Video Addon
        #skin.py, 6  Open settings
        #skin.py, 10 Description Flip
        #skin.py, 11 Popup Menu Style
        #skin.py, 12 Videowindow Flip
        #skin.py, 20  Refresh subs
        #skin.py, 22 Search ini
        #skin.py, 23 Play ini
        #skin.py, 25  Playlist
        #skin.py, 30  Record
        #skin.py, 666 Reset Database
        
        # Reopen Guide failsafe button if crash
        if mode == 1: _reopen()
        
        # Run core addon
        if mode == 5:
            xbmc.executebuiltin('XBMC.ActivateWindow(home)')
            xbmc.sleep(350)
            try:  xbmc.executebuiltin("RunAddon("+ADDONID_CORE+")")
            except: pass

        # Open core settings
        if mode == 6:
            #xbmc.executebuiltin('XBMC.ActivateWindow(home)')
            #xbmc.sleep(350)
            try:  xbmcaddon.Addon(id=ADDONID_CORE).openSettings();sys.exit(0)
            except: pass


        ###########################################
        # Toggle skin settings
        ###########################################
        
        # Toggle the picture in picture videowindow as a background
        if mode == 2: xbmcgui.Dialog().notification('Toggle', 'PIP Video Background', ICON, 1000, False); _pip_toggle()

        # Toggle the channel logo icons
        if mode == 3: xbmcgui.Dialog().notification('Toggle', 'Logos', ICON, 1000, False); _logos_toggle()


        # play url directly from playlist.m3u             wip
        if mode == 25:
            playlistFile = xbmc.translatePath(os.path.join(basePath, 'playlist.m3u'))
            playlistFile2 = xbmc.translatePath(os.path.join(basePath, 'resources', 'playlist.m3u'))
            xbmcgui.Dialog().notification('playlist.m3u', 'Browse playlist.m3u', ICON, 1000, False)
            if os.path.exists(playlistFile):
                xbmc.executebuiltin('ActivateWindow(10025,'+playlistFile+',return)')
            if not os.path.exists(playlistFile):
                if os.path.exists(playlistFile2):
                    xbmc.executebuiltin('ActivateWindow(10025,'+playlistFile2+',return)')
                    if not os.path.exists(playlistFile2):
                        xbmcgui.Dialog().notification('Missing', 'No playlist.m3u found.', ICON, 1000, False)


        ###########################################
        # Write skin settings
        ###########################################

        # Horizontal Reverse the description area with the epg columns
        if mode == 10:
            xbmcgui.Dialog().notification('Toggle', 'Flip Description', ICON, 1000, False)
            _skinflip_toggle(flipmenu, '720p')
            _skinflip_toggle(flipmain, '720p')
            _skinflip_toggle(flipvod, '720p')
            _skinflip_toggle(flipmenu, '1080i')
            _skinflip_toggle(flipmain, '1080i')
            _skinflip_toggle(flipvod, '1080i')
            _reopen()

        # Vertical Reverse the description area with videowindow
        if mode == 12: 
            xbmcgui.Dialog().notification('Toggle', 'Flip Videowindow', ICON, 1000, False)
            _skinvideowindow_toggle(flipmenu, '720p')
            _skinvideowindow_toggle(flipmain, '720p')
            _skinvideowindow_toggle(flipmenu, '1080i')
            _skinvideowindow_toggle(flipmain, '1080i')
            _reopen()


        # Change the popup menu style by overwriting xml with selected
        if mode == 11:
            _popupstyle_menu()
            _reopen()
        
        # Change the VOD menu style by overwriting xml with selected
        if mode == 13:
            _vodstyle_menu()
            _reopen()
        
        # Change the VOD menu style by overwriting xml with selected
        if mode == 14:
            _toggle_1080()
            _reopen()
        
        
        ###########################################
        # Extra Modules - common things people would want to add with the benefit of a pre made skin button
        ###########################################

        # Advanced Help Menu
        if mode == 4:
            try:  import menu_guis
            except ImportError:  dialog.ok('Help', 'Ironically Help Not available in skin "' + skin_user + '"')
            else:  menu_guis.help_Menu()


        # refresh inis
        if mode == 20:
            try:  import main_ini
            #except ImportError:  dialog.ok('Refresh', 'Please refresh addons in settings with skin "' + skin_user + '"')
            except ImportError:  xbmc.executebuiltin('RunScript(special://home/addons/'+ADDONID_CORE+'/ReloadAddonFolders.py)')
            else:
                main_ini.failsafes()
                if main_ini.StartCreate():
                    main_ini._refresh_subs_builtin()   # Recreate addon sub .ini taken from custom addonfolders.list
                    main_ini._recreate_subini()   # Recreate addons_subscriptions.ini taken from folders.list if in settings
                    main_ini._refresh_subs('special://profile/addon_data/'+ADDONID_CORE+'/folders.list')   # Recreate addons_subscriptions.ini taken from folders.list
                    main_ini._recreate_addonini() # Recreate main addons.ini
                    _reopen()


        # Extra custom Title search
        # 80000 this is entirely done inside the gui.py
        if mode == 21:
            try:  import menu_lookups
            except ImportError:  dialog.ok('Search Title', 'Not available in this skin "' + skin_user + '"')
            else:
                program = '(No Title)';season = '';episode = '';language = 'en';description = ''
                menu_lookups.lookups_menu(program,season,episode,language,description) # Lookups Menus


        # play url directly from ini
        if mode == 23:
            xbmcgui.Dialog().notification('Run', 'plugin.video.addons.ini.player', ICON, 1000, False)
            if xbmc.getCondVisibility('System.HasAddon(plugin.video.addons.ini.player)'): xbmc.executebuiltin("RunAddon(plugin.video.addons.ini.player)")
            if not xbmc.getCondVisibility('System.HasAddon(plugin.video.addons.ini.player)'):
                try:  xbmc.executebuiltin("ActivateWindow(10025,plugin://"+ADDONID+"/main_iniplayer,return)")
                except: pass


        # search channel in ini
        if mode == 22:
            xbmcgui.Dialog().notification('Run', 'plugin.video.addons.ini.search', ICON, 1000, False)
            if xbmc.getCondVisibility('System.HasAddon(plugin.video.addons.ini.search)'): xbmc.executebuiltin("RunAddon(plugin.video.addons.ini.search)")
            if not xbmc.getCondVisibility('System.HasAddon(plugin.video.addons.ini.search)'):
                try:  xbmc.executebuiltin("ActivateWindow(10025,plugin://"+ADDONID+"/search_dialog,return)")
                except: pass


        # ffmpeg record
        if mode == 30:
            try:  import skin_record
            except ImportError:  dialog.ok('Record', 'Not available in this skin "' + skin_user + '"')
            else:  skin_record.record_Menu()
        
        
        # Reset Database
        if mode == 666:
            xbmc.executebuiltin('XBMC.ActivateWindow(home)')
            xbmc.sleep(666)
            try:  import menu_guis
            except ImportError:  xbmc.executebuiltin('RunScript(special://home/addons/'+ADDONID_CORE+'/ResetDatabase.py, 1)')
            else:  menu_guis.deletedatabase_Menu()
            #RUN = 'RunAddon('+ADDONID+')'
            #RUN = 'RunScript('+ADDONID_CORE+')'
            #xbmc.executebuiltin(RUN)

    xbmcplugin.endOfDirectory(int(sys.argv[1]))
