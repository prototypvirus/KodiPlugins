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

class CCFan:
	def __init__(self):
		self.id = 'plugin.video.cc-fan'
		self.addon = xbmcaddon.Addon(self.id)
		self.icon = self.addon.getAddonInfo('icon')
		self.path = self.addon.getAddonInfo('path')
		self.profile = self.addon.getAddonInfo('profile')

		self.language = self.addon.getLocalizedString

		self.handle = int(sys.argv[1])
		self.params = sys.argv[2]

		self.url = 'http://cc-fan.ru'

		self.inext = os.path.join(self.path, 'resources/icons/next.png')
		self.debug = False
		self.thumbnails = os.path.join(self.path, 'thumbnails')
		self.makeDirs('southpark')
		self.makeDirs('brickleberry')
		self.makeDirs('drawntogether')

	def makeDirs(self, film):
		fx = os.path.join(self.thumbnails, film)
		if not os.path.exists(fx):
			os.makedirs(fx)

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
		uri = sys.argv[0] + '?mode=%s&film=%s' % ("seasons", "southpark")
		item = xbmcgui.ListItem("South Park", thumbnailImage=self.icon)
		xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

		uri = sys.argv[0] + '?mode=%s&film=%s' % ("seasons", "brickleberry")
		item = xbmcgui.ListItem("Brickleberry", thumbnailImage=self.icon)
		xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

		uri = sys.argv[0] + '?mode=%s&film=%s' % ("seasons", "drawntogether")
		item = xbmcgui.ListItem("Drawn Together", thumbnailImage=self.icon)
		xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

		xbmc.executebuiltin('Container.SetViewMode(52)')
		xbmcplugin.endOfDirectory(self.handle, True)

	def listSeasons(self, film):
		url = "http://%s.cc-fan.ru/seasons.php" % (film)
		req = requests.get(url);
		if not req.status_code == 200:
			xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("Error", 'Can\'t get page!', str(10 * 1000)))
			return

		uri = sys.argv[0] + '?mode=%s&film=%s' % ("random", film)
		item = xbmcgui.ListItem("Random", thumbnailImage=self.icon)
		item.setInfo(type='Video', infoLabels={})
		item.setProperty("IsPlayable", "true")
		xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

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

	def makeImgUrl(self, film, series):
		return "http://%s.fox-fan.ru/seasons/%s.jpg" % (film, str(series))

	def makeImgPath(self, film, series):
		return os.path.join(self.thumbnails, film, str(series))

	def listSeries(self, film, season):
		url = "http://%s.cc-fan.ru/season.php?id=%s" % (film, season)
		req = requests.get(url)
		if not req.status_code == 200:
			xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("Error", 'Can\'t get page!', str(10 * 1000)))
			return

		page = req.text  #.decode('cp1251').encode('utf-8')
		series = re.findall(r'\((.+)\).+href=\'series.php\?id=(\d+)', page);
		series = sorted(set(series), key=lambda x: x[1])

		for x in series:
			serieID = int(x[1])
			serieName = x[0]
			uri = sys.argv[0] + '?mode=%s&film=%s&season=%s&series=%s' % ("play", film, season, seriesID)
			imgPath = self.makeImgPath(film, serieID)
			if not os.path.isfile(imgPath):
				r = requests.get(self.makeImgUrl(film, serieID))
				if r.status_code == 200:
					with open(imgPath, 'wb') as f:
						for c in r:
							f.write(c)
				else:
					imgPath = self.icon
			item = xbmcgui.ListItem(serieName, thumbnailImage=imgPath)

			item.setInfo(type='Video', infoLabels={})
			item.setProperty("IsPlayable", "true")
			xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

		xbmc.executebuiltin('Container.SetViewMode(500)') #52-List | 500-thumbnails
		xbmcplugin.endOfDirectory(self.handle, True)

	def playItem(self, film, season, series):
		url = "http://%s.cc-fan.ru/series.php?id=%s" % (film, series)
		req = requests.get(url)
		if not req.status_code == 200:
			xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("Error", 'Can\'t get page!', str(10 * 1000)))
			return

		page = req.text.encode('utf-8')
		videoUrl = re.findall(r'(http\:\/\/[A-Za-z0-9\/\.\-_]+\.mp4)', page)
		
		print("CC-FAN ", videoUrl[0])

		item = xbmcgui.ListItem(path=videoUrl[0])
		xbmcplugin.setResolvedUrl(self.handle, True, item)

	def playRandom(self, film):
		url = "http://%s.cc-fan.ru/random.php" % (film)
		req = requests.get(url)
		if not req.status_code == 200:
			xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("Error", 'Can\'t get page!', str(10 * 1000)))
			return

		page = req.text.encode('utf-8')
		videoUrl = re.findall(r'series\.php\?id=(\d+)', page)
		
		print("CC-FAN ", videoUrl[0])

		self.playItem(film, -1, int(videoUrl[0]))

	def log(self, msg):
		pass

f = CCFan()
f.main()
