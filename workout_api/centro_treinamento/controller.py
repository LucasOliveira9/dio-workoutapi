from fastapi import APIRouter, status, Body, HTTPException, Query
from fastapi_pagination import Page, paginate

from workout_api.contrib.dependencies import DatabaseDependency
from workout_api.centro_treinamento.schemas import (
    CentroTreinamentoIn,
    CentroTreinamentoOut,
)
from workout_api.centro_treinamento.models import CentroTreinamentoModel

from sqlalchemy.future import select

from uuid import uuid4

from pydantic import UUID4

router = APIRouter()


@router.post(
    "/",
    summary="Criar novo centro de treinamento",
    status_code=status.HTTP_201_CREATED,
    response_model=CentroTreinamentoOut,
)
async def post(
    db_session: DatabaseDependency,
    Centro_de_treinamento_in: CentroTreinamentoIn = Body(...),
) -> CentroTreinamentoOut:
    Centro_de_treinamento_out = CentroTreinamentoOut(
        id=uuid4(), **Centro_de_treinamento_in.model_dump()
    )
    Centro_de_treinamento_model = CentroTreinamentoModel(
        **Centro_de_treinamento_out.model_dump()
    )
    db_session.add(Centro_de_treinamento_model)
    await db_session.commit()
    return Centro_de_treinamento_out


@router.get(
    "/",
    summary="Consultar todos os Centro de treinamento",
    status_code=status.HTTP_200_OK,
    response_model=Page[CentroTreinamentoOut],
)
async def query(
    db_session: DatabaseDependency,
    nome: str = Query(None, description="Centro de Treinamento"),
) -> Page[CentroTreinamentoOut]:
    query = select(CentroTreinamentoModel)
    if nome:
        query = query.filter(CentroTreinamentoModel.nome.ilike(f"%{nome}%"))

    Centro_de_treinamento: Page[CentroTreinamentoOut] = (
        (await db_session.execute(query)).scalars().all()
    )
    return paginate(Centro_de_treinamento)


@router.get(
    "/{id}",
    summary="Consultar um Centro de treinamento",
    status_code=status.HTTP_200_OK,
    response_model=CentroTreinamentoOut,
)
async def query_id(id: UUID4, db_session: DatabaseDependency) -> CentroTreinamentoOut:
    Centro_de_treinamento: CentroTreinamentoOut = (
        (await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id)))
        .scalars()
        .first()
    )
    if not Centro_de_treinamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Centro de treinamento não encontrado no id: {id}",
        )
    return Centro_de_treinamento
