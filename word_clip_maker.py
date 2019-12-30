import argparse
from utils import clean_word, BadOptionsError, makedir
from ffmpeg_utils import download_youtube_video, media_to_mono_flac, crop_audio, change_audio_speed
from youtube_utils import video_code_to_url
from google_utils import transcribe_audio, interval_of
import json

from datastore_utils import list_instances_of_word


FFMPEG_CONFIG = {'loglevel': 'panic', 'safe': 0, 'hide_banner': None, 'y': None}


def word_clip_maker(word):
    # TODO: Move instance list retrieval to videograms script...
    if not word:
        raise BadOptionsError('Must specify WORD')

    word = clean_word(word)

    # Find all instances of the word in our datastore captioned words
    instance_infos = []
    instances = list_instances_of_word(word)
    for instance in instances:
        instance_infos.append({
            'instance_key': instance.key.id,
            'start_time': instance['start_time'],
            'end_time': instance['end_time'],
            'video_code': instance['video_code']
        })

    # Pass instances out to workers
    ## TODO REmove here and about
    instance_info = instance_infos[0]

    makedir('tmp')

    # Download video segment to local disk
    video_segment_filepath = f'tmp/{word}.mp4'
    download_youtube_video(
        instance_info['video_code'],
        instance_info['start_time'],
        instance_info['end_time'],
        video_segment_filepath,
        safety_buffer=1.,
    )

    # Convert to FLAC
    flac_segment_filepath = f'tmp/{word}.flac'
    media_to_mono_flac(video_segment_filepath, flac_segment_filepath, **FFMPEG_CONFIG)

    # Slow clip to improve recognition
    slowed_segment_filepath = f'tmp/{word}-.8.flac'
    change_audio_speed(flac_segment_filepath, 0.8, slowed_segment_filepath)


    ######################
    # FIND WORD INTERVAL #
    ######################

    # Transcribe clip & find the word interval
    transcription = transcribe_audio(slowed_segment_filepath)
    word_interval = interval_of(word, transcription)
#    word_interval = (word_interval[0]-.1, word_interval[1]+.1)

    if not word_interval:
        print('Word not found in original segment')
        exit()

    # Clip to new length
    cropped_audio_filepath = f'tmp/{word}-tmp-cropped.flac'
    crop_audio(slowed_segment_filepath, *word_interval, cropped_audio_filepath, **FFMPEG_CONFIG)

    return 'ok'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--word')
    args = parser.parse_args()

    print(word_clip_maker(**vars(args)))
