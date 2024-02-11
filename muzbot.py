import os
import json
import asyncio
import discord
from discord.ext import commands
import yt_dlp as youtube_dl
from datetime import datetime

ROOT = os.path.dirname(__file__)
def get_token(token_name):

    auth_file = open(os.path.join(ROOT, 'auth.json'))
    auth_data = json.load(auth_file)
    token = auth_data[token_name]
    return token

    @bot.event
    async def on_member_join(member):
        guild_id = 292344953911377922
        guild = bot.get_guild(guild_id)
        channel_id = 1036784337846288424

        if guild:
            print(f'{member.name} joined the server at {datetime.now()}')
            channel = guild.get_channel(channel_id)
            if channel:
                timestamp = datetime.now().strftime("%d.%m.%Y, в %H:%M")
                await channel.send(f'{member.mention} зашёл {timestamp}.')
            else:
                print(f'Channel with ID {channel_id} not found.')

    @bot.event
    async def on_member_remove(member):
        guild_id = 292344953911377922
        guild = bot.get_guild(guild_id)
        channel_id = 1036784337846288424

        if guild:
            print(f'{member.name} left the server at {datetime.now()}')
            channel = guild.get_channel(channel_id)
            if channel:
                timestamp = datetime.now().strftime("%d.%m.%Y, в %H:%M")
                await channel.send(f'{member.mention} вышел {timestamp}.')
            else:
                print(f'Channel with ID {channel_id} not found.')

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.is_playing = False
        self.is_paused = False

        self.music_queue = []
        self.load_queue()

        self.ydl_options = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(ROOT, 'yt', '%(extractor)s-%(id)s-%(title)s.%(ext)s'),
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
        }

        self.ffmpeg_options = {
            'options': '-vn'
        }

        self.voice_client = None

    @commands.hybrid_command(name='serverid', brief='Get the ID of the current discord server.')
    async def get_server_id(self, ctx):
        guild_id = ctx.guild.id
        await ctx.send(f"The ID of this server is: {guild_id}")

    @commands.hybrid_command(name='getidchannel', brief='Get the ID of the current discord channel.')
    async def get_channel_id(self, ctx, *, channel_name=None):
        if channel_name is None:
            channel = ctx.channel
        else:
            channel = discord.utils.get(ctx.guild.channels, name=channel_name.strip(), case_insensitive=True)

            if channel is None:
                try:
                    channel_id = int(channel_name)
                    channel = discord.utils.get(ctx.guild.channels, id=channel_id)
                except ValueError:
                    pass

        if channel:
            await ctx.send(f'The ID of channel {channel_name or ctx.channel.name} is: {channel.id}')
        else:
            await ctx.send(f'Channel {channel_name} not found on this server.')

    def load_queue(self):
        try:
            with open(os.path.join(ROOT, 'queue.json'), 'r') as queue_file:
                self.music_queue = json.load(queue_file)
        except:
            print('Starting from empty queue.')

    def save_queue(self):
        with open(os.path.join(ROOT, 'queue.json'), 'w') as queue_file:
            json.dump(self.music_queue, queue_file, indent=4)

    def search_yt(self, item):
        if item.startswith("http"):
            return {
                'source': item,
                'title': 'Custom URL',
                'filename': None
            }
        else:
            with youtube_dl.YoutubeDL(self.ydl_options) as ydl:
                try:
                    info = ydl.extract_info(item, download=False)

                    if 'entries' in info:
                        info = info['entries'][0]
                        source = info['formats'][0]['url']
                    else:
                        source = info['url']

                    filename = ydl.prepare_filename(info)
                    return {
                        'source': source,
                        'title': info['title'],
                        'filename': filename
                    }
                except:
                    print('Something went wrong.')
                    return None

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True
            filepath = self.music_queue[0]['filename']
            self.music_queue.pop(0)
            self.save_queue()

            self.voice_client.play(discord.FFmpegPCMAudio(filepath, **self.ffmpeg_options),
                                   after=lambda e: self.play_next())
        else:
            self.is_playing = False

    async def play_music(self, ctx):
        print('Inside play_music method')
        if len(self.music_queue) > 0:
            self.is_playing = True
            item = self.music_queue[0]
            self.music_queue.pop(0)
            self.save_queue()

            print(f'Playing audio: {item["title"]}')

            try:
                if self.voice_client is not None and self.voice_client.is_connected():
                    print('Voice client is initialized. Attempting to play audio...')
                    source = item['source']
                    if source.startswith("http"):
                        await self.play_stream(source)
                    else:
                        self.voice_client.play(discord.FFmpegPCMAudio(item['filename'], **self.ffmpeg_options),
                                               after=lambda e: asyncio.create_task(self.play_next()))
                else:
                    print("Voice client is not initialized or not connected.")
            except Exception as e:
                print(f'Error playing audio: {e}')
        else:
            self.is_playing = False

    async def play_stream(self, url):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0',
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            self.voice_client.play(discord.FFmpegPCMAudio(filename, **self.ffmpeg_options),
                                   after=lambda e: asyncio.create_task(self.play_next()))

    @commands.hybrid_command(name='play', brief='Plays a song in the voice channel. Usage: !play <song>')
    async def play(self, ctx, *, song):
        channel = ctx.author.voice.channel
        print(f'User is in voice channel: {channel is not None}')

        if channel is None:
            await ctx.send('You\'re not connected to a voice channel.')
        elif self.is_paused:
            print('Resuming playback...')
            self.voice_client.resume()
        else:
            async with ctx.typing():
                print(f'Searching for song: {song}')
                result = self.search_yt(song)
                if type(result) == type(True):
                    print('Oops, something went wrong.')
                    await ctx.send('Oops, something went wrong.')
                else:
                    print(f'Adding {result["title"]} to the queue.')
                    self.music_queue.append(result)
                    self.save_queue()

                    if not self.is_playing:
                        print('Starting playback...')
                        await self.play_music(ctx)
                        await asyncio.sleep(1)  # Добавляем задержку
                        print('After awaiting play_music')
                    else:
                        await ctx.send(f'Added {result["title"]} to the queue.')

    async def play_music(self, ctx):
        print('Inside play_music method')
        if len(self.music_queue) > 0:
            self.is_playing = True
            filepath = self.music_queue[0]['filename']
            self.music_queue.pop(0)
            self.save_queue()

            print(f'Playing audio from file: {filepath}')

            try:
                self.voice_client.play(discord.FFmpegPCMAudio(filepath, **self.ffmpeg_options),
                                       after=lambda e: asyncio.create_task(self.play_next()))
            except Exception as e:
                print(f'Error playing audio: {e}')

        else:
            self.is_playing = False

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True
            filepath = self.music_queue[0]['filename']
            self.music_queue.pop(0)
            self.save_queue()

            self.voice_client.play(discord.FFmpegPCMAudio(filepath, **self.ffmpeg_options),
                                   after=lambda e: asyncio.create_task(self.play_next()))
        else:
            self.is_playing = False

    @commands.hybrid_command(name='pause', brief='Pause the currently playing song')
    async def pause(self, ctx):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.voice_client.pause()
        elif self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.voice_client.resume()

        await ctx.send('')

    @commands.hybrid_command(name='resume', brief='Resume the paused song')
    async def resume(self, ctx):
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.voice_client.resume()
        await ctx.send('')

    @commands.hybrid_command(name='skip', brief='Skips the current song and plays the next one in the queue.')
    async def skip(self, ctx):
        if self.voice_client != None and self.voice_client:
            self.voice_client.stop()
            await self.play_music()
            await ctx.send('')

    @commands.hybrid_command(name='queue',
                             brief='Displays the entire current music playlist.')
    async def queue(self, ctx):
        result = ''
        for q in self.music_queue:
            result += q['title'] + '\n'

        if result != '':
            await ctx.send(result)
        else:
            await ctx.send('Queue is empty.')

    @commands.hybrid_command(name='qclear',
                             brief='It forces you to clear the entire music playlist.')
    async def clear_queue(self, ctx):
        if ctx.guild.me.guild_permissions.add_reactions:
            await ctx.message.add_reaction("👍")  # Замените "👍" на нужный вам смайлик
        else:
            print("Bot doesn't have permission to add reactions.")

        if self.voice_client is not None and self.is_playing:
            self.voice_client.stop()

        self.music_queue = []
        self.save_queue()

        await ctx.send('Queue cleared.')

    @commands.hybrid_command(name='clearchat',
                             brief='Forces to clear the specified number of messages in the current channel where the command was sent.')
    async def clear_chat(self, ctx, amount: int):
        """
        Clear a specified number of messages in the channel.
        :param amount: Number of messages to clear.
        """
        # Проверка, что в логине Discord пользователя есть "kote" и у него есть роль 'Глава'
        if "kote" not in ctx.author.name.lower() or "Глава" not in [role.name for role in ctx.author.roles]:
            await ctx.send("You don't have the necessary permissions to use this command.")
            return

        if ctx.author.guild_permissions.manage_messages:
            await ctx.message.delete()

            deleted_messages = await ctx.channel.purge(limit=amount)

            await ctx.send(f'Cleared {len(deleted_messages)} messages.', delete_after=5)
        else:
            await ctx.send("You don't have the necessary permissions to manage messages.")

    @commands.hybrid_command(name='join',
                             brief='Bot enters the current discord channel of the teams author.')
    async def join(self, ctx):
        channel = ctx.author.voice.channel
        print(f'Current voice client status: {self.voice_client}')
        print(f'Attempting to join channel: {channel}')

        try:
            if channel is not None:
                print('Attempting to join voice channel...')
                if self.voice_client is None or not self.voice_client.is_connected():
                    print('Connecting to voice channel...')
                    self.voice_client = await channel.connect()
                    await ctx.send(f'Joined {channel.name}')
                    print('Successfully connected to the voice channel.')
                else:
                    await ctx.send('I am already connected to a voice channel.')
                    print('Already connected to a voice channel.')
            else:
                await ctx.send('You are not connected to a voice channel.')
                print('User is not connected to a voice channel.')
        except Exception as e:
            print(f'An error occurred while connecting to the voice channel: {e}')

    @commands.hybrid_command(name='leave', brief='Bot to exit the current discord voice channel.')
    async def leave(self, ctx):
        async with ctx.typing():
            if self.voice_client is not None and self.voice_client.is_connected():
                print('Leaving the voice channel...')
                self.is_playing = False
                self.is_paused = False
                await self.voice_client.disconnect()
                await ctx.send('Left the voice channel.')
                print('Successfully left the voice channel.')
            else:
                await ctx.send('I am not connected to a voice channel.')
                print('Not connected to a voice channel.')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or('!'),
    description='A music bot. Prefix ! + command',
    intents=intents
)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await bot.tree.sync()

async def main():
    async with bot:
        await bot.add_cog(MusicCog(bot))
        await bot.start(get_token('discord-token'))

asyncio.run(main())