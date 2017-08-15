'''
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''
import re, json, urllib2
from lib import helpers
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class AdultSwimResolver(UrlResolver):
    name = "AdultSwim"
    domains = ["adultswim.com"]
    pattern = "(?://|\.)(adultswim\.com)/videos/((?!streams)[a-z\-]+/[a-z\-]+)"

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        
        if html:
            try:
                json_data = re.search("""__AS_INITIAL_DATA__\s*=\s*({.*?});""", html).groups()[0]
                json_data = json_data.replace("\/", "/")
                a = json.loads(json_data)
                ep_id = a["show"]["sluggedVideo"]["id"]
                api_url = 'http://www.adultswim.com/videos/api/v2/videos/%s?fields=title,type,duration,collection_title,images,stream,segments,title_id&iframe=false' % ep_id
                headers.update({'Referer': web_url})
                api_data = self.net.http_GET(api_url, headers=headers).content
                api_data = api_data.replace("\/", "/")
                b = json.loads(api_data)
                sources = b["data"]["stream"]["assets"]
                sources = [("%sbps" % sources[i]["bitrate"], sources[i]["url"]) for i in range(len(sources)) if sources[i]["mime_type"]== "application/x-mpegURL" and self.__test_stream(sources[i]["url"])]
                
                if sources: return helpers.pick_source(sources) + helpers.append_headers(headers)
                
            except:
                raise ResolverError('Video not found')
                
        raise ResolverError('Video not found')
        
    def __test_stream(self, stream_url):
        '''
        Returns True if the stream_url gets a non-failure http status (i.e. <400) back from the server
        otherwise return False

        Intended to catch stream urls returned by resolvers that would fail to playback
        '''
        # parse_qsl doesn't work because it splits elements by ';' which can be in a non-quoted UA
        try: headers = dict([item.split('=') for item in (stream_url.split('|')[1]).split('&')])
        except: headers = {}
        for header in headers:
            headers[header] = urllib.unquote_plus(headers[header])
        common.logger.log_debug('Setting Headers on UrlOpen: %s' % (headers))

        try:
            msg = ''
            request = urllib2.Request(stream_url.split('|')[0], headers=headers)
            #  set urlopen timeout to 15 seconds
            http_code = urllib2.urlopen(request, timeout=15).getcode()
        except urllib2.URLError as e:
            if hasattr(e, 'reason'):
                # treat an unhandled url type as success
                if 'unknown url type' in str(e.reason).lower():
                    return True
                else:
                    msg = e.reason
                    
            if isinstance(e, urllib2.HTTPError):
                http_code = e.code
            else:
                http_code = 600
            if not msg: msg = str(e)
        except Exception as e:
            http_code = 601
            msg = str(e)

        # added this log line for now so that we can catch any logs on streams that are rejected due to test_stream failures
        # we can remove it once we are sure this works reliably
        if int(http_code) >= 400:
            common.logger.log_warning('Stream UrlOpen Failed: Url: %s HTTP Code: %s Msg: %s' % (stream_url, http_code, msg))

        return int(http_code) < 400

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='http://{host}/videos/{media_id}')