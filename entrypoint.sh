#!/bin/sh

# Função para verificar se o banco de dados está pronto
wait_for_db() {
  echo "Aguardando o banco de dados em fastzero_database:5432..."
  while ! nc -z fastzero_database 5432; do
    sleep 0.5
  done
  echo "Banco de dados pronto!"
}

# Chama a função para aguardar o banco de dados
wait_for_db

# Executa as migrações do banco de dados
echo "Executando migrações do Alembic..."
uv run alembic upgrade head
echo "Migrações concluídas!"

# Inicia a aplicação
echo "Iniciando a aplicação FastAPI..."
uv run uvicorn src.app:app --host 0.0.0.0 --port 8080