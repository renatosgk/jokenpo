-- 1. Criar Tabela de Jogadores se não existir
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tb_jogadores' AND xtype='U')
BEGIN
    CREATE TABLE tb_jogadores (
        id_jogador INT IDENTITY(1,1) PRIMARY KEY,
        nome_jogador VARCHAR(50) NOT NULL DEFAULT 'Jogador Anonimo',
        dt_criacao DATETIME DEFAULT (SYSDATETIMEOFFSET() AT TIME ZONE 'E. South America Standard Time')
    );
END;

-- 2. Criar Tabela de Partidas se não existir (com a chave estrangeira)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tb_partidas' AND xtype='U')
BEGIN
    CREATE TABLE tb_partidas (
        id_partida INT IDENTITY(1,1) PRIMARY KEY,
        id_jogador INT NOT NULL,
        escolha_jogador VARCHAR(10) NOT NULL CHECK (escolha_jogador IN ('pedra', 'papel', 'tesoura')),
        escolha_computador VARCHAR(10) NOT NULL CHECK (escolha_computador IN ('pedra', 'papel', 'tesoura')),
        resultado VARCHAR(15) NOT NULL CHECK (resultado IN ('Você', 'Computador', 'Empate')),
        dt_partida DATETIME DEFAULT (SYSDATETIMEOFFSET() AT TIME ZONE 'E. South America Standard Time'),
        CONSTRAINT FK_partidas_jogadores FOREIGN KEY (id_jogador) REFERENCES tb_jogadores(id_jogador) ON DELETE CASCADE
    );
END;

-- 3. Inserir dados de teste exemplo
IF NOT EXISTS (SELECT * FROM tb_jogadores WHERE nome_jogador = 'Jogador Teste')
BEGIN
    INSERT INTO tb_jogadores (nome_jogador) VALUES ('Jogador Teste');
END;

DECLARE @IdJogadorTeste INT;
SELECT @IdJogadorTeste = id_jogador FROM tb_jogadores WHERE nome_jogador = 'Jogador Teste';

-- Insere as partidas de teste vinculadas ao ID do Jogador Teste
INSERT INTO tb_partidas (id_jogador, escolha_jogador, escolha_computador, resultado) VALUES
(@IdJogadorTeste, 'pedra', 'tesoura', 'Você'),
(@IdJogadorTeste, 'papel', 'papel', 'Empate'),
(@IdJogadorTeste, 'tesoura', 'pedra', 'Computador'),
(@IdJogadorTeste, 'pedra', 'papel', 'Computador'),
(@IdJogadorTeste, 'papel', 'pedra', 'Você');
