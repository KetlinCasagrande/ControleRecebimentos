from sqlalchemy.orm import joinedload

from database import SessionLocal
from models import Recebimento


def buscar_ultimos_recebimentos(limite=10):

    with SessionLocal() as session:

        recebimentos = (
            session.query(Recebimento)
            .options(joinedload(Recebimento.recebedor))
            .order_by(Recebimento.data_hora.desc())
            .limit(limite)
            .all()
        )

        return recebimentos