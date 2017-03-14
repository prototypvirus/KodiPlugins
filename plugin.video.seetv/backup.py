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
import urllib
common = XbmcHelpers

class SeeTV
	def __init__(self):
		self.id = 'plugin.video.seetv'
		self.addon = xbmcaddon.Addon(self.id)
		self.icon = self.addon.getAddonInfo('icon')
		self.path = self.addon.getAddonInfo('path')
		self.profile = self.addon.getAddonInfo('profile')
		
		self.language = self.addon.getLocalizedString

		self.handle = int(sys.argv[1])
		self.params = sys.argv[2]

		self.url = 'http://seetv.tv'

		self.inext = os.path.join(self.path, 'resources/icons/next.png')
		self.debug = False

	def main(self):
		params = common.getParameters(self.params)
		mode = params['mode'] if 'mode' in params else None

		if mode == 'play':
			self.playChannel(params['channel'])
		else:
			self.listChannels()

	def listChannels(self):
		req = requests.get(self.url+'/online-tv-see')
		if req.status_code != 200:
			xbmc.executebuiltin("XBMC.Notification(%s,%s,%s)", % ("Error", 'Can\'t get page!', str(10 * 1000))
			return
		page = req.text
		channels  = re.findall(r"<a href=\"(http://seetv.tv/vse-tv-online/[A-Za-z0-9\-]+)\">([^<]+)</a>", page)
		for c in channels:
			uri = sys.argv[0] + '?mode=play&channel=%s' % c[1]
			item = xbmcgui.ListItem(c[0], thumbnailImage=self.icon)
			xbmcplugin.addDirectoryItem(self.handle, uri, item, True)
		xbmc.executebuiltin('Container.SetViewMode(52)')
		xbmcplugin.endOfDirectory(self.handle, True)

	def playChannel(self,  channel):
		req = requests.get(channel)
		if req.status_code != 200:
			xbmc.executebuiltin("XBMC.Notification(%s,%s,%s)" % ('Error', 'Can\'t get page!', str(10 * 1000))
			return
		page = req.text
		channel_num = re.findall(r"var\slinkTv\s=\s(\d+);", page)
		channel_num = channel_num[0]

		req = requests.get(self.url+'/get/player/'+channel_num, headers={'Referer': url, 'X-Requested-With': 'XMLHttpRequest'}, cookies=req.cookies)
		if req.status_code != 200:
			xbmc.executebuiltin("XBMC.Notification(%s,%s,%s)" % ('Error', 'Can\'t get page!', str(10 * 1000))
			return
		page = req.text
		obj = json.loads(page)
		file = urllib.unquote(obj.file)
		item = xbmcgui.ListItem(path=file)
		xbmcplugin.setResolvedUrl(self.handle, True, item)
