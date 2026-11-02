import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_KEY"]

print(url)
print(key)

try:
    supabase = create_client(url, key)
    response = supabase.table("clientes").select("id").limit(1).execute()
    print("Conexão com Supabase realizada com sucesso!")
    print(response.data)
except Exception as e:
    print(f"Erro ao acessar o Supabase: {e}")
