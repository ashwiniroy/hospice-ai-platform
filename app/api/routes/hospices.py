from fastapi import APIRouter, Query
import pandas as pd

from app.services.dataset_service import DatasetService
from app.services.hospice_service import HospiceService
from app.schemas.hospice import HospiceResponse
from app.schemas.hospice import HospiceListResponse
from app.utils.text import hospice_to_text

router = APIRouter(
    prefix="/api/hospices",
    tags=["Hospices"]
)

dataset_service = DatasetService()


@router.get("/", response_model =HospiceListResponse)
def get_hospices(
    q: str | None = None,
    state: str | None = None,
    city: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100)
):
    df = dataset_service.load_hospice_dataset().copy()
    row = df.iloc[0]

    text = hospice_to_text(row)

    print(text)

    if q:
        text_columns = df.select_dtypes(include=["object", "string"]).columns

        mask = pd.Series(False, index=df.index)

        for column in text_columns:
            mask = mask | (
                df[column]
                .fillna("")
                .astype(str)
                .str.contains(q, case=False, regex=False)
            )

        df = df[mask]

    if state and "state" in df.columns:
        df = df[
            df["state"]
            .fillna("")
            .astype(str)
            .str.upper() == state.upper()
        ]

    if city and "city" in df.columns:
        df = df[
            df["city"]
            .fillna("")
            .astype(str)
            .str.lower() == city.lower()
        ]

    total = len(df)

    start = (page - 1) * page_size
    end = start + page_size

    result_df = df.iloc[start:end].copy()

    result_df = result_df.astype(object)
    result_df = result_df.where(pd.notnull(result_df), None)

    records = result_df.to_dict(orient="records")

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": records
    }

hospice_service = HospiceService()

@router.get("/semantic-search")
def semantic_search(
    q: str,
    top_k: int = 5,
    state: str | None = None,
    ownership: str | None = None
):
    results = hospice_service.semantic_search(
        query=q,
        top_k=top_k,
        state=state,
        ownership=ownership
    )

    return {
        "query": q,
        "filters": {
            "state": state,
            "ownership": ownership
        },
        "count": len(results),
        "results": results
    }


@router.get("/{index}", response_model=HospiceResponse)
def get_hospice(index: int):

    hospice = hospice_service.get_hospice_by_index(index)

    if hospice is None:
        raise HTTPException(
            status_code=404,
            detail="Hospice record not found"
        )

    return hospice