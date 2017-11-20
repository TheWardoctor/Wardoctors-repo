import xbmc, xbmcgui, shutil, urllib2, urllib, os, xbmcaddon, zipfile, time, base64

source ='YUhSMGNEb3ZMekUyTXk0eE56SXVORFl1TVRJeUwyWnBiR1Z6TDJkMWFXUmxMMkZrWkdsMGFXOXVZV3d2'.decode('base64').decode('base64')

####META_ALL####
addon = xbmcaddon.Addon('script.stargate.guide')
url        = source + 'MetaPlayers.zip'
path       = xbmc.translatePath('special://home/userdata/addon_data/plugin.video.meta')
lib        = xbmc.translatePath(os.path.join(path,'MetaPlayers.zip'))
home       = xbmc.translatePath('special://home/userdata/addon_data/plugin.video.meta/players')
profile    = 'Master user'
lock       = 'false'
localtxt00 = 'Stargate Guide'
localtxt01 = 'Install'
localtxt08 = 'Downloading Custom Meta Players...'
localtxt03 = 'Downloaded: '
localtxt04 = 'Download Cancelled.'
localtxt05 = 'Updating'
localtxt06 = 'Succeeded'
localtxt07 = 'Unpacking MetaPlayers.zip. Please Wait.'

# xbmc.executebuiltin('Notification(Please ensure that, Meta is installed,special://home/addons/script.stargate.guide/icon.png)')
# time.sleep(1)

if not os.path.exists(home):
	os.makedirs(home)     

def DownloaderClass(url,dest):
	dp = xbmcgui.DialogProgress()
	dp.create(localtxt00,localtxt08,'')
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
		xbmc.executebuiltin('Notification(Download Failed,Please Try Again Later,50000,special://home/addons/script.stargate.guide/icon.png)')
	time.sleep(1)
	try:
		ExtractorClass(lib,home)
	except:
		xbmc.executebuiltin('Notification(Install Failed, Is Meta installed?,special://home/addons/script.stargate.guide/icon.png)')
	time.sleep(5)
		
os.remove(path + "/MetaPlayers.zip")
xbmc.executebuiltin('Notification(Third Party Meta Players, Installed,special://home/addons/script.stargate.guide/icon.png)')
time.sleep(1)
