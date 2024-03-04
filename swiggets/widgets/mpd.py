import logging
from typing import Literal, Tuple, Union

from mpd.asyncio import MPDClient
from pydantic import BaseModel, field_validator, validate_call

from ..core.click_event import MouseButton
from ..core.formatter import Formatter
from ..core.polling import Polling
from ..core.substitute import Substitute
from ..misc import Icons, Slider

logger = logging.getLogger(__name__)


class MPDStatus(BaseModel):
    volume: int
    repeat: bool
    random: bool
    single: bool
    consume: bool
    playlistlength: int
    state: Literal['play', 'stop', 'pause']
    xfade: float = 0
    song: int
    songid: int
    elapsed:  Union[float, Literal['']] = ''
    bitrate:  Union[float, Literal['']] = ''
    duration: Union[float, Literal['']] = ''
    audio: str = ''
    nextsong: int
    nextsongid: int

    @field_validator('elapsed', 'duration', mode='before')
    @classmethod
    @validate_call()
    def datetime_validator(cls, v: Union[float, Literal['']]):
        return v


class SongInfo(BaseModel):
    file: str = ''
    artist: str = ''
    title: str = ''
    album: str = ''
    track: str = ''
    date: str = ''
    genre: str = ''
    composer: str = ''
    disc: str = ''
    label: str = ''
    time: int
    duration: float
    pos: int
    id: int

    @field_validator('duration', mode='before')
    @classmethod
    @validate_call()
    def datetime_validator(cls, v: Union[float, Literal['']]):
        return v

    @property
    def album_short(self):
        if len(self.album) > 15:
            return f'{self.album[:10]}‥{self.album[-4:]}'
        else:
            return self.album

    @property
    def artist_short(self):
        if len(self.artist) > 15:
            return f'{self.artist[:10]}‥{self.artist[-4:]}'
        else:
            return self.artist

    @property
    def title_short(self):
        if len(self.title) > 15:
            return f'{self.title[:10]}‥{self.title[-4:]}'
        else:
            return self.title


class MPD(Polling):
    @validate_call(config=dict(validate_default=True))
    def __init__(
        self, *,
        host,
        port=6600,
        auto_connect=False,
        song_format_full: Formatter = '{song.artist}-{song.album}-{song.title} ({felapsed}/{fduration}) {status.volume}% {volume_icon}',  # noqa: E501
        song_format_short: Formatter = (
            lambda status, song, volume_icon, felapsed, fduration, **kw: (
            f'''{song.artist if len(song.artist) < 15 else
                f"{song.artist[:10]}‥{song.artist[-4:]}"}-{
                    song.album if len(song.album) < 15 else
                    f"{song.album[:10]}‥{song.album[-4:]}"}-{
                        song.title if len(song.title) < 15 else
                        f"{song.title[:10]}‥{song.title[-4:]}"} ({felapsed}/{
                            fduration}) {status.volume}% {volume_icon}'''
            )),
        slider_width_full=30,
        slider_width_short=8,
        icon_connect_switch: Tuple[str, str] = (
            Icons.toggle_off,
            Icons.toggle_on,
        ),
        icon_previous: str = Icons.previous_track,
        icon_next: str = Icons.next_track,
        icon_play: Tuple[str, str] = (
            f"<tt><b><span fgcolor='#FFFFFF'>{Icons.play}</span></b></tt>",
            f"<tt><b><span fgcolor='#EEEE44'>{Icons.play}</span></b></tt>",
        ),
        icon_stop: Tuple[str, str] = (
            f"<tt><b><span fgcolor='#FFFFFF'>{Icons.stop}</span></b></tt>",
            f"<tt><b><span fgcolor='#FF44FF'>{Icons.stop}</span></b></tt>",
        ),
        icon_pause: Tuple[str, str] = (
            f"<tt><b><span fgcolor='#FFFFFF'>{Icons.pause}</span></b></tt>",
            f"<tt><b><span fgcolor='#FF44FF'>{Icons.pause}</span></b></tt>",
        ),
        icon_volume: Substitute = {
            (0, 20): Icons.volume_off,
            (20, 60): Icons.volume_low,
            (60, 100): Icons.volume_high,
        },
        interval: int = 5,
        **kw_args
    ):
        super().__init__(interval=interval,
                         **kw_args)

        self.host = host
        self.port = port
        self.auto_connect = auto_connect
        self.slider_full = Slider(slider_width_full)
        self.slider_short = Slider(slider_width_short)
        self.icon_connect_switch = icon_connect_switch
        self.icon_volume = icon_volume
        self.icon_play = icon_play
        self.icon_stop = icon_stop
        self.icon_pause = icon_pause
        self.song_block = self.add_block(name='Current song',
                                         markup='pango',
                                         separator=False)
        self.slider_block = self.add_block(name='Slider',
                                           markup='pango',
                                           separator=False)

        self.prev_block = self.add_block(name='Prev track',
                                         full_text=icon_previous,
                                         min_width='nn',
                                         separator_block_width=0,
                                         border_left=0,
                                         border_right=0,
                                         separator=False)
        self.play_block = self.add_block(name='Play',
                                         full_text=self.icon_play[0],
                                         markup='pango',
                                         min_width='nn',
                                         separator_block_width=0,
                                         border_left=0,
                                         border_right=0,
                                         separator=False)
        self.pause_block = self.add_block(name='Pause',
                                          full_text=self.icon_pause[0],
                                          markup='pango',
                                          min_width='nn',
                                          separator_block_width=0,
                                          border_left=0,
                                          border_right=0,
                                          separator=False)
        self.stop_block = self.add_block(name='Stop',
                                         full_text=self.icon_stop[0],
                                         markup='pango',
                                         min_width='nn',
                                         separator_block_width=0,
                                         border_left=0,
                                         border_right=0,
                                         separator=False)
        self.next_block = self.add_block(name='Next track',
                                         full_text=icon_next,
                                         min_width='nn',
                                         border_left=0,
                                         border_right=0,
                                         border_top=0,
                                         separator=False)

        self.connected_block = self.add_block(name='IsConnected',
                                              markup='pango',
                                              separator=True)
        self.mpd_client = MPDClient()
        self.song_format_full = song_format_full
        self.song_format_short = song_format_short

    async def init(self):
        if self.auto_connect:
            await self.mpd_client.connect(self.host, self.port)

    async def loop(self):
        if not self.mpd_client.connected:
            self.connected_block.full_text = self.icon_connect_switch[0]
            self.song_block.full_text = ''
            self.slider_block.full_text = ''
            self.play_block.full_text = self.icon_play[0]
            self.pause_block.full_text = self.icon_pause[0]
            self.stop_block.full_text = self.icon_stop[0]
            return

        self.connected_block.full_text = Icons.toggle_on
        status = MPDStatus.validate(await self.mpd_client.status())
        if status.state == 'play':
            self.play_block.full_text = self.icon_play[1]
            self.pause_block.full_text = self.icon_pause[0]
            self.stop_block.full_text = self.icon_stop[0]
        elif status.state == 'pause':
            self.play_block.full_text = self.icon_play[0]
            self.pause_block.full_text = self.icon_pause[1]
            self.stop_block.full_text = self.icon_stop[0]
        elif status.state == 'stop':
            self.play_block.full_text = self.icon_play[0]
            self.pause_block.full_text = self.icon_pause[0]
            self.stop_block.full_text = self.icon_stop[1]
        else:
            self.play_block.full_text = self.icon_play[0]
            self.pause_block.full_text = self.icon_pause[0]
            self.stop_block.full_text = self.icon_stop[0]

        curr_song = SongInfo.validate(
            (await self.mpd_client.playlistid(status.songid))[0])
        next_song = SongInfo.validate(
            (await self.mpd_client.playlistid(status.nextsongid))[0])

        data = dict(
            volume_icon=self.icon_volume(status.volume),
            felapsed=(f'''{
                status.elapsed//60:.0f}:{
                    status.elapsed%60:02.0f}''' if status.elapsed else ''),
            fduration=(f'''{
                curr_song.duration//60:.0f}:{
                    curr_song.duration%60:02.0f}''' if curr_song.duration else ''),  # noqa: E501
            status=status, song=curr_song,
            curr_song=curr_song, next_song=next_song,
            )
        self.song_block.full_text = self.song_format_full(**data)
        self.song_block.short_text = self.song_format_short(**data)
        if status.elapsed:
            pos = status.elapsed/status.duration
            self.slider_block.full_text = self.slider_full(pos)
            self.slider_block.short_text = self.slider_short(pos)
        else:
            self.slider_block.full_text = ''
            self.slider_block.short_text = ''
        self.update()

    async def toggle_connect(self):
        if self.mpd_client.connected:
            self.mpd_client.disconnect()
        else:
            await self.mpd_client.connect(self.host, self.port)

    async def click_event(self, evt):
        try:
            if evt.name == 'IsConnected':
                if evt.button == MouseButton.left:
                    await self.toggle_connect()
            elif self.mpd_client.connected:
                if evt.name == 'Slider':
                    status = MPDStatus.validate(await self.mpd_client.status())
                    if evt.button == MouseButton.left:
                        if status.duration:
                            pos = evt.relative_x/evt.width * status.duration
                            await self.mpd_client.seekcur(pos)
                    elif evt.button == MouseButton.wheel_up:
                        await self.mpd_client.seekcur('+10')
                    elif evt.button == MouseButton.wheel_down:
                        # workaround as seekcur does not work with '-' sign
                        pos = status.elapsed - 10
                        await self.mpd_client.seekid(status.songid, pos)

                elif evt.button == MouseButton.left:
                    if evt.name == 'Play':
                        await self.mpd_client.play()
                    elif evt.name == 'Stop':
                        await self.mpd_client.stop()
                    elif evt.name == 'Pause':
                        await self.mpd_client.pause(1)
                    elif evt.name == 'Prev track':
                        await self.mpd_client.previous()
                    elif evt.name == 'Next track':
                        await self.mpd_client.next()

                elif evt.button == MouseButton.wheel_up:
                    self.mpd_client.volume(5)
                elif evt.button == MouseButton.wheel_down:
                    self.mpd_client.volume(-5)

            await self.loop()
        except Exception as e:
            logger.exception(repr(e))


if __name__ == "__main__":

    async def main():
        client = MPDClient()
        await client.connect("192.168.1.13", 6600)

        status = await client.status()
        print(status)
        song = (await client.playlistid(status['songid']))[0]
        print(song)
        try:
            status = MPDStatus.validate(status)
            print(status)
        except Exception as e:
            print(repr(e))
        try:
            song = SongInfo.validate(song)
        except Exception as e:
            print(repr(e))
    import asyncio
    asyncio.run(main())
