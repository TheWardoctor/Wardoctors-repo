import urllib,urllib2,sys,re,xbmcplugin,xbmcgui,xbmcaddon,datetime,os,json,base64,plugintools
import stargate
import common,xbmcvfs,zipfile,downloader,extract
import xml.etree.ElementTree as ElementTree
reload(sys)
dialog       =  xbmcgui.Dialog()
sys.setdefaultencoding('utf8')
SKIN_VIEW_FOR_MOVIES=""
Bananas = 'cGx1Z2luLnZpZGVvLnN0YXJnYXRl'
addonDir = plugintools.get_runtime_path()
global kontroll
background = "YmFja2dyb3VuZC5wbmc=" 
defaultlogo = "ZGVmYXVsdGxvZ28ucG5n" 
hometheater = "aG9tZXRoZWF0ZXIuanBn"
noposter = "bm9wb3N0ZXIuanBn"
theater = "dGhlYXRlci5qcGc="
addonxml = "YWRkb24ueG1s"
addonpy = "ZGVmYXVsdC5weQ=="
icon = "aWNvbi5wbmc="
fanart = "ZmFuYXJ0LmpwZw=="
message = "R0VUIElUIFVQIFlFUiE="

def run():
    global pnimi
    global televisioonilink
    global filmilink
    global andmelink
    global uuenduslink
    global lehekylg
    global LOAD_LIVE
    global uuendused
    global vanemalukk
    global version
    version = int(get_live("MQ=="))
    kasutajanimi=plugintools.get_setting("Username")
    salasona=plugintools.get_setting("Password")
    if not kasutajanimi:
        kasutajanimi = "NONE"
        salasona="NONE"
    lehekylg=get_live("aHR0cDovL3Nnc3RyZWFtcy50dg==")
    pordinumber=get_live("MjU0NjE=")
	
    uuendused=plugintools.get_setting(sync_data("dXVlbmR1c2Vk"))
    vanemalukk=plugintools.get_setting(sync_data("dmFuZW1hbHVraw=="))
    pnimi = get_live("T25lIFZpZXcg")
    LOAD_LIVE = os.path.join( plugintools.get_runtime_path() , "resources" , "art" )
    plugintools.log(pnimi+get_live("U3RhcnRpbmcgdXA="))
    televisioonilink = get_live("JXM6JXMvZW5pZ21hMi5waHA/dXNlcm5hbWU9JXMmcGFzc3dvcmQ9JXMmdHlwZT1nZXRfbGl2ZV9jYXRlZ29yaWVz")%(lehekylg,pordinumber,kasutajanimi,salasona)
    filmilink = vod_channels("JXM6JXMvZW5pZ21hMi5waHA/dXNlcm5hbWU9JXMmcGFzc3dvcmQ9JXMmdHlwZT1nZXRfdm9kX2NhdGVnb3JpZXM=")%(lehekylg,pordinumber,kasutajanimi,salasona)
    andmelink = vod_channels("JXM6JXMvcGFuZWxfYXBpLnBocD91c2VybmFtZT0lcyZwYXNzd29yZD0lcw==")%(lehekylg,pordinumber,kasutajanimi,salasona)
    params = plugintools.get_params()

    if params.get("action") is None:
        peamenyy(params)
    else:
        action = params.get("action")
        exec action+"(params)"
    plugintools.close_item_list()

def peamenyy(params):
    plugintools.log(pnimi+vod_channels("TWFpbiBNZW51")+repr(params))
    load_channels()
    if not lehekylg:
        plugintools.open_settings_dialog()

    channels = kontroll()
    if channels == 1 and stargate.mode != 5 and stargate.mode != 1:
        plugintools.log(pnimi+vod_channels("TG9naW4gU3VjY2VzcyAtIFdhcmRvY3RvciBXaW5zIQ=="))
        plugintools.addItem('[B]Stargate Guide[/B]','guide',8,stargate.Images + 'tardis.png',stargate.Images + 'background.png')
        plugintools.add_item( action=vod_channels("ZXhlY3V0ZV9haW5mbw=="),   title="[B]Account Information[/B]", thumbnail=os.path.join(LOAD_LIVE,vod_channels("bXlhY2MucG5n")), fanart=os.path.join(LOAD_LIVE,vod_channels("YmFja2dyb3VuZC5wbmc=")) ,  folder=True )
        plugintools.add_item( action=vod_channels("c2VjdXJpdHlfY2hlY2s="),  title="[B]Live TV[/B]" , thumbnail=os.path.join(LOAD_LIVE,vod_channels("bGl2ZXR2LnBuZw==")) , fanart=os.path.join(LOAD_LIVE,vod_channels("YmFja2dyb3VuZC5wbmc=")) ,  folder=True )
        plugintools.add_item( action=vod_channels("ZGV0ZWN0X21vZGlmaWNhdGlvbg=="),   title=vod_channels("W0JdVmlkZW8gT24gRGVtYW5kWy9CXQ==") , thumbnail=os.path.join(LOAD_LIVE,vod_channels("dm9kLnBuZw==")), fanart=os.path.join(LOAD_LIVE,vod_channels("YmFja2dyb3VuZC5wbmc=")) ,  folder=True )
        plugintools.addItem('[B]Tardis Fixtures[/B]','fixtures',13,stargate.Images + 'fixtures.png',stargate.Images + 'background.png')
        plugintools.add_item( action=vod_channels("bGljZW5zZV9jaGVjaw=="), title="[B]Settings[/B]" , thumbnail=os.path.join(LOAD_LIVE,vod_channels("c2V0dGluZ3MucG5n")), fanart=os.path.join(LOAD_LIVE,vod_channels("YmFja2dyb3VuZC5wbmc=")) ,  folder=False )
        if not xbmc.getCondVisibility('System.HasAddon(pvr.iptvsimple)'):
            plugintools.addItem('[B]Setup PVR Client with Stargate Streams[/B]','pvr',10,stargate.Images + 'pvr.png',stargate.Images + 'background.png')
        else:
            plugintools.addItem('[B]Launch PVR Stargate Streams[/B]','pvr',11,stargate.Images + 'pvr.png',stargate.Images + 'background.png')
        plugintools.addItem('[B]Run Speedtest[/B]','speed',9,stargate.Images + 'speed.png',stargate.Images + 'background.png')
        stargate.AddDir('[B][COLOR=red]Clear Cache[/B][/COLOR]','Clear Cache',7,stargate.Images + 'cache.png')
    elif channels != 1 and stargate.mode != 1:
        plugintools.add_item( action=vod_channels("bGljZW5zZV9jaGVjaw=="), title="[B]Step 1. Enter Your Stargate Streams Login Credentials.[/B]" , thumbnail=os.path.join(LOAD_LIVE,vod_channels("c2V0dGluZ3MucG5n")), folder=False )	
        plugintools.add_item( action=vod_channels("bGljZW5zZV9jaGVjazI="), title="[B]Step 2. Click Here to Login.[/B]" , thumbnail=os.path.join(LOAD_LIVE,vod_channels("c2V0dGluZ3MucG5n")), folder=False )	
    if plugintools.get_setting("improve")=="true":
        advancedsettings = xbmc.translatePath(sync_data("c3BlY2lhbDovL3VzZXJkYXRhL2FkdmFuY2Vkc2V0dGluZ3MueG1s")) ##System advanced settings##
        if os.path.exists(advancedsettings):
            file = open( os.path.join(plugintools.get_runtime_path(),vod_channels("cmVzb3VyY2Vz"),sync_data("YWR2YW5jZWRzZXR0aW5ncy54bWw=")) ) ##app advanced settings##
            data = file.read()
            file.close()
            file = open(advancedsettings,"w")
            file.write(data)
            file.close()

def license_check(params):
    plugintools.log(pnimi+get_live("U2V0dGluZ3MgbWVudSAtIFdhcmRvY3RvciB3aW5zIQ==")+repr(params))
    plugintools.open_settings_dialog()
def license_check2(params):
    xbmc.executebuiltin('Container.Refresh')
def security_check(params):
    plugintools.log(pnimi+sync_data("TGl2ZSBNZW51")+repr(params))
    request = urllib2.Request(televisioonilink, headers={"Accept" : "application/xml"})
    u = urllib2.urlopen(request)
    tree = ElementTree.parse(u)
    rootElem = tree.getroot()
    for channel in tree.findall(sync_data("Y2hhbm5lbA==")):
        kanalinimi = channel.find(get_live("dGl0bGU=")).text
        kanalinimi = base64.b64decode(kanalinimi)
        kategoorialink = channel.find(vod_channels("cGxheWxpc3RfdXJs")).text
        CatID = channel.find(get_live("Y2F0ZWdvcnlfaWQ=")).text        
        plugintools.add_item( action=get_live("c3RyZWFtX3ZpZGVv"), title=kanalinimi , url=CatID , thumbnail=os.path.join(LOAD_LIVE,sync_data("bGl2ZXR2LnBuZw==")) , fanart=os.path.join(LOAD_LIVE,sync_data("dGhlYXRlci5qcGc=")) ,info_labels=kanalinimi, folder=True )
	                            
    plugintools.set_view(plugintools.MOVIES)

def detect_modification(params):
    plugintools.log(pnimi+vod_channels("Vk9EIE1lbnUg")+repr(params))
    request = urllib2.Request(filmilink, headers={"Accept" : "application/xml"})
    u = urllib2.urlopen(request)
    tree = ElementTree.parse(u)
    rootElem = tree.getroot()
    for channel in tree.findall(sync_data("Y2hhbm5lbA==")):
        filminimi = channel.find(get_live("dGl0bGU=")).text
        filminimi = base64.b64decode(filminimi)
        kategoorialink = channel.find(vod_channels("cGxheWxpc3RfdXJs")).text
        plugintools.add_item( action=vod_channels("Z2V0X215YWNjb3VudA=="), title=filminimi , url=kategoorialink , thumbnail=os.path.join(LOAD_LIVE,sync_data("dm9kLnBuZw==")) , fanart=os.path.join(LOAD_LIVE,sync_data("dGhlYXRlci5qcGc=")) , folder=True )
	
    plugintools.set_view(plugintools.MOVIES)

def stream_video(params):
    plugintools.log(pnimi+sync_data("TGl2ZSBDaGFubmVscyBNZW51IA==")+repr(params))
    plugintools._log(vod_channels("V2FyZG9jdG9yIFdpbnMh"))
    kasutajanimi=plugintools.get_setting("Username")
    salasona=plugintools.get_setting("Password")
    CatID = params.get(get_live("dXJs")) #description
    url = get_live("aHR0cDovL3Nnc3RyZWFtcy50djoyNTQ2MS9lbmlnbWEyLnBocD91c2VybmFtZT0lcyZwYXNzd29yZD0lcyZ0eXBlPWdldF9saXZlX3N0cmVhbXMmY2F0X2lkPSVz")%(kasutajanimi,salasona,CatID)
    request = urllib2.Request(url, headers={"Accept" : "application/xml"})
    u = urllib2.urlopen(request)
    tree = ElementTree.parse(u)
    rootElem = tree.getroot()
    for channel in tree.findall(sync_data("Y2hhbm5lbA==")): #channel
        kanalinimi = channel.find(get_live("dGl0bGU=")).text #title
        kanalinimi = base64.b64decode(kanalinimi)
        kanalinimi = kanalinimi.partition("[")
        striimilink = channel.find(get_live("c3RyZWFtX3VybA==")).text #stream_url
        poo = striimilink
        if "http://sgstreams.tv/enigma2.php"  in striimilink: 
            poo = striimilink.split(kasutajanimi,1)[1]
            poo = poo.split(salasona,1)[1]
            poo = poo.split("/",1)[1]            
        pilt = channel.find(vod_channels("ZGVzY19pbWFnZQ==")).text #desc_image
        kava = kanalinimi[1]+kanalinimi[2]
        kava = kava.partition("]")
        kava = kava[2]
        kava = kava.partition("   ")
        kava = kava[2]
        shou = get_live("W0NPTE9SIHdoaXRlXSVzIFsvQ09MT1Jd")%(kanalinimi[0])+kava #[COLOR white]%s [/COLOR]
        kirjeldus = channel.find(sync_data("ZGVzY3JpcHRpb24=")).text #description
        if kirjeldus:
           kirjeldus = base64.b64decode(kirjeldus)
           nyyd = kirjeldus.partition("(")
           nyyd = sync_data("W0NPTE9SIGJsdWVdT24gTm93OlsvQ09MT1Jd") +nyyd[0]
           jargmine = kirjeldus.partition(")\n")
           jargmine = jargmine[2].partition("(")
           jargmine = sync_data("W0NPTE9SIHllbGxvd11PbiBOZXh0OlsvQ09MT1Jd") +jargmine[0] #shou
           kokku = nyyd+jargmine
        else:
           kokku = ""
        if pilt:
           plugintools.add_item( action=sync_data("cnVuX2Nyb25qb2I="), title=shou , url=poo, thumbnail=pilt, plot=kokku, fanart=os.path.join(LOAD_LIVE,sync_data("dGhlYXRlci5qcGc=")), extra="", isPlayable=True, folder=False )
        else:
           plugintools.add_item( action=sync_data("cnVuX2Nyb25qb2I="), title=shou , url=poo, thumbnail=os.path.join(LOAD_LIVE,vod_channels("YWxsY2hhbm5lbHMucG5n")) , plot=kokku, fanart=os.path.join(LOAD_LIVE,sync_data("dGhlYXRlci5qcGc=")) , extra="", isPlayable=True, folder=False )
    plugintools.set_view(plugintools.MOVIES)
#    xbmc.executebuiltin(vod_channels("Q29udGFpbmVyLlNldFZpZXdNb2RlKDUwKQ=="))
		
def get_myaccount(params):
        plugintools.log(pnimi+get_live("Vk9EIGNoYW5uZWxzIG1lbnUg")+repr(params))
        plugintools._log(vod_channels("V2FyZG9jdG9yIHdpbnMh"))
        if vanemalukk == "true":
           pealkiri = params.get("title")
           vanema_lukk(pealkiri)
        purl = params.get("url")
        request = urllib2.Request(purl, headers={"Accept" : "application/xml"})
        u = urllib2.urlopen(request)
        tree = ElementTree.parse(u)
        rootElem = tree.getroot()
        for channel in tree.findall("channel"):
            try:
                pealkiri = channel.find("title").text
                pealkiri = base64.b64decode(pealkiri)
                pealkiri = pealkiri.encode("utf-8")
                striimilink = channel.find("stream_url").text
                pilt = channel.find("desc_image").text
                kirjeldus = channel.find("description").text
                if kirjeldus:
                   kirjeldus = base64.b64decode(kirjeldus)
                if pilt:
                   plugintools.add_item( action="restart_service", title=pealkiri , url=striimilink, thumbnail=pilt, plot=kirjeldus, fanart=os.path.join(LOAD_LIVE,sync_data("dGhlYXRlci5qcGc=")) , extra="", isPlayable=True, folder=False )
                else:
                   plugintools.add_item( action="restart_service", title=pealkiri , url=striimilink, thumbnail=os.path.join("dm9kLnBuZw=="), plot=kirjeldus, fanart=os.path.join(LOAD_LIVE,sync_data("dGhlYXRlci5qcGc=")) , extra="", isPlayable=True, folder=False )
            except:
                kanalinimi = channel.find("title").text
                kanalinimi = base64.b64decode(kanalinimi)
                kategoorialink = channel.find("playlist_url").text
                plugintools._log(kategoorialink)
                CatID = channel.find("category_id").text
                plugintools.add_item( action=get_live("Z2V0X215YWNjb3VudA=="), title=kanalinimi , url=kategoorialink , thumbnail=os.path.join(LOAD_LIVE,sync_data("dm9kLnBuZw==")) , fanart=os.path.join(LOAD_LIVE,sync_data("dGhlYXRlci5qcGc=")) ,info_labels=kanalinimi, folder=True )

        plugintools.set_view(plugintools.MOVIES)
#        xbmc.executebuiltin('Container.SetViewMode(54)')

# televisioonilink = Live channels enigma2.php?username=%s&password=%s&type=get_live_categories
# 				   = VoD Folders   enigma2.php?username=%s&password=%s&type=get_vod_scategories&scat_id=82
# filmilink 	   = On Demand Section enigma2.php?username=%s&password=%s&type=get_vod_categories
# andmelink 	   = EPG JSON DATA panel_api.php?username=%s&password=%s
	
def run_cronjob(params):
    kasutajanimi=plugintools.get_setting("Username")
    salasona=plugintools.get_setting("Password")
    lopplink = params.get("url")
    lopplink = lopplink.replace("%username", kasutajanimi)
    lopplink = lopplink.replace("%password", salasona)
#    lopplink = lopplink.replace(".ts", ".m3u8")
    listitem = xbmcgui.ListItem(path=lopplink)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)

def sync_data(channel):
    video = base64.b64decode(channel)
    return video

def restart_service(params):
    lopplink = params.get(vod_channels("dXJs"))
    plugintools.play_resolved_url( lopplink )

def grab_epg():
    req = urllib2.Request(andmelink)
    req.add_header(sync_data("VXNlci1BZ2VudA==") , vod_channels("R2V0IGl0IHVwIHllciBNaWtrTSE="))
    response = urllib2.urlopen(req)
    link=response.read()
    jdata = json.loads(link.decode('utf8'))
    response.close()
    if jdata:
       plugintools.log(pnimi+sync_data("amRhdGEgbG9hZGVkIA=="))
       return jdata
def kontroll():
    randomstring = grab_epg()
    kasutajainfo = randomstring[sync_data("dXNlcl9pbmZv")]
    kontroll = kasutajainfo[get_live("YXV0aA==")]
    return kontroll
def get_live(channel):
    video = base64.b64decode(channel)
    return video
def execute_ainfo(params):
    plugintools.log(pnimi+get_live("TXkgYWNjb3VudCBNZW51IA==")+repr(params))
    andmed = grab_epg()
    kasutajaAndmed = andmed[sync_data("dXNlcl9pbmZv")]
    seis = kasutajaAndmed[get_live("c3RhdHVz")]
    aegub = kasutajaAndmed[sync_data("ZXhwX2RhdGU=")]
    if aegub:
       aegub = datetime.datetime.fromtimestamp(int(aegub)).strftime('%d/%m/%Y %H:%M')
    else:
       aegub = vod_channels("TmV2ZXI=")
    leavemealone = kasutajaAndmed[get_live("bWF4X2Nvbm5lY3Rpb25z")]
    polarbears = kasutajaAndmed[sync_data("dXNlcm5hbWU=")]
    plugintools.add_item( action="",   title=sync_data("W0NPTE9SID0gd2hpdGVdVXNlcjogWy9DT0xPUl0=")+polarbears , thumbnail=os.path.join(LOAD_LIVE,vod_channels("bXlhY2MucG5n")) , fanart=os.path.join(LOAD_LIVE,sync_data("dGhlYXRlci5qcGc=")) , folder=False )
    plugintools.add_item( action="",   title=sync_data("W0NPTE9SID0gd2hpdGVdU3RhdHVzOiBbL0NPTE9SXQ==")+seis , thumbnail=os.path.join(LOAD_LIVE,vod_channels("bXlhY2MucG5n")) , fanart=os.path.join(LOAD_LIVE,sync_data("dGhlYXRlci5qcGc=")) , folder=False )
    plugintools.add_item( action="",   title=get_live("W0NPTE9SID0gd2hpdGVdRXhwaXJlczogWy9DT0xPUl0=")+aegub , thumbnail=os.path.join(LOAD_LIVE,vod_channels("bXlhY2MucG5n")) , fanart=os.path.join(LOAD_LIVE,sync_data("dGhlYXRlci5qcGc=")) , folder=False )
    plugintools.add_item( action="",   title=vod_channels("W0NPTE9SID0gd2hpdGVdTWF4IGNvbm5lY3Rpb25zOiBbL0NPTE9SXQ==")+leavemealone , thumbnail=os.path.join(LOAD_LIVE,vod_channels("bXlhY2MucG5n")) , fanart=os.path.join(LOAD_LIVE,sync_data("dGhlYXRlci5qcGc=")) , folder=False )
	
    plugintools.set_view(plugintools.MOVIES)
def vanema_lukk(name):
        plugintools.log(pnimi+sync_data("UGFyZW50YWwgbG9jayA="))
        a = 'XXX', 'Adult', 'Adults','ADULT','ADULTS','adult','adults','Porn','PORN','porn','Porn','xxx'
        if any(s in name for s in a):
           xbmc.executebuiltin((u'XBMC.Notification("Parental Lock", "Channels may contain adult content", 2000)'))
           text = plugintools.keyboard_input(default_text="", title=get_live("UGFyZW50YWwgbG9jaw=="))
           if text==plugintools.get_setting(sync_data("dmFuZW1ha29vZA==")):
              return
           else:
              exit()
        else:
           name = ""
def DownloaderClass(url,dest):
    dp = xbmcgui.DialogProgress()
    dp.create(sync_data("R2V0dGluZyB1cGRhdGU="),get_live("RG93bmxvYWRpbmc="))
    urllib.urlretrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))
def check_user():
    plugintools.message(get_live("RVJST1I="),vod_channels("VU5BVVRIT1JJWkVEIEVESVQgT0YgQURET04h"))
    sys.exit()
def _pbhook(numblocks, blocksize, filesize, url=None,dp=None):
    try:
        percent = min((numblocks*blocksize*100)/filesize, 100)
        print percent
        dp.update(percent)
    except:
        percent = 100
        dp.update(percent)
    if dp.iscanceled(): 
        print "DOWNLOAD CANCELLED"
        dp.close()
def load_channels():
    statinfo = os.stat(LOAD_LIVE+"/"+get_live("YmFja2dyb3VuZC5wbmc="))

def vod_channels(channel):
    video = base64.b64decode(channel)
    return video

run()
