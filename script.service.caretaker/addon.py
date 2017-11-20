from xml.dom import minidom
from datetime import datetime
from resources.lib.tools import *


def get_addon_list(repo_path, exclude_id):
    addon_list = []
    if repo_path == '': return addon_list
    remote_url = None

    try:
        xml = minidom.parse(os.path.join(repo_path, 'addon.xml'))
        extensions = xml.getElementsByTagName('extension')
        for extension in extensions:
            if extension.getAttribute('point') == 'xbmc.addon.repository':
                remote_url = extension.getElementsByTagName('info')[0].firstChild.wholeText
                break
        if remote_url == None: return
        writeLog('Getting content from %s' % (remote_url))

        # we got the remote_url, fill the addon_list
        # tell the repo we are a firefox browser

        req = urllib2.Request(remote_url, None, headers={'User-agent': 'Mozilla/5.0'})
        xml = minidom.parseString(urllib2.urlopen(req, timeout=5).read())
        remote_addons = xml.getElementsByTagName('addon')
        for addon in remote_addons:
            if addon.getAttribute('id') == exclude_id: continue
            addon_list.append({'name': addon.getAttribute('name'),
                               'id': addon.getAttribute('id'),
                               'version': addon.getAttribute('version')})

    except urllib2.URLError, e:
        writeLog('Could not read content of remote repository', xbmc.LOGFATAL)
        writeLog('%s' % (e.reason), xbmc.LOGFATAL)

    except Exception, e:
        writeLog(e.message, xbmc.LOGERROR)

    return addon_list

def run_script():

    if os.path.exists(CT_LOG): os.remove(CT_LOG)
    writeLog('*** Starting %s V.%s at %s ***' %
             (ADDON_NAME, ADDON_VERSION, datetime.now().strftime('%Y-%m-%d %H:%M')), extra=CT_LOG)
    updateBlacklist(BLACKLIST_CACHE, BLACKLIST_REMOTE, BLACKLIST)
    try:
        with open(BLACKLIST_CACHE, 'r') as filehandle:
            blacklisted = filehandle.read().splitlines()
    except IOError:
        writeLog('Could not open blacklist file', xbmc.LOGFATAL)
        return

    writeLog('Use blacklist with timestamp %s' %
             (datetime.fromtimestamp(os.path.getmtime(BLACKLIST_CACHE)).strftime('%Y-%m-%d %H:%M')), extra=CT_LOG)
    writeLog('%s blacklisted items loaded' % (len(blacklisted)), extra=CT_LOG)

    bl_installed = []
    bl_addons_installed = []

    query = {"method": "Addons.GetAddons",
             "params": {"type": "xbmc.addon.repository",
                       "enabled": "all",
                       "properties": ["name", "path", "version"]}
             }

    response = jsonrpc(query)
    if 'addons' in response:
        writeLog('Check addon folder for blacklisted repositories', xbmc.LOGNOTICE, extra=CT_LOG)
        for repo in response['addons']:
            if repo.get('addonid', '') in blacklisted:
                time_installed = int(os.path.getmtime(repo.get('path','')))
                dt = datetime.fromtimestamp(time_installed).strftime('%Y-%m-%d %H:%M')
                repo.update({'timestamp': time_installed, 'datetime': dt})
                bl_installed.append(repo)

        if len(bl_installed) > 0:
            for bl_repo in bl_installed:
                writeLog('Repository \'%s\' found' % (bl_repo.get('addonid', '')), xbmc.LOGNOTICE, extra=CT_LOG)

                bl_addons = get_addon_list(bl_repo.get('path', ''), bl_repo.get('addonid', ''))
                if len(bl_addons) > 0:

                    query = {"method": "Addons.getAddons",
                             "params": {"enabled": "all",
                                        "properties": ["name", "path", "version"]}}

                    response = jsonrpc(query)
                    if 'addons' in response:

                        # add datetime properties to all addons

                        for addon in response['addons']:
                            time_installed = int(os.path.getmtime(addon.get('path', '')))
                            dt = datetime.fromtimestamp(time_installed).strftime('%Y-%m-%d %H:%M')
                            addon.update({'timestamp': time_installed, 'datetime': dt})

                        # compare and match lists

                        for addon in response['addons']:
                            for bl_addon in bl_addons:
                                if addon['addonid'] == bl_addon['id'] and addon not in bl_addons_installed:
                                    bl_addons_installed.append(addon)
                                    writeLog('installed from repo: \'%s\' (%s)' %
                                             (addon['addonid'], addon['datetime']), xbmc.LOGNOTICE, extra=CT_LOG)

                        # fuzzy logic, compare and match timestamps

                        if getAddonSetting('fuzzy', BOOL):
                            for t_addon in response['addons']:
                                for bl_addon_installed in bl_addons_installed:
                                    if abs(t_addon['timestamp'] - bl_addon_installed['timestamp']) < \
                                            getAddonSetting('variation', sType=NUM, multiplicator=60) and \
                                                    t_addon not in bl_addons_installed:
                                        bl_addons_installed.append(t_addon)
                                        writeLog('possibly installed (same timestamp): \'%s\' (%s)' %
                                                 (t_addon['addonid'], t_addon['datetime']), xbmc.LOGNOTICE, extra=CT_LOG)
                    else:
                        writeLog('Could not execute JSON query', xbmc.LOGFATAL)


            dialogOk(LS(30010), LS(30013))
        else:
            writeLog('No potentially harmful repositories found', xbmc.LOGNOTICE, extra=CT_LOG)
            notify(LS(30010), LS(30014))
    else:
        writeLog('Could not execute JSON query', xbmc.LOGFATAL)

if __name__ == '__main__':
    try:
        par = sys.argv[1]
        if par == 'actualize_blacklist':
            rv = updateBlacklist(BLACKLIST_CACHE, BLACKLIST_REMOTE, BLACKLIST, force=True)
            if rv == 'online':
                notify(LS(30010), LS(30022))
            else:
                notify(LS(30010), LS(30023))
    except IndexError:
        # Start without arguments (i.e. login|startup|restart)
        run_script()
