
-- Tabela de clientes
CREATE TABLE public.clientes (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome TEXT NOT NULL,
    endereco TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    celular_whatsapp TEXT NOT NULL,
    data_cadastro TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Validação do e-mail
    CONSTRAINT email_valido CHECK (
        email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    ),

    -- Celular com 10 a 13 dígitos
    CONSTRAINT celular_valido CHECK (
        celular_whatsapp ~ '^[0-9]{10,13}$'
    )
);

-- Tabela de ordens de serviço
CREATE TABLE public.ordens_servico (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cliente_id BIGINT NOT NULL,
    modelo_computador TEXT NOT NULL,
    problema_relatado TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Aberto',
    data_abertura TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    data_atualizacao TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Relacionamento com clientes
    CONSTRAINT fk_cliente FOREIGN KEY (cliente_id)
        REFERENCES public.clientes(id)
        ON DELETE CASCADE,

    -- Status permitidos
    CONSTRAINT status_valido CHECK (
        status IN (
            'Aberto',
            'Em análise',
            'Aguardando peça',
            'Concluído',
            'Entregue'
        )
    )
);

-- Índices para otimizar consultas
CREATE INDEX idx_os_cliente
    ON public.ordens_servico(cliente_id);

CREATE INDEX idx_os_status
    ON public.ordens_servico(status);

-- Atualização automática da data de modificação
CREATE OR REPLACE FUNCTION public.atualizar_data_os()
RETURNS TRIGGER AS $$
BEGIN
    NEW.data_atualizacao = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_atualizar_data_os
BEFORE UPDATE ON public.ordens_servico
FOR EACH ROW
EXECUTE FUNCTION public.atualizar_data_os();

-- Habilitar Row Level Security
ALTER TABLE public.clientes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ordens_servico ENABLE ROW LEVEL SECURITY;


