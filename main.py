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


    def miguSearch(self,key,pageindex):
        results = {}
        results['allnum'] = 0
        results['song'] = []
        search_url = 'http://pd.musicapp.migu.cn/MIGUM2.0/v1.0/content/search_all.do'
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
            print(jsonData)
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
        xl = [{'title':'线路1'},{'title':'线路2'}]
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
        playname = self.medias[item]['name']
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
            items.append({'name': item['name'] + '(' + item['singer'] +")", 'url': item['songurl']})
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