
import os
import re
import gradio as gr
import logging

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Configuração do Supabase
URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_KEY"]


def cadastrar(nome, endereco, email, celular, modelo, problema):
    """Cadastra um cliente e abre uma ordem de serviço."""

    nome = nome.strip()
    endereco = endereco.strip()
    email = email.strip().lower()
    celular = celular.strip()
    modelo = modelo.strip()
    problema = problema.strip()

    # Validação dos campos obrigatórios
    if not all([nome, endereco, email, celular, modelo, problema]):
        return "❌ Preencha todos os campos."

    # Validação do e-mail
    if not re.fullmatch(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        email
    ):
        return "❌ E-mail inválido."

    # Validação do celular
    if not re.fullmatch(r"[0-9]{10,13}", celular):
        return "❌ O celular deve conter de 10 a 13 dígitos."

    try:
        # Cliente independente para esta operação
        db = create_client(URL, KEY)

        # Login do atendente usando credenciais locais
        db.auth.sign_in_with_password({
            "email": os.environ["TECHFIX_USER_EMAIL"],
            "password": os.environ["TECHFIX_USER_PASSWORD"]
        })

        # Verifica se o cliente já existe
        resultado = (
            db.table("clientes")
            .select("id")
            .eq("email", email)
            .limit(1)
            .execute()
        )

        if resultado.data:
            cliente_id = resultado.data[0]["id"]
        else:
            novo_cliente = (
                db.table("clientes")
                .insert({
                    "nome": nome,
                    "endereco": endereco,
                    "email": email,
                    "celular_whatsapp": celular
                })
                .execute()
            )

            cliente_id = novo_cliente.data[0]["id"]

        # Cria a ordem de serviço
        nova_os = (
            db.table("ordens_servico")
            .insert({
                "cliente_id": cliente_id,
                "modelo_computador": modelo,
                "problema_relatado": problema,
                "status": "Aberto"
            })
            .execute()
        )

        os_id = nova_os.data[0]["id"]

        return f"✅ Ordem de Serviço #{os_id} cadastrada com sucesso!"

    except Exception as e:
        logging.exception("Erro ao cadastrar ordem de serviço")
        return "❌ Erro ao cadastrar. Consulte o terminal para detalhes."    

# Interface Gradio
with gr.Blocks(title="TechFix Informática") as demo:

    gr.Markdown("# TechFix Informática")
    gr.Markdown(
        "### Cadastro de Ordens de Serviço\n"
        "Preencha os dados abaixo para registrar um atendimento."
    )

    with gr.Row():
        with gr.Column():
            nome = gr.Textbox(
                label="Nome do Cliente",
                placeholder="Nome completo"
            )

            endereco = gr.Textbox(
                label="Endereço",
                placeholder="Rua, número, bairro e cidade"
            )

            email = gr.Textbox(
                label="E-mail",
                placeholder="cliente@exemplo.com"
            )

            celular = gr.Textbox(
                label="Celular / WhatsApp",
                placeholder="11999999999"
            )

        with gr.Column():
            modelo = gr.Textbox(
                label="Modelo do Computador",
                placeholder="Ex.: Dell Inspiron 15"
            )

            problema = gr.Textbox(
                label="Problema Apresentado",
                placeholder="Descreva o problema relatado",
                lines=6
            )

    with gr.Row():
        cadastrar_btn = gr.Button(
            "Cadastrar",
            variant="primary"
        )

        limpar_btn = gr.Button("Limpar")

    mensagem = gr.Textbox(
        label="Resultado do Cadastro",
        interactive=False
    )

    campos = [nome, endereco, email, celular, modelo, problema]

    cadastrar_btn.click(
        fn=cadastrar,
        inputs=campos,
        outputs=mensagem
    )

    limpar_btn.click(
        fn=lambda: [""] * 7,
        inputs=[],
        outputs=campos + [mensagem]
    )


if __name__ == "__main__":
    demo.launch(
    share=True,
    auth=(
            os.environ["GRADIO_USER"],
            os.environ["GRADIO_PASSWORD"]
        )
    )
