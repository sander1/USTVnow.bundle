import re
from xml.sax.saxutils import unescape

TITLE = 'USTVnow'
ART = 'art-default.jpeg'
ICON = 'icon-default.png'
ICON_PREFS = 'icon-prefs.png'
BASE_URL = 'http://lv2.ustvnow.com'
IPHONE_URL = '/iphone_ajax?tab=iphone_playingnow&token='

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
	page = HTML.ElementFromURL(BASE_URL + IPHONE_URL + Dict['token'])
	feeds = page.xpath("//div[@class='panel']")
	for feed in feeds:
		try:
			url = feed.xpath(".//a[@class='grayButton']")[0].get("href")
			name = feed.get("title")
			title = feed.xpath('.//td[@class="nowplaying_item"]')[0].text
			summary = feed.xpath('.//td[@class="nowplaying_itemdesc"]')[0].text_content()

			oc.add(CreateLiveTVObject(
				url = '%s%s%d' % ("rtmp", url[4:-1], 3),
				title = name + " - " + unescape(title),
				summary = unescape(summary.strip()),
				thumb = R(name.lower() + ".jpg")
			))

		except:
			continue
	return oc

####################################################################################################
def Login():

	username = Prefs["username"]
	password = Prefs["password"]

	if (username != None) and (password != None):
		authentication_url = BASE_URL + '/iphone_login?username=' +  username + '&password=' + password
		response = HTTP.Request(authentication_url, cacheTime=0).content
		for cookie in HTTP.CookiesForURL(BASE_URL).split(';'):
			if 'token' in cookie :
				Dict['token'] = cookie[7:]
				return True
	return False

####################################################################################################
@route('/video/ustvnow/createlivetvobject')
def CreateLiveTVObject(url, title, summary, thumb, include_container=False):

	sid = url.split('?')[1].split('=')[1]
	movie_obj = VideoClipObject(
		key = Callback(CreateLiveTVObject, url=url, title=title, summary=summary, thumb=thumb, include_container=True),
		rating_key = url,
		title = title,
		summary = summary,
		thumb = thumb,
		items = [
			MediaObject(
				video_codec = VideoCodec.H264,
				audio_codec = AudioCodec.AAC,
				audio_channels = 2,
				parts = [
					PartObject(
						key = RTMPVideoURL(url=url, swf_url='http://www.ustvnow.com/player/flowplayer.commercial-3.2.15.swf?sid=' + sid, live=True)
					)
				]
			)
		]
	)

	if include_container:
		return ObjectContainer(objects=[movie_obj])
	else:
		return movie_obj