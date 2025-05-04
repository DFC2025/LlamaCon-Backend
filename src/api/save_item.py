from fastapi import APIRouter, HTTPException

from src.core.deps import CurrentUser, DBClientDep
from src.core.models import Item, Tags

router = APIRouter()


@router.post("/")
async def save_item(
    item: Item,
    current_user: CurrentUser,
    client: DBClientDep,
):
    user_id = current_user.id

    try:
        saved_item = (
            client.table("shared_content")
            .insert(
                {
                    "url": item.url,
                    "text": item.title,
                    "meta": {
                        "source_url": item.sourceUrl,
                        "source_site": item.sourceSite,
                        "context": item.context,
                        "image_url": item.imageUrl,
                        "saved_from": item.savedFrom,
                        "type": item.type,
                    },
                    "user_id": user_id,
                }
            )
            .execute()
        )

        if not saved_item.data:
            raise HTTPException(
                status_code=500, detail="Failed to save item, no data returned."
            )

        return {"status": "success", "data": saved_item.data[0]}
    except Exception as e:
        print(f"Error saving item for user {user_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"An error occurred while saving: {e}"
        )


@router.put("/{item_id}/tags")
async def update_item_tags(
    item_id: str,
    tag_update: Tags,
    current_user: CurrentUser,
    client: DBClientDep,
):
    user_id = current_user.id

    try:
        item_check = (
            client.table("shared_content")
            .select("id")
            .eq("id", item_id)
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )
        if not item_check.data:
            raise HTTPException(
                status_code=404,
                detail="Item not found or user does not have permission",
            )

        client.table("tags").delete().eq("item_id", item_id).execute()

        tags_to_insert = [
            {
                "item_id": item_id,
                "name": tag.lower().strip(),
            }
            for tag in tag_update.tags
            if tag.strip()
        ]

        if tags_to_insert:
            result = client.table("tags").insert(tags_to_insert).execute()
            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to insert tags.")
            return {"status": "success", "data": result.data}

        return {"status": "success", "data": []}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Error updating tags for item {item_id}, user {user_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"An error occurred while updating tags: {e}"
        )
