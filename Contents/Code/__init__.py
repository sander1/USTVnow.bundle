import re
from xml.sax.saxutils import unescape

TITLE = 'USTVnow'
ART = 'art-default.jpeg'
ICON = 'icon-default.png'
ICON_PREFS = 'icon-prefs.png'
BASE_URL = 'http://lv2.ustvnow.com'

####################################################################################################
def Start():

	Plugin.AddPrefixHandler('/video/ustvnow', MainMenu, TITLE, ICON, ART)
	Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')

	ObjectContainer.title1 = TITLE
	ObjectContainer.art = R(ART)
	ObjectContainer.view_group = 'InfoList'

	DirectoryObject.thumb = R(ICON)
	DirectoryObject.art = R(ART)

	Login()

####################################################################################################
def MainMenu():

	oc = ObjectContainer()
	oc.add(DirectoryObject(key = Callback(GetChannels), title = 'Live'))
	#oc.add(DirectoryObject(key = Callback(GetRecordings), title = 'Recordings'))
	oc.add(PrefsObject(title = 'Preferences', thumb = R(ICON_PREFS)))
	return oc

####################################################################################################
def GetChannels():
	oc = ObjectContainer()

	channel_url = BASE_URL + "/iphone_ajax?tab=iphone_playingnow&token=" + Dict['token']
	response = HTTP.Request(channel_url, cacheTime=0).content

	for item in re.finditer('class="panel".+?title="(.+?)".+?src="' +
                                   '(.+?)".+?class="nowplaying_item">(.+?)' +
                                   '<\/td>.+?class="nowplaying_itemdesc".+?' +
                                   '<\/a>(.+?)<\/td>.+?href="(.+?)"',
                                   response, re.DOTALL):
		name, icon, title, summary, url = item.groups()

		if not url.startswith('http'):
			oc.add(VideoClipObject(
				url = '%s%s%d' % ("rtmp", url[4:-1], 3),
				title = name + " - " + unescape(title),
				summary = unescape(summary.strip()),
				thumb = Resource.ContentsOfURLWithFallback(url = icon, fallback=ICON))
			)

	return oc

####################################################################################################
def GetRecordings():

	oc = ObjectContainer()
	return oc

####################################################################################################
def Login():
	username = Prefs["username"]
	password = Prefs["password"]

	if (username != None) and (password != None):
		authentication_url = BASE_URL + "/iphone_login?username=" +  username + "&password=" + password
		response = HTTP.Request(authentication_url, cacheTime=0).content
		for cookie in HTTP.CookiesForURL(BASE_URL).split(';'):
			if 'token' in cookie :
				Dict['token'] = cookie[7:]
				return True
	return False


####################################################################################################
