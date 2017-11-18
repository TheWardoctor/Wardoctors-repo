from xbmcswift2 import Plugin
from xbmcswift2 import actions
import os
import re
import urllib
import requests
import xbmc,xbmcaddon,xbmcvfs,xbmcgui
import xbmcplugin
import json
import hashlib
import zipfile
import time
import os
from bs4 import BeautifulSoup
from urlparse import urlparse
import datetime
from datetime import timedelta
from rpc import RPC
from dateutil import tz
from resources.lib.pytz import timezone

plugin = Plugin()
big_list_view = True

def log(x):
    xbmc.log(repr(x))

def remove_formatting(label):
    label = re.sub(r"\[/?[BI]\]",'',label)
    label = re.sub(r"\[/?COLOR.*?\]",'',label)
    return label

def get_icon_path(icon_name):
    addon_path = xbmcaddon.Addon().getAddonInfo("path")
    return os.path.join(addon_path, 'resources', 'img', icon_name+".png")

def unescape( str ):
    str = str.replace("&lt;","<")
    str = str.replace("&gt;",">")
    str = str.replace("&quot;","\"")
    str = str.replace("&amp;","&")
    str = str.replace("&nbsp;"," ")
    str = str.replace("&dash;","-")
    str = str.replace("&ndash;","-")
    return str

@plugin.route('/play_channel/<station>')
def play_channel(station):
    streams = plugin.get_storage('streams')
    if station in streams and streams[station]:
        item = {'label': station,
             'path': streams[station],
             'is_playable': True,
             }
        plugin.play_video(item)
    else:
        choose_stream(station)

@plugin.route('/alternative_play/<station>')
def alternative_play(station):
    streams = plugin.get_storage('streams')
    if station in streams and streams[station]:
        xbmc.executebuiltin('XBMC.RunPlugin(%s)' % streams[station])
    else:
        choose_stream(station)

@plugin.route('/choose_stream/<station>')
def choose_stream(station):
    station = station.decode("utf8")
    streams = plugin.get_storage('streams')
    d = xbmcgui.Dialog()



    addons_ini = plugin.get_setting('addons.ini')
    data = xbmcvfs.File(addons_ini,'rb').read()
    no_addons_ini = False
    if not data:
        no_addons_ini = True
    lines = data.splitlines()
    addons = {}
    addon = ""
    for line in lines:
        if line.startswith('['):
            addon = line.strip('[] ')
            if addon not in addons:
                addons[addon] = {}
        elif not line.startswith('#'):
            channel_url = line.split('=',1)
            if addon and len(channel_url) == 2:
                addons[addon][remove_formatting(channel_url[0])] = channel_url[1].lstrip('@')

    m3u = plugin.get_setting('m3u')
    data = xbmcvfs.File(m3u,'rb').read()
    no_m3u = False
    if not data:
        no_m3u = True
    matches = re.findall(r'#EXTINF:(.*?),(.*?)\n([^#]*?)\n',data,flags=(re.MULTILINE))
    addons["m3u"] = {}
    for attributes,name,url in matches:
        if name and url:
            addons["m3u"][name.strip().decode("utf8")] = url.strip()
    if no_addons_ini:
        guess = "Guess (needs addons.ini)"
    else:
        guess = "Guess"
    addon_labels = [guess, "Browse", "Playlist", "PVR", "Favourites", "Clear"]+sorted(addons)
    addon = d.select("Addon: "+station,addon_labels)
    if addon == -1:
        return
    s = station.lower().replace(' ','')
    sword = s.replace('1','one')
    sword = sword.replace('2','two')
    sword = sword.replace('4','four')
    found_streams = {}
    if addon == 0:
        if no_addons_ini:
            plugin.open_settings()
            return
        for a in sorted(addons):
            for c in sorted(addons[a]):
                n = c.decode("utf8").lower().replace(' ','')
                if n:
                    label = "[%s] %s" % (a,c)
                    if (s.startswith(n) or n.startswith(s)):
                        found_streams[label] = addons[a][c]
                    elif (sword.startswith(n) or n.startswith(sword)):
                        found_streams[label] = addons[a][c]

        stream_list = sorted(found_streams)
        if stream_list:
            choice = d.select(station,stream_list)
            if choice == -1:
                return
            streams[station] = found_streams[stream_list[choice]]
            item = {'label': stream_list[choice],
                 'path': streams[station],
                 'is_playable': True,
                 }
            plugin.play_video(item)
            return
    elif addon == 1:
        try:
            response = RPC.addons.get_addons(type="xbmc.addon.video",properties=["name", "thumbnail"])
        except:
            return
        if "addons" not in response:
            return
        found_addons = response["addons"]
        if not found_addons:
            return
        name_ids = sorted([(remove_formatting(a['name']),a['addonid']) for a in found_addons])
        names = [x[0] for x in name_ids]
        selected_addon = d.select("Addon: "+station,names)
        if selected_addon == -1:
            return
        id = name_ids[selected_addon][1]
        path = "plugin://%s" % id
        while True:
            try:
                response = RPC.files.get_directory(media="files", directory=path, properties=["thumbnail"])
            except Exception as detail:
                return
            files = response["files"]
            dirs = sorted([[remove_formatting(f["label"]),f["file"],] for f in files if f["filetype"] == "directory"])
            links = sorted([[remove_formatting(f["label"]),f["file"]] for f in files if f["filetype"] == "file"])
            labels = ["[COLOR blue]%s[/COLOR]" % a[0] for a in dirs] + ["%s" % a[0] for a in links]
            selected = d.select("Addon: "+station,labels)
            if selected == -1:
                return
            if selected < len(dirs):
                dir = dirs[selected]
                path = dir[1]
            else:
                link = links[selected]
                streams[station] = link[1]
                name = link[0]
                item = {'label': name,
                     'path': streams[station],
                     'is_playable': True,
                     }
                plugin.play_video(item)
                return
    elif addon == 2:
        playlist = d.browse(1, 'Playlist: %s' % station, 'files', '', False, False)
        if not playlist:
            return
        data = xbmcvfs.File(playlist,'rb').read()
        matches = re.findall(r'#EXTINF:.*?,(.*?)\n(.*?)\n',data,flags=(re.DOTALL | re.MULTILINE))
        names = []
        urls =[]
        for name,url in matches:
            names.append(name.strip())
            urls.append(url.strip())
        if names:
            index = d.select("Choose stream: %s" % station,names)
            if index != -1:
                stream = urls[index]
                stream_name = names[index]
                streams[station] = stream
                item = {'label': stream_name,
                     'path': streams[station],
                     'is_playable': True,
                     }
                plugin.play_video(item)
                return
    elif addon == 3:
        index = 0
        urls = []
        channels = {}
        for group in ["radio","tv"]:
            dirs,files = xbmcvfs.listdir("pvr://channels/%s/" % group)
            all_channels = dirs[0]
            urls = urls + xbmcvfs.listdir("pvr://channels/%s/%s/" % (group,all_channels))[1]
        for group in ["radio","tv"]:
            groupid = "all%s" % group
            json_query = RPC.PVR.get_channels(channelgroupid=groupid, properties=[ "thumbnail", "channeltype", "hidden", "locked", "channel", "lastplayed", "broadcastnow" ] )
            if "channels" in json_query:
                for channel in json_query["channels"]:
                    channelname = channel["label"]
                    streamUrl = urls[index]
                    index = index + 1
                    url = "pvr://channels/%s/%s/%s" % (group,all_channels,streamUrl)
                    channels[channelname] = url
        labels = sorted(channels)
        selected_channel = d.select('PVR: %s' % station,labels)
        if selected_channel == -1:
            return
        stream_name = labels[selected_channel]
        stream = channels[stream_name]
        streams[station] = stream
        item = {'label': stream_name,
             'path': streams[station],
             'is_playable': True,
             }
        plugin.play_video(item)
        return
    elif addon == 4:
        data = xbmcvfs.File('special://profile/favourites.xml','rb').read()
        matches = re.findall(r'<favourite.*?name="(.*?)".*?>(.*?)<',data,flags=(re.DOTALL | re.MULTILINE))
        favourites = {}
        for name,value in matches:
            if value[0:11] == 'PlayMedia("':
                value = value[11:-2]
            elif value[0:10] == 'PlayMedia(':
                value = value[10:-1]
            elif value[0:22] == 'ActivateWindow(10025,"':
                value = value[22:-9]
            elif value[0:21] == 'ActivateWindow(10025,':
                value = value[22:-8]
            else:
                continue
            value = re.sub('&quot;','',value)
            favourites[name] = unescape(value)
        names = sorted(favourites)
        fav = d.select('PVR: %s' % station,names)
        if fav == -1:
            return
        stream_name = names[fav]
        stream = favourites[stream_name]
        streams[station] = stream
        item = {'label': stream_name,
             'path': streams[station],
             'is_playable': True,
             }
        plugin.play_video(item)
        return
    elif addon == 5:
        streams[station] = None
        xbmc.executebuiltin("Container.Refresh")
        return
    else:
        addon_id = addon_labels[addon]
        channel_labels = sorted(addons[addon_id])
        channel = d.select("["+addon_id+"] "+station,channel_labels)
        if channel == -1:
            return
        streams[station] = addons[addon_id][channel_labels[channel]]
        item = {'label': channel_labels[channel],
             'path': streams[station],
             'is_playable': True,
             }
        plugin.play_video(item)

@plugin.route('/remove_search/<name>')
def remove_search(name):
    searches = plugin.get_storage('searches')
    del searches[name]
    xbmc.executebuiltin('Container.Refresh')

@plugin.route('/new_search')
def new_search():
    d = xbmcgui.Dialog()
    what = d.input("New Search")
    if what:
        searches = plugin.get_storage('searches')
        searches[what] = ''
        return search_for(what)

@plugin.route('/search_for/<what>')
def search_for(what):
    if not what:
        return

    items = []
    country = plugin.get_setting('country')
    for day in ["Today","Tomorrow"]:
        url = "http://www.getyourfixtures.com/%s/live/%s/anySport" % (country,day.lower())
        items.append({
            'label': day,
            'path': plugin.url_for('listing', url=url, search="none"),
            'thumbnail':get_icon_path('clock'),
        })
        items = items + listing(url,what)
    return items

@plugin.route('/searches')
def searches():
    searches = plugin.get_storage('searches')
    items = []

    items.append({
        'label': 'New Search',
        'path': plugin.url_for('new_search'),
        'thumbnail':get_icon_path('search'),
    })
    for search in sorted(searches):
        context_items = []
        context_items.append(("[COLOR yellow][B]%s[/B][/COLOR] " % 'Remove Search', 'XBMC.RunPlugin(%s)' %
        (plugin.url_for(remove_search, name=search))))
        items.append({
            'label': search,
            'path': plugin.url_for('search_for',what=search),
            'thumbnail':get_icon_path('search'),
            'context_menu': context_items,
        })
    return items


@plugin.route('/channel_list')
def channel_list():
    global big_list_view
    big_list_view = True
    streams = plugin.get_storage('streams')
    stations = sorted(list(streams.keys()))
    items = []
    for station in stations:
        context_items = []
        context_items.append(('[COLOR yellow]Choose Stream[/COLOR]', 'XBMC.RunPlugin(%s)' % (plugin.url_for(choose_stream, station=station))))
        context_items.append(('[COLOR yellow]Alternative Play[/COLOR]', 'XBMC.RunPlugin(%s)' % (plugin.url_for(alternative_play, station=station))))
        if station in streams and streams[station]:
            label = "[COLOR yellow]%s[/COLOR]" % station.strip()
        else:
            label = station.strip()
        items.append(
        {
            'label': label,
            'path': plugin.url_for('play_channel', station=station),
            'thumbnail': 'special://home/addons/plugin.program.tardis-fixtures/icon.png',
            'context_menu': context_items,
        })
    return items

@plugin.route('/stations_list/<stations>/<start>/<end>/<label>')
def stations_list(stations,start,end,label):
    global big_list_view
    big_list_view = True
    streams = plugin.get_storage('streams')
    playable_items = []
    items = []
    for station in stations.split(','):
        station = station.strip()
        context_items = []
        context_items.append(('[COLOR yellow]Choose Stream[/COLOR]', 'XBMC.RunPlugin(%s)' % (plugin.url_for(choose_stream, station=station))))
        context_items.append(('[COLOR yellow]Alternative Play[/COLOR]', 'XBMC.RunPlugin(%s)' % (plugin.url_for(alternative_play, station=station))))
        context_items.append(("[COLOR yellow][B]%s[/B][/COLOR] " % 'AutoPlay', 'XBMC.RunPlugin(%s)' % (plugin.url_for('autoplay', stream=streams[station], start=start, end=end))))
        if station in streams and streams[station]:
            new_label = "[COLOR yellow]%s[/COLOR] %s" % (station.strip(), label)
            list = playable_items
        else:
            new_label = "[COLOR white]%s[/COLOR] %s" % (station.strip(), label)
            list = items
        list.append(
        {
            'label': new_label,
            'path': plugin.url_for('play_channel', station=station),
            'thumbnail': 'special://home/addons/plugin.program.tardis-fixtures/icon.png',
            'context_menu': context_items,
        })
    all_items = sorted(playable_items, key=lambda x: x["label"]) + sorted(items, key=lambda x: x["label"])
    return all_items

@plugin.route('/autoplay/<stream>/<start>/<end>')
def autoplay(stream,start,end):
    start_dt = datetime.datetime.fromtimestamp(float(start))
    end_dt = datetime.datetime.fromtimestamp(float(end))
    t = start_dt - datetime.datetime.now()
    timeToNotification = ((t.days * 86400) + t.seconds) / 60
    if timeToNotification < 0:
        timeToNotification = 0
    xbmc.executebuiltin('AlarmClock(%s-start,PlayMedia(%s),%d,True)' %
        (stream+start+end, stream, timeToNotification))

    # STOP is broken until sources have duration
    '''
    if plugin.get_setting('stop') == 'true':
        t = end_dt - datetime.datetime.now()
        timeToNotification = ((t.days * 86400) + t.seconds) / 60
        if timeToNotification > 0:
            xbmc.executebuiltin('AlarmClock(%s-end,PlayerControl(Stop),%d,True)' %
                (stream+start+end, timeToNotification))
    '''

@plugin.route('/channels_listing/<url>/<search>')
def channels_listing(url,search):
    global big_list_view
    big_list_view = True

    parts = url.split('/')
    day = parts[5]

    streams = plugin.get_storage('streams')
    parsed_uri = urlparse(url)
    domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
    timezone = plugin.get_setting('timezone')
    if timezone != "None":
        s = requests.Session()
        #r = s.get("http://www.getyourfixtures.com/setCookie.php?offset=%s" % timezone)
        r = s.get(url, cookies={"userTimeZoneGyf":urllib.quote_plus(timezone)})
        data = r.content
    else:
        data = requests.get(url).content
    if not data:
        return
    station_items = {}

    matches = data.split('<div class="match')
    images = {}
    found_stations = {}
    for match_div in matches[1:]:
        soup = BeautifulSoup('<div class="match'+match_div)
        sport_div = soup.find(class_=re.compile("sport"))
        sport = "unknown"
        if sport_div:
            sport = sport_div.img["alt"]
            icon = sport_div.img["src"]
            if icon:
                icon = domain+icon
                images[icon] = "special://profile/addon_data/plugin.program.tardis-fixtures/icons/%s" % icon.rsplit('/',1)[-1]
                local_icon = images[icon]
            else:
                icon = ''
        match_time = soup.find(class_=re.compile("time"))
        if match_time:
            match_time = unescape(' '.join(match_time.stripped_strings))
            match_time = match_time.replace("script async","script")
        else:
            pass
        competition = soup.find(class_=re.compile("competition"))
        if competition:
            competition = ' '.join(competition.stripped_strings)
        fixture = soup.find(class_=re.compile("fixture"))
        if fixture:
            fixture = ' '.join(fixture.stripped_strings)
        stations = soup.find(class_=re.compile("stations"))
        playable = False
        if stations:
            stations = stations.stripped_strings
            stations = list(stations)
            for s in stations:
                found_stations[s] = ""
                if s not in streams:
                    streams[s] = ""
                elif streams[s]:
                    playable = True
            stations_str = ', '.join(stations)

        if match_time:
            start_end = match_time.split(' - ')
            start_hour,start_minute = start_end[0].split(':')
            end_hour,end_minute = start_end[1].split(':')
            if day == "today":
                start = datetime.datetime.now()
            elif day == "tomorrow":
                start = datetime.datetime.now() + timedelta(days=1)
            else:
                day,month,year = day.split('-')
                start = datetime.datetime(year,month,year)
            end = start
            start = start.replace(hour=int(start_hour),minute=int(start_minute),second=0,microsecond=0)
            end = end.replace(hour=int(end_hour),minute=int(end_minute),second=0,microsecond=0)
            if end < start:
                end = end + timedelta(days=1)

            if playable:
                colour = "blue"
            else:
                colour = "dimgray"
            if plugin.get_setting('channels') == 'true':
                if '/anySport' in url:
                    label =  "[COLOR %s]%s[/COLOR] %s [COLOR dimgray]%s[/COLOR] %s [COLOR dimgray]%s[/COLOR]" % (colour, match_time, fixture, competition, sport, stations_str)
                else:
                    label =  "[COLOR %s]%s[/COLOR] %s [COLOR dimgray]%s[/COLOR] %s" % (colour, match_time, fixture, competition, stations_str )
            else:
                if '/anySport' in url:
                    label =  "[COLOR %s]%s[/COLOR] %s [COLOR dimgray]%s[/COLOR] %s" % (colour, match_time, fixture, competition, sport)
                else:
                    label =  "[COLOR %s]%s[/COLOR] %s [COLOR dimgray]%s[/COLOR]" % (colour, match_time, fixture, competition)


            item = {
                'label' : label,
                'thumbnail': local_icon,
                'start' : start,
                'end' : end,
            }
            for station in stations:
                if station not in station_items:
                    station_items[station] = []
                hide = plugin.get_setting('channels.hide') == 'true'
                if not hide or (hide and streams[station]):
                    station_items[station].append(item)

    xbmcvfs.mkdirs("special://profile/addon_data/icons/")
    for image in images:
        local_image = images[image]
        if not xbmcvfs.exists(local_image):
            xbmcvfs.copy(image,local_image)
            png = Image.open(xbmc.translatePath(local_image))
            png.load() # required for png.split()
            background = Image.new("RGB", png.size, (255, 255, 255))
            background.paste(png, mask=png.split()[3]) # 3 is the alpha channel
            background.save(xbmc.translatePath(local_image))

    all_items = []
    for station in sorted(station_items):
        items = station_items[station]
        for item in items:
            new_item = {} #item.copy()
            context_items = []
            if station in streams and streams[station]:
                label = "[COLOR yellow]%s[/COLOR] %s" % (station,item["label"])
                start = item['start']
                end = item['end']
                start_time = str(int(time.mktime(start.timetuple())))
                end_time = str(int(time.mktime(end.timetuple())))
                context_items.append(("[COLOR yellow][B]%s[/B][/COLOR] " % 'AutoPlay', 'XBMC.RunPlugin(%s)' % (plugin.url_for('autoplay', stream=streams[station], start=start_time, end=end_time))))
                context_items.append(('[COLOR yellow][B]Choose Stream[/B][/COLOR]', 'XBMC.RunPlugin(%s)' % (plugin.url_for(choose_stream, station=station.encode("utf8")))))
            else:
                label = "%s %s" % (station,item["label"])
            new_item['label'] = label
            new_item['thumbnail'] = item['thumbnail']
            new_item['path'] = plugin.url_for('play_channel', station=station.encode("utf8"))
            new_item['context_menu'] = context_items
            all_items.append(new_item)
    return all_items

@plugin.route('/run_channels_listing/<url>')
def run_channels_listing(url):
    actions.update_view(plugin.url_for('channels_listing', url=url, search="none")),

@plugin.route('/listing/<url>/<search>')
def listing(url,search):
    global big_list_view
    big_list_view = True

    parts = url.split('/')
    day = parts[5]

    streams = plugin.get_storage('streams')
    parsed_uri = urlparse(url)
    domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
    timezone = plugin.get_setting('timezone')
    if timezone != "None":
        s = requests.Session()
        #r = s.get("http://www.getyourfixtures.com/setCookie.php?offset=%s" % timezone)
        r = s.get(url, cookies={"userTimeZoneGyf":urllib.quote_plus(timezone)})
        data = r.content
    else:
        data = requests.get(url).content
    if not data:
        return
    items = []
    matches = data.split('<div class="match')
    images = {}
    for match_div in matches[1:]:
        soup = BeautifulSoup('<div class="match'+match_div)
        sport_div = soup.find(class_=re.compile("sport"))
        sport = "unknown"
        if sport_div:
            sport = sport_div.img["alt"]
            icon = sport_div.img["src"]
            if icon:
                icon = domain+icon
                images[icon] = "special://profile/addon_data/plugin.program.tardis-fixtures/icons/%s" % icon.rsplit('/',1)[-1]
                local_icon = images[icon]
            else:
                icon = ''
        match_time = soup.find(class_=re.compile("time"))
        if match_time:
            match_time = unescape(' '.join(match_time.stripped_strings))
            match_time = match_time.replace("script async","script")
        else:
            pass
        competition = soup.find(class_=re.compile("competition"))
        if competition:
            competition = ' '.join(competition.stripped_strings)
        fixture = soup.find(class_=re.compile("fixture"))
        if fixture:
            fixture = ' '.join(fixture.stripped_strings)
        stations = soup.find(class_=re.compile("stations"))
        playable = False
        playable_stations = []
        if stations:
            stations = stations.stripped_strings
            stations = list(stations)
            for s in stations:
                if s not in streams:
                    streams[s] = ""
                elif streams[s]:
                    playable_stations.append(s)
                    playable = True
            stations = ', '.join(stations)

        if match_time:
            start_end = match_time.split(' - ')
            start_hour,start_minute = start_end[0].split(':')
            end_hour,end_minute = start_end[1].split(':')
            if day == "today":
                start = datetime.datetime.now()
            elif day == "tomorrow":
                start = datetime.datetime.now() + timedelta(days=1)
            else:
                d,m,y = day.split('-')
                start = datetime.datetime(int(y),int(m),int(d))
            end = start
            start = start.replace(hour=int(start_hour),minute=int(start_minute),second=0,microsecond=0)
            end = end.replace(hour=int(end_hour),minute=int(end_minute),second=0,microsecond=0)
            if end < start:
                end = end + timedelta(days=1)
            start_time = str(int(time.mktime(start.timetuple())))
            end_time = str(int(time.mktime(end.timetuple())))

            if playable:
                colour = "blue"
            else:
                colour = "dimgray"
            if plugin.get_setting('channels') == 'true':
                if '/anySport' in url:
                    label =  "[COLOR %s]%s[/COLOR] %s [COLOR dimgray]%s[/COLOR] %s [COLOR dimgray]%s[/COLOR]" % (colour, match_time, fixture, competition, sport, stations)
                else:
                    label =  "[COLOR %s]%s[/COLOR] %s [COLOR dimgray]%s[/COLOR] %s" % (colour, match_time, fixture, competition, stations )
            else:
                if '/anySport' in url:
                    label =  "[COLOR %s]%s[/COLOR] %s [COLOR dimgray]%s[/COLOR] %s" % (colour, match_time, fixture, competition, sport)
                else:
                    label =  "[COLOR %s]%s[/COLOR] %s [COLOR dimgray]%s[/COLOR]" % (colour, match_time, fixture, competition)

            hide = plugin.get_setting('channels.hide') == 'true'
            if not hide or (hide and playable):
                if search and search != "none":
                    if not re.search(search,label,flags=re.IGNORECASE):
                        continue
                context_items = []
                if (len(playable_stations) == 1) and (plugin.get_setting('autoplay') == 'true'):
                    play_url = plugin.url_for('play_channel', station=playable_stations[0].encode("utf8"))
                    autoplay = True
                    context_items.append(('[COLOR yellow]Choose Channel[/COLOR]',  'ActivateWindow(%s,"%s")' % ('programs',
                    plugin.url_for('stations_list', stations=stations.encode("utf8"), start=start_time, end=end_time, label=label.encode("utf8")))))
                else:
                    play_url = plugin.url_for('stations_list', stations=stations.encode("utf8"), start=start_time, end=end_time, label=label.encode("utf8"))
                    autoplay = False
                items.append({
                    'label' : label,
                    'thumbnail': get_icon_path(sport),
                    'path': play_url,
                    'context_menu': context_items,
                })
    xbmcvfs.mkdirs("special://profile/addon_data/icons/")
    for image in images:
        local_image = images[image]
        if not xbmcvfs.exists(local_image):
            xbmcvfs.copy(image,local_image)
            png = Image.open(xbmc.translatePath(local_image))
            png.load() # required for png.split()
            background = Image.new("RGB", png.size, (255, 255, 255))
            background.paste(png, mask=png.split()[3]) # 3 is the alpha channel
            background.save(xbmc.translatePath(local_image))

    return items

@plugin.route('/sports_index/<day>')
def sports_index(day):
    global big_list_view
    big_list_view = True
    items = []

    sports = [
    "any Sport",
    "american football",
    "baseball",
    "basketball",
    "cricket",
    "cycling",
    "football",
    "golf",
    "ice hockey",
    "motorsports",
    "rugby",
    "tennis",
    "other",
    ]
    country = plugin.get_setting('country')
    for sport in sports:
        id = sport.replace(' ','')
        name = sport.title()
        '''
        image = 'http://www.getyourfixtures.com/gfx/disciplines/%s.png' % id
        local_image = 'special://profile/addon_data/plugin.program.tardis-fixtures/icons/%s.png' % id
        xbmcvfs.copy(image,local_image)
        png = Image.open(xbmc.translatePath(local_image))
        png.load() # required for png.split()
        background = Image.new("RGB", png.size, (255, 255, 255))
        background.paste(png, mask=png.split()[3]) # 3 is the alpha channel
        background.save(xbmc.translatePath(local_image))
        '''
        if plugin.get_setting('channels.prefix') == 'true':
            action = 'channels_listing'
        else:
            action = 'listing'
        context_items = []
        #TODO how do you update the view from the context menu?
        #context_items.append(("[COLOR yellow][B]%s[/B][/COLOR] " % 'By Channels', 'XBMC.RunPlugin(%s)' % (plugin.url_for('channels_listing', url='http://www.getyourfixtures.com/%s/live/%s/%s' % (country,day,id), search=""))))
        items.append(
        {
            'label': name,
            'path': plugin.url_for(action, url='http://www.getyourfixtures.com/%s/live/%s/%s' % (country,day,id), search="none"),
            'thumbnail': get_icon_path(id),
            'context_menu': context_items,
        })
    return items

@plugin.route('/export_mapping')
def export_mapping():
    streams = plugin.get_storage('streams')
    f = xbmcvfs.File('special://profile/addon_data/plugin.program.tardis-fixtures/channels.ini','wb')
    for channel in sorted(streams):
        stream = streams[channel]
        if not stream:
            stream = ""
        s = "%s=%s\n" % (channel,stream.decode("utf8"))
        f.write(bytearray(s, 'utf_8'))
    f.close()


@plugin.route('/import_mapping')
def import_mapping():
    streams = plugin.get_storage('streams')
    f = xbmcvfs.File('special://profile/addon_data/plugin.program.tardis-fixtures/channels.ini','rb')
    lines = f.read().splitlines()
    for line in lines:
        channel_stream = line.split('=',1)
        if len(channel_stream) == 2:
            channel = channel_stream[0].decode("utf8")
            stream = channel_stream[1].decode("utf8")
            streams[channel] = stream

@plugin.route('/clear_channels')
def clear_channels():
    streams = plugin.get_storage('streams')
    streams.clear()
    xbmc.executebuiltin('Container.Refresh')

@plugin.route('/clear_searches')
def clear_searches():
    searches = plugin.get_storage('searches')
    searches.clear()
    xbmc.executebuiltin('Container.Refresh')

@plugin.route('/bbc_scores/<sport>')
def bbc_scores(sport):
    url = "http://www.bbc.co.uk/sport/"+sport+"/scores-fixtures"
    html = requests.get(url).content
    morph = re.search("Morph\.setPayload\('/data/bbc-morph-football-scores-match-list-data/(.*?)'",html)
    if not morph:
        return
    s = urllib.quote(morph.group(1),'')
    url = 'http://push.api.bbci.co.uk/p?t=morph%3A%2F%2Fdata%2Fbbc-morph-football-scores-match-list-data%2F' + s
    j = requests.get(url,headers={"user-agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0"}).json()
    moments = j["moments"]
    if not moments:
        return
    payload = json.loads(moments[0]["payload"])
    matchData = payload["matchData"]
    items = []
    for tournament in matchData:
        tournament_name = tournament["tournamentMeta"]["tournamentName"]["full"]
        label = tournament_name
        tournamentDatesWithEvents = tournament["tournamentDatesWithEvents"]
        for date in tournamentDatesWithEvents:
            rounds = tournamentDatesWithEvents[date]
            for round in rounds:
                events = round["events"]
                for event in events:
                    ts = event["startTime"]
                    dt = datetime.datetime.strptime(ts[:-7],'%Y-%m-%dT%H:%M:%S')+ datetime.timedelta(hours=int(ts[-5:-3]), minutes=int(ts[-2:]))*int(ts[-6:-5]+'1')
                    home = event["homeTeam"]["name"]["full"]
                    away = event["awayTeam"]["name"]["full"]
                    search = "%s*%s" % (home.replace('Women','').strip(),away.replace('Women','').strip())
                    label = "%s - [B]%s v %s[/B] (%s)" % (dt.strftime("%Y-%m-%d %H:%M"),home,away,tournament_name)
                    items.append({
                        'label': label,
                        "path" : "plugin://plugin.video.tfixtures.listings/search/%s" % search
                    })
    return items

@plugin.route('/bbc_calendar/<sport>')
def bbc_calendar(sport):
    url = "http://www.bbc.co.uk/sport/"+sport+"/calendar"
    html = requests.get(url).content
    morph = re.search("Morph\.setPayload\('/data/bbc-morph-sportsdata-calendar/(.*?)', (.*?)\)",html)

    if not morph:
        return
    j = json.loads(morph.group(2))
    body = j["body"]
    tournamentList = body["tournamentList"]
    items = []
    for month in tournamentList:
        tournaments = month["tournaments"]
        for tournament in tournaments:
            tournamentName = tournament["tournamentName"]["full"]
            try: venue = tournament["venue"]["name"]
            except: venue = ""
            try: stageName = tournament["stageName"]["full"]
            except: stageName = ""
            date = tournament["date"]
            startDate = date["startDate"]
            date_label = startDate
            endDate = date["endDate"]
            if endDate:
                date_label += " - " + endDate
            if stageName:
                stageName = "(%s)" % stageName
            if venue:
                venue = "[%s]" % venue
            else:
                venue = ""
            if plugin.get_setting('venue') == 'true':
                label = "%s - [B]%s[/B] %s %s" % (date_label,tournamentName,stageName,venue,)
            else:
                label = "%s - [B]%s[/B] %s" % (date_label,tournamentName,stageName)
            items.append({
                'label': label,
                'path': plugin.url_for('bbc_calendar', sport=sport),
            })
    return items

@plugin.route('/bbc_calendar_morph/<sport>')
def bbc_calendar_morph(sport):
    url = 'http://push.api.bbci.co.uk/p?t=morph%3A%2F%2Fdata%2Fbbc-morph-sportsdata-calendar%2Fend-date-after%2Ftoday%2Fsource%2Fworld-sports-calendar%2Fsport%2F'+sport+'%2Fversion%2F1.0.5'
    j = requests.get(url,headers={"user-agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0"}).json()
    moments = j["moments"]
    if not moments:
        return
    payload = json.loads(moments[0]["payload"])
    tournamentList = payload["tournamentList"]
    items = []
    for month in tournamentList:
        tournaments = month["tournaments"]
        for tournament in tournaments:
            tournamentName = tournament["tournamentName"]["full"]
            try: venue = tournament["venue"]["name"]
            except: venue = ""
            try: stageName = tournament["stageName"]["full"]
            except: stageName = ""
            date = tournament["date"]
            startDate = date["startDate"]
            date_label = startDate
            endDate = date["endDate"]
            if endDate:
                date_label += " - " + endDate
            if stageName:
                stageName = "(%s)" % stageName
            if venue:
                venue = "[%s]" % venue
            else:
                venue = ""
            if plugin.get_setting('venue') == 'true':
                label = "%s - [B]%s[/B] %s %s" % (date_label,tournamentName,stageName,venue,)
            else:
                label = "%s - [B]%s[/B] %s" % (date_label,tournamentName,stageName)
            items.append({
                'label': label,
                'path': plugin.url_for('bbc_calendar_morph', sport=sport),
            })
    return items


@plugin.route('/bbc_fixtures/<sport>')
def bbc_fixtures(sport):
    url = "http://www.bbc.co.uk/sport/"+sport+"/fixtures"
    html = requests.get(url).content
    items = []
    table = html
    dates = table.split('<h3')
    for date in dates:
        d = re.search('data-role="date">(.*?)<',date)
        if d:
            d = d.group(1)
            d = d.split()
            if len(d) == 4:
                day = re.sub('[a-z]*','',d[1])
                month = d[2]
                year = d[3]
                dt = datetime.datetime.strptime("%s %s %s" % (day,month,year),"%d %B %Y")
        else:
            continue
        fixtures_block_list = date.split('<h4')
        for fixture_block in fixtures_block_list:
            competition = re.search('data-role="competition-name">(.*?)<',fixture_block)
            if competition:
                c = "(%s)" % competition.group(1).strip()
            else:
                c = ''
            fixtures = fixture_block.split("list-ui__item")
            for fixture in fixtures:
                home = re.search('<abbr title="([^>]*?)"[^>]*?data-role="home-team"',fixture)
                if home:
                    h = home.group(1)
                else:
                    h = ""
                away = re.search('<abbr title="([^>]*?)"[^>]*?data-role="away-team"',fixture)
                if away:
                    a = away.group(1)
                else:
                    a = ""
                if h or a:
                    search = "%s*%s" % (h,a)
                    label = "%s - [B]%s v %s[/B] %s" % (dt.strftime("%Y-%m-%d"),h,a,c)
                    items.append({
                        "label": label,
                        "path" : "plugin://plugin.video.tfixtures.listings/search/%s" % search
                    })
    return items

@plugin.route('/bbc_us_fixtures/<sport>')
def bbc_us_fixtures(sport):
    url = "http://www.bbc.co.uk/sport/"+sport+"/fixtures"
    html = requests.get(url).content
    items = []
    table = html
    dates = table.split('<h3 class="gel-pica-bold gel-mb"')
    for date in dates:
        d = re.search('>(.*?)<',date)
        dt = None
        if d:
            d = d.group(1)
            d = d.split()
            if len(d) == 4:
                day = re.sub('[a-z]*','',d[1])
                month = d[2]
                year = d[3]
                dt = datetime.datetime.strptime("%s %s %s" % (day,month,year),"%d %B %Y")
        else:
            continue
        fixtures_block_list = date.split('<li class="list-ui__item gel-pb-"')
        for fixture_block in fixtures_block_list:
            home = re.search('fixture-team-home\.0\.0\.0">(.*?)</span>',fixture_block)
            if home:
                h = home.group(1)
            else:
                h = ""
            away = re.search('fixture-team-away\.0\.0\.0">(.*?)</span>',fixture_block)
            if away:
                a = away.group(1)
            else:
                a = ""
            if h or a:
                search = "%s*%s" % (h,a)
                label = "%s - [B]%s v %s[/B]" % (dt.strftime("%Y-%m-%d"),h,a)
                items.append({
                    "label": label.strip(),
                     "path" : "plugin://plugin.video.tfixtures.listings/search/%s" % search
                })
    return items



def sports():
    html = requests.get("http://www.bbc.co.uk/sport/all-sports").content
    sports_list = re.findall('href="/sport/([^"]*?)">(.*?)</a>',html)
    log(sports_list)
    for sport in sports_list:
        log(sport)
    links = [x[0] for x in sports_list]
    return links

def bbc_index():
    fixtures_list = []
    calendar_list = []
    scores_list = []
    morph_list = []
    for sport in ["motor-racing","motorcycling","speedway",'all-sports', 'american-football', 'archery', 'athletics', 'badminton', 'baseball', 'basketball', 'bowls', 'boxing', 'canoeing', 'cricket', 'curling', 'cycling', 'darts', 'disability-sport', 'diving', 'equestrian', 'fencing', 'football', 'formula1', 'northern-ireland/gaelic-games', 'golf', 'gymnastics', 'handball', 'hockey', 'horse-racing', 'ice-hockey', 'judo', 'modern-pentathlon', 'motorsport', 'netball', 'olympics', 'rowing', 'rugby-league', 'rugby-union', 'sailing', 'shooting', 'snooker', 'squash', 'swimming', 'table-tennis', 'taekwondo', 'tennis', 'triathlon', 'volleyball', 'weightlifting', 'winter-sports', 'wrestling']:
        url = "http://www.bbc.co.uk/sport/"+sport+"/fixtures"
        r = requests.get(url)
        if r.status_code == 200:
            fixtures_list.append(sport)
        url = "http://www.bbc.co.uk/sport/"+sport+"/scores-fixtures"
        r = requests.get(url)
        if r.status_code == 200:
            scores_list.append(sport)
        url = "http://www.bbc.co.uk/sport/"+sport+"/calendar"
        r = requests.get(url)
        if r.status_code == 200:
            calendar_list.append(sport)
    log(fixtures_list)
    log(scores_list)
    log(calendar_list)

@plugin.route('/bbc_sports_index')
def bbc_sports_index():
    global big_list_view
    big_list_view = False

    items = []

    for sport in ['football']:
        items.append({
            'label': "%s" % sport.replace('-',' ').title(),
            'path': plugin.url_for('bbc_scores', sport=sport),
        })
    for sport in ['american-football', 'basketball', 'ice-hockey', ]:
        items.append({
            'label': "%s" % sport.replace('-',' ').title(),
            'path': plugin.url_for('bbc_us_fixtures', sport=sport),
        })
    for sport in ['cricket', 'rugby-league', 'rugby-union']:
        items.append({
            'label': "%s" % sport.replace('-',' ').title(),
            'path': plugin.url_for('bbc_fixtures', sport=sport),
        })
    for sport in ['athletics', 'badminton', 'bowls', 'boxing', 'cycling', 'darts', 'equestrian', 'golf', 'horse-racing', 'motorsport', 'rowing', 'snooker', 'swimming', 'tennis', 'triathlon', 'winter-sports']:
        items.append({
            'label': "%s" % sport.replace('-',' ').title(),
            'path': plugin.url_for('bbc_calendar', sport=sport),
        })
    for sport in ["motorcycling","speedway"]:
        items.append({
            'label': "%s" % sport.replace('-',' ').title(),
            'path': plugin.url_for('bbc_calendar_morph', sport=sport),
        })

    return sorted(items, key=lambda x: x["label"])


@plugin.route('/thefixtures/<sport>')
def thefixtures(sport):
    streams = plugin.get_storage('streams')
    url = "http://thefixtures.website/"+sport
    html = requests.get(url).content
    bst = re.search("All times are BST",html)
    items = []
    matches = re.findall(r'(<h([0-9]).*?</h\2>)',html,flags=(re.MULTILINE|re.DOTALL))
    fixture = ''
    dt = None
    for match in matches:
        if match[1] == '2':
            date = re.sub('<.*?>','',match[0]).strip('.\n')
            if date not in ["Fundraising",'Timezone Converter']:
                match = re.search('([^ ]*?) ([0-9]*)[^ ]*? (.*)',date)
                day = match.group(2)
                month = match.group(3)
                months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
                month = months.index(month) + 1
                now = datetime.datetime.now()
                midnight = datetime.datetime(now.year,now.month,now.day)
                dt = datetime.datetime(now.year,month,int(day))
                if dt < midnight:
                    dt = dt.replace(year=dt.year+1)
                '''
                items.append({
                    "label": date,
                    'thumbnail':get_icon_path('calendar'),
                })
                '''
        elif match[1] == '1':
            fixture = re.sub('<.*?>','',match[0]).strip('.\n').replace('\n',' ')
            match = re.search("([0-9]{2}):([0-9]{2})",fixture)
            if match:
                hour = int(match.group(1))
                min = int(match.group(2))
        elif match[1] == '3':
            channels = re.sub('<br />','|',match[0])
            channels = re.sub('<.*?>','',channels).strip('.\n').replace('\n',' ')
            channels = re.sub('&amp;','&',channels)
            channel_list = channels.split('|')
            channels = []
            for channel in channel_list:
                channel = channel.strip()
                channels.append(channel)
                if channel not in streams:
                    streams[channel] = ""
            channels = ','.join(channels)
            if channels:
                utc = timezone('Europe/London')
                start = dt.replace(minute=min,hour=hour,tzinfo=utc)
                to_zone = tz.tzlocal()
                start = start.astimezone(to_zone)
                if bst:
                    start = start - datetime.timedelta(hours=1)
                label = "%04d-%02d-%02d %02d:%02d [B]%s[/B] [%s]" % (start.year,start.month,start.day,start.hour,start.minute,fixture[8:],channels)
                end = start
                start_time = str(int(time.mktime(start.timetuple())))
                end_time = str(int(time.mktime(end.timetuple())))
                path = plugin.url_for('stations_list', stations=channels, start=start_time, end=end_time, label=fixture)
                items.append({
                    "label": label,
                    "path": path,
                    'thumbnail':get_icon_path('clock'),
                })
    return items

@plugin.route('/thefixtures_football/<sport>')
def thefixtures_football(sport):
    streams = plugin.get_storage('streams')
    url = "http://thefixtures.website/"+sport
    html = requests.get(url).content
    bst = re.search("British Summer Time",html)
    match = re.findall("http://thefixtures.website/.*?day.*?/",html)
    items = []
    days = int(plugin.get_setting('thefixtures.days'))
    for match_day_url in match[:days]:
        html = requests.get(match_day_url).content


        matches = re.findall(r'(<h([0-9]).*?</h\2>)',html,flags=(re.MULTILINE|re.DOTALL))
        fixture = ''
        dt = None
        for match in matches:
            #log(match)
            if match[1] == '1':
                if "entry-title" in match[0]:
                    date = re.sub('<.*?>','',match[0]).strip('.\n')
                    if date not in ["Fundraising",'Timezone Converter']:
                        #log(date)
                        match = re.search('([^ ]*?) ([0-9]*)[^ ]*? (.*)',date)
                        #log(match)
                        if(match):
                            day = match.group(2)
                            month = match.group(3)
                            months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
                            month = months.index(month) + 1
                            now = datetime.datetime.now()
                            midnight = datetime.datetime(now.year,now.month,now.day)
                            dt = datetime.datetime(now.year,month,int(day))
                            if dt < midnight:
                                dt = dt.replace(year=dt.year+1)
                            #log(dt)
                            '''
                            items.append({
                                "label": date,
                                'thumbnail':get_icon_path('calendar'),
                            })
                            '''
                else:
                    fixture = re.sub('<.*?>','',match[0]).strip('.\n').replace('\n',' ')
                    fixture = re.sub('&amp;','&',fixture)
                    #log(fixture)
                    match = re.search("([0-9]{2}):([0-9]{2})",fixture)
                    if match:
                        hour = int(match.group(1))
                        min = int(match.group(2))
                        #log((hour,min))
            elif match[1] == '3':
                channels = re.sub('<br />','|',match[0])
                channels = re.sub('<.*?>','',channels).strip('.\n').replace('\n',' ')
                channels = re.sub('&amp;','&',channels)
                channel_list = channels.split('|')
                channels = []
                for channel in channel_list:
                    channel = channel.strip()
                    channels.append(channel)
                    if channel not in streams:
                        streams[channel] = ""
                channels = ','.join(channels)
                #log(channels)
                if channels and dt:
                    utc = timezone('Europe/London')
                    start = dt.replace(minute=min,hour=hour,tzinfo=utc)
                    to_zone = tz.tzlocal()
                    start = start.astimezone(to_zone)
                    if bst:
                        start = start - datetime.timedelta(hours=1)
                    label = "%04d-%02d-%02d %02d:%02d [B]%s[/B] [%s]" % (start.year,start.month,start.day,start.hour,start.minute,fixture[8:],channels)
                    end = start
                    start_time = str(int(time.mktime(start.timetuple())))
                    end_time = str(int(time.mktime(end.timetuple())))
                    path = plugin.url_for('stations_list', stations=channels, start=start_time, end=end_time, label=fixture)
                    items.append({
                        "label": label,
                        "path": path,
                        'thumbnail':get_icon_path('clock'),
                    })
    return items


@plugin.route('/thefixtures_index')
def thefixtures_index():
    global big_list_view
    big_list_view = False

    items = []
    for sport,label in [('cricket','Cricket'),('rugby','Rugby'),('boxingmma','Boxing/MMA'),('gaelic-games','Gaelic Games'),('baseball','Baseball')]:
        items.append({
            'label': label,
            'path': plugin.url_for('thefixtures', sport=sport),
            'thumbnail':get_icon_path(sport),
        })
    for sport,label in [('football','Football')]:
        items.append({
            'label': label,
            'path': plugin.url_for('thefixtures_football', sport=sport),
            'thumbnail':get_icon_path(sport),
        })
    return sorted(items, key=lambda x: x["label"])


@plugin.route('/')
def index():
    global big_list_view
    big_list_view = False

    items = []
    '''
    context_items = []
    context_items.append(("[COLOR yellow][B]%s[/B][/COLOR] " % 'Clear Channels', 'XBMC.RunPlugin(%s)' % (plugin.url_for(clear_channels))))
    items.append({
        'label': "Channels",
        'path': plugin.url_for('channel_list'),
        'thumbnail': 'special://home/addons/plugin.program.tardis-fixtures/resources/img/tv.png',
        'context_menu': context_items,
    })
    '''
    items.append({
        'label': "BBC Sport",
        'path': plugin.url_for('bbc_sports_index'),
    })
    '''
    items.append({
        'label': "The Fixtures",
        'path': plugin.url_for('thefixtures_index'),
    })
    '''
    return items


if __name__ == '__main__':
    plugin.run()
    if big_list_view:
        plugin.set_view_mode(int(plugin.get_setting('view')))