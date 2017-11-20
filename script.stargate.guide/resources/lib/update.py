import os,re,urllib2,xbmcgui
import xbmc,xbmcaddon,xbmcvfs
import sys

ADDON = xbmcaddon.Addon(id='script.stargate.guide')



def OPEN_URL(url):
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link

def open_file(file):
	try:
		f = open(file, 'r')
		content = f.read()
		f.close()
		return content	
	except:
		pass 

####checks hash for update, replaces file if newer and runs update####
def check_update():
	text_file = xbmc.translatePath('special://home/addons/script.stargate.guide/resources/sfhash.txt')
	HTML = OPEN_URL('https://github.com/Stargate GuideTV/addons/blob/master/Stargate Guide.zip')
	regex = re.compile('Stargate GuideTV/addons/commit/(.+?)" class="message').findall(HTML)
	for commit in regex:
		text = commit
		text_file_contents = open_file(text_file)
		if text == text_file_contents:
			pass
		else:
			open(text_file, 'w').close()
			text_file = open(text_file, 'a')
			text_file.write((commit))
			text_file.close()
			print commit
			xbmc.executebuiltin('RunScript(special://home/addons/script.stargate.guide/resources/lib/updateSF.py)')
						
check_update()