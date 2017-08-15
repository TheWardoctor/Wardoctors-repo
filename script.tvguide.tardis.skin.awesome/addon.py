import xbmc,xbmcgui,xbmcaddon
dialog = xbmcgui.Dialog()

SKINS = [["Awesome", "Awesome"]]

d = xbmcgui.Dialog()
names = [s[0] for s in SKINS]
skin = d.select("TV Guide Tardis - Set Default Skin", names)
if skin > -1:
    tvgf = xbmcaddon.Addon("script.tvguide.tardis")
    if tvgf:
        tvgf.setSetting('skin.source', '2')
        tvgf.setSetting('skin.folder', 'special://home/addons/script.tvguide.tardis.skin.awesome/')
        tvgf.setSetting('skin.user', SKINS[skin][1])
        tvgf.setSetting('categories.background.color', '[COLOR ffb22222]firebrick[/COLOR]')
        tvgf.setSetting('epg.nofocus.color', '[COLOR ffffffff]white[/COLOR]')
        tvgf.setSetting('epg.focus.color', '[COLOR ffffffff]black[/COLOR]')
        tvgf.setSetting('timebar.color', '[COLOR ffffff00]yellow[/COLOR]')
        tvgf.setSetting('epg.video.pip', 'true')
        tvgf.setSetting('program.image.scale', 'false')
        tvgf.setSetting('program.background.image.source', '0')
        tvgf.setSetting('program.background.color', '[COLOR ff4682b4]steelblue[/COLOR]')
        tvgf.setSetting('program.background.flat', 'true')
        tvgf.setSetting('program.background.enabled', 'false')
        tvgf.setSetting('action.bar', 'true')
        dialog.ok('Done', 'Using "' + SKINS[skin][1] + '"')
    if not tvgf: dialog.ok('Error', 'Cannot set "' + SKINS[skin][1] + '"')

