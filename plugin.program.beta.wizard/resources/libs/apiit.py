################################################################################
#      Copyright (C) 2015 Surfacingx                                           #
#                                                                              #
#  This Program is free software; you can redistribute it and/or modify        #
#  it under the terms of the GNU General Public License as published by        #
#  the Free Software Foundation; either version 2, or (at your option)         #
#  any later version.                                                          #
#                                                                              #
#  This Program is distributed in the hope that it will be useful,             #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of              #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
#  GNU General Public License for more details.                                #
#                                                                              #
#  You should have received a copy of the GNU General Public License           #
#  along with XBMC; see the file COPYING.  If not, write to                    #
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.       #
#  http://www.gnu.org/copyleft/gpl.html                                        #
################################################################################

import xbmc, xbmcaddon, xbmcgui, xbmcplugin, os, sys, xbmcvfs, glob
import shutil
import urllib2,urllib
import re
import uservar
import time
try:    from sqlite3 import dbapi2 as database
except: from pysqlite2 import dbapi2 as database
from datetime import date, datetime, timedelta
from resources.libs import wizard as wiz

ADDON_ID       = uservar.ADDON_ID
ADDONTITLE     = uservar.ADDONTITLE
ADDON          = wiz.addonId(ADDON_ID)
DIALOG         = xbmcgui.Dialog()
HOME           = xbmc.translatePath('special://home/')
ADDONS         = os.path.join(HOME,      'addons')
USERDATA       = os.path.join(HOME,      'userdata')
PLUGIN         = os.path.join(ADDONS,    ADDON_ID)
PACKAGES       = os.path.join(ADDONS,    'packages')
ADDONDATA      = os.path.join(USERDATA,  'addon_data', ADDON_ID)
ADDOND         = os.path.join(USERDATA,  'addon_data')
APIFOLD        = os.path.join(ADDONDATA, 'api')
ICON           = os.path.join(PLUGIN,    'icon.png')
TODAY          = date.today()
TOMORROW       = TODAY + timedelta(days=1)
THREEDAYS      = TODAY + timedelta(days=3)
KEEPAPI        = wiz.getS('keepapi')
APISAVE        = wiz.getS('apilastsave')
COLOR1         = uservar.COLOR1
COLOR2         = uservar.COLOR2
ORDER          = ['elysium', 'exodus', 'metalliq', 'masterreborn', 'salts', 'saltsrd', 'covenant', 'rebirth', 'genesisreborn', 'youtube']

APIID = { 
	'elysium': {
		'name'     : 'Elysium',
		'plugin'   : 'plugin.video.elysium',
		'saved'    : 'apielysium',
		'path'     : os.path.join(ADDONS, 'plugin.video.elysium'),
		'icon'     : os.path.join(ADDONS, 'plugin.video.elysium', 'icon.png'),
		'fanart'   : os.path.join(ADDONS, 'plugin.video.elysium', 'fanart.jpg'),
		'file'     : os.path.join(APIFOLD, 'elysium_api'),
		'settings' : os.path.join(ADDOND, 'plugin.video.elysium', 'settings.xml'),
		'default'  : 'tmdb_apikey',
		'data'     : ['tmdb_apikey'],
		'activate' : ''},
	'exodus': {
		'name'     : 'Exodus',
		'plugin'   : 'plugin.video.exodus',
		'saved'    : 'apiexodus',
		'path'     : os.path.join(ADDONS, 'plugin.video.exodus'),
		'icon'     : os.path.join(ADDONS, 'plugin.video.exodus', 'icon.png'),
		'fanart'   : os.path.join(ADDONS, 'plugin.video.exodus', 'fanart.jpg'),
		'file'     : os.path.join(APIFOLD, 'exodus_api'),
		'settings' : os.path.join(ADDOND, 'plugin.video.exodus', 'settings.xml'),
		'default'  : 'tm.user',
		'data'     : ['tm.user'],
		'activate' : ''},
	'metalliq': {
		'name'     : 'MetalliQ',
		'plugin'   : 'plugin.video.metalliq',
		'saved'    : 'apimetalliq',
		'path'     : os.path.join(ADDONS, 'plugin.video.metalliq'),
		'icon'     : os.path.join(ADDONS, 'plugin.video.metalliq', 'icon.png'),
		'fanart'   : os.path.join(ADDONS, 'plugin.video.metalliq', 'fanart.jpg'),
		'file'     : os.path.join(APIFOLD, 'metalliq_api'),
		'settings' : os.path.join(ADDOND, 'plugin.video.metalliq', 'settings.xml'),
		'default'  : 'tmdb_api',
		'data'     : ['lastfm_api_key', 'lastfm_api_shared_secret', 'tmdb_api', 'tvdb_api'],
		'activate' : ''},
	'masterreborn': {
		'name'     : 'Master Reborn',
		'plugin'   : 'plugin.video.master.reborn',
		'saved'    : 'apimasterreborn',
		'path'     : os.path.join(ADDONS, 'plugin.video.master.reborn'),
		'icon'     : os.path.join(ADDONS, 'plugin.video.master.reborn', 'icon.png'),
		'fanart'   : os.path.join(ADDONS, 'plugin.video.master.reborn', 'fanart.jpg'),
		'file'     : os.path.join(APIFOLD, 'masterreborn_api'),
		'settings' : os.path.join(ADDOND, 'plugin.video.master.reborn', 'settings.xml'),
		'default'  : 'tmdb_apikey',
		'data'     : ['tmdb_apikey'],
		'activate' : ''},
	'salts': {
		'name'     : 'Streaming All The Sources',
		'plugin'   : 'plugin.video.salts',
		'saved'    : 'apisalts',
		'path'     : os.path.join(ADDONS, 'plugin.video.salts'),
		'icon'     : os.path.join(ADDONS, 'plugin.video.salts', 'icon.png'),
		'fanart'   : os.path.join(ADDONS, 'plugin.video.salts', 'fanart.jpg'),
		'file'     : os.path.join(APIFOLD, 'salts_api'),
		'settings' : os.path.join(ADDOND, 'plugin.video.salts', 'settings.xml'),
		'default'  : 'tmdb_key',
		'data'     : ['fanart_person_key', 'tmdb_key', 'tvdb_key'],
		'activate' : ''},
	'saltsrd': {
		'name'     : 'Salts RD',
		'plugin'   : 'plugin.video.saltsrd.lite',
		'saved'    : 'apisaltsrd',
		'path'     : os.path.join(ADDONS, 'plugin.video.saltsrd.lite'),
		'icon'     : os.path.join(ADDONS, 'plugin.video.saltsrd.lite', 'icon.png'),
		'fanart'   : os.path.join(ADDONS, 'plugin.video.saltsrd.lite', 'fanart.jpg'),
		'file'     : os.path.join(APIFOLD, 'saltsrd_api'),
		'settings' : os.path.join(ADDOND, 'plugin.video.saltsrd.lite', 'settings.xml'),
		'default'  : 'tmdb_key',
		'data'     : ['fanart_person_key', 'tmdb_key', 'tvdb_key'],
		'activate' : ''},
	'covenant': {
		'name'     : 'Covenant',
		'plugin'   : 'plugin.video.covenant',
		'saved'    : 'apicovenant',
		'path'     : os.path.join(ADDONS, 'plugin.video.covenant'),
		'icon'     : os.path.join(ADDONS, 'plugin.video.covenant', 'icon.png'),
		'fanart'   : os.path.join(ADDONS, 'plugin.video.covenant', 'fanart.jpg'),
		'file'     : os.path.join(APIFOLD, 'covenant_api'),
		'settings' : os.path.join(ADDOND, 'plugin.video.covenant', 'settings.xml'),
		'default'  : 'tm.user',
		'data'     : ['tm.user'],
		'activate' : ''},
	'rebirth': {
		'name'     : 'Rebirth',
		'plugin'   : 'plugin.video.rebirth',
		'saved'    : 'apirebirth',
		'path'     : os.path.join(ADDONS, 'plugin.video.rebirth'),
		'icon'     : os.path.join(ADDONS, 'plugin.video.rebirth', 'icon.png'),
		'fanart'   : os.path.join(ADDONS, 'plugin.video.rebirth', 'fanart.jpg'),
		'file'     : os.path.join(APIFOLD, 'rebirth_api'),
		'settings' : os.path.join(ADDOND, 'plugin.video.rebirth', 'settings.xml'),
		'default'  : 'imdb.user',
		'data'     : ['imdb.user', 'tm.user'],
		'activate' : ''},
	'genesisreborn': {
		'name'     : 'GenesisReborn',
		'plugin'   : 'plugin.video.genesisreborn',
		'saved'    : 'apigenesisreborn',
		'path'     : os.path.join(ADDONS, 'plugin.video.genesisreborn'),
		'icon'     : os.path.join(ADDONS, 'plugin.video.genesisreborn', 'icon.png'),
		'fanart'   : os.path.join(ADDONS, 'plugin.video.genesisreborn', 'fanart.jpg'),
		'file'     : os.path.join(APIFOLD, 'genesisreborn_api'),
		'settings' : os.path.join(ADDOND, 'plugin.video.genesisreborn', 'settings.xml'),
		'default'  : 'imdb.user',
		'data'     : ['imdb.user', 'tm.user'],
		'activate' : ''},
	'youtube': {
		'name'     : 'YouTube',
		'plugin'   : 'plugin.video.youtube',
		'saved'    : 'apiyoutube',
		'path'     : os.path.join(ADDONS, 'plugin.video.youtube'),
		'icon'     : os.path.join(ADDONS, 'plugin.video.youtube', 'icon.png'),
		'fanart'   : os.path.join(ADDONS, 'plugin.video.youtube', 'fanart.jpg'),
		'file'     : os.path.join(APIFOLD, 'youtube_api'),
		'settings' : os.path.join(ADDOND, 'plugin.video.youtube', 'settings.xml'),
		'default'  : 'youtube.api.id',
		'data'     : ['youtube.api.id', 'youtube.api.key', 'youtube.api.secret'],
		'activate' : ''}		
}

def apiUser(who):
	user=None
	if APIID[who]:
		if os.path.exists(APIID[who]['path']):
			try:
				add = wiz.addonId(APIID[who]['plugin'])
				user = add.getSetting(APIID[who]['default'])
			except:
				pass
	return user

def apiIt(do, who):
	if not os.path.exists(ADDONDATA): os.makedirs(ADDONDATA)
	if not os.path.exists(APIFOLD): os.makedirs(APIFOLD)
	if who == 'all':
		for log in ORDER:
			if os.path.exists(APIID[log]['path']):
				try:
					addonid   = wiz.addonId(APIID[log]['plugin'])
					default   = APIID[log]['default']
					user      = addonid.getSetting(default)
					if user == '' and do == 'update': continue
					updateApi(do, log)
				except: pass
			else: wiz.log('[API Data] %s(%s) is not installed' % (APIID[log]['name'],APIID[log]['plugin']), xbmc.LOGERROR)
		wiz.setS('apilastsave', str(THREEDAYS))
	else:
		if APIID[who]:
			if os.path.exists(APIID[who]['path']):
				updateApi(do, who)
		else: wiz.log('[API Data] Invalid Entry: %s' % who, xbmc.LOGERROR)

def clearSaved(who, over=False):
	if who == 'all':
		for api in APIID:
			clearSaved(api,  True)
	elif APIID[who]:
		file = APIID[who]['file']
		if os.path.exists(file):
			os.remove(file)
			wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, APIID[who]['name']),'[COLOR %s]API Data: Removed![/COLOR]' % COLOR2, 2000, APIID[who]['icon'])
		wiz.setS(APIID[who]['saved'], '')
	if over == False: wiz.refresh()

def updateApi(do, who):
	file      = APIID[who]['file']
	settings  = APIID[who]['settings']
	data      = APIID[who]['data']
	addonid   = wiz.addonId(APIID[who]['plugin'])
	saved     = APIID[who]['saved']
	default   = APIID[who]['default']
	user      = addonid.getSetting(default)
	suser     = wiz.getS(saved)
	name      = APIID[who]['name']
	icon      = APIID[who]['icon']

	if do == 'update':
		if not user == '':
			try:
				with open(file, 'w') as f:
					for api in data: 
						f.write('<api>\n\t<id>%s</id>\n\t<value>%s</value>\n</api>\n' % (api, addonid.getSetting(api)))
					f.close()
				user = addonid.getSetting(default)
				wiz.setS(saved, user)
				wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, name), '[COLOR %s]API Data: Saved![/COLOR]' % COLOR2, 2000, icon)
			except Exception, e:
				wiz.log("[API Data] Unable to Update %s (%s)" % (who, str(e)), xbmc.LOGERROR)
		else: wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, name), '[COLOR %s]API Data: Not Registered![/COLOR]' % COLOR2, 2000, icon)
	elif do == 'restore':
		if os.path.exists(file):
			f = open(file,mode='r'); g = f.read().replace('\n','').replace('\r','').replace('\t',''); f.close();
			match = re.compile('<api><id>(.+?)</id><value>(.+?)</value></api>').findall(g)
			try:
				if len(match) > 0:
					for api, value in match:
						addonid.setSetting(api, value)
				user = addonid.getSetting(default)
				wiz.setS(saved, user)
				wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, name), '[COLOR %s]API Data: Restored![/COLOR]' % COLOR2, 2000, icon)
			except Exception, e:
				wiz.log("[API Data] Unable to Restore %s (%s)" % (who, str(e)), xbmc.LOGERROR)
		#else: wiz.LogNotify(name,'API Data: [COLOR red]Not Found![/COLOR]', 2000, icon)
	elif do == 'clearaddon':
		wiz.log('%s SETTINGS: %s' % (name, settings), xbmc.LOGDEBUG)
		if os.path.exists(settings):
			try:
				f = open(settings, "r"); lines = f.readlines(); f.close()
				f = open(settings, "w")
				for line in lines:
					match = wiz.parseDOM(line, 'setting', ret='id')
					if len(match) == 0: f.write(line)
					else:
						if match[0] not in data: f.write(line)
						else: wiz.log('Removing Line: %s' % line, xbmc.LOGNOTICE)
				f.close()
				wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, name),'[COLOR %s]API Data: Cleared![/COLOR]' % COLOR2, 2000, icon)
			except Exception, e:
				wiz.log("[API Data] Unable to Clear Addon %s (%s)" % (who, str(e)), xbmc.LOGERROR)
	wiz.refresh()

def autoUpdate(who):
	if who == 'all':
		for log in APIID:
			if os.path.exists(APIID[log]['path']):
				autoUpdate(log)
	elif APIID[who]:
		if os.path.exists(APIID[who]['path']):
			u  = apiUser(who)
			su = wiz.getS(APIID[who]['saved'])
			n = APIID[who]['name']
			if u == None or u == '': return
			elif su == '': apiIt('update', who)
			elif not u == su:
				if DIALOG.yesno(ADDONTITLE, "[COLOR %s]Would you like to save the [COLOR %s]API[/COLOR] data for [COLOR %s]%s[/COLOR]?" % (COLOR2, COLOR1, COLOR1, n), "Addon: [COLOR green][B]%s[/B][/COLOR]" % u, "Saved:[/COLOR] [COLOR red][B]%s[/B][/COLOR]" % su if not su == '' else 'Saved:[/COLOR] [COLOR red][B]None[/B][/COLOR]', yeslabel="[B][COLOR green]Save Data[/COLOR][/B]", nolabel="[B][COLOR red]No Cancel[/COLOR][/B]"):
					apiIt('update', who)
			else: apiIt('update', who)

def importlist(who):
	if who == 'all':
		for log in APIID:
			if os.path.exists(APIID[log]['file']):
				importlist(log)
	elif APIID[who]:
		if os.path.exists(APIID[who]['file']):
			d  = APIID[who]['default']
			sa = APIID[who]['saved']
			su = wiz.getS(sa)
			n  = APIID[who]['name']
			f  = open(APIID[who]['file'],mode='r'); g = f.read().replace('\n','').replace('\r','').replace('\t',''); f.close();
			m  = re.compile('<api><id>%s</id><value>(.+?)</value></api>' % d).findall(g)
			if len(m) > 0:
				if not m[0] == su:
					if DIALOG.yesno(ADDONTITLE, "[COLOR %s]Would you like to import the [COLOR %s]API[/COLOR] data for [COLOR %s]%s[/COLOR]?" % (COLOR2, COLOR1, COLOR1, n), "File: [COLOR green][B]%s[/B][/COLOR]" % m[0], "Saved:[/COLOR] [COLOR red][B]%s[/B][/COLOR]" % su if not su == '' else 'Saved:[/COLOR] [COLOR red][B]None[/B][/COLOR]', yeslabel="[B]Save Data[/B]", nolabel="[B]No Cancel[/B]"):
						wiz.setS(sa, m[0])
						wiz.log('[Import Data] %s: %s' % (who, str(m)), xbmc.LOGNOTICE)
					else: wiz.log('[Import Data] Declined Import(%s): %s' % (who, str(m)), xbmc.LOGNOTICE)
				else: wiz.log('[Import Data] Duplicate Entry(%s): %s' % (who, str(m)), xbmc.LOGNOTICE)
			else: wiz.log('[Import Data] No Match(%s): %s' % (who, str(m)), xbmc.LOGNOTICE)

def activateApi(who):
	if APIID[who]:
		if os.path.exists(APIID[who]['path']): 
			act     = APIID[who]['activate']
			addonid = wiz.addonId(APIID[who]['plugin'])
			if act == '': addonid.openSettings()
			else: url = xbmc.executebuiltin(APIID[who]['activate'])
		else: DIALOG.ok(ADDONTITLE, '%s is not currently installed.' % APIID[who]['name'])
	else: 
		wiz.refresh()
		return
	check = 0
	while apiUser(who) == None:
		if check == 30: break
		check += 1
		time.sleep(10)
	wiz.refresh()