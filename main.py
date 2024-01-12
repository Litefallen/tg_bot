import asyncio
import telegram
import pytube
import os
import ffmpeg

API_KEY = '6984693091:AAGlvm4tnrC_FFYe6cGMZaE2l0y0Ow6BdLk'
# commands_list = ['/how',]

def aud_splitter(audio_path,audio_duration):
    file_size = os.path.getsize(audio_path)/1000
    # file_size = 440
    # chunk = 49900
    chunk = float(10000)
    one_unit = audio_duration/file_size
    # one_unit = 120/file_size
    length = int(one_unit*chunk)
    input_stream = ffmpeg.input(audio_path)
    print(input_stream)
    start = 0
    end = 0 + length
    for part in range(int(file_size//chunk) + 1):
        audio = input_stream.filter_('atrim', start=start, end=end)
        print(audio)
        output = ffmpeg.output(audio, filename=f'{part}',format="mp3")
        # first part is split by length variable
        # next parts starts from length variable and end by length variable + length variable
        start,end = end,end+length
        ffmpeg.run(output)
def link_check(link: str):
    try:
        valid_yt_object = pytube.YouTube(link)
        return valid_yt_object
    except pytube.exceptions.RegexMatchError:
        print('The link you sent is invalid. Please send a valid link')
        return False
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
            # if new_update[0].message.text in commands_list:
            #     continue
            yt = link_check(new_update[0].message.text)
            update_id = new_update[0].update_id
            chat_id = new_update[0].message.chat_id
            if yt:
                print('The link is okay, downloading audio now..')

                await bot.send_message(text='The link is okay, downloading audio now..',chat_id=chat_id)
                yt.streams.get_audio_only().download(filename=f"{yt.title}.mp3")
                if os.path.getsize(f"{yt.title}.mp3")/1000 >10000:
                    aud_splitter(audio_path=f"{yt.title}.mp3",audio_duration=yt.length)
                # await bot.send_audio(audio=f"{yt.title}.mp3",chat_id=chat_id, title= yt.title)
                else:
                    await bot.send_audio(audio=f"{yt.title}.mp3",chat_id=chat_id, title= yt.title)
                    print('The audio has been sent.')
            if not yt:
                await bot.send_message(text='The link you sent is invalid. Please send a valid link',chat_id=chat_id)


if __name__ == '__main__':
    asyncio.run(main())
