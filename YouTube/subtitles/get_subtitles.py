#!/usr/bin/env python

from youtube_transcript_api import YouTubeTranscriptApi
from pprint import pprint

def get_subtitles(youtube_id: str):
	subtitles = YouTubeTranscriptApi.get_transcript(youtube_id, languages=['uk', 'ru'])
	pprint(subtitles)

# get_subtitles('Tes245tkUWo')
# get_subtitles('Jr3Q6Cw92fE')
get_subtitles('CNA6EFtkO68')
