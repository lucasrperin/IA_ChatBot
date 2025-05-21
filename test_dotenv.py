from dotenv import dotenv_values

# Tente carregar as variáveis manualmente
config = dotenv_values(".env")  # Carrega manualmente as variáveis do .env

print(config)
