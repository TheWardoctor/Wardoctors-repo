import sys
import os.path
# force the lib directory in to the python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

import xbmcgui
from retrying import RetryError
from tvcatchup import TVCatchup, TVCatchupBlocked
from simpleplugin import Plugin

plugin = Plugin()
_ = plugin.initialize_gettext()


@plugin.action()
def play(params):
    channel_id = params.get("id") or 1
    region = TVCatchup.lookup_region(plugin.get_setting("region"))
    api = TVCatchup(region)

    try:
        url = api.stream(channel_id)

        if url:
            return Plugin.resolve_url(play_item={
                "path": url,
                "label": params.get("name"),
                "icon": params.get("logo"),
                "info": {"Video": {"Plot": params.get("plot")}}
            })
        else:
            plugin.log_error("Failed to open stream {0} (Could not find stream URL)".format(params.get("slug")))
    except RetryError as err:
        plugin.log_error("Failed to open stream {0} ({1})".format(params.get("slug"), err.last_attempt))
    except TVCatchupBlocked as err:
        plugin.log_error("Failed to open stream {0} (Blocked: {1})".format(params.get("slug"), err))

    xbmcgui.Dialog().notification(_("Warning"),
                                  _("Could not open stream for {0}!").format(params.get("name") or _("Unknown")))
    return Plugin.resolve_url(succeeded=False)


@plugin.action()
def root(params):
    items = []

    region = TVCatchup.lookup_region(plugin.get_setting("region"))
    api = TVCatchup(region)

    for channel in api.channels():
        items.append({
            "label": channel["name"],
            "label2": channel["epg"]["programme_title"],
            "url": plugin.get_url(action="play",
                                  id=channel["id"],
                                  name=channel["name"],
                                  logo=channel["logo"],
                                  slug=channel["slug"],
                                  plot=channel["epg"]["programme_desc"],
                                  title=channel["epg"]["programme_title"]
                                  ),
            "thumb": channel["logo"],
            "is_playable": channel["online"] == 1,
            "info": {
                "Video": {
                    "Plot": channel["epg"]["programme_desc"],
                }
            }
        })

    return Plugin.create_listing(items, sort_methods=(0, ), content="movies")


if __name__ == "__main__":
    plugin.run()
