# python3 -m venv .venv && source .venv/bin/activate

from app_agent import app_agent_main


def main(num_exemplo: int):
    print("\nTeste Assistente Multi-função\n")
    if num_exemplo == 2:
        app_agent_main()
    else:
        print("Exemplo não encontrado")


if __name__ == "__main__":
    main(2) # -> OK
