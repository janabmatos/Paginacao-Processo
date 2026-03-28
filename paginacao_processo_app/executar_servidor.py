import os

def iniciar_servidor():
    # Comando para rodar o servidor Django
    os.system("python manage.py runserver")

if __name__ == "__main__":
    print("Iniciando o servidor Django...")
    iniciar_servidor()