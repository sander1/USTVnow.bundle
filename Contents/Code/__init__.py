import re
from xml.sax.saxutils import unescape

TITLE = 'USTVnow'
ART = 'art-default.jpeg'
ICON = 'icon-default.png'
ICON_PREFS = 'icon-prefs.png'
BASE_URL = "http://www.ustvnow.com?a=do_login&force_redirect=1&manage_proper=1&input_username=%s&input_password=%s#%s"
IPHONE_BASE_URL = 'http://lv2.ustvnow.com'
IPHONE_URL = "/iphone_ajax?tab=iphone_playingnow&token=%s"

####################################################################################################
def Start():

	ObjectContainer.title1 = TITLE
	ObjectContainer.art = R(ART)
	DirectoryObject.thumb = R(ICON)
	DirectoryObject.art = R(ART)

####################################################################################################
@handler('/video/ustvnow', TITLE, art=ART, thumb=ICON)
def MainMenu():

	Login()

	oc = ObjectContainer()
	oc.add(DirectoryObject(key = Callback(GetChannels), title = 'Live'))
	oc.add(PrefsObject(title = 'Preferences', thumb = R(ICON_PREFS)))
	return oc

####################################################################################################
@route('/video/ustvnow/getchannels')
def GetChannels():

	if "token" not in Dict: Login()

	oc = ObjectContainer()
	page = HTML.ElementFromURL(IPHONE_BASE_URL + IPHONE_URL % (Dict['token']))
	feeds = page.xpath("//div[@class='panel']")
	for feed in feeds:

		rtsp = feed.xpath(".//a[@class='grayButton']")
		if len(rtsp) > 0:
			name = feed.get("title")
			url = BASE_URL % (Prefs["username"], Prefs["password"], name)
			title = feed.xpath('.//td[@class="nowplaying_item"]')[0].text
			summary = feed.xpath('.//td[@class="nowplaying_itemdesc"]')[0].text_content()
			thumb = R(name.lower() + ".jpg")

			oc.add(VideoClipObject(
				url = url,
				title = name + " - " + unescape(title),
				summary = unescape(summary.strip()),
				art = thumb,
				thumb = thumb
			))

	return oc

####################################################################################################
def Login():

	username = Prefs["username"]
	password = Prefs["password"]

	if (username != None) and (password != None):
		authentication_url = IPHONE_BASE_URL + '/iphone_login?username=' +  username + '&password=' + password
		response = HTTP.Request(authentication_url, cacheTime=0).content
		for cookie in HTTP.CookiesForURL(IPHONE_BASE_URL).split(';'):
			if 'token' in cookie :
				Dict['token'] = cookie[7:]
				return True
	return False