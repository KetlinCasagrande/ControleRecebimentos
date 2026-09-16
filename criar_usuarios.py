from database import SessionLocal, criar_banco
from models import Usuario


def criar_usuarios():

    criar_banco()

    with SessionLocal() as session:

        usuarios = [
            Usuario(
                nome="Fellipe",
                login="fellipe",
                senha="1234"
            ),
            Usuario(
                nome="Tuany",
                login="tuany",
                senha="1234"
            )
        ]

        for usuario in usuarios:

            existente = session.query(Usuario).filter_by(
                login=usuario.login
            ).first()

            if not existente:
                session.add(usuario)

        session.commit()

    print("Usuários criados com sucesso!")


if __name__ == "__main__":
    criar_usuarios()