#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Apr 2, 2013

@author: wu.qunfei@gmail.com
'''
import logging
import ConfigParser
import os
import urllib2
import json
import time
import threading

try:
    import wx
    import vlc
except Exception, e:
    print("Sorry,need python wx and vlc lib\r\nPlease run install.sh first!")
    exit()


class MakeMarquee(threading.Thread):
    def __init__(self, logger, player, streamData):
        threading.Thread.__init__(self)
        self.player = player
        self.title = None
        if streamData is not None:
            self.title = streamData['STREAM_NAME']
        self.logger = logger

        if streamData is not None:
            pass
            # You can do your logic here,and display more information on channel

    def run(self):
        try:
            time.sleep(5)
            try:
                volume = self.player.audio_get_volume()
                if volume == 0:
                    self.title += u"No Volume"
            except Exception, e:
                self.logger.error(e)
            if self.title is not None:
                self.player.video_set_marquee_int(vlc.VideoMarqueeOption.Enable, 1)
                self.player.video_set_marquee_int(vlc.VideoMarqueeOption.Size, 48)
                self.player.video_set_marquee_int(vlc.VideoMarqueeOption.Position, 8)
                self.player.video_set_marquee_int(vlc.VideoMarqueeOption.Timeout, 0)
                self.player.video_set_marquee_string(vlc.VideoMarqueeOption.Text, self.title)

        except Exception, e:
            self.logger.error("Make Marquee failed")
            self.logger.error(e)


class Player(wx.Frame):
    def __init__(self, parent, title, logger):
        super(Player, self).__init__(parent, title=title, size=wx.DisplaySize())
        self.logger = logger
        cf = ConfigParser.ConfigParser()
        self.path = os.getcwd()
        try:
            configFileName = os.path.join(self.path, 'config.ini')
            cf.read(configFileName)
            self.streamType = cf.get("default", "stream_type")
            self.streamLocal = cf.get("default", "stream_local_path")
            self.streamConfig = cf.get("default", "stream_local_config")
            self.streamNetwork = cf.get("default", "stream_network_address")
            self.xAmount = cf.getint("default", "x_amount")
            self.yAmount = cf.getint("default", "y_amount")
            self.periodTime = cf.getint("default", "period_time")

        except Exception, e:
            self.logger.error("Can't read config.ini,application stop")
            self.logger.error(e)
            return
        self.vlc = vlc.Instance()
        self.players = []
        self.panels = []
        self.gs = None
        self.makeAllWindows()
        self.SetSizer(self.gs)
        self.Show(True)
        self.Center()
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.getPlayerAddress, self.timer)
        if self.periodTime == -1:
            if self.streamType == 1:
                self.getPlayLocalFile(None)
            elif self.streamType == 2:
                self.getPlayConfigStream(None)
            elif self.streamType == 3:
                self.getPlayNetStream(None)

        else:
            self.timer.Start(self.periodTime * 1000)
            if self.streamType == 1:
                self.getPlayLocalFile(None)
            elif self.streamType == 2:
                self.getPlayConfigStream(None)
            elif self.streamType == 3:
                self.getPlayNetStream(None)


    def makeAllWindows(self):
        try:
            self.gs = wx.GridSizer(self.yAmount, self.xAmount, 0, 0)
            for x in range(self.xAmount):
                for y in range(self.yAmount):
                    player = self.vlc.media_player_new()
                    self.players.append(player)
                    panel = wx.Panel(self, -1)
                    panel.SetBackgroundColour(wx.BLACK)
                    self.panels.append(panel)
                    self.gs.Add(panel, 0, wx.EXPAND)
        except Exception, e:
            self.logger.error("Can't init all windows panel")
            self.logger.error(e)

    def getPlayLocalFile(self, event):
        files = []
        playIndex = 0
        for file in files:
            try:
                bean = {'STREAM_ADDRESS': file}
                self.setPlayerRun(bean, playIndex)
                playIndex += 1
            except Exception, e:
                self.logger.error(e)
                self.logger.error("Can't play stream %s" % file)

    def getPlayConfigStream(self, event):
        if self.streamConfig is not None:
            streams = self.streamConfig.split(",")
            if len(streams) > 0:
                playIndex = 0
                for stream in streams:
                    stream = stream.trim()
                    if stream is not None:
                        try:
                            bean = {'STREAM_ADDRESS': stream}
                            self.setPlayerRun(bean, playIndex)
                            playIndex += 1
                        except Exception, e:
                            self.logger.error(e)
                            self.logger.error("Can't play stream %s" % stream)

    def getPlayNetStream(self, event):
        try:
            response = urllib2.urlopen(self.streamNetwork, None, 60)
            if response.code == 200:
                content = response.read()
                if content is not None:
                    streams = json.loads(content)
                    if len(streams) > 0:
                        playIndex = 0
                        for stream in streams:
                            try:
                                bean = {'STREAM_ADDRESS': stream['address'], 'STREAM_DATA': stream['data']}
                                self.setPlayerRun(bean, playIndex)
                                playIndex += 1
                            except Exception, e:
                                self.logger.error(e)
                                self.logger.error("Can't play stream %s" % stream)

            else:
                pass
        except Exception, e:
            self.logger.error(e)


    def setPlayerRun(self, bean, playIndex):
        """

        :param bean: one channel information
        :param playIndex: which player
        """
        try:
            streamUrl = bean['STREAM_ADDRESS']
            streamData = bean['STREAM_DATA']
            player = self.players[playIndex]
            panel = self.panels[playIndex]
            if player is not None and panel is not None:
                player.stop()
                media = self.vlc.media_new(streamUrl, 'sub-filter=marq')

                player.set_media(media)
                player.set_xwindow(panel.GetHandle())
                player.audio_set_mute(True)
                player.play()
                try:
                    make = MakeMarquee(self.logger, player, streamData)
                    make.start()
                    time.sleep(1)
                except Exception, e:
                    self.logger.error("Make Marquee thread failed")
                    self.logger.error(e)

        except Exception, e:
            self.logger.error("Can't set player and url")
            self.logger.error(e)


def main():
    logFileName = os.path.join(os.getcwd(), 'player.log')
    logging.basicConfig(filename=logFileName, level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
    logger = logging.getLogger('player')
    logger.setLevel(logging.INFO)
    app = wx.App()
    myPlayer = Player(None, 'Sanss IPTV Player', logger)
    app.MainLoop()


if __name__ == '__main__':
    main()













