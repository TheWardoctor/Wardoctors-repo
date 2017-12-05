# #!/usr/bin/env python
####################################################################################################
# Import From other Modules
####################################################################################################
import os
import xbmc
import xbmcaddon

####################################################################################################
# Plugin Information
####################################################################################################
ADDON_ID = 'plugin.video.iwn'
REAL_SETTINGS = xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME = REAL_SETTINGS.getAddonInfo('name')
ADDON_PATH = (REAL_SETTINGS.getAddonInfo('path').decode('utf-8'))
ADDON_VERSION = REAL_SETTINGS.getAddonInfo('version')
ADDON_CONTACT = 'kodi.projects@gmail.com'
ADDON_GITHUB = 'https://github.com/jg555/kodi/tree/master/plugin.video.iwn'
UPDATE_CONTENT = 'https://raw.githubusercontent.com/jg555/kodi/master/_content/zips/plugin.video.iwn-content.zip'
UPDATE_CONTENT_MD5 = 'https://raw.githubusercontent.com/jg555/kodi/master/_content/zips/plugin.video.iwn-content.zip.md5'
UPDATE_CONTENT_VERSION = 'https://raw.githubusercontent.com/jg555/kodi/master/_content/zips/iwn.version'

####################################################################################################
# Variables
####################################################################################################
fanart = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.iwn', 'fanart.jpg'))

####################################################################################################
# SoundCloud Playback and Scraper Variables
####################################################################################################
soundcloud_url = 'plugin://plugin.audio.soundcloud/play/?audio_id='
soundcloud_logo_url = 'http://i1.sndcdn.com/'
soundcloud_user_url = 'http://feeds.soundcloud.com/users/soundcloud:users:'
soundcloud_user_url2 = "/sounds.rss"

####################################################################################################
# YouTube Playback and Scraper Variables
####################################################################################################
youtube_api_key='AIzaSyDVXPP5yqlSf6JBZxIrzD1bPedR-IJ4GQA'
youtube_play_url = 'plugin://plugin.video.youtube/play/?video_id='
youtube_channel_url = 'https://www.googleapis.com/youtube/v3/search?key='+youtube_api_key+'&channelId='
youtube_channel_url_end = '&part=snippet,id&order=date&maxResults=50'
youtube_playlist_url = 'https://www.youtube.com/playlist?list='
youtube_logo_url = 'https://yt3.ggpht.com/'
youtube_user_url = 'https://www.youtube.com/feeds/videos.xml?user='
youtube_user_to_channel_url = 'https://www.googleapis.com/youtube/v3/channels?part=contentDetails&forUsername='
youtube_user_to_channel_url_end = '&key='+youtube_api_key+'&maxResults=50'

####################################################################################################
# Vimeo Playback and Scraper Variables
####################################################################################################
vimeo_url = 'plugin://plugin.video.vimeo/?action=play_video&videoid='
vimeo_play_url = 'plugin://plugin.video.vimeo/play/?video_id='
vimeo_logo_url = 'https://i.vimeocdn.com/video/'
vimeo_thumbnail_url = 'https://i.vimeocdn.com/portrait/'
vimeo_channel_url = 'https://vimeo.com/channels/'
vimeo_user_url = 'https://vimeo.com/'
vimeo_url_end = '/videos'