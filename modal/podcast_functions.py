from podgen import Podcast, Episode, Media
from openai import OpenAI
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from modal_setup import image
import modal
import os
import uuid
from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment
import tempfile
from bucket_functions import upload_to_bucket
from prompts import PODCAST_PROMPT,MULTIPLE_PODCAST_PROMPT,MULTIPLE_PODCAST_SUMMARY_PROMPT,WEEKLY_DIGEST_TITLE_PROMPT,PODCAST_PROMPT_HINDI,HINDI_SUMMARY

import feedparser
from podgen import Podcast, Episode, Media
import datetime, pytz


load_dotenv()
url=os.environ.get("SUPABASE_URL")
key=os.environ.get("SUPABASE_KEY")
GROQ_API_KEY=os.environ.get("GROQ_API_KEY")
ELEVENLABS_API_KEY=os.environ.get("ELEVENLABS_API_KEY")
supabase: Client = create_client(url, key)

app = modal.App(image=image,name="podcast_function2")






API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not API_KEY:
    raise ValueError("ELEVENLABS_API_KEY environment variable not set")

client = ElevenLabs(api_key=API_KEY)

# === CONFIGURATION ===
HOST1_VOICE_ID = "UgBBYS2sOqTuMpoF3BR0"  # e.g. Adam
HOST2_VOICE_ID = "zGjIP4SZlMnY9m93k97r"  # e.g. Rachel
MODEL_ID       = "eleven_multilingual_v2" 


# low-latency turbo model


HOST1_HINDI_VOICE_ID = "zT03pEAEi0VHKciJODfn"
HOST2_HINDI_VOICE_ID = "zGjIP4SZlMnY9m93k97r"

def synthesize_segment(text: str, voice_id: str) -> AudioSegment:
    """Call ElevenLabs and return a pydub.AudioSegment for this text + voice."""
    stream = client.text_to_speech.convert(
        voice_id=voice_id,
        model_id=MODEL_ID,
        optimize_streaming_latency="0",
        text=text,
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
        ),
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        for chunk in stream:
            if chunk:
                tmp.write(chunk)
        tmp_path = tmp.name

    return AudioSegment.from_file(tmp_path, format="mp3")

def build_podcast(script,output_path="podcast_episode.mp3"):
    """Generate and concatenate all segments, then export as a single MP3."""
    final_mix = AudioSegment.silent(duration=500)  # half-second lead-in
    for speaker, text in script:
        voice = HOST1_VOICE_ID if speaker == "Host1" else HOST2_VOICE_ID
        seg = synthesize_segment(text, voice)
        final_mix += seg + AudioSegment.silent(duration=300)  # small gap between segments

    print(f"Exporting full episode to {output_path}")
    final_mix.export(output_path, format="mp3")



def build_hindi_podcast(script,output_path="podcast_episode.mp3"):
    """Generate and concatenate all segments, then export as a single MP3."""
    final_mix = AudioSegment.silent(duration=500)  # half-second lead-in
    for speaker, text in script:
        voice = HOST1_HINDI_VOICE_ID if speaker == "Host1" else HOST2_HINDI_VOICE_ID
        seg = synthesize_segment(text, voice)
        final_mix += seg + AudioSegment.silent(duration=300)  # small gap between segments

    print(f"Exporting full episode to {output_path}")
    final_mix.export(output_path, format="mp3")

def parse_transcript(transcript_text):
    """
    Parses a transcript string with alternating speakers into a list of tuples.

    Args:
        transcript_text: A string containing the full transcript.

    Returns:
        A list of tuples, where each tuple is (speaker, dialogue).
    """
    lines = transcript_text.strip().split('\n')
    parsed_script = []
    current_speaker = None
    current_dialogue = []

    for line in lines:
        line = line.strip()
        if line:
            # Assuming speaker labels are at the beginning of the line followed by a colon
            if ':' in line:
                speaker, dialogue = line.split(':', 1)
                speaker = speaker.strip()
                dialogue = dialogue.strip()

                if current_speaker is not None and current_speaker != speaker:
                    parsed_script.append((current_speaker, " ".join(current_dialogue)))
                    current_dialogue = []

                current_speaker = speaker
                current_dialogue.append(dialogue)
            elif current_speaker is not None:
                # If a line doesn't have a speaker label, assume it continues the previous speaker's dialogue
                current_dialogue.append(line)

    # Add the last speaker's dialogue
    if current_speaker is not None and current_dialogue:
        parsed_script.append((current_speaker, " ".join(current_dialogue)))

    return parsed_script





def download_xml(id:str):
    data = supabase.storage.from_("podcast").download(f"{id}/rss_feed/podcast.xml")
    with open('downloaded.xml', 'wb') as f:
        f.write(data)
        

        
def upload_xml(id:str):
    # upsert=true
    with open('rss.xml', 'rb') as f:
        data = (
            supabase.storage.from_("podcast").upload(f"{id}/rss_feed/podcast.xml", f,file_options={"upsert":"true","content-type":"application/rss+xml"})
        )
    return data

# 1) Parse the old feed
def load_and_update_rss(title,summary,url,length):
    
    old = feedparser.parse("downloaded.xml")

    p = Podcast(
        name        = old.feed.get("title", ""),
        website     = old.feed.get("link", ""),
        description = old.feed.get("description", ""),
        explicit    = False            # or derive from old.feed.itunes_explicit
    )

    # 3) Re-create each old entry as a PodGen Episode
    for entry in old.entries:
        ep = p.add_episode()
        ep.title            = entry.get("title", "")
        ep.summary          = entry.get("summary", "")
        ep.link             = entry.get("link", "")
        # Publication date (convert struct_time → datetime)
        if hasattr(entry, "published_parsed"):
            dt = entry.published_parsed
            ep.publication_date = datetime.datetime(*dt[:6], tzinfo=pytz.UTC)
        # First enclosure → media
        if entry.get("enclosures"):
            m = entry.enclosures[0]
            ep.media = Media(
                m.href,
                size = int(m.get("length", 0)),
                type = m.get("type", None)
            )

    # 4) Add your new episode(s)
    new_ep = p.add_episode()
    new_ep.title   = title
    new_ep.summary = summary
    new_ep.media   = Media(
        url,
        size     = length
    )

    # 5) Write out the merged feed
    p.rss_file("rss.xml")

@app.function()
@modal.fastapi_endpoint(method="GET")
def get_xml_url_from_id(id:str):
    exists = supabase.storage.from_('podcast').exists(f'{id}/rss_feed/podcast.xml')
    print(exists)
    if exists:
        url = supabase.storage.from_('podcast').get_public_url(f'{id}/rss_feed/podcast.xml')
        return url
    else:
        return None
    


# @app.function()
# @modal.fastapi_endpoint(method="POST")
# def create_podcast(name, description, website, explicit,id):
#     p = Podcast(
#         name=name,
#         description=description,
#         website=website,
#         explicit=explicit,
#     )
#     rss = p.rss_str()
#     # save the rss to the supabase storage
#     try:
#         with open("podcast.xml", "w") as f:
#             f.write(rss)
#         with open("podcast.xml", "rb") as f:
#             res= supabase.storage.from_('podcast').upload(f'{id}/rss_feed/podcast.xml',f,file_options={"content-type":"application/rss+xml"})
#             print(res)
#         url = supabase.storage.from_('podcast').get_public_url(f'{id}/rss_feed/podcast.xml')
#         return url
#     except Exception as e:
#         return False
    




def get_response(query,prompt):
        print("running llama4 on groq")
        print(GROQ_API_KEY)
        client=OpenAI(
            api_key="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",
            base_url="https://api.groq.com/openai/v1"
        )
        response=client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=[{"role":"system","content":prompt},{"role":"user","content":query}]
        )
        return response.choices[0].message.content 
    

def get_content_from_bucket(id:str,file_name:str="cleaned_markdown.md"):
    path=f'{id}/{file_name}'
    data: bytes = supabase.storage.from_("content").download(path) 
    return data.decode("utf-8")


def get_title_and_summary(id:str):
    title=supabase.table('shared_content').select('text').eq('id',id).execute().data[0]['text']
    summary=supabase.table('documents').select('content').eq('content_id',id).execute().data[0]['content']
    return title,summary

def add_episode_to_rss(title,summary,url,user_id):
    download_xml(user_id)
    load_and_update_rss(title,summary,url,2131)
    upload_xml(user_id)


def mp3_upload_to_bucket(local_path: str, remote_path: str,bucket_name: str="podcast") -> bool:
    with open(local_path, "rb") as f:
        res = (
            supabase.storage.from_(bucket_name)
        .upload(
          path=remote_path,
          file=f,
          file_options={"content-type": "audio/mpeg", "upsert":"true"}
        )
    )
    return res


@app.function()
@modal.fastapi_endpoint(method="POST")
def generate_podcast(id:str,user_id:str):
    content=get_content_from_bucket(id,'cleaned_markdown.md')
    content=content.replace("```markdown", "")
    content=content.replace("```", "")
    response = get_response(content,PODCAST_PROMPT)
    response = response.replace("```", "")
    response=response.replace("```markdown", "")
    parsed_script = parse_transcript(response)
    build_podcast(parsed_script,"podcast_episode.mp3")
    mp3_upload_to_bucket('podcast_episode.mp3',f'{id}/podcast_episode.mp3')
    url=supabase.storage.from_('podcast').get_public_url(f'{id}/podcast_episode.mp3')
    title,summary=get_title_and_summary(id)
    add_episode_to_rss(title,summary,url,user_id)
    print(response)
    return response


@app.function()
@modal.fastapi_endpoint(method="POST")
def generate_hindi_podcast(id:str,user_id:str):
    content=get_content_from_bucket(id,'cleaned_markdown.md')
    content=content.replace("```markdown", "")
    content=content.replace("```", "")
    response = get_response(content,PODCAST_PROMPT_HINDI)
    response = response.replace("```", "")
    response=response.replace("```markdown", "")
    parsed_script = parse_transcript(response)
    build_hindi_podcast(parsed_script,"podcast_episode.mp3")
    mp3_upload_to_bucket('podcast_episode.mp3',f'{id}/podcast_episode.mp3')
    url=supabase.storage.from_('podcast').get_public_url(f'{id}/podcast_episode.mp3')
    title,summary=get_title_and_summary(id)
    hindi_summary=get_response(summary,HINDI_SUMMARY)
    add_episode_to_rss(title,hindi_summary,url,user_id)
    print(response)
    return response




from pydantic import BaseModel
from typing import List

class PodcastRequest(BaseModel):
    ids: List[str]
    user_id: str

@app.function()
@modal.fastapi_endpoint(method="POST")
def generate_multiple_podcast(request: PodcastRequest):
    base_path="weekly_digest"
    cumulative_content=""
    summaries=""
    for id in request.ids:
        content=get_content_from_bucket(id,'cleaned_markdown.md')
        content=content.replace("```markdown", "")
        content=content.replace("```", "")
        title,summary=get_title_and_summary(id)
        cumulative_content+=f"Title: {title}\n\nSummary: {summary}\n\nContent: {content}\n\n"
        summaries+=f"Title: {title}\n\nSummary: {summary}\n\n"
    response = get_response(cumulative_content,MULTIPLE_PODCAST_PROMPT)
    summary_response=get_response(summaries,MULTIPLE_PODCAST_SUMMARY_PROMPT)
    title_response=get_response(summaries,WEEKLY_DIGEST_TITLE_PROMPT)
    response = response.replace("```", "")
    response=response.replace("```markdown", "")
    parsed_script = parse_transcript(response)
    build_podcast(parsed_script,"podcast_episode.mp3")
    mp3_upload_to_bucket('podcast_episode.mp3',f'{base_path}/{request.ids[0]}/podcast_episode.mp3')
    url=supabase.storage.from_('podcast').get_public_url(f'{base_path}/{request.ids[0]}/podcast_episode.mp3')
    add_episode_to_rss(title_response,summary_response,url,request.user_id)
    print(response)
    return response



# def create_podcast(name, description, website, explicit):

# # Create the Podcast
#     p = Podcast(
#         name="LLamaCast",
#         description="A podcast created for you, from your interests by your llamabuddy",
#         website="https://llamacast.com",
#         explicit=False,
#     )

#     # Add some episodes
#     p.episodes += [
#         Episode(
#             title="F1",
#             media=Media("https://ystckzgheqqdookbyjex.supabase.co/storage/v1/object/public/podcast/episodes/f1.mp3?", 11932295),  # URL and size in bytes
#             summary="This is my first episode about...",
#         ),
#     ]

#     # Generate the RSS feed
#     rss = p.rss_str()

#     # Save to a file
#     with open("podcast.xml", "w") as f:
#         f.write(rss)

