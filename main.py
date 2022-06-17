import time
import bs4
import requests
import StellarPlayer
import re
import urllib.parse
import urllib.request
import math
import json
import urllib3
import os
import sys

class netmusicplugin(StellarPlayer.IStellarPlayerPlugin):
    def __init__(self,player:StellarPlayer.IStellarPlayer):
        super().__init__(player)
        urllib3.disable_warnings()
        self.keyword = ''
        self.medias = []
        self.actPlayItem = 0
        self.allmovidesdata = {}
        self.mediaclass = []
        self.pageindex = 1
        self.pagenumbers = 0
        self.apitype = 0
        self.cur_page = ''
        self.max_page = ''
        self.nextpg = ''
        self.previouspg = ''
        self.firstpg = ''
        self.lastpg = ''
        self.pg = ''
        self.spy = []
        self.stoptimes = 0
        self.listflag = hasattr(self.player, 'addToPlaylist')
        
    def start(self):
        super().start()
        
        
    def QianQiansearch(self,key,page=0):
        results = {}
        results['allnum'] = 0
        results['song'] = []
        headers={'referer':'http://music.163.com/',
            'proxy':"false",
            'user-agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'}
        data={'s':'',
            'type':1,
            'offset':1,
            'limit':20}
        
        neteaseurl = 'http://music.163.com/api/cloudsearch/pc'
        data['offset'] = page
        data['s'] = key
        req = requests.post(neteaseurl,headers=headers,data=data,timeout=1)
        if req.status_code != 200:
            return request
        d = json.loads(req.text)
        song_url = ['http://music.163.com/song/media/outer/url?id=','.mp3']
        results['allnum'] = d["result"]["songCount"]
        songs = d["result"]['songs']
        for i in songs:
            songinfo = {}
            songinfo['songurl'] = str(i['id']).join(song_url)
            songinfo['name'] = i["name"]
            songinfo['singer'] = i['ar'][0]["name"]
            songinfo['pic'] = i['al']['picUrl']
            songinfo['lrc'] = self.getQianQianLrc(i['id'])
            songinfo['lrctype'] = 'text'
            results['song'].append(songinfo)
        return results
        
    def getQianQianLrc(self,song_id):
        headers = {
            "user-agent" : "Mozilla/5.0",
            "Referer" : "http://music.163.com",
            "Host" : "music.163.com"
        }
        if not isinstance(song_id, str):
            song_id = str(song_id)
        url = f"http://music.163.com/api/song/lyric?id={song_id}+&lv=1&tv=-1"
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            return ""
        r.encoding = r.apparent_encoding
        json_obj = json.loads(r.text)
        return json_obj["lrc"]["lyric"]

    def getQQLrc(self,songmid):
        headers={'user-agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1',
                'referer' : 'https://m.y.qq.com'}
        url='https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric.fcg?songmid={}&format=json&nobase64=1&songtype=0&callback=c'.format(songmid)
        try:
            html = requests.get(url,headers=headers)
            d = json.loads(html.text[2:-1])['lyric']
            return d
        except:
            return ""
    
    def getQQSongUrl(self,songid):
        url_part = "https://u.y.qq.com/cgi-bin/musicu.fcg?format=json&data=%7B%22req_0%22%3A%7B%22module%22%3A%22vkey.GetVkeyServer%22%2C%22method%22%3A%22CgiGetVkey%22%2C%22param%22%3A%7B%22guid%22%3A%22358840384%22%2C%22songmid%22%3A%5B%22{}%22%5D%2C%22songtype%22%3A%5B0%5D%2C%22uin%22%3A%221443481947%22%2C%22loginflag%22%3A1%2C%22platform%22%3A%2220%22%7D%7D%2C%22comm%22%3A%7B%22uin%22%3A%2218585073516%22%2C%22format%22%3A%22json%22%2C%22ct%22%3A24%2C%22cv%22%3A0%7D%7D".format(songid)
        music_document_html_json = requests.get(url_part).text
        music_document_html_dict = json.loads(music_document_html_json)  #将文件从json格式转化为字典格式
        music_url_part = music_document_html_dict["req_0"]["data"]["midurlinfo"][0]["purl"]
        if music_url_part != '':
            return music_document_html_dict['req_0']['data']['sip'][0]+music_url_part
        else:
            return ""

    
    def qqSearch(self,key,pageindex):
        results = {}
        results['allnum'] = 0
        results['song'] = []
        headers={'user-agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1',
            'referer' : 'https://m.y.qq.com'}

        self.url='https://c.y.qq.com/soso/fcgi-bin/client_search_cp?p='+str(self.pageindex)+'&n=20&w='+key
        resp = requests.get(self.url, headers=headers)
        json_str = resp.text
        json_str = json_str[9:-1]
        json_dict = json.loads(json_str)
        music_list = json_dict["data"]["song"]["list"]
        for music in music_list:
            songinfo = {}
            songurl = self.getQQSongUrl(music["songmid"])
            if songurl != "":
                songinfo['name'] = music["songname"]
                songinfo['singer'] = music["singer"][0]["name_hilight"]
                songinfo['songurl'] = songurl
                songinfo['lrc'] = self.getQQLrc(music["songmid"])
                songinfo['lrctype'] = 'text'
                songinfo['pic'] = 'https://y.gtimg.cn/music/photo_new/T002R300x300M000' + music["albummid"]+ '.jpg'
                results['song'].append(songinfo)
        results['allnum'] = json_dict["data"]["song"]["totalnum"]
        return results
            
    
    def miguSearch(self,key,pageindex):
        results = {}
        results['allnum'] = 0
        results['song'] = []
        search_url = 'http://pd.musicapp.migu.cn/MIGUM3.0/v1.0/content/search_all.do'
        params = {
            'ua': "Android_migu",
            "version": "5.0.1",
            "text": key,
            "pageNo": pageindex,
            "searchSwitch": '{"song":1,"album":0,"singer":0,"tagSong":0,"mvSong":0,"songlist":0,"bestShow":0}'
        }
        dataGeted = True
        jsonData = {}
        try:
            res = requests.get(search_url, params=params,timeout = 5,verify=False)
            if res.status_code != 200:
                return results
            else:
                jsonData = res.json()
        except:
            dataGeted = False
        if dataGeted == False:
            return results

        if jsonData['info'] != '成功':
            return results
        if not ('songResultData' in jsonData):
            return results
        songdata = jsonData['songResultData']
        results['allnum'] = int(songdata['totalCount'])
        for item in songdata['result']:
            songinfo = {}
            songinfo['name'] = item['name']
            strsinger = ''
            for singer in item['singers']:
                strsinger = strsinger + ' ' + singer['name']
            songinfo['singer'] = strsinger
            songinfo['lrc'] = item['lyricUrl']
            songinfo['lrctype'] = 'url'
            imgurl = ''
            imgsize = '10000'
            for imageinfo in item['imgItems']:
                if imgsize > imageinfo['imgSizeType']:
                    imgsize = imageinfo['imgSizeType']
                    imgurl = imageinfo['img']
            songinfo['pic'] = imgurl
            hasPQ = False
            hasHQ = False
            hasSQ = False
            hasLQ = False
            hasZQ24 = False
            hasZQ32 = False
            hasZ3D = False
            for rateformat in item['rateFormats']:
                if rateformat['formatType'] == 'LQ':
                    hasLQ = True
                if rateformat['formatType'] == 'SQ':
                    hasSQ = True
                if rateformat['formatType'] == 'HQ':
                    hasHQ = True
                if rateformat['formatType'] == 'PQ':
                    hasPQ = True
                if rateformat['formatType'] == 'Z3D':
                    hasZ3D = True
                if rateformat['formatType'] == 'ZQ':
                    if rateformat['iosBit'] == 24 or rateformat['androidBit'] == 24:
                        hasZQ24 = True
                    if rateformat['iosBit'] == 32 or rateformat['androidBit'] == 32:
                        hasZQ24 = True
            for rateformat in item['newRateFormats']:
                if rateformat['formatType'] == 'LQ':
                    hasLQ = True
                if rateformat['formatType'] == 'SQ':
                    hasSQ = True
                if rateformat['formatType'] == 'HQ':
                    hasHQ = True
                if rateformat['formatType'] == 'PQ':
                    hasPQ = True
                if rateformat['formatType'] == 'Z3D':
                    hasZ3D = True
                if rateformat['formatType'] == 'ZQ':
                    if rateformat['iosBit'] == 24 or rateformat['androidBit'] == 24:
                        hasZQ24 = True
                    if rateformat['iosBit'] == 32 or rateformat['androidBit'] == 32:
                        hasZQ24 = True
            toneType = ''
            if hasZ3D:
                toneType = 'Z3d'
            elif hasZQ32:
                toneType = 'ZQ32'
            elif hasZQ24:
                toneType = 'ZQ24'
            elif hasLQ:
                toneType = 'LQ'
            elif hasSQ:
                toneType = 'SQ'
            elif hasHQ:
                toneType = 'HQ'
            elif hasPQ:
                toneType = 'PQ'
            if toneType != '':
                songurl = 'http://app.pd.nf.migu.cn/MIGUM2.0/v1.0/content/sub/listenSong.do?toneFlag=' + toneType + '&netType=00&resourceType=2&channel=0&copyrightId=' + item['copyrightId'] + '&contentId=' + item['contentId']
                songinfo['songurl'] = songurl
                results['song'].append(songinfo)
        return results

    def kugouSearch(self,key,pageindex):
        results = {}
        results['allnum'] = 0
        results['song'] = []
        search_url = 'http://songsearch.kugou.com/song_search_v2'
        params = {
            "keyword": key,
            "page": pageindex,
            "pagesize": 20
        }
        dataGeted = True
        jsonData = {}
        try:
            res = requests.get(search_url, params=params,timeout = 5,verify=False)
            if res.status_code != 200:
                dataGeted = False
            else:
                jsonData = res.json()
        except:
            dataGeted = False
        if dataGeted == False:
            return results
        results['allnum'] = jsonData['data']['total']
        hasharr = []
        for item in jsonData['data']['lists']:
            hasharr.append({'hash':item['FileHash'],'id':item['AlbumID']})
        for hashval in hasharr:
            strhash = hashval['hash']
            strid = hashval['id']
            dataGeted = True
            url = 'http://wwwapi.kugou.com/yy/index.php'
            par = {
                "r": 'play/getdata',
                "hash": strhash,
                "album_id": strid,
                'mid': 'ccbb9592c3177be2f3977ff292e0f145'
            }
            singData = {}
            try:
                res = requests.get(url, params=par,timeout = 5,verify=False)
                if res.status_code != 200:
                    dataGeted = False
                else:
                    singData = res.json()
            except:
                dataGeted = False
            if singData['status'] != 1:
                dataGeted = False
            if dataGeted:
                songinfo = {}
                songinfo['name'] = singData['data']['song_name']
                songinfo['singer'] = singData['data']['author_name']
                songinfo['lrc'] = singData['data']['lyrics']
                songinfo['lrctype'] = 'text'
                songinfo['pic'] = singData['data']['img']
                songinfo['songurl'] = singData['data']['play_url']
                results['song'].append(songinfo)
        return results
    
    def show(self):
        controls = self.makeLayout()
        self.doModal('main',800,700,'',controls)        
    
    def makeLayout(self):
        xl = [{'title':'线路1'},{'title':'线路2'},{'title':'线路3'},{'title':'线路4'}]
        zywz_layout = [
            {'type':'link','name':'title','@click':'onMainMenuClick'}
        ]

        mediagrid_layout = []
        if self.listflag:
            mediagrid_layout = [
                [
                    {
                        'group': [
                            {'type':'link','name':'name','textColor':'#A52A2A','fontSize':15,'height':0.1, '@click':'on_name_click'},
                            {'type':'image','name':'pic', '@click':'on_grid_click'},
                            {'type':'link','name':'singer','textColor':'#800000','fontSize':15,'height':0.1, '@click':'on_singer_click'},
                            {
                                'group': [
                                    {'type':'link','name':'播放','textColor':'#3CB371','fontSize':15, '@click':'on_play_click'},
                                    {'type':'space','width':80},
                                    {'type':'link','name':'收藏','textColor':'#008000','fontSize':15, '@click':'on_listsave_click'}
                                ],
                                'height':25
                            }
                        ],
                        'dir':'vertical'
                    }
                ]
            ]
        else:
            mediagrid_layout = [
                [
                    {
                        'group': [
                            {'type':'link','name':'name','textColor':'#ff7f00','fontSize':15,'height':0.1, '@click':'on_name_click'},
                            {'type':'image','name':'pic', '@click':'on_grid_click'},
                            {'type':'link','name':'singer','textColor':'#ff002f','fontSize':15,'height':0.1, '@click':'on_singer_click'}
                        ],
                        'dir':'vertical'
                    }
                ]
            ]
        if self.listflag:
            pagecontrols = [
                                {'type':'label','name':'cur_page',':value':'cur_page'},
                                {'type':'link','name':'首页','@click':'onClickFirstPage'},
                                {'type':'link','name':'上一页','@click':'onClickFormerPage'},
                                {'type':'link','name':'下一页','@click':'onClickNextPage'},
                                {'type':'link','name':'末页','@click':'onClickLastPage'},
                                {'type':'label','name':'max_page',':value':'max_page'},
                                {'type':'space','width':50},
                                {'type':'link','name':'收藏本页','@click':'onSaveThisPage'},
                            ]
        else:
            pagecontrols = [
                                {'type':'label','name':'cur_page',':value':'cur_page'},
                                {'type':'link','name':'首页','@click':'onClickFirstPage'},
                                {'type':'link','name':'上一页','@click':'onClickFormerPage'},
                                {'type':'link','name':'下一页','@click':'onClickNextPage'},
                                {'type':'link','name':'末页','@click':'onClickLastPage'},
                                {'type':'label','name':'max_page',':value':'max_page'},
                        ]
        controls = [
            {'type':'space','height':5},
            {
                'group':[
                    {'type':'edit','name':'search_edit','label':'搜索','width':0.4},
                    {'type':'button','name':'搜索','@click':'onSearch','width':80},
                    {'type':'label','name':'注释','value':'点击歌手名、歌名为搜索;点击歌曲封面播放'}
                ],
                'width':1.0,
                'height':30
            },
            {'type':'space','height':10},
            {'type':'grid','name':'zygrid','itemlayout':zywz_layout,'value':xl,'itemheight':30,'itemwidth':80,'height':50},
            {'type':'space','height':5},
            {'type':'grid','name':'mediagrid','itemlayout':mediagrid_layout,'value':self.medias,'separator':True,'itemheight':250,'itemwidth':150},
            {'group':
                [
                    {'type':'space'},
                    {'group':pagecontrols
                        ,'width':0.7
                    },
                    {'type':'space'}
                ]
                ,'height':30
            },
            {'type':'space','height':5}
        ]
        return controls
    
    def onMainMenuClick(self, page, listControl, item, itemControl): 
        search_word = self.player.getControlValue('main','search_edit').strip()
        if search_word == '':
            self.player.toast("main","搜索条件不能为空")
            return 
        self.keyword = search_word
        self.loading()
        self.apitype = item
        self.pageindex = 1
        self.loaddatas()
        self.loading(True)
         
    
    def on_grid_click(self, page, listControl, item, itemControl):
        url = self.medias[item]['songurl']
        playname = self.medias[item]['name']
        try:
            self.player.play(url, caption=playname)
        except:
            self.player.play(url)
        self.actPlayItem = item
        
    def on_play_click(self, page, listControl, item, itemControl):
        url = self.medias[item]['songurl']
        playname = self.medias[item]['name']
        items = [
            {'name': playname, 'url': url}
        ]
        self.player.addToPlaylist("在线音乐", items,0)
    
    def on_listsave_click(self, page, listControl, item, itemControl):
        url = self.medias[item]['songurl']
        playname = self.medias[item]['name'].strip() + '(' + self.medias[item]['singer'].strip() +")"
        items = [
            {'name': playname, 'url': url}
        ]
        self.player.addToPlaylist("在线音乐", items,-1)
        
    def on_name_click(self, page, listControl, item, itemControl):
        name = self.medias[item]['name']
        self.player.updateControlValue('main','search_edit',name)
        self.keyword = name
        self.loading()
        self.pageindex = 1
        self.loaddatas()
        self.loading(True) 
  
    def on_singer_click(self, page, listControl, item, itemControl):
        singer = self.medias[item]['singer']
        self.player.updateControlValue('main','search_edit',singer)
        self.keyword = singer
        self.loading()
        self.pageindex = 1
        self.loaddatas()
        self.loading(True) 
    
    def loaddatas(self):
        searchres = {}
        searchres['allnum'] = 0
        searchres['song'] = []
        if self.apitype == 0:
            searchres = self.miguSearch(self.keyword,self.pageindex)
        if self.apitype == 1:
            searchres = self.kugouSearch(self.keyword,self.pageindex)
        if self.apitype == 2:
            searchres = self.qqSearch(self.keyword,self.pageindex)
        if self.apitype == 3:
            searchres = self.QianQiansearch(self.keyword,self.pageindex)
        allsongnum = searchres['allnum']
        self.pagenumbers = allsongnum // 20
        if self.pagenumbers * 20 < allsongnum:
            self.pagenumbers = self.pagenumbers + 1
        self.cur_page = '第' + str(self.pageindex) + '页'
        self.max_page = '共' + str(self.pagenumbers) + '页'  
        self.medias = searchres['song']
        self.player.updateControlValue('main','mediagrid',self.medias)
            
    
    def onSearch(self, *args):
        search_word = self.player.getControlValue('main','search_edit').strip()
        if search_word == '':
            self.player.toast("main","搜索条件不能为空")
            return 
        self.keyword = search_word
        self.loading()
        self.pageindex = 1
        self.loaddatas()
        self.loading(True)       
               
    def onClickFirstPage(self, *args):
        self.loading()
        self.pageindex = 1
        self.loaddatas()
        self.loading(True) 
        
    def onClickFormerPage(self, *args):
        self.loading()
        self.pageindex = self.pageindex - 1
        if self.pageindex < 1:
            self.pageindex = 1
        self.loaddatas()
        self.loading(True) 
    
    def onClickNextPage(self, *args):
        self.loading()
        self.pageindex = self.pageindex + 1
        if self.pageindex > self.pagenumbers:
            self.pageindex = self.pagenumbers
        self.loaddatas()
        self.loading(True) 
        
    def onClickLastPage(self, *args):
        self.loading()
        self.pageindex = self.pagenumbers
        self.loaddatas()
        self.loading(True)
                
    def onSaveThisPage(self, *args):
        items = []
        for item in self.medias:
            addtitle = item['name'].strip() + '(' + item['singer'].strip() +")"
            items.append({'name': addtitle, 'url': item['songurl']})
        if len(items) > 0:
            self.player.addToPlaylist("在线音乐", items,-1)
            
            
    def playMovieUrl(self,playpageurl):
        return
        
    def loading(self, stopLoading = False):
        if hasattr(self.player,'loadingAnimation'):
            self.player.loadingAnimation('main', stop=stopLoading)

def newPlugin(player:StellarPlayer.IStellarPlayer,*arg):
    plugin = netmusicplugin(player)
    return plugin

def destroyPlugin(plugin:StellarPlayer.IStellarPlayerPlugin):
    plugin.stop()