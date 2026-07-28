from fastapi import APIRouter, HTTPException

from app.models.schemas import AddToLibraryRequest, LibraryItem, UpdateLibraryItemRequest
from app.services import library_store, vector_store

router = APIRouter(prefix="/api/library", tags=["library"])


@router.get("", response_model=list[LibraryItem])
def list_library(collection: str | None = None, tag: str | None = None):
    """List saved papers, optionally filtered by collection or tag —
    the 'smart organization' surface of the app."""
    items = library_store.list_items()
    if collection:
        items = [i for i in items if i.collection == collection]
    if tag:
        items = [i for i in items if tag in i.tags]
    return items


@router.post("", response_model=LibraryItem)
def add_to_library(req: AddToLibraryRequest):
    item = LibraryItem(paper=req.paper, tags=req.tags, collection=req.collection)
    return library_store.upsert_item(item)


@router.patch("/{paper_id}", response_model=LibraryItem)
def update_library_item(paper_id: str, req: UpdateLibraryItemRequest):
    item = library_store.get_item(paper_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not in library")

    if req.tags is not None:
        item.tags = req.tags
    if req.collection is not None:
        item.collection = req.collection
    if req.status is not None:
        item.status = req.status
    if req.notes is not None:
        item.notes = req.notes

    return library_store.upsert_item(item)


@router.delete("/{paper_id}")
def remove_from_library(paper_id: str):
    deleted = library_store.delete_item(paper_id)
    vector_store.delete_paper(paper_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not in library")
    return {"paper_id": paper_id, "deleted": True}


@router.get("/collections/list")
def list_collections():
    items = library_store.list_items()
    collections = sorted({i.collection for i in items})
    return {"collections": collections}
