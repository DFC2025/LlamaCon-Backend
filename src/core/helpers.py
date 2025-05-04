from src.core.db_client import supabase_client
import json


def get_domain(url:str):
    return url.split("/")[2]


def get_favicon(url:str):
    domain = get_domain(url)
    return f"https://www.google.com/s2/favicons?domain={domain}"

def clean_items(items:list):
    for item in items:
        # get favicon from url
        item['image']=get_favicon(supabase_client.table("shared_content").select("url").eq("id",item['content_id']).execute().data[0]["url"])
        item['title'] = supabase_client.table("shared_content").select("text").eq("id",item['content_id']).execute().data[0]["text"]
        item['tags'] = json.loads(item['tags'])
    return items
