"""Crea un usuario manualmente (no hay registro público en este sistema).

Uso:
    python create_user.py "Nombre Apellido" correo@empresa.com
"""

import getpass
import sys

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User


def main() -> None:
    if len(sys.argv) != 3:
        print("Uso: python create_user.py \"Nombre Apellido\" correo@empresa.com")
        sys.exit(1)

    name, email = sys.argv[1], sys.argv[2]
    password = getpass.getpass("Contraseña: ")
    password_confirm = getpass.getpass("Confirmar contraseña: ")
    if password != password_confirm:
        print("Las contraseñas no coinciden.")
        sys.exit(1)

    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == email).first():
            print(f"Ya existe un usuario con el correo {email}.")
            sys.exit(1)
        user = User(name=name, email=email, password_hash=hash_password(password))
        db.add(user)
        db.commit()
        print(f"Usuario creado: {email} (id={user.id})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
