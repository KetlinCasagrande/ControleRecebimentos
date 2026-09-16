from decimal import Decimal

from database import SessionLocal
from models import Recebimento, Usuario


def buscar_recebimento(recebimento_id):

    with SessionLocal() as session:

        recebimento = (
            session.query(Recebimento)
            .filter(
                Recebimento.id == recebimento_id
            )
            .first()
        )

        if not recebimento:
            return None

        return {
            "id": recebimento.id,
            "valor": Decimal(
                recebimento.valor
            ),
            "recebedor": (
                recebimento.recebedor.nome
            ),
            "forma_pagamento": (
                recebimento.forma_pagamento
            ),
            "observacao": (
                recebimento.observacao or ""
            ),
        }


def editar_recebimento(
    recebimento_id,
    valor,
    recebedor,
    forma_pagamento,
    observacao
):

    with SessionLocal() as session:

        recebimento = (
            session.query(Recebimento)
            .filter(
                Recebimento.id == recebimento_id
            )
            .first()
        )

        if not recebimento:
            raise ValueError(
                "Recebimento não encontrado."
            )

        usuario = (
            session.query(Usuario)
            .filter(
                Usuario.nome == recebedor
            )
            .first()
        )

        if not usuario:
            raise ValueError(
                "Recebedor não encontrado."
            )

        try:

            valor_decimal = Decimal(
                str(valor)
                .replace(".", "")
                .replace(",", ".")
            )

        except Exception:

            raise ValueError(
                "Valor inválido."
            )

        if valor_decimal <= 0:

            raise ValueError(
                "O valor deve ser maior que zero."
            )

        recebimento.valor = valor_decimal

        recebimento.usuario_id = usuario.id

        recebimento.forma_pagamento = (
            forma_pagamento
        )

        recebimento.observacao = (
            observacao.strip()
            if observacao
            else None
        )

        session.commit()


def excluir_recebimento(
    recebimento_id
):

    with SessionLocal() as session:

        recebimento = (
            session.query(Recebimento)
            .filter(
                Recebimento.id == recebimento_id
            )
            .first()
        )

        if not recebimento:

            raise ValueError(
                "Recebimento não encontrado."
            )

        session.delete(
            recebimento
        )

        session.commit()