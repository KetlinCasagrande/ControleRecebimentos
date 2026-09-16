from datetime import datetime

from sqlalchemy import func

from database import SessionLocal
from models import Recebimento, Usuario


def buscar_resumo():

    hoje = datetime.now().date()

    with SessionLocal() as session:

        total = session.query(
            func.sum(Recebimento.valor)
        ).filter(
            func.date(Recebimento.data_hora) == hoje
        ).scalar() or 0

        fellipe = session.query(
            func.sum(Recebimento.valor)
        ).join(Usuario).filter(
            Usuario.nome == "Fellipe",
            func.date(Recebimento.data_hora) == hoje
        ).scalar() or 0

        tuany = session.query(
            func.sum(Recebimento.valor)
        ).join(Usuario).filter(
            Usuario.nome == "Tuany",
            func.date(Recebimento.data_hora) == hoje
        ).scalar() or 0

        return {
            "total": float(total),
            "fellipe": float(fellipe),
            "tuany": float(tuany)
        }