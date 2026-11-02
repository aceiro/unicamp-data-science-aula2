
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)

email = input("E-mail: ")
password = input("Senha: ")

try:
    auth = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

    print("Autenticação realizada com sucesso!")

    response = (
        supabase.table("clientes")
        .select("*")
        .limit(5)
        .execute()
    )

    print("Clientes encontrados:", response.data)

except Exception as e:
    print("Erro na autenticação ou consulta:", e)