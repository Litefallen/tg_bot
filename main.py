import asyncio
import telegram
import pytube
import requests

# yt = pytube.YouTube('https://www.youtube.com/watch?v=g7Yvi7pHyII')
# print(yt.fmt_streams)
API_KEY = '6984693091:AAGlvm4tnrC_FFYe6cGMZaE2l0y0Ow6BdLk'

def link_check(link: str):
    try:
        valid_yt_object = pytube.YouTube(link)
        return valid_yt_object
    except pytube.exceptions.RegexMatchError:
        print('The link you sent is invalid. Please send a valid link')
        return False
# CHAT='@litefallen'
async def main():
    bot = telegram.Bot(API_KEY)
    while True:
        last_update = await bot.get_updates()
        if last_update:
            update_id = last_update[-1].update_id - 1
            break

    while True:
        new_update = await bot.get_updates(offset=update_id+1)
        if new_update:
            yt = link_check(new_update[0].message.text)
            update_id = new_update[0].update_id
            chat_id = new_update[0].message.chat_id
            if yt:
                print('The link is okay, downloading audio now..')
                yt.streams.get_audio_only().download(filename='file.mp3')
                await bot.send_audio(audio='file.mp3',chat_id=chat_id, title=yt.title)


if __name__ == '__main__':
    asyncio.run(main())
