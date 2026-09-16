from decimal import Decimal, InvalidOperation

from database import SessionLocal
from models import Recebimento, Usuario


def criar_recebimento(valor, recebedor, forma_pagamento, observacao=None):

    try:
        valor = Decimal(str(valor).replace(",", "."))
    except (InvalidOperation, ValueError):
        raise ValueError("Valor inválido.")

    if valor <= 0:
        raise ValueError("O valor deve ser maior que zero.")

    with SessionLocal() as session:

        usuario = session.query(Usuario).filter_by(
            nome=recebedor
        ).first()

        if not usuario:
            raise ValueError(
                f"Recebedor '{recebedor}' não encontrado."
            )

        recebimento = Recebimento(
            valor=valor,
            forma_pagamento=forma_pagamento,
            usuario_id=usuario.id,
            observacao=observacao
        )

        session.add(recebimento)
        session.commit()

        return recebimento