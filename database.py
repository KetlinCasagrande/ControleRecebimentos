from pathlib import Path
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


# ==========================================================
# DIRETÓRIO DA APLICAÇÃO
# ==========================================================

if getattr(sys, "frozen", False):
    # Quando estiver rodando como .exe
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    # Quando estiver rodando pelo Python
    BASE_DIR = Path(__file__).resolve().parent


# ==========================================================
# PASTA DO BANCO
# ==========================================================

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)


# ==========================================================
# ARQUIVO DO BANCO
# ==========================================================

DATABASE_FILE = DATA_DIR / "meu_caixa.db"


# ==========================================================
# CONEXÃO SQLITE
# ==========================================================

DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

engine = create_engine(
    DATABASE_URL,
    echo=False
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


# ==========================================================
# BASE
# ==========================================================

class Base(DeclarativeBase):
    pass


# ==========================================================
# CRIAR BANCO
# ==========================================================

def criar_banco():

    from models import Usuario, Recebimento

    Base.metadata.create_all(engine)

    with SessionLocal() as session:

        usuarios_padrao = [
            {
                "nome": "Fellipe",
                "login": "fellipe",
                "senha": "1234",
            },
            {
                "nome": "Tuany",
                "login": "tuany",
                "senha": "1234",
            },
        ]

        for dados in usuarios_padrao:

            usuario = (
                session.query(Usuario)
                .filter_by(
                    login=dados["login"]
                )
                .first()
            )

            if not usuario:

                session.add(
                    Usuario(
                        nome=dados["nome"],
                        login=dados["login"],
                        senha=dados["senha"],
                    )
                )

        session.commit()