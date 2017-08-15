import json
import urllib2
import re

from httplib import HTTPException

from retrying import Retrying

stream_re = re.compile(r"""(?P<q>['"])(?P<stream_url>https?://.*m3u8\?.*clientKey=.*?)(?P=q)""")


def retry_if_http_error(exception):
    """Return True if we should retry (in this case when it"s an IOError), False otherwise"""
    return isinstance(exception, (IOError, HTTPException))


class TVCatchupError(Exception):
    pass


class TVCatchupBlocked(TVCatchupError):
    pass


class TVCatchup(object):
    API_URL = "http://www.tvcatchup.com/api/{0}"
    USER_AGENT = "TVCatchup/1.0.1 (samsung/SM-J7008; Android 4.4.2/KOT49H)"

    def __init__(self, region=1):
        self.region = region

    @staticmethod
    def lookup_region(name):
        return {"Greater London": 1, "West Midlands": 2, "Greater Manchester": 3, "West Yorkshire": 4, "Kent": 5,
                "Essex": 6, "Merseyside": 7, "South Yorkshire": 8, "Hampshire": 9, "Lancashire": 10, "Surrey": 11,
                "Hertfordshire": 12, "Tyne and Wear": 13, "Norfolk": 14, "Staffordshire": 15, "West Sussex": 16,
                "Nottinghamshire": 17, "Derbyshire": 18, "Devon": 19, "Suffolk": 20, "Lincolnshire": 21,
                "Northamptonshire": 22, "Oxfordshire": 23, "Leicestershire": 24, "Cambridgeshire": 25,
                "North Yorkshire": 26, "Gloucestershire": 27, "Worcestershire": 28, "Warwickshire": 29, "Cornwall": 30,
                "Somerset": 31, "East Sussex": 32, "County Durham": 33, "Buckinghamshire": 34, "Cumbria": 35,
                "Wiltshire": 36, "Bristol": 37, "Dorset": 38, "Cheshire East": 39, "East Riding of Yorkshire": 40,
                "Leicester": 41, "Cheshire West and Chester": 42, "Northumberland": 43, "Shropshire": 44,
                "Nottingham": 45, "Brighton & Hove": 46, "Medway": 47, "South Gloucestershire": 48, "Plymouth": 49,
                "Hull": 50, "Central Bedfordshire": 51, "Milton Keynes": 52, "Derby": 53, "Stoke-on-Trent": 54,
                "Southampton": 55, "Swindon": 56, "Portsmouth": 57, "Luton": 58, "North Somerset": 59, "Warrington": 60,
                "York": 61, "Stockton-on-Tees": 62, "Peterborough": 63, "Herefordshire": 64, "Bournemouth": 65,
                "Bath and North East Somerset": 66, "Southend-on-Sea": 67, "North Lincolnshire": 68,
                "Telford and Wrekin": 69, "North East Lincolnshire": 70, "Thurrock": 71, "Bedford": 72, "Reading": 73,
                "Wokingham": 74, "West Berkshire": 75, "Poole": 76, "Blackburn with Darwen": 77,
                "Windsor and Maidenhead": 78, "Blackpool": 79, "Slough": 80, "Middlesbrough": 81, "Isle of Wight": 82,
                "Redcar and Cleveland": 83, "Torbay": 84, "Halton": 85, "Bracknell Forest": 86, "Darlington": 87,
                "Hartlepool": 88, "Rutland": 89, "Isles of Scilly": 90, "Wales": 92, "Scotland": 93}.get(name, 1)

    def api_call(self, path, headers=None, retries=10, **kwargs):
        timeout = kwargs.pop("timeout", 10.0)

        opener = urllib2.build_opener()
        opener.addheaders = [("User-Agent", self.USER_AGENT),
                             ("region-id", str(self.region))]

        req = urllib2.Request(self.API_URL.format(path), **kwargs)

        # Make the request, with retries
        retrier = Retrying(stop_max_attempt_number=retries,
                           wait_exponential_multiplier=500,
                           wait_exponential_max=5000,
                           retry_on_exception=retry_if_http_error,
                           wrap_exception=True)
        res = retrier.call(opener.open, req, timeout=timeout)
        return json.loads(res.read())

    def channels(self):
        return self.api_call("appcache")

    def stream(self, channel_id):
        data = self.api_call("stream/{0}".format(channel_id))
        if data["blocked"]:
            raise TVCatchupBlocked(data.get("blocked_message"))
        else:
            return data["stream"]
