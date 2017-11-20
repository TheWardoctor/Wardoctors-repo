import xbmc,xbmcaddon,xbmcvfs,xbmcgui,os,re,urllib2

ADDON = xbmcaddon.Addon(id='script.stargate.guide')

path = xbmc.translatePath('special://home/addons/script.stargate.guide/resources/eventList.txt')
f = open(path, 'r+')
f.truncate()
#os.remove(path)


def OPEN_URL(url):
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link			

def Stargate GuideINFO():
    eventList = xbmc.translatePath('special://home/addons/script.stargate.guide/resources/eventList.txt')
    HTML = OPEN_URL('http://pastebin.com/raw/BGZK28iq')
    re1 = '\n(.+?)-(.+?)-(.+?)$'
    match = re.compile(re1,re.MULTILINE).findall(HTML)
    for time,game,channel in match:
		open(eventList, 'a').close()
		text_file = eventList
		text_file = open(text_file, "a")
		text_file.write((time).replace('Monday','\n'+'[COLOR orange]'+'Monday'+'[/COLOR]').replace('Tuesday','\n'+'[COLOR orange]'+'Tuesday'+'[/COLOR]').replace('Wednesday','\n'+'[COLOR orange]'+'Wednesday'+'[/COLOR]').replace('Thursday','\n'+'[COLOR orange]'+'Thursday'+'[/COLOR]').replace('Friday','\n'+'[COLOR orange]'+'Friday'+'[/COLOR]').replace('Saturday','\n'+'[COLOR orange]'+'Saturday'+'[/COLOR]').replace('Sunday','\n'+'[COLOR orange]'+'Sunday'+'[/COLOR]')+' - '+game.replace(game,'[COLOR blue]'+game+'[/COLOR]').replace('10th','[COLOR orange]'+'10th'+'[/COLOR]').replace('11th','[COLOR orange]'+'11th'+'[/COLOR]').replace('12th','[COLOR orange]'+'12th'+'[/COLOR]').replace('13th','[COLOR orange]'+'13th'+'[/COLOR]').replace('14th','[COLOR orange]'+'14th'+'[/COLOR]').replace('15th','[COLOR orange]'+'15th'+'[/COLOR]').replace('16th','[COLOR orange]'+'16th'+'[/COLOR]').replace('17th','[COLOR orange]'+'17th'+'[/COLOR]').replace('18th','[COLOR orange]'+'18th'+'[/COLOR]').replace('19th','[COLOR orange]'+'19th'+'[/COLOR]').replace('20th','[COLOR orange]'+'20th'+'[/COLOR]').replace('21st','[COLOR orange]'+'21st'+'[/COLOR]').replace('22nd','[COLOR orange]'+'22nd'+'[/COLOR]').replace('23rd','[COLOR orange]'+'23rd'+'[/COLOR]').replace('24th','[COLOR orange]'+'24th'+'[/COLOR]').replace('25th','[COLOR orange]'+'25th'+'[/COLOR]').replace('26th','[COLOR orange]'+'26th'+'[/COLOR]').replace('27th','[COLOR orange]'+'27th'+'[/COLOR]').replace('28th','[COLOR orange]'+'28th'+'[/COLOR]').replace('29th','[COLOR orange]'+'29th'+'[/COLOR]').replace('30th','[COLOR orange]'+'30th'+'[/COLOR]').replace('31st','[COLOR orange]'+'31st'+'[/COLOR]').replace('1st','[COLOR orange]'+'1st'+'[/COLOR]').replace('2nd','[COLOR orange]'+'2nd'+'[/COLOR]').replace('3rd','[COLOR orange]'+'3rd'+'[/COLOR]').replace('4th','[COLOR orange]'+'4th'+'[/COLOR]').replace('5th','[COLOR orange]'+'5th'+'[/COLOR]').replace('6th','[COLOR orange]'+'6th'+'[/COLOR]').replace('7th','[COLOR orange]'+'7th'+'[/COLOR]').replace('8th','[COLOR orange]'+'8th'+'[/COLOR]').replace('9th','[COLOR orange]'+'9th'+'[/COLOR]')+' - '+(channel).replace('September','[COLOR orange]September[/COLOR]').replace('Stargate Guide 1','[COLOR red]Stargate Guide 1[/COLOR]').replace('Stargate Guide 2','[COLOR red]Stargate Guide 2[/COLOR]').replace('Stargate Guide 3','[COLOR red]Stargate Guide 3[/COLOR]').replace('Stargate Guide 4','[COLOR red]Stargate Guide 4[/COLOR]').replace('Stargate Guide 5','[COLOR red]Stargate Guide 5[/COLOR]').replace('Stargate Guide 6','[COLOR red]Stargate Guide 6[/COLOR]').replace('Stargate Guide 7','[COLOR red]Stargate Guide 7[/COLOR]').replace('Stargate Guide 8','[COLOR red]Stargate Guide 8[/COLOR]').replace('Stargate Guide 9','[COLOR red]Stargate Guide 9[/COLOR]').replace('Stargate Guide 10','[COLOR red]Stargate Guide 10[/COLOR]')+'\n\n')
		text_file.close()
		
Stargate GuideINFO()