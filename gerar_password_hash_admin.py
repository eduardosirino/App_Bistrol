from werkzeug.security import generate_password_hash

def main():
    password = input("Digite a senha que deseja hashar: ")
    password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    print("\nSenha hashada:")
    print(password_hash)

if __name__ == "__main__":
    main()
