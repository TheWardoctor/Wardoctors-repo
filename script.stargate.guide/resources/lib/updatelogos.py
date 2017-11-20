# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 PodGod

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>
"""
import xbmc, xbmcgui, shutil, urllib2, urllib, os, xbmcaddon, zipfile, time, base64

source ='YUhSMGNEb3ZMekUyTXk0eE56SXVORFl1TVRJeUwyWnBiR1Z6TDJkMWFXUmxMMkZrWkdsMGFXOXVZV3d2'.decode('base64').decode('base64')
print source

#########LOGOS############

addon = xbmcaddon.Addon('script.stargate.guide')
url        = source + 'logos.zip'
path       = xbmc.translatePath('special://home/userdata/addon_data/script.stargate.guide')
lib        = xbmc.translatePath(os.path.join(path,'logos.zip'))
home       = xbmc.translatePath('special://home/userdata/addon_data/script.stargate.guide/')
profile    = 'Master user'
lock       = 'false'
localtxt00 = 'Stargate Guide'
localtxt01 = 'Install'
localtxt02 = 'Downloading Logos...'
localtxt03 = 'Downloaded: '
localtxt04 = 'Download Cancelled.'
localtxt05 = 'Updating'
localtxt06 = 'Succeeded'
localtxt07 = 'Unpacking logos.zip. Please Wait.'

def DownloaderClass(url,dest):
	dp = xbmcgui.DialogProgress()
	dp.create(localtxt00,localtxt02,'')
	urllib.urlretrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))

def _pbhook(numblocks, blocksize, filesize, url=None,dp=None):
	try:
		percent = min((numblocks*blocksize*100)/filesize, 100)
		print localtxt03+str(percent)+'%'
		dp.update(percent)
	except:
		percent = 100
		dp.update(percent)
	if dp.iscanceled():
		raise Exception("Cancelled")
		dp.close()

def ExtractorClass(_in, _out):
	dp = xbmcgui.DialogProgress()
	zin    = zipfile.ZipFile(_in,  'r')
	nFiles = float(len(zin.infolist()))
	count  = 0
	for item in zin.infolist():
		count += 1
		update = count / nFiles * 100
		zin.extract(item, _out)

if __name__ == '__main__':
	dialog = xbmcgui.Dialog()
	try:
		DownloaderClass(url,lib)
	except:
		xbmc.executebuiltin('Notification(Download Failed,Please Try Again Later,50000,special://skin/icon.png)')
	time.sleep(1)
	try:
		ExtractorClass(lib,home)
	except:
		xbmc.executebuiltin('Notification(Install Failed, Try Later,special://home/addons/script.stargate.guide/icon.png)')
	time.sleep(1)


os.remove(path + "/logos.zip")
xbmc.executebuiltin('Notification(Logos, Updated,special://home/addons/script.stargate.guide/icon.png)')
time.sleep(1)
