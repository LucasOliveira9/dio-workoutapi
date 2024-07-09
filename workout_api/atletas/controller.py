from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Body, HTTPException, status, Query
from fastapi_pagination import Page, paginate
from pydantic import UUID4
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from workout_api.atletas.models import AtletaModel
from workout_api.atletas.schemas import  AtletaIn, AtletaOut, AtletaOutGet, AtletaUpdate
from workout_api.categorias.models import CategoriaModel
from workout_api.centro_treinamento.models import CentroTreinamentoModel
from workout_api.contrib.dependencies import DatabaseDependency

router = APIRouter()

@router.post(
    "/",
    summary="Criar novo atleta",
    status_code=status.HTTP_201_CREATED,
    response_model=AtletaOutGet,
)
async def post(
    db_session: DatabaseDependency, atleta_in: AtletaIn = Body(...)
) -> AtletaOutGet:
    categoria_nome = atleta_in.categoria.nome
    centro_treinamento_nome = atleta_in.centro_treinamento.nome
    categoria = (
        (
            await db_session.execute(
                select(CategoriaModel).filter_by(nome=categoria_nome)
            )
        )
        .scalars()
        .first()
    )
    centro_treinamento = (
        (
            await db_session.execute(
                select(CentroTreinamentoModel).filter_by(nome=centro_treinamento_nome)
            )
        )
        .scalars()
        .first()
    )
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Categoria {categoria_nome} não encontrada",
        )

    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Centro de treinamento {centro_treinamento_nome} não encontrado",
        )

    try:
        atleta_out = AtletaOut(
            id=uuid4(), created_at=datetime.utcnow(), **atleta_in.model_dump()
        )
        atleta_out_get = AtletaOutGet(**atleta_out.model_dump(include = {"nome", "centro_treinamento", "categoria", "id", "created_at"}))
        atleta_model = AtletaModel(
            **atleta_out.model_dump(exclude={"categoria", "centro_treinamento"})
        )
        atleta_model.categoria_id = categoria.pk_id
        atleta_model.centro_treinamento_id = centro_treinamento.pk_id
        db_session.add(atleta_model)
        await db_session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_300_MULTIPLE_CHOICES,
            detail=f"Já existe um atleta cadastrado com o cpf: {atleta_in.cpf}",
        )
    return atleta_out_get


@router.get(
    "/",
    summary="Consultar todos os atletas",
    status_code=status.HTTP_200_OK,
    response_model=Page[AtletaOutGet],
)
async def query(db_session: DatabaseDependency, nome: str = Query(None, description="Nome do Atleta"),
                 cpf: str = Query(None, description = "CPF do Atleta")) -> Page[AtletaOutGet]:
    query = select(AtletaModel)

    if nome:
        query = query.filter(AtletaModel.nome.ilike(f"%{nome}%"))
    if cpf:
        query = query.filter(AtletaModel.cpf == cpf)

    atletas: Page[AtletaOutGet] = (await db_session.execute(query)).scalars().all()
    return paginate([AtletaOutGet.model_validate(atleta) for atleta in atletas])


@router.get(
    "/{id}",
    summary="Consultar um atleta",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOutGet,
)
async def query_id(id: UUID4, db_session: DatabaseDependency) -> AtletaOutGet:
    atleta: AtletaOutGet = (
        (await db_session.execute(select(AtletaModel).filter_by(id=id)))
        .scalars()
        .first()
    )
    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrada no id: {id}",
        )
    return atleta


@router.patch(
    "/{id}",
    summary="Editar atleta",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def query_update(
    id: UUID4, db_session: DatabaseDependency, atleta_up: AtletaUpdate = Body(...)
) -> AtletaOut:
    atleta: AtletaOut = (
        (await db_session.execute(select(AtletaModel).filter_by(id=id)))
        .scalars()
        .first()
    )
    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrada no id: {id}",
        )

    atleta_update = atleta_up.model_dump(exclude_unset=True)

    for key, value in atleta_update.items():
        setattr(atleta, key, value)

    await db_session.commit()
    await db_session.refresh(atleta)
    return atleta


@router.delete(
    "/{id}",
    summary="Deletar um atleta",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def query_delete(id: UUID4, db_session: DatabaseDependency) -> None:
    atleta: AtletaOut = (
        (await db_session.execute(select(AtletaModel).filter_by(id=id)))
        .scalars()
        .first()
    )
    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrada no id: {id}",
        )
    await db_session.delete(atleta)
    await db_session.commit()