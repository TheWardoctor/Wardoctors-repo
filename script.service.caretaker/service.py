from resources.lib.tools import *

bl_installed = []

def run_service():
    updateBlacklist(BLACKLIST_CACHE, BLACKLIST_REMOTE, BLACKLIST)
    try:
        with open(BLACKLIST, 'r') as filehandle:
            blacklisted = filehandle.read().splitlines()
    except IOError:
        writeLog('Could not open blacklist file', xbmc.LOGFATAL)
        return

    writeLog('%s blacklisted repositories loaded' % (len(blacklisted)))

    query = {"method": "Addons.GetAddons",
             "params": {"type": "xbmc.addon.repository",
                       "enabled": "all",
                       "properties": ["name", "path", "version"]}
             }

    response = jsonrpc(query)
    if 'addons' in response:
        writeLog('Check addon folder for blacklisted repositories', xbmc.LOGNOTICE)
        for addon in response['addons']:
            aid = addon.get('addonid', '')
            if aid in blacklisted: bl_installed.append(addon)

        if len(bl_installed) > 0:
            for bl_repo in bl_installed:
                writeLog('Repository \'%s\' found' %
                         (bl_repo.get('addonid', '')), xbmc.LOGNOTICE)
            notify(LS(30011), LS(30012), icon=xbmcgui.NOTIFICATION_WARNING)
            xbmcgui.Window(10000).setProperty('script.service.caretaker.found.blacklisted', 'true')
        else:
            writeLog('No potentially harmful repositories found', xbmc.LOGNOTICE)
            xbmcgui.Window(10000).setProperty('script.service.caretaker.found.blacklisted', 'false')

    else:
        writeLog('Could not execute JSON query', xbmc.LOGFATAL)

if __name__ == '__main__':

    monitor = xbmc.Monitor()
    loop = 0
    while not monitor.abortRequested() and (getAddonSetting('permanent', BOOL) or loop == 0):
        run_service()
        loop += 1
        if monitor.waitForAbort(1800): break

