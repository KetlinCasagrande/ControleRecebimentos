from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Usuario(Base):

    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    nome: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    login: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    senha: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    recebimentos = relationship(
        "Recebimento",
        back_populates="recebedor"
    )


class Recebimento(Base):

    __tablename__ = "recebimentos"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    data_hora: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    valor: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    forma_pagamento: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"),
        nullable=False
    )

    observacao: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
    )

    recebedor = relationship(
        "Usuario",
        back_populates="recebimentos"
    )