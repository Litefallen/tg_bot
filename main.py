import asyncio
import shutil
import telegram
import pytube
import os
import ffmpeg
import dotenv
from asyncffmpeg import FFmpegCoroutineFactory
from asynccpu import ProcessTaskPoolExecutor
from functools import partial

dotenv.load_dotenv() # hide sensitive data
my_api_key = os.environ.get('API')
API_KEY = my_api_key
def get_timestamps(file_size,chunk_size,audio_duration): # Function to calculate timestamps for splitting the audio
    timestamps_list = []
    chunk_length = int((audio_duration/file_size)*chunk_size)
    start = 0
    end = 0 + chunk_length
    for i in range(int(file_size // chunk_size) + 1):
        timestamps_list.append((start,end))
        start,end = end-1, end+chunk_length
    return timestamps_list

# Asynchronous function to split the audio using FFmpeg
async def aud_splitter(audio_path,timests:tuple,part = int):
    print('Splitting the audio into parts..')
    chunk = 49900
    input_stream = ffmpeg.input(f"{audio_path}.mp3")
    audio = input_stream.filter_('atrim', start=timests[0], end=timests[1])
    # print(audio)
    output = ffmpeg.output(audio, filename=f'{audio_path}_part_{part}',format="mp3")
    return output


def link_check(link: str):
# Function to check if a given link is a valid YouTube link
    try:
        valid_yt_object = pytube.YouTube(link)
        return valid_yt_object
    except pytube.exceptions.RegexMatchError:
        print('The link you sent is invalid. Please send a valid link')
        return False
async def main():
    bot = telegram.Bot(API_KEY)
    while True: # Get the last update ID
        last_update = await bot.get_updates()
        if last_update:
            update_id = last_update[-1].update_id - 1
            break

    while True:  # Main loop for processing updates
        new_update = await bot.get_updates(offset=update_id)
        if new_update:
            yt = link_check(new_update[0].message.text)
            chat_id = new_update[0].message.chat_id
            if yt: # If the link is valid, proceed with audio processing
                main_dir = os.getcwd()
                print('The link is okay, downloading audio now..')
                await bot.send_message(text='The link is okay, downloading audio now..',chat_id=chat_id)
                if os.path.exists(f'{chat_id}_files'):
                    shutil.rmtree(f'{chat_id}_files')
                os.mkdir(f'{chat_id}_files') # Create a temporary directory for processing audio files
                os.chdir(f'{chat_id}_files')
                yt.streams.get_audio_only().download(filename=f"{yt.title}.mp3")  # Download the audio stream
                audio_duration = yt.length
                audio_size = os.path.getsize(f"{yt.title}.mp3")/1000
                if os.path.getsize(f"{yt.title}.mp3")/1000 >49000: # Check if the audio needs to be split into parts
                    timests = get_timestamps(file_size=audio_size, audio_duration = audio_duration,chunk_size = 49000)
                    ffmpeg_coroutine = FFmpegCoroutineFactory.create()  # Create FFmpeg coroutine and ProcessTaskPoolExecutor
                    with ProcessTaskPoolExecutor(max_workers=None, cancel_tasks_when_shutdown=True) as executor:

                        awaitables = (
                            executor.create_process_task(ffmpeg_coroutine.execute, create_stream_spec)
                            for create_stream_spec in
                        [partial(aud_splitter, audio_path =f"{yt.title}",timests=timests[i],part = i) for i in range(len(timests))]
                        )
                        await asyncio.gather(*awaitables)

                    files =sorted([l for i in os.walk(os.getcwd()) for l in i[2] if 'part' in l]) # Get the list of created audio files
                    print(files)
                    for file in files:
                        print(file)
                        await bot.send_audio(audio=file,chat_id=chat_id, title= file)
                        print('The audio has been sent.')
                    await bot.send_message(text='All audio parts has been sent.',chat_id=chat_id)


                else:
                    await bot.send_audio(audio=f"{yt.title}.mp3",chat_id=chat_id, title= yt.title)
                    await bot.send_message(text='The audio has been sent.',chat_id=chat_id)
                    print('The audio has been sent.')

                os.chdir(main_dir) # Clean up temporary files and directories
                shutil.rmtree(f'{chat_id}_files')


            if not yt:
                await bot.send_message(text='The link you sent is invalid. Please send a valid link',chat_id=chat_id)
            update_id = new_update[0].update_id+1

if __name__ == '__main__':
    asyncio.run(main())
