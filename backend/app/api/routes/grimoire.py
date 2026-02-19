from fastapi import APIRouter, Depends, Query
from app.db.database import get_db

router = APIRouter()


@router.get("")
async def list_grimoire(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tier: str | None = None,
    name: str | None = None,
    db=Depends(get_db),
):
    """Return all spells, paginated and filterable."""
    offset = (page - 1) * page_size
    query = "SELECT * FROM grimoire WHERE 1=1"
    params: list = []

    if name:
        query += " AND spell_name LIKE ?"
        params.append(f"%{name}%")

    count_row = await db.execute(
        f"SELECT COUNT(*) FROM grimoire WHERE 1=1{'AND spell_name LIKE ?' if name else ''}",
        ([f"%{name}%"] if name else []),
    )
    total = (await count_row.fetchone())[0]

    query += " LIMIT ? OFFSET ?"
    params.extend([page_size, offset])

    cursor = await db.execute(query, params)
    rows = await cursor.fetchall()
    spells = [dict(r) for r in rows]

    return {"spells": spells, "total": total, "page": page, "page_size": page_size}


@router.get("/{ingredient_key}")
async def get_spell(
    ingredient_key: str,
    variant_index: int = Query(0, ge=0),
    db=Depends(get_db),
):
    """Return a specific spell by ingredient combo + variant."""
    cursor = await db.execute(
        "SELECT * FROM grimoire WHERE ingredient_key = ? AND variant_index = ?",
        (ingredient_key, variant_index),
    )
    row = await cursor.fetchone()
    if not row:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Spell not found")
    return dict(row)
