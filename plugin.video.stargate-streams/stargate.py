import threading,xbmc,xbmcplugin,xbmcgui,re,os,xbmcaddon,sys
import shutil,plugintools
import glob
import GoDev
import zipfile
import urlparse
import urllib,urllib2,json
import common,xbmcvfs,downloader,extract
from datetime import datetime, timedelta
import base64, time
import unicodedata
AddonID = 'plugin.video.stargate-streams'
ADDON=xbmcaddon.Addon(id='plugin.video.stargate-streams')
__icon__        = ADDON.getAddonInfo('icon')
__self__        = xbmcaddon.Addon(id='plugin.video.stargate-streams')
dialog       =  xbmcgui.Dialog()
dialogprocess =  xbmcgui.DialogProgress()
log_path   =  xbmc.translatePath('special://logpath/')
USERDATA     =  xbmc.translatePath(os.path.join('special://home/userdata',''))
GUI          =  xbmc.translatePath(os.path.join(USERDATA,'guisettings.xml'))
GUIFIX       =  xbmc.translatePath(os.path.join(USERDATA,'guifix.xml'))
INSTALL      =  xbmc.translatePath(os.path.join(USERDATA,'install.xml'))
FAVS         =  xbmc.translatePath(os.path.join(USERDATA,'favourites.xml'))
SOURCE       =  xbmc.translatePath(os.path.join(USERDATA,'sources.xml'))
ADVANCED     =  xbmc.translatePath(os.path.join(USERDATA,'advancedsettings.xml'))
PROFILES     =  xbmc.translatePath(os.path.join(USERDATA,'profiles.xml'))
RSS          =  xbmc.translatePath(os.path.join(USERDATA,'RssFeeds.xml'))
KEYMAPS      =  xbmc.translatePath(os.path.join(USERDATA,'keymaps','keyboard.xml'))
HOME         =  xbmc.translatePath('special://home/')
zip          =  ADDON.getSetting('zip')
USB          =  xbmc.translatePath(os.path.join(zip))
skin =  xbmc.getSkinDir()
Images = xbmc.translatePath(os.path.join('special://home','addons',AddonID,'resources/art/'));
Username=plugintools.get_setting("Username")
Password=plugintools.get_setting("Password")
ServerURL = "http://sgstreams.tv:25461//get.php?username=%s&password=%s&type=m3u&output=mpegts"%(Username,Password)

try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database
def Add_Directory_Item(handle, url, listitem, isFolder):
    xbmcplugin.addDirectoryItem(handle, url, listitem, isFolder)
def Fix_Special(url):
    dialogprocess.create("Kodi UK","Renaming paths...",'', 'Please Wait')
    for root, dirs, files in os.walk(url):  #Search all xml files and replace physical with special
        for file in files:
            if file.endswith(".xml"):
                 dialogprocess.update(0,"Fixing",file, 'Please Wait')
                 a=open((os.path.join(root, file))).read()
                 b=a.replace(HOME, 'special://home/')
                 f = open((os.path.join(root, file)), mode='w')
                 f.write(str(b))
                 f.close()

def correctPVR():

	flawiptv = xbmcaddon.Addon('plugin.video.stargate-streams')
	username_text = flawiptv.getSetting(id='Username')
	password_text = flawiptv.getSetting(id='Password')
	jsonSetPVR = '{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"pvrmanager.enabled", "value":true},"id":1}'
	IPTVon 	   = '{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","params":{"addonid":"pvr.iptvsimple","enabled":true},"id":1}'
	nulldemo   = '{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","params":{"addonid":"pvr.demo","enabled":false},"id":1}'
	loginurl   = "http://sgstreams.tv:25461/get.php?username=" + username_text + "&password=" + password_text + "&type=m3u_plus&output=mpegts"
	EPGurl     = "http://sgstreams.tv:25461/xmltv.php?username=" + username_text + "&password=" + password_text + "&type=m3u_plus&output=mpegts"

	xbmc.executeJSONRPC(jsonSetPVR)
	xbmc.executeJSONRPC(IPTVon)
	xbmc.executeJSONRPC(nulldemo)
	
	moist = xbmcaddon.Addon('pvr.iptvsimple')
	moist.setSetting(id='m3uUrl', value=loginurl)
	moist.setSetting(id='epgUrl', value=EPGurl)
	moist.setSetting(id='m3uCache', value="false")
	moist.setSetting(id='epgCache', value="false")
	dialog.ok("Stargate Streams",'IPTV Simple Client set-up is complete.',' ','Please allow it time to load the EPG to avoid issues.')
	xbmc.executebuiltin("Container.Refresh")

def LaunchPVR():
	xbmc.executebuiltin('ActivateWindow(TVGuide)')

def speed():
	xbmc.executebuiltin('Runscript("special://home/addons/plugin.video.stargate-streams/speedtest.py")')
	
def guide():
	xbmc.executebuiltin('Runscript("special://home/addons/script.stargate.guide/addon.py")')

def fixtures():
	xbmc.executebuiltin('ActivateWindow(10001,plugin://plugin.program.tardis-fixtures,return)')

def Clear_Cache():
    choice = xbmcgui.Dialog().yesno('Clear your Cache?', 'This will Refresh your Live Events', 'It can help with Buffering issues also','If you have any issues, Make sure you are in our facebook group - Were here to help.', nolabel='Cancel',yeslabel='Delete')
    if choice == 1:
        GoDev.Wipe_Cache()

def Read_Zip(url):
    z = zipfile.ZipFile(url, "r")
    for filename in z.namelist():
        if 'guisettings.xml' in filename:
            a = z.read(filename)
            r='<setting type="(.+?)" name="%s.(.+?)">(.+?)</setting>'% skin
            match=re.compile(r).findall(a)
            for type,string,setting in match:
                setting=setting.replace('&quot;','') .replace('&amp;','&') 
                xbmc.executebuiltin("Skin.Set%s(%s,%s)"%(type.title(),string,setting))
        if 'favourites.xml' in filename:
            a = z.read(filename)
            f = open(FAVS, mode='w')
            f.write(a)
            f.close()
        if 'sources.xml' in filename:
            a = z.read(filename)
            f = open(SOURCE, mode='w')
            f.write(a)
            f.close()
        if 'advancedsettings.xml' in filename:
            a = z.read(filename)
            f = open(ADVANCED, mode='w')
            f.write(a)
            f.close()
        if 'RssFeeds.xml' in filename:
            a = z.read(filename)
            f = open(RSS, mode='w')
            f.write(a)
            f.close()
        if 'keyboard.xml' in filename:
            a = z.read(filename)
            f = open(KEYMAPS, mode='w')
            f.write(a)
            f.close()  	
def AddDir(name, url, mode, iconimage, description="", isFolder=True, background=None):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&description="+urllib.quote_plus(description)
    a=sys.argv[0]+"?url=None&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&description="+urllib.quote_plus(description)
    print name.replace('-[US]','').replace('-[EU]','').replace('[COLOR yellow]','').replace('[/COLOR]','').replace(' (G)','')+'='+a
    liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={ "Title": name, "Plot": description})
    liz.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=isFolder)

def addXMLMenu(name,url,mode,iconimage,fanart,description):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&fanart="+urllib.quote_plus(fanart)+"&description="+urllib.quote_plus(description)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": description } )
        liz.setProperty( "Fanart_Image", fanart )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        return ok
def OPEN_URL(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    return link

def ExtraMenu():
    link = OPEN_URL('http://futurestreams.tk/Backup/Downloads/ExtrasList2.xml').replace('\n','').replace('\r','')  #Spaf
    match = re.compile('name="(.+?)".+?rl="(.+?)".+?mg="(.+?)".+?anart="(.+?)".+?escription="(.+?)"').findall(link)
    for name,url,iconimage,FanArt,description in match:
        addXMLMenu(name,url,6,iconimage,FanArt,description)
		
def Archive_File(sourcefile, destfile):
    zipobj = zipfile.ZipFile(destfile , 'w', zipfile.ZIP_DEFLATED)
    rootlen = len(sourcefile)
    for_progress = []
    ITEM =[]
    dialogprocess.create("Kodi UK","Archiving...",'', 'Please Wait')
    for base, dirs, files in os.walk(sourcefile):
        for file in files:
            ITEM.append(file)
    N_ITEM =len(ITEM)
    for base, dirs, files in os.walk(sourcefile):
        for file in files:
            for_progress.append(file) 
            progress = len(for_progress) / float(N_ITEM) * 100  
            dialogprocess.update(int(progress),"Backing Up",'[COLOR yellow]%s[/COLOR]'%file, 'Please Wait')
            dialogprocess.update(int(progress),"Backing Up",'[COLOR yellow]%s[/COLOR]'%file, 'Please Wait')
            fn = os.path.join(base, file)
            if not 'temp' in dirs:
                if not 'plugin.program.kodiuktv' in dirs:
                   import time
                   FORCE= '01/01/1980'
                   FILE_DATE=time.strftime('%d/%m/%Y', time.gmtime(os.path.getmtime(fn)))
                   if FILE_DATE > FORCE:
                       zipobj.write(fn, fn[rootlen:])  
    zipobj.close()
    dialogprocess.close()	
def Delete_Packages():
    print 'DELETING PACKAGES'
    packages_cache_path = xbmc.translatePath(os.path.join('special://home/addons/packages', ''))
    for root, dirs, files in os.walk(packages_cache_path):
        file_count = 0
        file_count += len(files)
    # Count files and give option to delete
        if file_count > 0:
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))
def Delete_Logs():  
    for infile in glob.glob(os.path.join(log_path, 'xbmc_crashlog*.*')):
         File=infile
         print infile
         os.remove(infile)
         dialog = xbmcgui.Dialog()
         dialog.ok("Crash Logs Deleted", "Your old crash logs have now been deleted.")
def Delete_Userdata():
    print '############################################################       DELETING USERDATA             ###############################################################'
    addon_data_path = xbmc.translatePath(os.path.join('special://home/userdata/addon_data', ''))
    for root, dirs, files in os.walk(addon_data_path):
        file_count = 0
        file_count += len(files)
    # Count files and give option to delete
        if file_count >= 0:
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))    
def Wipe_Cache():
    xbmc_cache_path = os.path.join(xbmc.translatePath('special://home'), 'cache')
    if os.path.exists(xbmc_cache_path)==True:
        for root, dirs, files in os.walk(xbmc_cache_path):
            file_count = 0
            file_count += len(files)
            if file_count > 0:
                for f in files:
                    try:
                        os.unlink(os.path.join(root, f))
                    except:
                        pass
                for d in dirs:
                    try:
                        shutil.rmtree(os.path.join(root, d))
                    except:
                        pass
    if xbmc.getCondVisibility('system.platform.ATV2'):
        atv2_cache_a = os.path.join('/private/var/mobile/Library/Caches/AppleTV/Video/', 'Other')
        for root, dirs, files in os.walk(atv2_cache_a):
            file_count = 0
            file_count += len(files)
            if file_count > 0:
                for f in files:
                    os.unlink(os.path.join(root, f))
                for d in dirs:
                    shutil.rmtree(os.path.join(root, d))
        atv2_cache_b = os.path.join('/private/var/mobile/Library/Caches/AppleTV/Video/', 'LocalAndRental')        
        for root, dirs, files in os.walk(atv2_cache_b):
            file_count = 0
            file_count += len(files)
            if file_count > 0:
                for f in files:
                    os.unlink(os.path.join(root, f))
                for d in dirs:
                    shutil.rmtree(os.path.join(root, d))
    # Set path to script.module.simple.downloader cache files
    downloader_cache_path = os.path.join(xbmc.translatePath('special://profile/addon_data/script.module.simple.downloader'), '')
    if os.path.exists(downloader_cache_path)==True:    
        for root, dirs, files in os.walk(downloader_cache_path):
            file_count = 0
            file_count += len(files)
            if file_count > 0:
                for f in files:
                    os.unlink(os.path.join(root, f))
                for d in dirs:
                    shutil.rmtree(os.path.join(root, d))
    # Set path to script.image.music.slideshow cache files
    imageslideshow_cache_path = os.path.join(xbmc.translatePath('special://profile/addon_data/script.image.music.slideshow/cache'), '')
    if os.path.exists(imageslideshow_cache_path)==True:    
        for root, dirs, files in os.walk(imageslideshow_cache_path):
            file_count = 0
            file_count += len(files)
            if file_count > 0:
                for f in files:
                    os.unlink(os.path.join(root, f))
                for d in dirs:
                    shutil.rmtree(os.path.join(root, d))
    # Set path to BBC iPlayer cache files
    iplayer_cache_path= os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.iplayer/iplayer_http_cache'), '')
    if os.path.exists(iplayer_cache_path)==True:    
        for root, dirs, files in os.walk(iplayer_cache_path):
            file_count = 0
            file_count += len(files)
            if file_count > 0:
                for f in files:
                    os.unlink(os.path.join(root, f))
                for d in dirs:
                    shutil.rmtree(os.path.join(root, d))
    itv_cache_path = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.itv/Images'), '')
    if os.path.exists(itv_cache_path)==True:    
        for root, dirs, files in os.walk(itv_cache_path):
            file_count = 0
            file_count += len(files)
            if file_count > 0:
                for f in files:
                    os.unlink(os.path.join(root, f))
                for d in dirs:
                    shutil.rmtree(os.path.join(root, d))
    navix_cache_path= os.path.join(xbmc.translatePath('special://profile/addon_data/script.navi-x/cache'), '')
    if os.path.exists(navix_cache_path)==True:    
        for root, dirs, files in os.walk(navix_cache_path):
            file_count = 0
            file_count += len(files)
            if file_count > 0:
                for f in files:
                    os.unlink(os.path.join(root, f))
                for d in dirs:
                    shutil.rmtree(os.path.join(root, d))
    phoenix_cache_path= os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.phstreams/Cache'), '')
    if os.path.exists(phoenix_cache_path)==True:    
        for root, dirs, files in os.walk(phoenix_cache_path):
            file_count = 0
            file_count += len(files)
            if file_count > 0:
                for f in files:
                    os.unlink(os.path.join(root, f))
                for d in dirs:
                    shutil.rmtree(os.path.join(root, d))
    ramfm_cache_path= os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.audio.ramfm/cache'), '')
    if os.path.exists(ramfm_cache_path)==True:    
        for root, dirs, files in os.walk(ramfm_cache_path):
            file_count = 0
            file_count += len(files)
            if file_count > 0:
                for f in files:
                    os.unlink(os.path.join(root, f))
                for d in dirs:
                    shutil.rmtree(os.path.join(root, d))
    wtf_cache_path = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.whatthefurk/cache'), '')
    if os.path.exists(wtf_cache_path)==True:    
        for root, dirs, files in os.walk(wtf_cache_path):
            file_count = 0
            file_count += len(files)
            if file_count > 0:
                for f in files:
                    os.unlink(os.path.join(root, f))
                for d in dirs:
                    shutil.rmtree(os.path.join(root, d))
    try:
        genesisCache = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.genesis'), 'cache.db')
        dbcon = database.connect(genesisCache)
        dbcur = dbcon.cursor()
        dbcur.execute("DROP TABLE IF EXISTS rel_list")
        dbcur.execute("VACUUM")
        dbcon.commit()
        dbcur.execute("DROP TABLE IF EXISTS rel_lib")
        dbcur.execute("VACUUM")
        dbcon.commit()
    except:
        pass
def Destroy_Path(path):
    dialogprocess.create("Kodi UK ","Cleaning...",'', 'Please Wait')
    shutil.rmtree(path, ignore_errors=True)
def Remove_Textures():
    textures   =  xbmc.translatePath('special://home/userdata/Database/Textures13.db')
    try:
        dbcon = database.connect(textures)
        dbcur = dbcon.cursor()
        dbcur.execute("DROP TABLE IF EXISTS path")
        dbcur.execute("VACUUM")
        dbcon.commit()
        dbcur.execute("DROP TABLE IF EXISTS sizes")
        dbcur.execute("VACUUM")
        dbcon.commit()
        dbcur.execute("DROP TABLE IF EXISTS texture")
        dbcur.execute("VACUUM")
        dbcon.commit()
        dbcur.execute("""CREATE TABLE path (id integer, url text, type text, texture text, primary key(id))""")
        dbcon.commit()
        dbcur.execute("""CREATE TABLE sizes (idtexture integer,size integer, width integer, height integer, usecount integer, lastusetime text)""")
        dbcon.commit()
        dbcur.execute("""CREATE TABLE texture (id integer, url text, cachedurl text, imagehash text, lasthashcheck text, PRIMARY KEY(id))""")
        dbcon.commit()
    except:
        pass
def Read_Zip(url):
    import zipfile
    z = zipfile.ZipFile(url, "r")
    for filename in z.namelist():
        if 'guisettings.xml' in filename:
            a = z.read(filename)
            r='<setting type="(.+?)" name="%s.(.+?)">(.+?)</setting>'% skin
            
            match=re.compile(r).findall(a)
            print match
            for type,string,setting in match:
                setting=setting.replace('&quot;','') .replace('&amp;','&') 
                xbmc.executebuiltin("Skin.Set%s(%s,%s)"%(type.title(),string,setting))  
                
        if 'favourites.xml' in filename:
            a = z.read(filename)
            f = open(FAVS, mode='w')
            f.write(a)
            f.close()  
			               
        if 'sources.xml' in filename:
            a = z.read(filename)
            f = open(SOURCE, mode='w')
            f.write(a)
            f.close()    
                         
        if 'advancedsettings.xml' in filename:
            a = z.read(filename)
            f = open(ADVANCED, mode='w')
            f.write(a)
            f.close()                 

        if 'RssFeeds.xml' in filename:
            a = z.read(filename)
            f = open(RSS, mode='w')
            f.write(a)
            f.close()                 
            
        if 'keyboard.xml' in filename:
            a = z.read(filename)
            f = open(KEYMAPS, mode='w')
            f.write(a)
            f.close()  			
def Check_Path():
    if zip=='':
     if dialog.yesno("Kodi UK Wizard", "You Have Not Set Your Storage Path", 'Set The Storage Path Now ?',''):
        ADDON.openSettings()
        print '######### ZIP DIRECTORY #########'
        for filename in os.listdir(USB):
            print filename			
def RestoreIt():
    import time
    dialog = xbmcgui.Dialog()
    if zip == '':
        dialog.ok('Kodi UK Wizard','You have not set your ZIP Folder.\nPlease update the addon settings and try again.','','')
        ADDON.openSettings(sys.argv[0])
    dialogprocess.create("Kodi UK Wizard","Restoring",'', 'Please Wait')   
    lib=xbmc.translatePath(os.path.join(zip,'backup.zip'))
    Read_Zip(lib)
    dialogprocess.create("Kodi UK Wizard","Checking ",'', 'Please Wait')
    HOME = xbmc.translatePath(os.path.join('special://','home'))
    dialogprocess.update(0,"", "Extracting Zip Please Wait")
    extract.all(lib,HOME,dialogprocess)
    time.sleep(1)
    xbmc.executebuiltin('UpdateLocalAddons ')    
    xbmc.executebuiltin("UpdateAddonRepos")
    time.sleep(1)
    xbmc.executebuiltin('UnloadSkin()') 
    xbmc.executebuiltin('ReloadSkin()')    
    xbmc.executebuiltin("Loadialogprocessrofile(Master user)")
    dialogprocess.close()
    dialog.ok("Kodi UK Wizard", "All Done, DONT PRESS OK", "Wait a 5 minutes and pull the Power","")	
	
def Backupzip():  
    if zip == '':
        dialog.ok('Kodi UK Wizard','You have not set your ZIP Folder.\nPlease update the addon settings and try again.','','')
        ADDON.openSettings(sys.argv[0])
    to_backup = xbmc.translatePath(os.path.join('special://','home'))
    backup_zip = xbmc.translatePath(os.path.join(USB,'backup.zip'))
    Delete_Packages()    
    import zipfile
    
    dialogprocess.create("Kodi UK Wizard","Backing Up",'', 'Please Wait')
    zipobj = zipfile.ZipFile(backup_zip , 'w', zipfile.ZIP_DEFLATED)
    rootlen = len(to_backup)
    for_progress = []
    ITEM =[]
    for base, dirs, files in os.walk(to_backup):
        for file in files:
            ITEM.append(file)
    N_ITEM =len(ITEM)
    for base, dirs, files in os.walk(to_backup):
        for file in files:
            for_progress.append(file) 
            progress = len(for_progress) / float(N_ITEM) * 100  
            dialogprocess.update(int(progress),"Backing Up",'[COLOR yellow]%s[/COLOR]'%file, 'Please Wait')
            fn = os.path.join(base, file)
            if not 'temp' in dirs:
                if not 'plugin.program.kodiuktv' in dirs:
                   import time
                   Spaf= '01/01/1980'
                   FILE_DATE=time.strftime('%d/%m/%Y', time.gmtime(os.path.getmtime(fn)))
                   if FILE_DATE > Spaf:
                       zipobj.write(fn, fn[rootlen:])  
    zipobj.close()
    dialogprocess.close()
    dialog.ok("Kodi UK Wizard", "You Are Now Backed Up", '','')

def Buildlist(url):
    list = common.m3u2list(url)
    for channel in list:
        name = common.GetEncodeString(channel["display_name"])
        AddDir(name ,channel["url"], 3, iconimage, isFolder=False)
		
def PlayUrl(name, url, iconimage=None):
        _NAME_=name
        list = common.m3u2list(ServerURL)
        for channel in list:
            name = common.GetEncodeString(channel["display_name"])
            stream=channel["url"]
            if _NAME_ in name:
                listitem = xbmcgui.ListItem(path=stream, thumbnailImage=iconimage)
                listitem.setInfo(type="Video", infoLabels={ "Title": name })
                xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)				
def Get_Params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?','')
        if (params[len(params)-1] == '/'):
            params = params[0:len(params)-2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0].lower()] = splitparams[1]
    return param
	
params=Get_Params()
url=None
name=None
mode=None
iconimage=None
description=None

try:url = urllib.unquote_plus(params["url"])
except:pass
try:name = urllib.unquote_plus(params["name"])
except:pass
try:iconimage = urllib.unquote_plus(params["iconimage"])
except:pass
try:mode = int(params["mode"])
except:pass
try:description = urllib.unquote_plus(params["description"])
except:pass

if mode == 7:
	Clear_Cache()
elif mode == 5:
	ExtraMenu()
elif mode == 1:
	Buildlist(url)
elif mode == 3:
    PlayUrl(name, url, iconimage)
elif mode == 13:
	fixtures()
elif mode == 8:
	tardis()
elif mode == 9:
	speed()
elif mode == 10:
	correctPVR()
elif mode == 11:
	LaunchPVR()
elif mode == 12:
	runiVue()