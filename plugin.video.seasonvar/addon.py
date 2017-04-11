#!/usr/bin/python
# Writer (c) 2016, SymbX
# Rev. 0.0.0
# -*- coding: utf-8 -*-

import os
import sys
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import XbmcHelpers
import requests
import re
import json
common = XbmcHelpers

class Seasonvar:
    def __init__(self):
        self.id = 'plugin.video.seasonvar'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')

        self.language = self.addon.getLocalizedString

        self.handle = int(sys.argv[1])
        self.params = sys.argv[2]

        self.url = 'http://seasonvar.ru'

        self.inext = os.path.join(self.path, 'resources/icons/next.png')
        self.debug = False
        self.history = []
        self.loadHistory()

    def main(self):
        self.log("Addon: %s"  % self.id)
        self.log("Handle: %d" % self.handle)
        self.log("Params: %s" % self.params)

        params = common.getParameters(self.params)

        mode = params['mode'] if 'mode' in params else None

        if mode == 'play':
            self.playItem(params['series'])
        if mode == 'series':
            self.listSeries(params['season'])
        if mode == 'seasons':
            self.listSeasons(params['serial'])
        if mode == 'serials':
            self.listSerials(int(params['genre']), 0)
        if mode == 'page':
            self.pagination(int(params['genre']), int(params['page']))
        if mode == 'genres':
            self.listGenres()
        if mode == 'history':
            self.listHistory()
        if mode == 'updates':
            self.listUpdates(params['date'])
        if mode == 'clearhistory':
            self.clearHistory()
            self.menu()
        elif mode is None:
            self.menu() #Genres

    def addGenre(self, gid, gname):
        uri = sys.argv[0] + '?mode=%s&genre=%d' % ('serials', gid)
        item = xbmcgui.ListItem(gname, thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

    def menu(self):
        uri = sys.argv[0] + '?mode=%s' % ('genres')
        item = xbmcgui.ListItem("[COLOR=FFC2FFA4]<Genres>[/COLOR]", thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)
        uri = sys.argv[0] + '?mode=%s' % ('history')
        item = xbmcgui.ListItem("[COLOR=FFC2FFA4]<History>[/COLOR]", thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        url = 'http://seasonvar.ru/'
        req = requests.get(url)
        if not req.status_code == 200:
            xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("Error", 'Can\'t get page!', str(10 * 1000)))
            return

        page = req.text
        dates = re.findall(r'<div class="news-head">\s+([0-9\.]+)\s+<\/div>', page)

        for x in dates:
            uri = sys.argv[0] + '?mode=%s&date=%s' % ('updates', x)
            item = xbmcgui.ListItem(x, thumbnailImage=self.icon)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def pagination(self, genre, page):
        self.listSerials(genre, page)

    def listGenres(self):
        self.addGenre(19, 'Discovery & BBC')
        self.addGenre(1, 'Animation')
        self.addGenre(18, 'Anime')
        self.addGenre(5, 'Militants')
        self.addGenre(6, 'Detectives')
        self.addGenre(13, 'Documentary')
        self.addGenre(8, 'Drama')
        self.addGenre(14, 'Historical')
        self.addGenre(17, 'Comedy')
        self.addGenre(9, 'Criminal')
        self.addGenre(4, 'Melodrama')
        self.addGenre(15, 'Mystical')
        self.addGenre(10, 'Native')
        self.addGenre(11, 'Adventure')
        self.addGenre(20, 'Reality show')
        self.addGenre(12, 'Family')
        self.addGenre(16, 'Thriller')
        self.addGenre(7, 'Horrors')
        self.addGenre(2, 'Fi')
        self.addGenre(3, 'Fantasy')

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def listUpdates(self, date):
        url = 'http://seasonvar.ru/'
        req = requests.get(url)
        if not req.status_code == 200:
            xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("Error", 'Can\'t get page!', str(10 * 1000)))
            return

        rStart = re.compile(r'<div class="news-head">\s+'+date+'\s+<\/div>')
        rEnd = re.compile(r'<\/div>\s+<\/a>\s+<\/div>')
        page = req.text
        pStart = rStart.search(page)
        page = page[pStart.end():]
        pEnd = rEnd.search(page)
        page = page[:pEnd.start()]
        links = re.findall(r'<a\shref="(\/[a-zA-Z0-9\-_\.]+)"\s+data-id="\d+">\s+<div\sclass="news-w">\s+<div\sclass="news_n">\s+([\s\w,:\(\)\-_\.]+(?<!\s\s))\s+<\/div>\s+(\([\w\s\-_\.]+\))?\s+<span class="news_s">([\w\s\-_\.\(\),]+)<\/span>', page, re.UNICODE)

        for x in links:
            uri = sys.argv[0] + '?mode=%s&serial=%s' % ("seasons", x[0])
            upd = x[2].strip() if len(x) == 3 else x[2].strip()+' '+x[3].strip()
            item = xbmcgui.ListItem("%s [COLOR=FF939393]%s[/COLOR]" % (x[1].strip(), upd), thumbnailImage=self.icon)
            #item = xbmcgui.ListItem(label=x[1], label2=upd, thumbnailImage=self.icon)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def listSerials(self, genre, page):
        url = "http://seasonvar.ru/index.php"

        postData = {
        'filter[block]': '',
        'filter[engName]': '',
        'filter[hd]': '',
        'filter[history]': '',
        'filter[mark]': '',
        'filter[nw]': '',
        'filter[only]': '',
        'filter[quotG][]': str(genre),
        'filter[rait]': 'kp',
        'filter[sub]': ''
        }

        req = requests.post(url, data=postData);
        if not req.status_code == 200:
            xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("Error", 'Can\'t get page!', str(10 * 1000)))
            return

        pageData = req.text
        serials = re.findall(r'"/(serial-\d+-[^\.]+\.html)"[^>]+>\s*([^<]+)</a>', pageData)
        serials = sorted(set(serials), key=lambda x: x[1])

        pagx = page*20

        if page > 0:
            uri = sys.argv[0] + '?mode=%s&page=%d&genre=%d' % ("page", page - 1, genre)
            item = xbmcgui.ListItem("Prev page", thumbnailImage=self.icon)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        playlist = serials[pagx:pagx+20]

        for x in playlist:
            uri = sys.argv[0] + '?mode=%s&serial=%s' % ("seasons", x[0])
            item = xbmcgui.ListItem(x[1], thumbnailImage=self.icon)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        if len(serials) > pagx+20:
            uri = sys.argv[0] + '?mode=%s&page=%d&genre=%d' % ("page", page + 1, genre)
            item = xbmcgui.ListItem("Next page", thumbnailImage=self.icon)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def listSeasons(self, serial):
        url = 'http://seasonvar.ru/%s' % (serial)
        req = requests.get(url)
        if not req.status_code == 200:
            xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("Error", 'Can\'t get page!', str(10 * 1000)))
            return

        page = req.text
        data = re.findall(r'<li class="act">([^\$]+)<\/li>', page)
        seasons = re.findall(r'href="\/(serial-\d+-[^\.]+.html)".+\s+(\d+)[^<]', data[0])

        for x in seasons:
            uri = sys.argv[0] + '?mode=%s&season=%s' % ("series", x[0])
            item = xbmcgui.ListItem("Season %s" % (x[1]), thumbnailImage=self.icon)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def listSeries(self, season):
        url = "http://seasonvar.ru/%s" % (season)
        req = requests.get(url, cookies={'html5default': '1'})
        if not req.status_code == 200:
            xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("Error", 'Can\'t get page!', str(10 * 1000)))
            return

        page = req.text
        timeAndSecure = re.findall(r"var\s+data4play\s+=\s+{\s+'secureMark':\s+'([a-zA-Z0-9]+)',\s+'time':\s+(\d+)\s+}", page)
        timeAndSecure = timeAndSecure[0]
        IDs = re.findall(r"data-id-(season|serial)=\"(\d+)\"", page)
        cont = {
            'secure': timeAndSecure[0],
            'time': timeAndSecure[1],
            'id': IDs[0][1] if IDs[0][0] == 'season' else IDs[1][1],
            'serial': IDs[0][1] if IDs[0][0] == 'serial' else IDs[1][1],
            'type': 'html5'
        }
        title = re.findall(r'<title>([^<]+)<\/title>', page)
        self.addHistory(IDs[0][1] if IDs[0][0] == 'serial' else IDs[1][1], season, title[0])
        req = requests.post('http://seasonvar.ru/player.php', data=cont, cookies={'html5default': '1'}, headers={'Referer':"http://seasonvar.ru/%s" % (season), 'X-Requested-With': 'XMLHttpRequest'})
        if not req.status_code == 200:
            xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ('Error', 'Can\'t get page!', str(10 * 1000)))
            return
        page = req.text
        playlistFile = re.findall(r"var\s+pl\s+=\s+{'0':\s+\"(\/[A-Za-z0-9\/\.\?=]+)\"};", page);

        url = "http://seasonvar.ru/%s" % (playlistFile[0])
        req = requests.get(url, cookies={'html5default': '1'})
        if not req.status_code == 200:
            xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("Error", 'Can\'t get page!', str(10 * 1000)))
            return

        #page = req.text
        #series = re.findall(r'"file":"(http://[A-Za-z0-9\-\._\/,\[\]]+)"', page)
        series = json.loads(req.text)
        series = series['playlist']

        for x in series:
            item = xbmcgui.ListItem(x['comment'][:-4] if x['comment'].endswith('<br>') else x['comment'], thumbnailImage=self.icon)
            item.setInfo(type='Video', infoLabels={})
            item.setProperty("IsPlayable", "true")
            xbmcplugin.addDirectoryItem(self.handle, x['file'], item, False)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def log(self, msg):
        pass

    def loadHistory(self):
	path = xbmc.translatePath(self.profile)
        if not os.path.exists(os.path.join(path, 'history.json')):
            return
        with open(os.path.join(path, 'history.json'), 'r') as fp:
            data = json.load(fp)
            self.history = data['history']

    def saveHistory(self):
	path = xbmc.translatePath(self.profile)
        with open(os.path.join(path, 'history.json'), 'w') as fp:
            data = { 'history': self.history }
            json.dump(data, fp)

    def addHistory(self, id, link, text):
        self.history = [i for i in self.history if not i['id'] == id]
        item = {
            'id': id,
            'link': link,
            'text': text
        }
        self.history.insert(0, item)
        self.history = self.history[0:10]
        self.saveHistory()

    def clearHistory(self):
        self.history = []
        self.saveHistory()

    def listHistory(self):
	self.loadHistory()
        for x in self.history:
            uri = sys.argv[0] + '?mode=%s&serial=%s' % ("seasons", x['link'])
            item = xbmcgui.ListItem(x['text'], thumbnailImage=self.icon)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=clearhistory'
        item = xbmcgui.ListItem('Clear', thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

f = Seasonvar()
f.main()
