import sys
import os.path
import urllib
# force the lib directory in to the python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

import xbmcgui
from retrying import RetryError
from tvcatchup import TVCatchup, TVCatchupBlocked, TVCatchupAgentBlocked
from simpleplugin import Plugin

plugin = Plugin()
_ = plugin.initialize_gettext()


@plugin.action()
def play(params):
    channel_id = params.get("id") or 1
    region = TVCatchup.lookup_region(plugin.get_setting("region"))
    user_agent = plugin.get_setting("useragent")
    api = TVCatchup(region, user_agent)

    try:
        url = api.stream(channel_id)

        if url:
            return Plugin.resolve_url(play_item={
                "path": url + "|User-Agent={0}".format(urllib.quote(user_agent)),
                "label": params.get("name"),
                "icon": params.get("logo"),
                "info": {"Video": {"Plot": params.get("plot")}}
            })
        else:
            plugin.log_error("Failed to open stream {0} (Could not find stream URL)".format(params.get("slug")))
    except RetryError as err:
        plugin.log_error("Failed to open stream {0} ({1})".format(params.get("slug"), err.last_attempt))
    except TVCatchupAgentBlocked as err:
        plugin.log_error("Failed to open stream {0} (User Agent has been blocked)".format(params.get("slug"), err))

        xbmcgui.Dialog().notification(_("Warning"),
                                      _("User Agent has been blocked, set a custom User Agent in the Addon's settings"))
        return Plugin.resolve_url(succeeded=False)
    except TVCatchupBlocked as err:
        plugin.log_error("Failed to open stream {0} (Blocked: {1})".format(params.get("slug"), err))

    xbmcgui.Dialog().notification(_("Warning"),
                                  _("Could not open stream for {0}!").format(params.get("name") or _("Unknown")))
    return Plugin.resolve_url(succeeded=False)


@plugin.action()
def root(params):
    items = []

    region = TVCatchup.lookup_region(plugin.get_setting("region"))
    user_agent = plugin.get_setting("useragent")
    api = TVCatchup(region, user_agent)

    for channel in api.channels():
        items.append({
            "label": channel["name"] + (" [COLOR red][B](Off-air)[/B][/COLOR]" if channel["online"] != 1 else ""),
            "label2": channel["epg"]["programme_title"],
            "url": plugin.get_url(action="play",
                                  id=channel["id"],
                                  name=channel["name"],
                                  logo=channel["logo"],
                                  slug=channel["slug"],
                                  plot=channel["epg"]["programme_desc"],
                                  title=channel["epg"]["programme_title"]
                                  ),
            "thumb": channel["logo"] + "|User-Agent={0}".format(urllib.quote(user_agent)),
            "is_playable": True,
            "info": {
                "Video": {
                    "Plot": channel["epg"]["programme_desc"],
                }
            }
        })

    return Plugin.create_listing(items, sort_methods=(0, ), content="movies")


if __name__ == "__main__":
    plugin.run()
