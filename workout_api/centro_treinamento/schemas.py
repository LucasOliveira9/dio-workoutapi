from workout_api.contrib.schemas import BaseSchema
from typing import Annotated
from pydantic import Field, UUID4


class CentroTreinamentoIn(BaseSchema):
    nome: Annotated[
        str,
        Field(
            description="Nome do Centro de Treinamento",
            example="CT King",
            max_length=20,
        ),
    ]
    endereco: Annotated[
        str,
        Field(
            description="Endereço do Centro de Treinamento",
            example="Rua X, Q 5",
            max_length=60,
        ),
    ]
    proprietario: Annotated[
        str,
        Field(
            description="Proprietario do Centro de Treinamento",
            example="Fernando Bola",
            max_length=30,
        ),
    ]


class CentroTreinamentoAtleta(BaseSchema):
    nome: Annotated[
        str,
        Field(
            description="Nome do Centro de Treinamento",
            example="CT King",
            max_length=20,
        ),
    ]

class CentroTreinamentoOut(CentroTreinamentoIn):
    id: Annotated[UUID4, Field(description="Identificador do Centro de treinamento")]
