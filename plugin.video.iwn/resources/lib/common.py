# #!/usr/bin/env python
####################################################################################################
# Import From other Modules
####################################################################################################
import filecmp
import json
import os
import re
import sys
import urllib
import urllib2
import xbmcplugin
import xbmcgui
import zipfile
from bs4 import BeautifulSoup
from defusedxml.minidom import parse
from shutil import copyfile
from xbmc import log as xbmc_log

####################################################################################################
# Set Variables
####################################################################################################
from resources.lib.const import *

####################################################################################################
# Logging
####################################################################################################
def __log(msg):
    xbmc_log(u'%s: %s' % (ADDON_ID, msg))

####################################################################################################
# Menu Items
####################################################################################################
# Create Menu Item - Link
####################################################################################################
def AddMenuLink(name, url, mode, iconimage):
    __log('Menu Link name - '+str(name))
    __log('Menu Link url - '+str(url))
    __log('Menu Link mode - '+str(mode))
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name=" \
        +urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setProperty('fanart_image', fanart)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

####################################################################################################
# Create Menu Item - Non Link
####################################################################################################
def AddMenuItem(name,iconimage):
    __log('Menu Item name - '+str(name))
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="blank.png", thumbnailImage=iconimage)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url='', listitem=liz, isFolder=False)
    return ok

####################################################################################################
# About Plugin
####################################################################################################
def AboutPlugin():
    AddMenuItem('Name - ' + ADDON_NAME, '')
    AddMenuItem('Path - ' + ADDON_PATH, '')
    AddMenuItem('Version - ' + ADDON_VERSION, '')
    AddMenuItem('Contact - ' + ADDON_CONTACT, '')
    AddMenuItem('GitHub - ' + ADDON_GITHUB, '')

####################################################################################################
# Update Content
####################################################################################################
def GetFile(url, filename, location):
   download_file = urllib2.urlopen(url)
   download_data = download_file.read()
   with open(location+filename, "wb") as downloaded_file:
    downloaded_file.write(download_data)

def UpdateContent():
    if os.path.exists(xbmc.translatePath('special://home/addons/' + ADDON_ID + \
        '/resources/data/plugin.video.iwn-content.zip.md5')):
        copyfile(xbmc.translatePath('special://home/addons/' + ADDON_ID + \
            '/resources/data/plugin.video.iwn-content.zip.md5'), \
            xbmc.translatePath('special://home/addons/' + ADDON_ID + \
            '/resources/data/plugin.video.iwn-content.zip.md5.old'))
    file_location = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/resources/data/')
    GetFile(UPDATE_CONTENT_VERSION, 'iwn.version', file_location)
    content_file = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/resources/data/iwn.version')
    with open(content_file,"r") as version_file:
        version = ""
        lines = version_file.readlines()
        for line in lines:
            version = version + line.strip();
    version_file.close
    __log('Content Version Check - ' + version)
    __log('Addon Version - ' + ADDON_VERSION)
    if version == ADDON_VERSION:
        GetFile(UPDATE_CONTENT_MD5, 'plugin.video.iwn-content.zip.md5', file_location)
        if os.path.exists(xbmc.translatePath('special://home/addons/' + ADDON_ID + \
            '/resources/data/plugin.video.iwn-content.zip.md5.old')):
            if filecmp.cmp(xbmc.translatePath('special://home/addons/' + ADDON_ID + \
                '/resources/data/plugin.video.iwn-content.zip.md5'), \
                xbmc.translatePath('special://home/addons/' + ADDON_ID + \
                '/resources/data/plugin.video.iwn-content.zip.md5.old')):
                if os.path.exists(xbmc.translatePath('special://home/addons/' + ADDON_ID + \
                    '/resources/data/plugin.video.iwn-content.zip.md5.old')):
                    os.remove(xbmc.translatePath('special://home/addons/' + ADDON_ID + \
                        '/resources/data/plugin.video.iwn-content.zip.md5.old'))
                xbmcgui.Dialog().ok(ADDON_NAME, 'No Updates Available...', '', '')
            else:
                if os.path.exists(xbmc.translatePath('special://home/addons/' + ADDON_ID + \
                    '/resources/data/plugin.video.iwn-content.zip')):
                    os.remove(xbmc.translatePath('special://home/addons/' + ADDON_ID + \
                        '/resources/data/plugin.video.iwn-content.zip'))
                GetFile(UPDATE_CONTENT, 'plugin.video.iwn-content.zip', file_location)
                zip_name=xbmc.translatePath('special://home/addons/' + ADDON_ID + \
                    '/resources/data/plugin.video.iwn-content.zip')
                with zipfile.ZipFile(zip_name, "r") as zip_file:
                    zip_file.extractall(path=file_location)
                    zip_file.close()
                if os.path.exists(xbmc.translatePath('special://home/addons/' + ADDON_ID + \
                    '/resources/data/plugin.video.iwn-content.zip.md5.old')):
                    os.remove(xbmc.translatePath('special://home/addons/' + ADDON_ID + \
                        '/resources/data/plugin.video.iwn-content.zip.md5.old'))
                if os.path.exists(xbmc.translatePath('special://home/addons/' + ADDON_ID + \
                    '/resources/data/plugin.video.iwn-content.zip')):
                    os.remove(xbmc.translatePath('special://home/addons/' + ADDON_ID + \
                        '/resources/data/plugin.video.iwn-content.zip'))
                xbmcgui.Dialog().ok(ADDON_NAME, 'Content Updated...', '', '')
    else:
	    xbmcgui.Dialog().ok(ADDON_NAME, 'Please Update Plugin', 'New Version Available', '')
    ReadXML('Menus/Settings.xml')

####################################################################################################
# Create List Item for Audio
####################################################################################################
def AddListItemAudio(name, url, mode, iconimage):
    __log('Audio List Item name - '+str(name))
    __log('Audio List Item url - '+str(url))
    __log('Audio List Item mode - '+str(mode))
    contextMenuItems = []
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name=" \
        +urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.addContextMenuItems(contextMenuItems, True)
    liz.setInfo(type="Music", infoLabels={"Title": name})
    liz.setProperty('fanart_image', fanart)
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

####################################################################################################
# Create List Item for Video
####################################################################################################
def AddListItemVideo(name, url, mode, iconimage):
    __log('Video List Item name - '+str(name))
    __log('Video List Item url - '+str(url))
    __log('Video List Item mode - '+str(mode))
    contextMenuItems = []
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name=" \
        +urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.addContextMenuItems(contextMenuItems, True)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    liz.setProperty('fanart_image', fanart)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

####################################################################################################
# Create Playable Item from URL
####################################################################################################
def AddPlayableAudioItem(action="", title="", plot="", url="", thumbnail="", isPlayable=False, \
        folder=True):
    __log('Audio Item action - '+str(action))
    __log('Audio Item url - '+str(url))
    __log('Audio Item thumbnail - '+str(thumbnail))
    liz = xbmcgui.ListItem(title, iconImage="DefaultVideo.png", thumbnailImage=thumbnail)
    liz.setInfo(type="Music", infoLabels={"Title": title})
    if url.startswith("plugin://"):
        itemurl = url
        liz.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=itemurl, listitem=liz, \
            isFolder=folder)
    elif isPlayable:
        liz.setProperty("Video", "true")
        liz.setProperty('IsPlayable', 'true')
        itemurl = '%s?action=%s&title=%s&url=%s&thumbnail=%s&plot=%s' \
            %(sys.argv[0], action, urllib.quote_plus(title), urllib.quote_plus(url), \
        urllib.quote_plus(thumbnail), urllib.quote_plus(plot))
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=itemurl, listitem=liz, \
            isFolder=folder)

def AddPlayableVideoItem(action="", title="", plot="", url="", thumbnail="", isPlayable=False, \
        folder=True):
    __log('Video Item action - '+str(action))
    __log('Video Item url - '+str(url))
    __log('Video Item thumbnail - '+str(thumbnail))
    liz = xbmcgui.ListItem(title, iconImage="DefaultVideo.png", thumbnailImage=thumbnail)
    liz.setInfo(type="Video", infoLabels={"Title": title})
    if url.startswith("plugin://"):
        itemurl = url
        liz.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=itemurl, listitem=liz, \
            isFolder=folder)
    elif isPlayable:
        liz.setProperty("Video", "true")
        liz.setProperty('IsPlayable', 'true')
        itemurl = '%s?action=%s&title=%s&url=%s&thumbnail=%s&plot=%s' \
            %(sys.argv[0], action, urllib.quote_plus(title), urllib.quote_plus(url), \
        urllib.quote_plus(thumbnail), urllib.quote_plus(plot))
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=itemurl, listitem=liz, \
            isFolder=folder)

####################################################################################################
# Check and Get URLs
####################################################################################################
# Check URL
####################################################################################################
def CheckURL(url):
    __log('Check URL url - '+str(url))
    request = urllib2.Request(url)
    request.get_method = lambda: 'HEAD'
    try:
        response = urllib2.urlopen(request)
        return True
    except:
        return False
####################################################################################################
# Fix Title
####################################################################################################
def Fix_Title(tmptitle):
    title = tmptitle.encode("utf-8").replace("\\xe2\\x80\\x99","'").replace("\\xe2\\x80\\x9c",'"') \
    .replace("\\xe2\\x80\\x9d",'"').replace("&amp;","&").replace("\\xc3\\xa1","a").replace("&quot;",'"')
    return title

####################################################################################################
# Get URL
####################################################################################################
def GetURL(content_type, url):
    __log('Get URL url - '+str(url))
    __log('Get URL type - '+str(content_type))
    request = urllib2.Request(url)
    request.add_header('User-Agent', \
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    if content_type == 'json':
        url_parse = json.load(urllib2.urlopen(request))
    elif content_type == 'html':
        url_parse = urllib2.urlopen(request)
    elif content_type == 'xml':
        url_parse = parse(urllib2.urlopen(request))
    return url_parse

def GetChannelID(user_id):
    get_channel_url=youtube_user_to_channel_url+user_id+youtube_user_to_channel_url_end
    __log('Get Channel ID url - '+str(get_channel_url))
    json_data = GetURL('json', get_channel_url)
    youtube_channel_id = str(re.findall(" u'id': u'(.+?)'",str(json_data))).strip("['").strip("']")
    __log('Get Channel Found Channel ID for '+str(user_id)+' us '+str(youtube_channel_id))
    return youtube_channel_id

####################################################################################################
# Create Specific Playback Menus
####################################################################################################
# Read XML File and Create List
####################################################################################################
def ReadXML(filename):
    file_parse = parse(xbmc.translatePath('special://home/addons/' + ADDON_ID + \
       '/resources/data/' + filename))
    __log('Read XML - '+ xbmc.translatePath('special://home/addons/' + ADDON_ID + \
       '/resources/data/' + filename))
    for item in file_parse.getElementsByTagName('item'):
        file_provider = item.getElementsByTagName('provider')[0].firstChild.data
        file_title = item.getElementsByTagName('title')[0].firstChild.data
        try:
            file_id = item.getElementsByTagName('id')[0].firstChild.data
        except:
            file_id = ''
        try:
            file_logo = item.getElementsByTagName('logo')[0].firstChild.data
        except:
            file_logo = ''
        try:
            file_custom_logo = item.getElementsByTagName('customlogo')[0].firstChild.data
        except:
             file_custom_logo = ''
        if file_provider == 'MenuLink':
            __log('Provider - ' + file_provider)
            AddMenuLink(file_title, 'url', file_id, file_custom_logo)
        if file_provider == 'MenuItem':
            __log('Provider - ' + file_provider)
            AddMenuItem(file_title, file_custom_logo)
        if file_provider == 'SoundCloud':
            __log('Provider - ' + file_provider)
            if file_custom_logo:
                AddListItemAudio(file_title, soundcloud_user_url + file_id + \
                    soundcloud_user_url2 + '', 11, file_custom_logo + '')
            else:
                AddListItemAudio(file_title, soundcloud_user_url + file_id + \
                    soundcloud_user_url2 + '', 11, soundcloud_logo_url + file_logo + '')
            xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
        if file_provider == 'Youtube':
            file_type = file_id[:2]
            if file_type == 'PL':
                __log('Provider -' + file_provider + 'Type - Playlist')
                if file_custom_logo:
                    AddListItemVideo(file_title, youtube_playlist_url + file_id + \
                       '', 12, file_custom_logo  + '')
                else:
                    AddListItemVideo(file_title, youtube_playlist_url + file_id + \
                       '', 12, youtube_logo_url  +file_logo  + '')
            elif file_type == 'UC':
                __log('Provider -' + file_provider + 'Type - Channel')
                if file_custom_logo:
                    AddListItemVideo(file_title, youtube_channel_url + file_id + \
                        youtube_channel_url_end +'', 14, file_custom_logo + '')
                else:
                    AddListItemVideo(file_title, youtube_channel_url + file_id + \
                        youtube_channel_url_end +'', 14, youtube_logo_url + file_logo + '')
            else:
                __log('Provider -' + file_provider + 'Type - User')
                youtube_channel_id=GetChannelID(file_id)
                if youtube_channel_id:
                    __log('Provider -' + file_provider + 'Type - Channel')
                    if file_custom_logo:
                        AddListItemVideo(file_title, youtube_channel_url +  youtube_channel_id + \
                            youtube_channel_url_end +'', 14, file_custom_logo + '')
                    else:
                        AddListItemVideo(file_title, youtube_channel_url + youtube_channel_id + \
                           youtube_channel_url_end +'', 14, youtube_logo_url + file_logo + '')
                else:
                    if file_custom_logo:
                        AddListItemVideo(file_title, youtube_user_url + file_id + \
                            '', 10, file_custom_logo + '')
                    else:
                        AddListItemVideo(file_title, youtube_user_url + file_id + \
                            '', 10, youtube_logo_url + file_logo + '')
            xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
        if file_provider == 'VimeoChannel':
            __log('Provider -' + file_provider)
            if file_custom_logo:
                AddListItemVideo(file_title, vimeo_channel_url + file_id + vimeo_url_end + \
                    '', 13, file_custom_logo + '')
            else:
                AddListItemVideo(file_title, vimeo_channel_url + file_id + vimeo_url_end + \
                    '', 13, vimeo_thumbnail_url +  file_logo + '')
            xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
        if file_provider == 'VimeoUser':
            __log('Provider -' + file_provider)
            if file_custom_logo:
                AddListItemVideo(file_title, vimeo_user_url + file_id + vimeo_url_end + \
                    '', 13, file_custom_logo + '')
            else:
                AddListItemVideo(file_title, vimeo_user_url + file_id + vimeo_url_end + \
                    '', 13, vimeo_thumbnail_url +  file_logo + '')
            xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)

####################################################################################################
# Soundcloud Playback
####################################################################################################
def SoundCloud_Play(url):
    sc_parse = GetURL('xml', url)
    counter = 0
    for item in sc_parse.getElementsByTagName('item'):
        try:
            # Title
            title = ''
            tmptitle = item.getElementsByTagName('title')[0].firstChild.data
            title = Fix_Title(tmptitle)
        except:
            title = ''
        try:
            # Description
            plot = ''
            plot = item.getElementsByTagName('itunes:summary')[0].firstChild.data
        except:
            plot = ''
        try:
            # Thumbnail
            thumbnail = ''
            thumbnail = item.getElementsByTagName('itunes:image')[0].getAttribute('href')
        except:
            thumbnail = ''
        try:
            # Video ID
            video_id = ''
            video_id = item.getElementsByTagName('guid')[0].firstChild.data
        except:
            video_id = ''
        play_url = soundcloud_url+video_id
        AddPlayableAudioItem(action="play", title=title, plot=plot, url=play_url, \
            thumbnail=thumbnail, isPlayable=True, folder=False)
        counter = counter + 1
        __log('SC Play title - '+str(title))
        __log('SC Play url - '+str(url))
    AddMenuItem(str(counter) + ' Items Available', '')

####################################################################################################
# Youtube Channel Playback
####################################################################################################
def YouTubeChannel_Play(url):
    json_data = GetURL('json', url)
    counter = 0
    for item in json_data['items']:
        try:
            # Title
            title = ''
            title = str(re.findall(" u'title': u'(.+?)'",str(item))).strip("['").strip("']")
            if not title:
                title = str(re.findall("u'title': u\"(.+?)\"",str(item))).strip("['").strip("']").strip('"')
        except:
            title = ''
        try:
            # Description
            plot = ''
            plot = str(re.findall(" u'description': u'(.+?)'",str(item))).strip("['").strip("']")
        except:
            plot = ''
        try:
            # Thumbnail
            thumbnail = ''
            thumbnail = str(re.findall('https://i.ytimg.com/vi/.*/default.jpg',str(item))).strip("['").strip("']")
        except:
            thumbnail = ''
        try:
            # Video ID
            play_url = ''
            video_id = ''
            video_id = str(re.findall(" u'videoId': u'(.+?)'",str(item))).strip("['").strip("']")
            play_url = youtube_play_url+video_id
        except:
            play_url = ''
            video_id = ''
        if video_id and thumbnail:
            counter = counter + 1
            AddPlayableVideoItem(action="play", title=title, plot=plot, url=play_url, \
                thumbnail=thumbnail, isPlayable=True, folder=False)
            __log('YTC Play title - '+str(title))
            __log('YTC Play url - '+str(url))
    AddMenuItem(str(counter) + ' Items Available', '')

####################################################################################################
# Youtube Playlist Playback
####################################################################################################
def YouTubePlaylist_Play(url):
    yt_pl_parse = GetURL('html', url)
    counter = 0
    soup = BeautifulSoup(yt_pl_parse, "html.parser")
    items = soup.find_all("tr")
    for item in items:
        try:
            # Title
            title = ''
            tmptitle = str(re.findall('data-title="(.+?)"', str(item))).strip("['").strip("']")
            title = Fix_Title(tmptitle)
            if not title:
                title = ''
                title = str(re.findall('<a class[^>]+>([^<]+)</a>', \
                    str(item))).strip("['").strip("']").strip('\Wn').lstrip()
            if title == 'Deleted video' or title == 'Private video' :
                continue
        except:
            title = ''
        try:
            # Video ID
            play_url = ''
            video_id = ''
            video_id = str(re.findall('data-video-id="(.+?)"', str(item))).strip("['").strip("']")
            play_url = youtube_play_url+video_id
        except:
            play_url = ''
            video_id = ''
        try:
            # Thumbnail
            thumbnail = ''
            thumbnail = str(re.findall('data-thumb="(.+?)"', \
                str(item))).strip("['").strip("']").split('.jpg', 1)[0] + '.jpg'
        except:
            thumbnail = ''
        AddPlayableVideoItem(action="play", title=title, plot='', url=play_url, \
            thumbnail=thumbnail, isPlayable=True, folder=False)
        counter = counter + 1
        __log('YTP Play title - '+str(title))
        __log('YTP Play url - '+str(url))
    AddMenuItem(str(counter) + ' Items Available', '')

####################################################################################################
# Youtube User Playback
####################################################################################################
def YouTubeUser_Play(url):
    yt_parse = GetURL('xml', url)
    counter = 0
    for item in yt_parse.getElementsByTagName('entry'):
        try:
            # Title
            title = ''
            tmptitle = item.getElementsByTagName('media:title')[0].firstChild.data
            title = Fix_Title(tmptitle)
        except:
            title = ''
        try:
            # Description
            plot = ''
            plot = item.getElementsByTagName('media:description')[0].firstChild.data
        except:
            plot = ''
        try:
            # Thumbnail
            thumbnail = ''
            thumbnail = item.getElementsByTagName('media:thumbnail')[0].getAttribute('url')
        except:
            thumbnail = ''
        try:
            # Video ID
            play_url = ''
            video_id = ''
            video_id = item.getElementsByTagName('yt:videoId')[0].firstChild.data
            play_url = youtube_play_url+video_id
        except:
            play_url = ''
            video_id = ''
        AddPlayableVideoItem(action="play", title=title, plot=plot, url=play_url, \
            thumbnail=thumbnail, isPlayable=True, folder=False)
        counter = counter + 1
        __log('YTU Play title - '+str(title))
        __log('YTU Play url - '+str(url))
    AddMenuItem(str(counter) + ' Items Available', '')

####################################################################################################
# Vimeo Playback
####################################################################################################
def Vimeo_Play(url):
    if url.find("/page:") == -1:
        url2 = url+"/page:1"
        page = 1
    else:
        url2 = url
        page2 = url2.split('/page:', 1)[1]
        page = int(page2)
    counter = 0
    vm_parse = GetURL('html', url2)
    soup = BeautifulSoup(vm_parse, "html.parser")
    items = soup.find_all("li")
    for item in items:
        try:
            # Title
            title = ''
            tmptitle = str(re.findall('title="(.+?)"', str(item))).strip("['").strip("']")
            title = Fix_Title(tmptitle)
        except:
            title = ''
        try:
            # Video ID
            play_url = ''
            video_id = ''
            video_id = str(re.findall('id="clip_(.+?)"', str(item))).strip("['").strip("']")
            play_url = vimeo_play_url+video_id
        except:
            play_url = ''
            video_id = ''
        try:
            # Thumbnail
            thumbnail = ''
            thumbnail1 = str(re.findall('src="(.+?)"', str(item))).strip("['").strip("']")
            thumbnail2 = thumbnail1.rpartition('/')
            thumbnail = vimeo_logo_url+thumbnail2[2]
        except:
            thumbnail = ''
        if title and video_id:
            AddPlayableVideoItem(action="play", title=title, plot='', url=play_url, \
                thumbnail=thumbnail, isPlayable=True, folder=False)
            __log('VM Play title - '+str(title))
            __log('VM Play url - '+str(url))
            counter = counter + 1
    AddMenuItem(str(counter) + ' Items Available', '')
    page2 = url2.split('/page:', 1)[1]
    page = int(page2)
    url3 = url2.split('/page:', 1)[0]
    url4 = url3+"/page:"+str(int(page+1))
    if CheckURL(url4):
        __log('Next Page Detected')
        AddMenuLink('Next Page', url4, 13, '')
    else:
        __log('No Next Page Detected')