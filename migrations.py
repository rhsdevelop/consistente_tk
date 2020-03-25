def data_update(conn, c):
    # USUÁRIOS
    command = '''CREATE TABLE IF NOT EXISTS usuarios(
    id                      INTEGER PRIMARY KEY AUTOINCREMENT, 
    nome                    VARCHAR(50) NOT NULL, 
    senha                   VARCHAR(50) NOT NULL, 
    observacao              VARCHAR(200) NOT NULL)'''
    c.execute(command)

    # BANCOS
    command= '''CREATE TABLE IF NOT EXISTS bancos(
    id                      INTEGER      PRIMARY KEY AUTOINCREMENT, 
    datacadastro            VARCHAR(10) NOT NULL, 
    nomebanco               VARCHAR(50) NOT NULL, 
    tipomov                 INTEGER NOT NULL, 
    numero                  VARCHAR(19), 
    diavenc                 INTEGER, 
    gerafatura              INTEGER, 
    agencia                 VARCHAR(10), 
    conta                   VARCHAR(12), 
    tipoconta               INTEGER,
    usuario                 INTEGER,
    FOREIGN KEY(usuario)    REFERENCES usuarios(id))'''
    c.execute(command)
    # TipoMov               0 Dinheiro em mãos  1 Conta bancária  2 Cartão de Crédito  3 Pré pago
    # Numero                numero do cartão de crédito
    # DiaVenc               pra cartão de crédito (inteiro de 1 a 30)
    # GeraFatura            0 Não e 1 Sim 
    # Agencia               pra conta bancária
    # Conta                 pra conta bancária
    # TipoConta             pra conta bancária: 0 Conta Corrente  1 Poupança  2 CDB/Outras'''

    # CATEGORIAS
    command = '''CREATE TABLE IF NOT EXISTS categorias(
    id                      INTEGER PRIMARY KEY AUTOINCREMENT, 
    categoria               VARCHAR(50) NOT NULL, 
    tipomov                 INTEGER NOT NULL, 
    classifica              INTEGER NOT NULL,
    usuario                 INTEGER,
    FOREIGN KEY(usuario)    REFERENCES usuarios(id))'''
    c.execute(command)
    # TipoMov               0 para Receita e 1 para Despesa
    # Repete                0 para False e 1 para True

    # PARCEIROS
    command = '''CREATE TABLE IF NOT EXISTS parceiros(
    id                      INTEGER PRIMARY KEY AUTOINCREMENT, 
    datacadastro            VARCHAR(10) NOT NULL, 
    nome                    VARCHAR(30) NOT NULL, 
    nomecompleto            VARCHAR(100) NOT NULL, 
    tipo                    INTEGER NOT NULL, 
    doc                     VARCHAR(30), 
    endereco                VARCHAR(100), 
    telefone                VARCHAR(20), 
    observacao              VARCHAR(200), 
    modo                    INTEGER,
    usuario                 INTEGER,
    FOREIGN KEY(usuario)    REFERENCES usuarios(id))'''
    c.execute(command)
    # Tipo INTEGER NOT NULL, ') # 0 para Pessoa Física e 1 para Pessoa Jurídica
    # Modo INTEGER') # 0 Ambos     1 Cliente      2 Fornecedor

    # MOVIMENTO BANCÁRIO
    command = '''CREATE TABLE IF NOT EXISTS diario(
    id                      INTEGER PRIMARY KEY AUTOINCREMENT, 
    datafirstupdate         VARCHAR(10), 
    datalastupdate          VARCHAR(10), 
    datadoc                 VARCHAR(10), 
    datavenc                VARCHAR(10), 
    datapago                VARCHAR(10), 
    parceiro                INTEGER NOT NULL, 
    banco                   INTEGER NOT NULL, 
    fatura                  VARCHAR(20), 
    descricao               VARCHAR(100) NOT NULL, 
    valor                   REAL NOT NULL, 
    tipomov                 INTEGER NOT NULL, 
    categoriamov            INTEGER NOT NULL, 
    usuario                 INTEGER,
    FOREIGN KEY(usuario)    REFERENCES usuarios(id))'''
    c.execute(command)
    # Fatura VARCHAR(20), ') # Se o pagamento for cartão de crédito, ano/mes. Sugere e usuario pode mudar
    # TipoMov INTEGER NOT NULL, ') # 0 para Receita e 1 para Despesa 3 Transf Ent 4 Transf Sai
    # CategoriaMov VARCHAR(10) NOT NULL') # Categoria de Receita ou Despesa

    # INTEGRAÇÃO GOOGLE DRIVE
    command = '''CREATE TABLE IF NOT EXISTS drive(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    arquivo VARCHAR(30) NOT NULL,
    idgoogle VARCHAR(100) NOT NULL)'''
    c.execute(command)

def initial_values(conn, c):
    command = 'INSERT INTO usuarios (nome, senha, observacao) VALUES ("Renan", "1234", "Proprietario")'
    #command = '''INSERT INTO bancos (datacadastro, nomebanco, tipomov, numero, gerafatura, agencia, conta, tipoconta, usuario) 
    #VALUES ("2019-01-03", "Inter", 1, "", 1, "0001", "705797-5", 0, 1)'''
    c.execute(command)
    conn.commit()

if __name__ == '__main__':
    import sqlite3
    from config import *
    conn = sqlite3.connect(SQLITE_DB)
    c = conn.cursor()
    data_update(conn, c)
    initial_values(conn, c)
