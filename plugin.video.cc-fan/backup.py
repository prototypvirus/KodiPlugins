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
common = XbmcHelpers

class FoxFan:
    def __init__(self):
        self.id = 'plugin.video.fox-fan'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')

        self.language = self.addon.getLocalizedString

        self.handle = int(sys.argv[1])
        self.params = sys.argv[2]

        self.url = 'http://fox-fan.ru'

        self.inext = os.path.join(self.path, 'resources/icons/next.png')
        self.debug = False

    def main(self):
        self.log("Addon: %s"  % self.id)
        self.log("Handle: %d" % self.handle)
        self.log("Params: %s" % self.params)

        params = common.getParameters(self.params)

        mode = params['mode'] if 'mode' in params else None

        if mode == 'play':
            self.playItem(params['film'], params['season'], params['series'])
        if mode == 'series':
            self.listSeries(params['film'], params['season'])
        if mode == 'seasons':
            self.listSeasons(params['film'])
        if mode == 'random':
            self.playRandom(params['film'])
        elif mode is None:
            self.menu()

    def menu(self):
        uri = sys.argv[0] + '?mode=%s&film=%s' % ("seasons", "americandad")
        item = xbmcgui.ListItem("American Dad", thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&film=%s' % ("seasons", "clevelandshow")
        item = xbmcgui.ListItem("Cleveland Show", thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&film=%s' % ("seasons", "familyguy")
        item = xbmcgui.ListItem("Family Guy", thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&film=%s' % ("seasons", "futurama")
        item = xbmcgui.ListItem("Futurama", thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&film=%s' % ("seasons", "simpsons")
        item = xbmcgui.ListItem("Simpsons", thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def listSeasons(self, film):
    	url = "http://%s.fox-fan.ru/seasons.php" % (film)
    	req = requests.get(url);
    	if not req.status_code == 200:
    		xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("Error", 'Can\'t get page!', str(10 * 1000)))
    		return

    	page = req.text.encode('utf-8')
    	seasons = re.findall(r'season\.php\?id=(\d+)', page)
    	seasons = [int(x) for x in seasons]
    	seasons = sorted(set(seasons))

    	for x in seasons:
    		uri = sys.argv[0] + '?mode=%s&film=%s&season=%d' % ("series", film, x)
	        item = xbmcgui.ListItem("Season %s" % (x), thumbnailImage=self.icon)
	        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def listSeries(self, film, season):
    	url = "http://%s.fox-fan.ru/season.php?id=%s" % (film, season)
    	req = requests.get(url)
    	if not req.status_code == 200:
    		xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("Error", 'Can\'t get page!', str(10 * 1000)))
    		return

    	page = req.text  #.decode('cp1251').encode('utf-8')
    	series = re.findall(r'\((.+)\).+href=\'series.php\?id=(\d+)', page);
    	series = sorted(set(series), key=lambda x: x[1])

    	for x in series:
    		uri = sys.argv[0] + '?mode=%s&film=%s&season=%s&series=%s' % ("play", film, season, int(x[1]))
	        item = xbmcgui.ListItem(x[0], thumbnailImage=self.icon)
		item.setInfo(type='Video', infoLabels={})
		item.setProperty("IsPlayable", "true")
	        xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def playItem(self, film, season, series):
    	url = "http://%s.fox-fan.ru/series.php?id=%s" % (film, series)
    	req = requests.get(url)
    	if not req.status_code == 200:
    		xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("Error", 'Can\'t get page!', str(10 * 1000)))
    		return

    	page = req.text.encode('utf-8')
    	videoUrl = re.findall(r'(http\:\/\/[A-Za-z0-9\/\.\-_]+\.mp4)', page)
    	
	print("FOX-FAN ", videoUrl[0])

        item = xbmcgui.ListItem(path=videoUrl[0])
        xbmcplugin.setResolvedUrl(self.handle, True, item)

    def playRandom(self, film):
        url = "http://%s.fox-fan.ru/random.php" % (film)
        req = request
    def log(self, msg):
    	pass

f = FoxFan()
f.main()
