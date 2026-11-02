
import os
import pandas as pd
import streamlit as st
import re
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

st.set_page_config(
    page_title="TechFix | Administração",
    page_icon="🛠️",
    layout="wide"
)

st.title("🛠️ TechFix Informática")
st.caption("Painel Administrativo de Ordens de Serviço")

STATUS = [
    "Aberto",
    "Em análise",
    "Aguardando peça",
    "Concluído",
    "Entregue"
]


def conectar():
    db = create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_KEY"]
    )

    db.auth.sign_in_with_password({
        "email": os.environ["TECHFIX_USER_EMAIL"],
        "password": os.environ["TECHFIX_USER_PASSWORD"]
    })

    return db


def carregar_ordens(db):
    resposta = (
        db.table("ordens_servico")
        .select(
            "id, modelo_computador, problema_relatado, "
            "status, data_abertura, "
            "clientes(nome, email, celular_whatsapp)"
        )
        .order("id", desc=True)
        .execute()
    )

    registros = []

    for ordem in resposta.data:
        cliente = ordem.get("clientes") or {}

        registros.append({
            "OS": ordem["id"],
            "Cliente": cliente.get("nome", ""),
            "E-mail": cliente.get("email", ""),
            "WhatsApp": cliente.get("celular_whatsapp", ""),
            "Equipamento": ordem["modelo_computador"],
            "Problema": ordem["problema_relatado"],
            "Status": ordem["status"],
            "Abertura": ordem["data_abertura"]
        })

    return pd.DataFrame(registros)


def renderizar_aba_cadastrar(db):
    """Renderiza o formulário de cadastro de ordens de serviço."""

    st.subheader("Cadastrar Ordem de Serviço")

    with st.form("form_cadastro", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            nome = st.text_input("Nome do Cliente")
            endereco = st.text_input("Endereço")
            email = st.text_input("E-mail")
            celular = st.text_input("Celular / WhatsApp")

        with col2:
            modelo = st.text_input("Modelo do Computador")
            problema = st.text_area("Problema Apresentado")

        enviar = st.form_submit_button(
            "Cadastrar Ordem de Serviço",
            type="primary"
        )

    if enviar:
        try:
            os_id = cadastrar_os(
                db, nome, endereco, email,
                celular, modelo, problema
            )

            st.success(
                f"Ordem de Serviço #{os_id} cadastrada com sucesso!"
            )

            st.info(
                "Atualize a página para visualizar a nova OS."
            )

        except ValueError as e:
            st.warning(str(e))

        except Exception:
            st.error(
                "Não foi possível cadastrar a ordem. "
                "Verifique os dados e as permissões."
            )


def atualizar_status_os(db, os_id, novo_status):
    """Atualiza o status de uma ordem de serviço."""

    if novo_status not in STATUS:
        raise ValueError("Status inválido.")

    resposta = (
        db.table("ordens_servico")
        .update({"status": novo_status})
        .eq("id", os_id)
        .execute()
    )

    if not resposta.data:
        raise ValueError("Ordem de serviço não encontrada.")

    return resposta.data[0]



def renderizar_aba_editar_excluir(db, df):
    """Gerencia status, dados do cliente e exclusões."""

    st.subheader("Gerenciar Ordens de Serviço")

    if df.empty:
        st.info("Nenhuma ordem de serviço encontrada.")
        return

    os_id = st.selectbox(
        "Selecione uma Ordem de Serviço",
        options=df["OS"].tolist(),
        format_func=lambda x: f"OS #{x}"
    )

    ordem = df[df["OS"] == os_id].iloc[0]

    # Recuperar o ID do cliente vinculado à OS
    resposta = (
        db.table("ordens_servico")
        .select("cliente_id")
        .eq("id", int(os_id))
        .single()
        .execute()
    )

    cliente_id = resposta.data["cliente_id"]

    st.write(f"**Cliente:** {ordem['Cliente']}")
    st.write(f"**Equipamento:** {ordem['Equipamento']}")

    aba_status, aba_cliente, aba_exclusao = st.tabs([
        "Alterar Status",
        "Editar Cliente",
        "Excluir"
    ])

    with aba_status:
        status_atual = ordem["Status"]

        novo_status = st.selectbox(
            "Status da OS",
            options=STATUS,
            index=STATUS.index(status_atual)
        )

        if st.button("Salvar Status", type="primary"):
            try:
                atualizar_status_os(db, os_id, novo_status)
                st.success("Status atualizado!")
                st.rerun()

            except Exception:
                st.error("Não foi possível atualizar o status.")

    with aba_cliente:
        renderizar_edicao_cliente(db, cliente_id)

    with aba_exclusao:
        renderizar_exclusao(db, os_id, cliente_id)


def atualizar_cliente(db, cliente_id, endereco, email, celular):
    """Atualiza os dados de um cliente."""

    email = email.strip().lower()
    endereco = endereco.strip()
    celular = celular.strip()

    if not endereco:
        raise ValueError("O endereço é obrigatório.")

    if not re.fullmatch(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        email
    ):
        raise ValueError("E-mail inválido.")

    if not re.fullmatch(r"[0-9]{10,13}", celular):
        raise ValueError("Celular deve conter de 10 a 13 dígitos.")

    resposta = (
        db.table("clientes")
        .update({
            "endereco": endereco,
            "email": email,
            "celular_whatsapp": celular
        })
        .eq("id", cliente_id)
        .execute()
    )

    if not resposta.data:
        raise ValueError("Cliente não encontrado.")

    return resposta.data[0]


def excluir_os(db, os_id):
    """Exclui uma ordem de serviço."""

    resposta = (
        db.table("ordens_servico")
        .delete()
        .eq("id", os_id)
        .execute()
    )

    if not resposta.data:
        raise ValueError("Ordem de serviço não encontrada.")


def excluir_cliente(db, cliente_id):
    """Exclui um cliente e suas ordens vinculadas."""

    resposta = (
        db.table("clientes")
        .delete()
        .eq("id", cliente_id)
        .execute()
    )

    if not resposta.data:
        raise ValueError("Cliente não encontrado.")


def renderizar_edicao_cliente(db, cliente_id):
    """Renderiza o formulário de edição do cliente."""

    try:
        resultado = (
            db.table("clientes")
            .select("*")
            .eq("id", cliente_id)
            .single()
            .execute()
        )

        cliente = resultado.data

    except Exception:
        st.error("Não foi possível carregar os dados do cliente.")
        return

    with st.form(f"editar_cliente_{cliente_id}"):
        st.write(f"**Cliente:** {cliente['nome']}")

        endereco = st.text_input(
            "Endereço",
            value=cliente["endereco"]
        )

        email = st.text_input(
            "E-mail",
            value=cliente["email"]
        )

        celular = st.text_input(
            "Celular / WhatsApp",
            value=cliente["celular_whatsapp"]
        )

        salvar = st.form_submit_button(
            "Salvar dados do cliente",
            type="primary"
        )

    if salvar:
        try:
            atualizar_cliente(
                db, cliente_id, endereco, email, celular
            )
            st.success("Cliente atualizado com sucesso!")
            st.rerun()

        except ValueError as e:
            st.warning(str(e))

        except Exception:
            st.error("Não foi possível atualizar o cliente.")


def renderizar_exclusao(db, os_id, cliente_id):
    """Renderiza exclusões com confirmação explícita."""

    st.warning(
        "A exclusão é permanente. Excluir um cliente "
        "também remove todas as suas ordens de serviço."
    )

    tipo = st.radio(
        "O que deseja excluir?",
        ["Ordem de Serviço", "Cliente"],
        key="tipo_exclusao"
    )

    confirmar = st.checkbox(
        "Confirmo que desejo excluir permanentemente "
        "o registro selecionado.",
        value=False,
        key=f"confirmar_{tipo}_{os_id}_{cliente_id}"
    )

    if st.button(
        "Excluir registro",
        disabled=not confirmar,
        type="primary"
    ):
        try:
            if tipo == "Ordem de Serviço":
                excluir_os(db, os_id)
            else:
                excluir_cliente(db, cliente_id)

            st.success("Registro excluído com sucesso!")
            st.rerun()

        except Exception:
            st.error("Não foi possível excluir o registro.")


def cadastrar_os(db, nome, endereco, email, celular, modelo, problema):
    """Cadastra uma OS, reutilizando o cliente pelo e-mail."""

    import re

    nome = nome.strip()
    endereco = endereco.strip()
    email = email.strip().lower()
    celular = celular.strip()
    modelo = modelo.strip()
    problema = problema.strip()

    if not all([nome, endereco, email, celular, modelo, problema]):
        raise ValueError("Preencha todos os campos.")

    if not re.fullmatch(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        email
    ):
        raise ValueError("E-mail inválido.")

    if not re.fullmatch(r"[0-9]{10,13}", celular):
        raise ValueError("Celular deve conter de 10 a 13 dígitos.")

    # Procurar cliente existente
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
        cliente = (
            db.table("clientes")
            .insert({
                "nome": nome,
                "endereco": endereco,
                "email": email,
                "celular_whatsapp": celular
            })
            .execute()
        )
        cliente_id = cliente.data[0]["id"]

    # Criar ordem de serviço
    resposta = (
        db.table("ordens_servico")
        .insert({
            "cliente_id": cliente_id,
            "modelo_computador": modelo,
            "problema_relatado": problema,
            "status": "Aberto"
        })
        .execute()
    )

    return resposta.data[0]["id"]


def renderizar_aba_indicadores(df):
    """Exibe métricas e gráfico das ordens de serviço."""

    st.subheader("Indicadores de Ordens de Serviço")

    if df.empty:
        st.info("Nenhuma ordem de serviço encontrada.")
        return

    # Total de ordens por status
    contagem = (
        df["Status"]
        .value_counts()
        .reindex(STATUS, fill_value=0)
    )

    # Indicador geral
    st.metric("Total de Ordens", len(df))

    # Indicadores individuais
    colunas = st.columns(5)

    for coluna, status in zip(colunas, STATUS):
        with coluna:
            st.metric(
                label=status,
                value=int(contagem[status])
            )

    st.divider()

    # Gráfico de barras
    st.subheader("Distribuição das Ordens por Status")

    grafico = pd.DataFrame({
        "Status": STATUS,
        "Quantidade": contagem.values
    }).set_index("Status")

    st.bar_chart(
        grafico,
        y="Quantidade",
        x_label="Status da OS",
        y_label="Quantidade de Ordens"
    )

    # Indicador complementar
    concluidas = int(
        contagem["Concluído"] + contagem["Entregue"]
    )

    taxa_conclusao = (concluidas / len(df)) * 100

    st.metric(
        "Taxa de Conclusão",
        f"{taxa_conclusao:.1f}%"
    )


try:
    db = conectar()
    df = carregar_ordens(db)

    st.sidebar.header("Filtros")

    busca_nome = st.sidebar.text_input("Nome do cliente")
    busca_email = st.sidebar.text_input("E-mail")

    filtro_status = st.sidebar.selectbox(
        "Status",
        ["Todos"] + STATUS
    )

    if not df.empty:
        if busca_nome:
            df = df[
                df["Cliente"].str.contains(
                    busca_nome, case=False, na=False, regex=False
                )
            ]

        if busca_email:
            df = df[
                df["E-mail"].str.contains(
                    busca_email, case=False, na=False, regex=False
                )
            ]

        if filtro_status != "Todos":
            df = df[df["Status"] == filtro_status]

    aba_consultar, aba_cadastrar, aba_editar, aba_indicadores = st.tabs([
        "Consultar",
        "Cadastrar",
        "Editar / Excluir",
        "Indicadores"
    ])

    with aba_consultar:
        st.subheader("Ordens de Serviço")
        st.metric("Ordens encontradas", len(df))

        if df.empty:
            st.info("Nenhuma ordem encontrada.")
        else:
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            st.download_button(
                "Exportar CSV",
                data=df.to_csv(index=False).encode("utf-8-sig"),
                file_name="ordens_servico.csv",
                mime="text/csv"
            )

    with aba_cadastrar:
        # st.info("Cadastro será implementado na próxima etapa.")
        renderizar_aba_cadastrar(db)

    with aba_editar:
        # st.info("Edição e exclusão serão implementadas na próxima etapa.")
        renderizar_aba_editar_excluir(db, df)

    with aba_indicadores:
        # st.info("Indicadores serão implementados na próxima etapa.")
        renderizar_aba_indicadores(df)
        
except Exception as e:
    st.error("Erro ao carregar o painel administrativo.")
    st.exception(e)
