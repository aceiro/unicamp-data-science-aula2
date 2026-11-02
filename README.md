# TechFix Informática — Sistema de Ordens de Serviço

Projeto desenvolvido para a Atividade da Aula 2 da disciplina de Data Science — Unicamp.

## Objetivo

Desenvolver um sistema web de gerenciamento de ordens de serviço para uma loja fictícia de informática, integrando duas aplicações Python a um banco de dados PostgreSQL na nuvem.

## Tecnologias

- **Python:** linguagem de programação.
- **Gradio:** interface web para cadastro de clientes e ordens de serviço.
- **Streamlit:** painel administrativo para gerenciamento das ordens.
- **Supabase / PostgreSQL:** armazenamento e gerenciamento dos dados.
- **Pandas:** processamento, filtragem e exportação dos registros.

## Funcionalidades

### Aplicação Gradio
- Cadastro de clientes e equipamentos.
- Validação de e-mail, celular e campos obrigatórios.
- Reutilização de clientes previamente cadastrados.
- Geração automática de ordens com status inicial `Aberto`.
- Interface acessível por computador e celular.

### Painel Streamlit
- Consulta e filtragem das ordens de serviço.
- Cadastro manual de novas ordens.
- Atualização do status e dos dados dos clientes.
- Exclusão de ordens e clientes com confirmação.
- Indicadores de acompanhamento por status.
- Exportação dos dados filtrados em CSV.

## Banco de dados

O banco possui duas tabelas principais:

- `clientes`: informações cadastrais.
- `ordens_servico`: equipamentos, problemas relatados e acompanhamento dos atendimentos.

O relacionamento é de um para muitos (1:N), permitindo que um cliente possua várias ordens de serviço.

## Instalação

Crie e ative um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Crie o arquivo `.env` a partir de `.env.example` e configure as credenciais do Supabase e dos usuários de teste.

Execute o script `sql/schema.sql` no SQL Editor do Supabase e configure as permissões e políticas RLS necessárias.

## Execução

Aplicação de cadastro:

```bash
python app_gradio.py
```

Painel administrativo:

```bash
streamlit run app_streamlit.py
```

## Segurança

- Credenciais armazenadas em variáveis de ambiente.
- Arquivo `.env` excluído do versionamento.
- Políticas RLS habilitadas no Supabase.
- Validação dos dados de entrada.
- Tratamento de exceções.
- Utilização de dados fictícios para testes.

**Observação:** o projeto é um protótipo acadêmico. As aplicações e as políticas de acesso precisam de controles adicionais antes de qualquer utilização em produção.

## Evidências

A pasta `evidencias/` contém capturas das interfaces, registros no Supabase e funcionalidades implementadas.

## Autor

Erik Aceiro  
Disciplina de Data Science — Unicamp  
2026