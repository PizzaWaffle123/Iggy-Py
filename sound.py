import discord

client = None


async def play(sfx_name):
    global client
    vc = client.guilds[0].voice_channels[0]
    voice_client = await vc.connect()
    voice_client.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source=f"./sfx/{sfx_name}.mp3"))
    # voice_client.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source="./vine-boom.mp3"))
    # voice_client.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source="./vine-boom.mp3"))
    while voice_client.is_playing():
        pass
    await voice_client.disconnect()
