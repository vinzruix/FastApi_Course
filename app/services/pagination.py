from math import ceil
from typing import Optional, Dict, Any
from fastapi.params import Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.db import Base, get_db

DEFAULT_PER_PAGE = 10
MAX_PER_PAGE = 100


async def sanitize_pagination(page: int = 1, per_page: int = DEFAULT_PER_PAGE):
    page = max(1, int(page or 1))
    per_page = min(MAX_PER_PAGE, max(1, int(per_page or DEFAULT_PER_PAGE)))

    return page, per_page


async def paginate_query(db: Session = Depends(get_db),
                         model = None,
                         base_query=None,
                         page: int = 1,
                         per_page: int = DEFAULT_PER_PAGE,
                         order_by: Optional[str] = None,
                         direction: str = "asc",
                         allowed_order: Optional[Dict[str, Any]] = None
                         ):
    page, per_page = await sanitize_pagination(page, per_page)
    query = base_query if base_query is not None else select(
        model)  # Base query es una preconsultab a la base , es decir un select MODEL

    total = db.scalar(select(func.count()).select_from(model)) or 0

    if total == 0:
        return {"total": 0, "pages": 0, "page": page, "per_page": per_page, "items": []}

    if allowed_order and order_by:
        col = allowed_order.get(order_by, allowed_order.get("id"))
        query = query.order_by(col.desc() if direction == "desc" else col.asc())

    items = db.execute(query.offset((page - 1) * per_page).limit(
        per_page)).scalars().all()  # scalars convierte los resultados en objetos del Base (clase de los bd)


    return {"total": total, "pages": ceil(total / per_page), "page": page, "per_page": per_page, "items": items}
