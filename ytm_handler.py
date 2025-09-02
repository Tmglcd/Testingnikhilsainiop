import os
import requests
import subprocess
import asyncio
import yt_dlp
from pytube import YouTube
from pyromod import listen
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from vars import CREDIT
from vars import cookies_file_path, AUTH_USERS

#==========================================================================================================================================================================================
async def ytm_handler(bot: Client, m: Message):
    global processing_request, cancel_requested
    processing_request = True
    cancel_requested = False
    editable = await m.reply_text("__**Input Type**__\n\n<blockquote><b>01 •Send me the .txt file containing YouTube links\n02 •Send Single link or Set of YouTube multiple links</b></blockquote>")
    input: Message = await bot.listen(editable.chat.id)
    if input.document and input.document.file_name.endswith(".txt"):
        x = await input.download()
        file_name, ext = os.path.splitext(os.path.basename(x))
        playlist_name = file_name.replace('_', ' ')
        try:
            with open(x, "r") as f:
                content = f.read()
            content = content.split("\n")
            links = []
            for i in content:
                links.append(i.split("://", 1))
            os.remove(x)
        except:
             await m.reply_text("**Invalid file input.**")
             os.remove(x)
             return

        await editable.edit(f"**•ᴛᴏᴛᴀʟ 🔗 ʟɪɴᴋs ғᴏᴜɴᴅ ᴀʀᴇ --__{len(links)}__--\n•sᴇɴᴅ ғʀᴏᴍ ᴡʜᴇʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ...")
        try:
            input0: Message = await bot.listen(editable.chat.id, timeout=20)
            raw_text = input0.text
            await input0.delete(True)
        except asyncio.TimeoutError:
            raw_text = '1'
        
        await editable.delete()
        arg = int(raw_text)
        count = int(raw_text)
        try:
            if raw_text == "1":
                playlist_message = await m.reply_text(f"<blockquote><b>⏯️Playlist : {playlist_name}</b></blockquote>")
                await bot.pin_chat_message(m.chat.id, playlist_message.id)
                message_id = playlist_message.id
                pinning_message_id = message_id + 1
                await bot.delete_messages(m.chat.id, pinning_message_id)
        except Exception as e:
            pass
    
    elif input.text:
        content = input.text.strip()
        content = content.split("\n")
        links = []
        for i in content:
            links.append(i.split("://", 1))
        count = 1
        arg = 1
        await editable.delete()
        await input.delete(True)
    else:
        await m.reply_text("**Invalid input. Send either a .txt file or YouTube links set**")
        return
 
    try:
        for i in range(arg-1, len(links)):  # Iterate over each link
            if cancel_requested:
                await m.reply_text("🚦**STOPPED**🚦")
                processing_request = False
                cancel_requested = False
                return
            Vxy = links[i][1].replace("www.youtube-nocookie.com/embed", "youtu.be")
            url = "https://" + Vxy
            oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
            response = requests.get(oembed_url)
            audio_title = response.json().get('title', 'YouTube Video')
            audio_title = audio_title.replace("_", " ")
            name = f'{audio_title[:60]} {CREDIT}'        
            name1 = f'{audio_title} {CREDIT}'

            if "youtube.com" in url or "youtu.be" in url:
                prog = await m.reply_text(f"<i><b>Audio Downloading</b></i>\n<blockquote><b>{str(count).zfill(3)}) {name1}</b></blockquote>")
                cmd = f'yt-dlp -x --audio-format mp3 --cookies {cookies_file_path} "{url}" -o "{name}.mp3"'
                print(f"Running command: {cmd}")
                os.system(cmd)
                if os.path.exists(f'{name}.mp3'):
                    await prog.delete(True)
                    print(f"File {name}.mp3 exists, attempting to send...")
                    try:
                        await bot.send_document(chat_id=m.chat.id, document=f'{name}.mp3', caption=f'**🎵 Title : **[{str(count).zfill(3)}] - {name1}.mp3\n\n🔗**Video link** : {url}\n\n🌟** Extracted By **: {CREDIT}')
                        os.remove(f'{name}.mp3')
                        count+=1
                    except Exception as e:
                        await m.reply_text(f'⚠️**Downloading Failed**⚠️\n**Name** =>> `{str(count).zfill(3)} {name1}`\n**Url** =>> {url}', disable_web_page_preview=True)
                        count+=1
                else:
                    await prog.delete(True)
                    await m.reply_text(f'⚠️**Downloading Failed**⚠️\n**Name** =>> `{str(count).zfill(3)} {name1}`\n**Url** =>> {url}', disable_web_page_preview=True)
                    count+=1
                               
    except Exception as e:
        await m.reply_text(f"<b>Failed Reason:</b>\n<blockquote><b>{str(e)}</b></blockquote>")
    finally:
        await m.reply_text("<blockquote><b>All YouTube Music Download Successfully</b></blockquote>")

#========================================================================================================================================================================================================
async def y2t(client, message: Message):
    user_id = str(message.from_user.id)
    
    editable = await message.reply_text(
        f"<blockquote><b>Send YouTube Website/Playlist link for convert in .txt file</b></blockquote>"
    )

    input_message: Message = await bot.listen(message.chat.id)
    youtube_link = input_message.text.strip()
    await input_message.delete(True)
    await editable.delete(True)

    # Fetch the YouTube information using yt-dlp with cookies
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'force_generic_extractor': True,
        'forcejson': True,
        'cookies': 'youtube_cookies.txt'  # Specify the cookies file
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(youtube_link, download=False)
            if 'entries' in result:
                title = result.get('title', 'youtube_playlist')
            else:
                title = result.get('title', 'youtube_video')
        except yt_dlp.utils.DownloadError as e:
            await message.reply_text(
                f"<blockquote>{str(e)}</blockquote>"
            )
            return

    # Extract the YouTube links
    videos = []
    if 'entries' in result:
        for entry in result['entries']:
            video_title = entry.get('title', 'No title')
            url = entry['url']
            videos.append(f"{video_title}: {url}")
    else:
        video_title = result.get('title', 'No title')
        url = result['url']
        videos.append(f"{video_title}: {url}")

    # Create and save the .txt file with the custom name
    txt_file = os.path.join("downloads", f'{title}.txt')
    os.makedirs(os.path.dirname(txt_file), exist_ok=True)  # Ensure the directory exists
    with open(txt_file, 'w') as f:
        f.write('\n'.join(videos))

    # Send the generated text file to the user with a pretty caption
    await message.reply_document(
        document=txt_file,
        caption=f'<a href="{youtube_link}">__**Click Here to Open Link**__</a>\n<blockquote>{title}.txt</blockquote>\n'
    )

    # Remove the temporary text file after sending
    os.remove(txt_file)
    
