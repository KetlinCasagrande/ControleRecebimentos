from pathlib import Path
from datetime import datetime
import shutil
import sys


# ==========================================================
# DIRETÓRIO DA APLICAÇÃO
# ==========================================================

if getattr(sys, "frozen", False):

    # Quando estiver rodando como .exe
    BASE_DIR = Path(sys.executable).resolve().parent

else:

    # Quando estiver rodando pelo Python
    BASE_DIR = Path(__file__).resolve().parent.parent


# ==========================================================
# BANCO
# ==========================================================

BANCO = BASE_DIR / "data" / "meu_caixa.db"


# ==========================================================
# PASTA DE BACKUPS
# ==========================================================

PASTA_BACKUP = BASE_DIR / "backups"

PASTA_BACKUP.mkdir(
    exist_ok=True
)


# ==========================================================
# CRIAR BACKUP
# ==========================================================

def criar_backup():

    if not BANCO.exists():
        return None

    data_hora = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    nome_backup = (
        f"backup_{data_hora}.db"
    )

    destino = PASTA_BACKUP / nome_backup

    shutil.copy2(
        BANCO,
        destino
    )

    return destino