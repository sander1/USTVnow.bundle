TITLE = 'USTVnow'
ART = 'art-default.jpeg'
ICON = 'icon-default.png'
ICON_PREFS = 'icon-prefs.png'

BASE_URL = "http://m.ustvnow.com"
LOGIN_URL = BASE_URL + "/iphone/1/live/login?username=%s&password=%s"
MOBILE_URL = BASE_URL + "/iphone/1/live/playingnow?pgonly=true&token=%s"

####################################################################################################
def Start():

	HTTP.Headers['User-Agent'] = """"Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_0 like Mac OS X; en-us)
									 AppleWebKit/532.9 (KHTML, like Gecko) Version/4.0.5 Mobile/8A293
									 Safari/6531.22.7"""

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

	oc = ObjectContainer()
	page = HTML.ElementFromURL(MOBILE_URL % (Dict['token']))
	feeds = page.xpath("//div[contains(@class, 'livetv-content-pages')]")
	for feed in feeds:
		url = feed.xpath('.//a[@class="viewlink"]')
		if len(url) > 0:
			name = feed.xpath('.//h1')[0].text
			url = BASE_URL + url[0].get("href")
			title = feed.xpath('.//td[@class="nowplaying_item"]')[0].text
			summary = feed.xpath('.//td[@class="nowplaying_itemdesc"]')[0].text_content()
			thumb = R(name.lower() + ".jpg")

			oc.add(VideoClipObject(
				url = url,
				title = name + " - " + String.DecodeHTMLEntities(title),
				summary = String.DecodeHTMLEntities(summary.strip()),
				art = thumb,
				thumb = thumb
			))

	return oc

####################################################################################################
def Login():

	Dict['token'] = ""
	username = Prefs["username"]
	password = Prefs["password"]

	if (username != None) and (password != None):
		x = HTTP.Request(LOGIN_URL % (username, password), cacheTime=0).content
		for cookie in HTTP.CookiesForURL(BASE_URL).split(';'):
			if 'token' in cookie:
				Dict['token'] = cookie.split("=")[1]
				return True
	return False
