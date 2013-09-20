multiSceenPlayer
================

MultiScreenPlayer is a video player that can play multi-stream together. It could support local media file or network streams. Owning to basic VLC and Python- Wx library, almost media formats are supported. So it always used in monitoring like CCTV. Now that almost VOD and Multi Systems are quite expensive, it’s free architecture for building a monitor system.
MultiScreenPlayer features are following,
1. Support VOD and Multi Stream from Internet
2. Local media files could player together
3. Customize your streams/channel/file amounts
4. Loop your stream automatically
5. Subtitles could display in every stream for example adding your chancel Name, alarm Message or time string. I left stream data method to develop your own subtitles
6. Easy to install and develop deeply.
Describe config.ini to use,
Stream_type is INT from 1 to 3.
1: stream_local_path | You can configurate a local video file path
2: stream_local_config | You can configurate a videos list that split with comma. For example: v1,v2,v3,v4
3: stream_network_address | You can use a web server to response a JSON data to your player. JSON Format is [{‘address’:yourChannelAddress,’data’:yourMoreSubtitles},{...},{...}]
Hope you could enjoy it. Andy questions can send me email:
wu.qunfei@gmail.com