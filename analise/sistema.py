from entidades.interacao import Interacao
from entidades.plataforma import Plataforma
from entidades.usuario import Usuario
from entidades.conteudo import Conteudo
from database.datahandler import MySQLHandler

class SistemaAnaliseEngajamento:
    """
    Classe que representa o sistema de análise de engajamento de conteúdos.
    Atributos:
        - VERSAO_ANALISE (str): Versão do sistema de análise.
        - __plataformas_registradas (dict): Dicionário que armazena as plataformas registradas.
        - __conteudos_registrados (dict): Dicionário que armazena os conteúdos registrados.
        - __usuarios_registrados (dict): Dicionário que armazena os usuários registrados.
        - __proximo_id_plataforma (int): Próximo ID a ser atribuído a uma plataforma.
    Métodos:
        - __init__: Inicializa o sistema com dicionários vazios e um ID inicial para plataformas.
        - cadastrar_plataforma: Cadastra uma nova plataforma ou retorna a existente.
        - obter_plataforma: Obtém uma plataforma pelo nome.
        - listar_plataformas: Lista todas as plataformas registradas.
        - _carregar_interacoes_csv: Carrega interações de um arquivo CSV.
        - processar_interacoes_do_csv: Processa interações do CSV e registra usuários, conteúdos e interações.
        - gerar_relatorio_engajamento_conteudos: Gera um relatório de engajamento dos conteúdos.
        - gerar_relatorio_atividade_usuarios: Gera um relatório de atividade dos usuários.
        - identificar_top_conteudos: Identifica os top conteúdos com base em uma métrica específica.
    """
    VERSAO_ANALISE = "2.0"

    def __init__(self, host, port, database, user, password):
        self.__plataformas_registradas = {}
        self.__conteudos_registrados = {}
        self.__usuarios_registrados = {}
        self.__proximo_id_plataforma = 1
        self.db = MySQLHandler(host, port, database, user, password)
        self.db.connect()

    def cadastrar_plataforma(self, nome_plataforma):
        if nome_plataforma in self.__plataformas_registradas:
            return self.__plataformas_registradas[nome_plataforma]
        plataforma = Plataforma(nome_plataforma, id_plataforma=self.__proximo_id_plataforma)
        self.__plataformas_registradas[nome_plataforma] = plataforma
        self.__proximo_id_plataforma += 1
        return plataforma
    
    def cadastrar_plataforma_bd(self, nome_plataforma):
        query = "SELECT * FROM plataforma WHERE nome_plataforma = %s"
        result = self.db.fetch_one(query, (nome_plataforma,))
        if result:
            return result
        else:
            data = {'nome_plataforma': nome_plataforma}
            self.db.insert('plataforma', data)
            return self.db.fetch_one(query, (nome_plataforma,))


    def obter_plataforma(self, nome_plataforma):
        return self.__plataformas_registradas.get(nome_plataforma)

    def listar_plataformas(self):
        return list(self.__plataformas_registradas.values())
    
    def _carregar_interacoes_csv(self, caminho_arquivo):
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                linhas = arquivo.readlines()
                dados_brutos = [linha.strip().split(',') for linha in linhas]
                return dados_brutos
        except FileNotFoundError:
            print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
            return []
    
    def processar_interacoes_do_csv(self, caminho_arquivo):
        dados_brutos = self._carregar_interacoes_csv(caminho_arquivo)
        cabecalho = ['id_conteudo', 'nome_conteudo', 'id_usuario', 'timestamp_interacao', 'nome_plataforma', 'tipo_interacao', 'watch_duration_seconds', 'comment_text']
        for linha in dados_brutos[1:]:  # Ignora o cabeçalho
            try:
                dados = dict(zip(cabecalho, linha))
                usuario_id = int(dados['id_usuario'])
                timestamp_interacao = dados['timestamp_interacao']
                tipo_interacao = dados['tipo_interacao']
                try:
                    watch_duration_seconds = int(dados['watch_duration_seconds']) if dados['watch_duration_seconds'] else 0
                except ValueError:
                    watch_duration_seconds = 0
                    print(f"Erro ao converter watch_duration_seconds para inteiro na linha: {linha}")
                comment_text = dados['comment_text']
                nome_plataforma = dados['nome_plataforma']
                nome_conteudo = dados['nome_conteudo']
                plataforma = self.cadastrar_plataforma(nome_plataforma)
                conteudo = self.__conteudos_registrados.get(nome_conteudo)
                if not conteudo:
                    conteudo = Conteudo(id_conteudo=len(self.__conteudos_registrados) + 1, nome_conteudo=nome_conteudo)
                    self.__conteudos_registrados[nome_conteudo] = conteudo
                usuario = self.__usuarios_registrados.get(usuario_id)
                if not usuario:
                    usuario = Usuario(id_usuario=usuario_id)
                    self.__usuarios_registrados[usuario_id] = usuario
                dados_interacao = {
                    'id_usuario': usuario_id,
                    'timestamp_interacao': timestamp_interacao,
                    'tipo_interacao': tipo_interacao,
                    'watch_duration_seconds': watch_duration_seconds,
                    'comment_text': comment_text
                }
                interacao = Interacao(dados_interacao, conteudo, plataforma)
                conteudo.adicionar_interacao(interacao)
                usuario.registrar_interacao(interacao)
            except ValueError as e:
                print(f"Erro ao processar interação: {e} - Dados: {linha}")
            except KeyError as e:
                print(f"Erro ao processar interação: campo {e} não encontrado - Dados: {linha}")

        
    # def processar_interacoes_do_csv_bd(self, caminho_arquivo):
    #     dados_brutos = self._carregar_interacoes_csv(caminho_arquivo)
    #     cabecalho = ['id_conteudo', 'nome_conteudo', 'id_usuario', 'timestamp_interacao', 'nome_plataforma', 'tipo_interacao', 'watch_duration_seconds', 'comment_text']

    #     def get_or_create_conteudo(id_conteudo, nome_conteudo, id_plataforma):
    #         query = "SELECT id_conteudo FROM conteudo WHERE id_conteudo = %s"
    #         result = self.db.fetch_one(query, (id_conteudo,))
    #         if not result:
    #             self.db.insert('conteudo', {'id_conteudo': id_conteudo, 'nome_conteudo': nome_conteudo, 'id_plataforma': id_plataforma})
    #         return id_conteudo

    #     def get_or_create_usuario(id_usuario):
    #         query = "SELECT id_usuario FROM usuario WHERE id_usuario = %s"
    #         result = self.db.fetch_one(query, (id_usuario,))
    #         if not result:
    #             self.db.insert('usuario', {'id_usuario': id_usuario})
    #         return id_usuario

    #     ids_conteudo = set()
    #     for linha in dados_brutos[1:]:
    #         try:
    #             dados = dict(zip(cabecalho, linha))
    #             plataforma = self.cadastrar_plataforma_bd(dados['nome_plataforma'])
    #             id_conteudo = int(dados['id_conteudo'])
    #             ids_conteudo.add(id_conteudo)
    #             id_conteudo = get_or_create_conteudo(id_conteudo, dados['nome_conteudo'], plataforma[0])
    #             id_usuario = get_or_create_usuario(dados['id_usuario'])
    #             data_interacao = {
    #                 'id_conteudo': id_conteudo,
    #                 'id_usuario': id_usuario,
    #                 'timestamp_interacao': dados['timestamp_interacao'],
    #                 'tipo_interacao': dados['tipo_interacao'],
    #                 'watch_duration_seconds': dados['watch_duration_seconds'],
    #                 'comment_text': dados['comment_text']
    #             }
    #             self.db.insert('interacao', data_interacao)
    #         except Exception as e:
    #             print(f"Erro ao processar interação: {e} - Dados: {linha}")
    #     print(f"IDs de conteúdo utilizados: {ids_conteudo}")
        
    def criar_tabelas(self):
        queries = [
            """
            CREATE TABLE plataforma (
            id_plataforma INT AUTO_INCREMENT PRIMARY KEY,
            nome_plataforma VARCHAR(255) UNIQUE NOT NULL
            );
            """,
            """
            -- TABELA DE USUÁRIOS
            CREATE TABLE usuario (
            id_usuario INT PRIMARY KEY
            );
            """,
            """
            -- TABELA DE TIPOS DE INTERAÇÃO
            CREATE TABLE tipo_interacao (
            id_tipo_interacao INT AUTO_INCREMENT PRIMARY KEY,
            nome_tipo VARCHAR(50) UNIQUE NOT NULL
            );
            """,
            """
            -- TABELA DE CONTEÚDOS
            CREATE TABLE conteudo (
            id_conteudo INT PRIMARY KEY,
            nome_conteudo VARCHAR(255) NOT NULL
            );
            """,
            """
            -- RELAÇÃO N:N ENTRE CONTEÚDO E PLATAFORMA
            CREATE TABLE conteudo_plataforma (
            id_conteudo INT,
            id_plataforma INT,
            PRIMARY KEY (id_conteudo, id_plataforma),
            FOREIGN KEY (id_conteudo) REFERENCES conteudo(id_conteudo),
            FOREIGN KEY (id_plataforma) REFERENCES plataforma(id_plataforma)
            );
            """,
            """
            -- TABELA DE INTERAÇÕES
            CREATE TABLE interacao (
            id_interacao INT AUTO_INCREMENT PRIMARY KEY,
            id_conteudo INT NOT NULL,
            id_usuario INT NOT NULL,
            id_plataforma INT NOT NULL,
            id_tipo_interacao INT NOT NULL,
            timestamp_interacao DATETIME NOT NULL,
            watch_duration_seconds INT,
            comment_text TEXT,
            FOREIGN KEY (id_conteudo) REFERENCES conteudo(id_conteudo),
            FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
            FOREIGN KEY (id_plataforma) REFERENCES plataforma(id_plataforma),
            FOREIGN KEY (id_tipo_interacao) REFERENCES tipo_interacao(id_tipo_interacao)
            );
            """
        
        ]
        for query in queries:
            try:
                self.db.execute_query(query)
                print("Tabela criada com sucesso!")
            except Exception as e:
                print(f"Erro ao criar tabela: {e}")   

    
    def processar_interacoes_do_csv_bd(self, caminho_arquivo):
        dados_brutos = self._carregar_interacoes_csv(caminho_arquivo)
        cabecalho = ['id_conteudo', 'nome_conteudo', 'id_usuario', 'timestamp_interacao',
                    'nome_plataforma', 'tipo_interacao', 'watch_duration_seconds', 'comment_text']

        def get_or_create_conteudo(id_conteudo, nome_conteudo):
            query = "SELECT id_conteudo FROM conteudo WHERE id_conteudo = %s"
            result = self.db.fetch_one(query, (id_conteudo,))
            if not result:
                self.db.insert('conteudo', {
                    'id_conteudo': id_conteudo,
                    'nome_conteudo': nome_conteudo
                })
            return id_conteudo

        def get_or_create_usuario(id_usuario):
            query = "SELECT id_usuario FROM usuario WHERE id_usuario = %s"
            result = self.db.fetch_one(query, (id_usuario,))
            if not result:
                self.db.insert('usuario', {'id_usuario': id_usuario})
            return id_usuario

        def get_or_create_plataforma(nome_plataforma):
            query = "SELECT id_plataforma FROM plataforma WHERE nome_plataforma = %s"
            result = self.db.fetch_one(query, (nome_plataforma,))
            if not result:
                self.db.insert('plataforma', {'nome_plataforma': nome_plataforma})
                result = self.db.fetch_one(query, (nome_plataforma,))
            return result[0]

        def get_or_create_tipo_interacao(nome_tipo):
            query = "SELECT id_tipo_interacao FROM tipo_interacao WHERE nome_tipo = %s"
            result = self.db.fetch_one(query, (nome_tipo,))
            if not result:
                self.db.insert('tipo_interacao', {'nome_tipo': nome_tipo})
                result = self.db.fetch_one(query, (nome_tipo,))
            return result[0]

        def vincular_conteudo_plataforma(id_conteudo, id_plataforma):
            query = "SELECT 1 FROM conteudo_plataforma WHERE id_conteudo = %s AND id_plataforma = %s"
            result = self.db.fetch_one(query, (id_conteudo, id_plataforma))
            if not result:
                self.db.insert('conteudo_plataforma', {
                    'id_conteudo': id_conteudo,
                    'id_plataforma': id_plataforma
                })

        ids_conteudo = set()
        for linha in dados_brutos[1:]:
            try:
                dados = dict(zip(cabecalho, linha))
                id_conteudo = int(dados['id_conteudo'])
                ids_conteudo.add(id_conteudo)

                id_plataforma = get_or_create_plataforma(dados['nome_plataforma'])
                id_conteudo = get_or_create_conteudo(id_conteudo, dados['nome_conteudo'])
                vincular_conteudo_plataforma(id_conteudo, id_plataforma)

                id_usuario = get_or_create_usuario(dados['id_usuario'])
                id_tipo_interacao = get_or_create_tipo_interacao(dados['tipo_interacao'])

                data_interacao = {
                    'id_conteudo': id_conteudo,
                    'id_usuario': id_usuario,
                    'id_tipo_interacao': id_tipo_interacao,
                    'id_plataforma': id_plataforma,
                    'timestamp_interacao': dados['timestamp_interacao'],
                    'watch_duration_seconds': int(dados['watch_duration_seconds']) if dados['watch_duration_seconds'] else None,
                    'comment_text': dados['comment_text'] if dados['comment_text'] else None
                }
                self.db.insert('interacao', data_interacao)

            except Exception as e:
                print(f"Erro ao processar interação: {e} - Dados: {linha}")

        print(f"IDs de conteúdo utilizados: {ids_conteudo}")

    

    # def criar_queries(self, caminho_arquivo):
    #     dados_brutos = self._carregar_interacoes_csv(caminho_arquivo)
    #     cabecalho = [
    #         'id_conteudo', 'nome_conteudo', 'id_usuario',
    #         'timestamp_interacao', 'nome_plataforma', 'tipo_interacao',
    #         'watch_duration_seconds', 'comment_text'
    #     ]

    #     queries_conteudo = []
    #     queries_usuario = set()
    #     queries_interacao = []
    #     plataformas = set()
    #     conteudos_inseridos = set()

    #     for linha in dados_brutos[1:]:
    #         dados = dict(zip(cabecalho, linha))

    #         id_conteudo = dados['id_conteudo']
    #         nome_conteudo = dados['nome_conteudo'].replace("'", "''").replace("\n", " ").strip()
    #         id_usuario = dados['id_usuario']
    #         timestamp_interacao = dados['timestamp_interacao']
    #         nome_plataforma = dados['nome_plataforma'].replace("'", "''").strip()
    #         tipo_interacao = dados['tipo_interacao'].replace("'", "''").strip()
    #         watch_duration_seconds = dados['watch_duration_seconds'] or 0
    #         comment_text = dados['comment_text'].replace("'", "''").strip() if dados['comment_text'] else 'NULL'

    #         # Inserção única por plataforma
    #         plataformas.add(f"('{nome_plataforma}')")

    #         # Inserção única por conteúdo
    #         if id_conteudo not in conteudos_inseridos:
    #             queries_conteudo.append(
    #                 f"({id_conteudo}, '{nome_conteudo}', "
    #                 f"(SELECT id_plataforma FROM plataforma WHERE nome_plataforma = '{nome_plataforma}'))"
    #             )
    #             conteudos_inseridos.add(id_conteudo)

    #         # Inserção única por usuário
    #         queries_usuario.add(f"({id_usuario})")

    #         # Query de interação
    #         if comment_text == 'NULL':
    #             queries_interacao.append(
    #                 f"({id_conteudo}, {id_usuario}, '{timestamp_interacao}', "
    #                 f"'{tipo_interacao}', {watch_duration_seconds}, NULL)"
    #             )
    #         else:
    #             queries_interacao.append(
    #                 f"({id_conteudo}, {id_usuario}, '{timestamp_interacao}', "
    #                 f"'{tipo_interacao}', {watch_duration_seconds}, '{comment_text}')"
    #             )

    #     # Montagem das queries finais
    #     query_plataforma = (
    #         "INSERT INTO plataforma (nome_plataforma) VALUES\n"
    #         + ",\n".join(sorted(plataformas)) + ";"
    #     )
    #     query_conteudo = (
    #         "INSERT INTO conteudo (id_conteudo, nome_conteudo, id_plataforma) VALUES\n"
    #         + ",\n".join(queries_conteudo) + ";"
    #     )
    #     query_usuario = (
    #         "INSERT INTO usuario (id_usuario) VALUES\n"
    #         + ",\n".join(sorted(queries_usuario)) + ";"
    #     )
    #     query_interacao = (
    #         "INSERT INTO interacao (id_conteudo, id_usuario, timestamp_interacao, tipo_interacao, watch_duration_seconds, comment_text) VALUES\n"
    #         + ",\n".join(queries_interacao) + ";"
    #     )

    #     # Impressão final
    #     print(query_plataforma)
    #     print()
    #     print(query_conteudo)
    #     print()
    #     print(query_usuario)
    #     print()
    #     print(query_interacao)

    def criar_queries(self, caminho_arquivo):
        dados_brutos = self._carregar_interacoes_csv(caminho_arquivo)
        cabecalho = [
            'id_conteudo', 'nome_conteudo', 'id_usuario',
            'timestamp_interacao', 'nome_plataforma', 'tipo_interacao',
            'watch_duration_seconds', 'comment_text'
        ]

        queries_plataforma = set()
        queries_usuario = set()
        queries_tipo_interacao = set()
        queries_conteudo = set()
        queries_conteudo_plataforma = set()
        queries_interacao = []

        for linha in dados_brutos[1:]:
            dados = dict(zip(cabecalho, linha))

            id_conteudo = dados['id_conteudo']
            nome_conteudo = dados['nome_conteudo'].replace("'", "''").replace("\n", " ").strip()
            id_usuario = dados['id_usuario']
            timestamp_interacao = dados['timestamp_interacao']
            nome_plataforma = dados['nome_plataforma'].replace("'", "''").strip()
            tipo_interacao = dados['tipo_interacao'].replace("'", "''").strip()
            watch_duration_seconds = dados['watch_duration_seconds'] or 'NULL'
            comment_text = dados['comment_text'].replace("'", "''").strip() if dados['comment_text'] else 'NULL'

            # Dados únicos
            queries_plataforma.add(f"('{nome_plataforma}')")
            queries_usuario.add(f"({id_usuario})")
            queries_tipo_interacao.add(f"('{tipo_interacao}')")
            queries_conteudo.add(f"({id_conteudo}, '{nome_conteudo}')")
            queries_conteudo_plataforma.add(
                f"({id_conteudo}, (SELECT id_plataforma FROM plataforma WHERE nome_plataforma = '{nome_plataforma}'))"
            )

            # Inserção da interação
            if comment_text == 'NULL':
                queries_interacao.append(
                    f"({id_conteudo}, {id_usuario}, "
                    f"(SELECT id_plataforma FROM plataforma WHERE nome_plataforma = '{nome_plataforma}'), "
                    f"(SELECT id_tipo_interacao FROM tipo_interacao WHERE nome_tipo = '{tipo_interacao}'), "
                    f"'{timestamp_interacao}', {watch_duration_seconds}, NULL)"
                )
            else:
                queries_interacao.append(
                    f"({id_conteudo}, {id_usuario}, "
                    f"(SELECT id_plataforma FROM plataforma WHERE nome_plataforma = '{nome_plataforma}'), "
                    f"(SELECT id_tipo_interacao FROM tipo_interacao WHERE nome_tipo = '{tipo_interacao}'), "
                    f"'{timestamp_interacao}', {watch_duration_seconds}, '{comment_text}')"
                )

        # Geração final das queries
        query_plataforma = (
            "INSERT INTO plataforma (nome_plataforma) VALUES\n"
            + ",\n".join(sorted(queries_plataforma)) + ";"
        )
        query_usuario = (
            "INSERT INTO usuario (id_usuario) VALUES\n"
            + ",\n".join(sorted(queries_usuario)) + ";"
        )
        query_tipo_interacao = (
            "INSERT INTO tipo_interacao (nome_tipo) VALUES\n"
            + ",\n".join(sorted(queries_tipo_interacao)) + ";"
        )
        query_conteudo = (
            "INSERT INTO conteudo (id_conteudo, nome_conteudo) VALUES\n"
            + ",\n".join(sorted(queries_conteudo)) + ";"
        )
        query_conteudo_plataforma = (
            "INSERT INTO conteudo_plataforma (id_conteudo, id_plataforma) VALUES\n"
            + ",\n".join(sorted(queries_conteudo_plataforma)) + ";"
        )
        query_interacao = (
            "INSERT INTO interacao (id_conteudo, id_usuario, id_plataforma, id_tipo_interacao, timestamp_interacao, watch_duration_seconds, comment_text) VALUES\n"
            + ",\n".join(queries_interacao) + ";"
        )

        with open("insercoes.sql", "w", encoding="utf-8") as f:
            f.write(query_plataforma + "\n\n")
            f.write(query_conteudo + "\n\n")
            f.write(query_usuario + "\n\n")
            f.write(query_tipo_interacao + "\n\n")  # Se você adicionou essa parte
            f.write(query_conteudo_plataforma + "\n\n")  # Se estiver usando também
            f.write(query_interacao + "\n")

        # Impressão
        # print(query_plataforma, end="\n\n")
        # print(query_usuario, end="\n\n")
        # print(query_tipo_interacao, end="\n\n")
        # print(query_conteudo, end="\n\n")
        # print(query_conteudo_plataforma, end="\n\n")
        # print(query_interacao)


    def gerar_inserts_interacoes_do_csv_bd_2(self, caminho_arquivo):
        dados_brutos = self._carregar_interacoes_csv(caminho_arquivo)
        cabecalho = ['id_conteudo', 'nome_conteudo', 'id_usuario', 'timestamp_interacao', 'nome_plataforma', 'tipo_interacao', 'watch_duration_seconds', 'comment_text']

        inserts = []

        def get_insert_conteudo(id_conteudo, nome_conteudo):
            return f"INSERT INTO conteudo (id_conteudo, nome_conteudo) VALUES ({id_conteudo}, '{nome_conteudo}');"

        def get_insert_usuario(id_usuario):
            return f"INSERT INTO usuario (id_usuario) VALUES ({id_usuario});"

        def get_insert_plataforma(nome_plataforma):
            return f"INSERT INTO plataforma (nome_plataforma) VALUES ('{nome_plataforma}');"

        plataformas = set()
        conteudos = set()
        usuarios = set()

        for linha in dados_brutos[1:]:
            try:
                dados = dict(zip(cabecalho, linha))
                plataformas.add(dados['nome_plataforma'])
                conteudos.add((int(dados['id_conteudo']), dados['nome_conteudo']))
                usuarios.add(int(dados['id_usuario']))

                insert_interacao = f"INSERT INTO interacao (id_conteudo, id_usuario, id_plataforma, timestamp_interacao, tipo_interacao, watch_duration_seconds, comment_text) VALUES ({int(dados['id_conteudo'])}, {int(dados['id_usuario'])}, (SELECT id_plataforma FROM plataforma WHERE nome_plataforma = '{dados['nome_plataforma']}'), '{dados['timestamp_interacao']}', '{dados['tipo_interacao']}', {dados['watch_duration_seconds']}, '{dados['comment_text'] or 'NULL'}');"
                inserts.append(insert_interacao)

                if dados['comment_text']:
                    insert_comentario = f"INSERT INTO comentario (id_conteudo, id_usuario, texto) VALUES ({int(dados['id_conteudo'])}, {int(dados['id_usuario'])}, '{dados['comment_text']}');"
                    inserts.append(insert_comentario)

            except Exception as e:
                print(f"Erro ao gerar insert: {e} - Dados: {linha}")

        for plataforma in plataformas:
            inserts.insert(0, get_insert_plataforma(plataforma))

        for conteudo in conteudos:
            inserts.insert(0, get_insert_conteudo(conteudo[0], conteudo[1]))

        for usuario in usuarios:
            inserts.insert(0, get_insert_usuario(usuario))

        return inserts
    def gerar_relatorio_engajamento_conteudos(self, top_n=None):
        conteudos = list(self.__conteudos_registrados.values())
        if top_n:
            conteudos = sorted(conteudos, key=lambda c: c.calcular_total_interacoes_engajamento(), reverse=True)[:top_n]
        print()
        print(("-" * 30), "X",("-" * 30))
        print(("-" * 30), "X",("-" * 30))
        print(f"Relatório de Engajamento de Conteúdos (Versão: {self.VERSAO_ANALISE})".center(60))
        print(("-" * 30), "X",("-" * 30))
        print(("-" * 30), "X",("-" * 30))
        print()
        print(f"Total de conteúdos analisados: {len(conteudos)}")
        print(f"Total de usuários registrados: {len(self.__usuarios_registrados)}")
        print(f"Total de plataformas registradas: {len(self.__plataformas_registradas)}")
        print()
        print(("-" * 30), " X ",("-" * 30))
        print()
        for conteudo in conteudos:
            print(f"Conteúdo: {conteudo.nome_conteudo.strip().title()} (ID: {conteudo.id_conteudo})")
            print()
            print(f"  Total de interações de engajamento: {conteudo.calcular_total_interacoes_engajamento()}")
            for tipo, total in conteudo.calcular_contagem_por_tipo_interacao().items():
                print(f"    {tipo}: {total}")
            # print(f"  Contagem por tipo de interação: {conteudo.calcular_contagem_por_tipo_interacao()}")
            print()
            print(f"  Tempo total de consumo: {conteudo.calcular_tempo_total_consumo()} segundos")
            print()
            print(f"  Média de tempo de consumo: {conteudo.calcular_media_tempo_consumo():.2f} segundos")
            print()
            if len(conteudo.listar_comentarios()) > 0:
                print("  Comentários:")
            for i, comment in enumerate(conteudo.listar_comentarios(), start=1):
                print(f"    Comentário {i}: {comment}")
            # for i, comment in conteudo.listar_comentarios():
            #     print(f"    Comentário{i}: {comment}")
            # print(f"  Comentários: {conteudo.listar_comentarios()}\n")
            print()
            print(("-" * 30), " X ",("-" * 30))
            print()
        print()
        print(("-" * 30), "X",("-" * 30))
        print(("-" * 30), "X",("-" * 30))
        print()
        print("Relatório de Engajamento de Conteúdos Finalizado".center(60))
        print()
        print(("-" * 30), "X",("-" * 30))
        print(("-" * 30), "X",("-" * 30))
        print()
        
        return conteudos
    
    def gerar_relatorio_engajamento_conteudos_bd(self, top_n=None):
        query = """
            SELECT 
                c.nome_conteudo, 
                c.id_conteudo, 
                SUM(i.watch_duration_seconds) AS tempo_total_consumo,
                COUNT(i.id_interacao) AS total_interacoes,
                COUNT(CASE WHEN ti.nome_tipo = 'like' THEN 1 END) AS likes,
                COUNT(CASE WHEN ti.nome_tipo = 'comment' THEN 1 END) AS comentarios,
                COUNT(CASE WHEN ti.nome_tipo = 'share' THEN 1 END) AS shares,
                COUNT(CASE WHEN ti.nome_tipo = 'view_start' THEN 1 END) AS view_start
            FROM conteudo c
            JOIN interacao i ON c.id_conteudo = i.id_conteudo
            JOIN tipo_interacao ti ON i.id_tipo_interacao = ti.id_tipo_interacao
            GROUP BY c.nome_conteudo, c.id_conteudo
            ORDER BY total_interacoes DESC;
        """
        if top_n:
            query += f" LIMIT {top_n}"
        resultados = self.db.fetch_all(query)

        print("Relatório de Engajamento de Conteúdos")
        print("-------------------------------")
        for resultado in resultados:
            nome_conteudo = resultado[0]
            id_conteudo = resultado[1]
            tempo_total_consumo = resultado[2]
            total_interacoes = resultado[3]
            likes = resultado[4]
            comentarios = resultado[5]
            shares = resultado[6]
            view_start = resultado[7]


            print(f"Conteúdo: {nome_conteudo} (ID: {id_conteudo})")
            print(f"Total de interações: {total_interacoes}")
            print(f"Tempo total de consumo: {tempo_total_consumo} segundos")
            print(f"Likes: {likes}")
            print(f"Comentários: {comentarios}")
            print(f"Shares: {shares}")
            print(f"view-start: {view_start}")
            print("-------------------------------")
    
    def gerar_relatorio_atividade_usuarios(self, top_n=None):
        usuarios = list(self.__usuarios_registrados.values())
        if top_n:
            usuarios = sorted(usuarios, key=lambda u: len(u._Usuario__interacoes_realizadas), reverse=True)[:top_n]
        for usuario in usuarios:
            print(f"\nUsuário ID: {usuario.id_usuario}")
            print(f"  Total de interações: {len(usuario._Usuario__interacoes_realizadas)}")
            print(f"  Conteúdos únicos consumidos: {len(usuario.obter_conteudos_unicos_consumidos())}")
            print("Plataformas mais frequentes:")
            plataformas_frequentes = usuario.plataformas_mais_frequentes()
            for nome_plataforma in plataformas_frequentes:
                plataforma = self.cadastrar_plataforma(nome_plataforma)
                tempo_consumo = usuario.calcular_tempo_total_consumo_plataforma(plataforma)
                print(f" - {plataforma.nome_plataforma}: {tempo_consumo} segundos")

            # plataformas_frequentes = usuario.plataformas_mais_frequentes()
            # for plataforma in plataformas_frequentes:
            #     tempo_consumo = usuario.calcular_tempo_total_consumo_plataforma(plataforma)
            #     print(f"    - {plataforma.nome_plataforma}: {tempo_consumo} segundos")
                # print(f"    - {plataforma} - {tempo_consumo} segundos")
            # print(f"  Tempo total de consumo por plataforma:")
            # for plataforma in self.listar_plataformas():
            #     tempo_consumo = usuario.calcular_tempo_total_consumo_plataforma(plataforma)
            #     print(f"    {plataforma.nome_plataforma}: {tempo_consumo} segundos")
            
            print()
                

            # print(f"  Plataformas mais frequentes: {usuario.plataformas_mais_frequentes()}\n")

        return usuarios
    
    def gerar_relatorio_atividade_usuarios_bd(self, top_n=None):
        query_usuarios = """ 
            SELECT u.id_usuario, 
                COUNT(i.id_interacao) AS total_interacoes, 
                COUNT(DISTINCT i.id_conteudo) AS conteudos_unicos 
            FROM usuario u 
            JOIN interacao i ON u.id_usuario = i.id_usuario 
            GROUP BY u.id_usuario 
            ORDER BY total_interacoes DESC 
        """
        if top_n:
            query_usuarios += f" LIMIT {top_n}"

        resultados = self.db.fetch_all(query_usuarios)

        query_plataformas = """ 
            SELECT p.nome_plataforma, 
                SUM(i.watch_duration_seconds) AS tempo_consumo 
            FROM interacao i
            JOIN conteudo c ON i.id_conteudo = c.id_conteudo
            JOIN conteudo_plataforma cp ON c.id_conteudo = cp.id_conteudo
            JOIN plataforma p ON cp.id_plataforma = p.id_plataforma
            WHERE i.id_usuario = %s
            GROUP BY p.nome_plataforma
            ORDER BY tempo_consumo DESC 
        """

        relatorio = []
        for id_usuario, total_interacoes, conteudos_unicos in resultados:
            plataformas_frequentes = self.db.fetch_all(query_plataformas, (id_usuario,))

            usuario_info = {
                'id_usuario': id_usuario,
                'total_interacoes': total_interacoes,
                'conteudos_unicos': conteudos_unicos,
                'plataformas_frequentes': [
                    {'nome': nome, 'tempo_consumo': tempo}
                    for nome, tempo in plataformas_frequentes
                ]
            }
            relatorio.append(usuario_info)

            # Impressão opcional (pode remover se for apenas backend)
            print(f"\nUsuário ID: {id_usuario}")
            print(f" Total de interações: {total_interacoes}")
            print(f" Conteúdos únicos consumidos: {conteudos_unicos}")
            print("Plataformas mais frequentes:")
            for plataforma in usuario_info['plataformas_frequentes']:
                print(f" - {plataforma['nome']}: {plataforma['tempo_consumo']} segundos")
            print()

        return relatorio

    
    def identificar_top_conteudos(self, metrica, n=5):
        if metrica not in ['tempo_total_consumo', 'total_interacoes_engajamento']:
            raise ValueError("Métrica inválida. Use 'tempo_total_consumo' ou 'total_interacoes_engajamento'.")
        conteudos = list(self.__conteudos_registrados.values())
        if metrica == 'tempo_total_consumo':
            conteudos = sorted(conteudos, key=lambda c: c.calcular_tempo_total_consumo(), reverse=True)[:n]
        elif metrica == 'total_interacoes_engajamento':
            conteudos = sorted(conteudos, key=lambda c: c.calcular_total_interacoes_engajamento(), reverse=True)[:n]
        # print(f"Total de conteúdos analisados: {len(conteudos)}")
        
        print(f"\nTop {n} conteúdos por '{metrica}':")
        print()
        for conteudo in conteudos:
            print(f"Conteúdo: {conteudo.nome_conteudo} (ID: {conteudo.id_conteudo})")
            if metrica == 'tempo_total_consumo':
                print(f"  Tempo total de consumo: {conteudo.calcular_tempo_total_consumo()} segundos")
            elif metrica == 'total_interacoes_engajamento':
                print(f"  Total de interações de engajamento: {conteudo.calcular_total_interacoes_engajamento()}")
            print()
        
        print()
        print(("-" * 20), " X ",("-" * 20))
        print()
        
        print(f"Total de usuários registrados: {len(self.__usuarios_registrados)}")
        print(f"Total de plataformas registradas: {len(self.__plataformas_registradas)}")
        print(f"Versão do sistema de análise: {self.VERSAO_ANALISE}")
        print()


    QUERIES_METRICAS = {
    'tempo_total_consumo': """
        SELECT c.id_conteudo, c.nome_conteudo, SUM(i.watch_duration_seconds) AS tempo_total_consumo
        FROM conteudo c JOIN interacao i ON c.id_conteudo = i.id_conteudo
        GROUP BY c.id_conteudo, c.nome_conteudo
        ORDER BY tempo_total_consumo DESC
        LIMIT %s
    """,
    'total_interacoes_engajamento': """
        SELECT c.id_conteudo, c.nome_conteudo, SUM(CASE WHEN i.tipo_interacao IN ('like', 'comment', 'share', 'view_start') THEN 1 ELSE 0 END) AS total_interacoes_engajamento,
               SUM(CASE WHEN i.tipo_interacao = 'like' THEN 1 ELSE 0 END) AS total_likes,
               SUM(CASE WHEN i.tipo_interacao = 'comment' THEN 1 ELSE 0 END) AS total_comments,
               SUM(CASE WHEN i.tipo_interacao = 'share' THEN 1 ELSE 0 END) AS total_shares,
               SUM(CASE WHEN i.tipo_interacao = 'view_start' THEN 1 ELSE 0 END) AS total_view_start
        FROM conteudo c JOIN interacao i ON c.id_conteudo = i.id_conteudo
        GROUP BY c.id_conteudo, c.nome_conteudo
        ORDER BY total_interacoes_engajamento DESC
        LIMIT %s
    """
    }

    # query = QUERIES_METRICAS[metrica]
    

    def identificar_top_conteudos_bd(self, metrica, n=5):
        if metrica not in ['tempo_total_consumo', 'total_interacoes_engajamento']:
            raise ValueError("Métrica inválida. Use 'tempo_total_consumo' ou 'total_interacoes_engajamento'.")

        if metrica == 'tempo_total_consumo':
            query = """ 
            SELECT c.id_conteudo, c.nome_conteudo, SUM(i.watch_duration_seconds) AS tempo_total_consumo 
            FROM conteudo c 
            JOIN interacao i ON c.id_conteudo = i.id_conteudo 
            GROUP BY c.id_conteudo, c.nome_conteudo 
            ORDER BY tempo_total_consumo DESC 
            LIMIT %s 
            """
        elif metrica == 'total_interacoes_engajamento':
            query = """ 
            SELECT 
                c.id_conteudo, 
                c.nome_conteudo, 
                SUM(CASE WHEN t.nome_tipo IN ('like', 'comment', 'share', 'view_start') THEN 1 ELSE 0 END) AS total_interacoes_engajamento,
                SUM(CASE WHEN t.nome_tipo = 'like' THEN 1 ELSE 0 END) AS total_likes,
                SUM(CASE WHEN t.nome_tipo = 'comment' THEN 1 ELSE 0 END) AS total_comments,
                SUM(CASE WHEN t.nome_tipo = 'share' THEN 1 ELSE 0 END) AS total_shares,
                SUM(CASE WHEN t.nome_tipo = 'view_start' THEN 1 ELSE 0 END) AS total_view_start
            FROM conteudo c 
            JOIN interacao i ON c.id_conteudo = i.id_conteudo 
            JOIN tipo_interacao t ON i.id_tipo_interacao = t.id_tipo_interacao
            GROUP BY c.id_conteudo, c.nome_conteudo 
            ORDER BY total_interacoes_engajamento DESC 
            LIMIT %s
            """

        resultados = self.db.fetch_all(query, (n,))
        print(f"\nTop {n} conteúdos por '{metrica}':")
        print()
        for resultado in resultados:
            id_conteudo = resultado[0]
            nome_conteudo = resultado[1]
            valor_metrica = resultado[2]
            print(f"Conteúdo: {nome_conteudo} (ID: {id_conteudo})")
            if metrica == 'tempo_total_consumo':
                print(f" Tempo total de consumo: {valor_metrica} segundos")
            elif metrica == 'total_interacoes_engajamento':
                print(f" Total de interações de engajamento: {valor_metrica}")
                print(f" Detalhes:")
                print(f"  Likes: {resultado[3]}")
                print(f"  Comentários: {resultado[4]}")
                print(f"  Compartilhamentos: {resultado[5]}")
                print(f"  Inícios de visualização: {resultado[6]}")
            print()

        totais = self.obter_totais()
        print(("-" * 20), " X ", ("-" * 20))
        print()
        print(f"Total de usuários registrados: {totais['total_usuarios']}")
        print(f"Total de plataformas registradas: {totais['total_plataformas']}")
        print(f"Versão do sistema de análise: {self.VERSAO_ANALISE}")
        print()

    def obter_totais(self):
        query_totais = """ 
        SELECT 
            (SELECT COUNT(DISTINCT id_usuario) FROM usuario) AS total_usuarios,
            (SELECT COUNT(*) FROM plataforma) AS total_plataformas
 
        """
        totais = self.db.fetch_one(query_totais)
        return {
            'total_usuarios': totais[0],
            'total_plataformas': totais[1]
        }

    
    def top_usuarios_por_interacao_bd(self, top_n=10):
        # Buscar tipos de interação disponíveis
        tipos_interacao = self.db.fetch_all("SELECT DISTINCT nome_tipo FROM tipo_interacao")
        
        for tipo_interacao in tipos_interacao:
            tipo_interacao = tipo_interacao[0]
            
            if tipo_interacao == 'comment':
                usuarios_com_mais_comentarios = self.db.fetch_all(""" 
                    SELECT u.id_usuario 
                    FROM interacao i 
                    JOIN usuario u ON i.id_usuario = u.id_usuario 
                    JOIN tipo_interacao t ON i.id_tipo_interacao = t.id_tipo_interacao
                    WHERE t.nome_tipo = 'comment' 
                    GROUP BY u.id_usuario 
                    ORDER BY COUNT(*) DESC 
                    LIMIT %s 
                """, (top_n,))

                for usuario in usuarios_com_mais_comentarios:
                    id_usuario = usuario[0]
                    comentarios = self.db.fetch_all(""" 
                        SELECT i.comment_text, co.nome_conteudo, p.nome_plataforma 
                        FROM interacao i 
                        JOIN conteudo co ON i.id_conteudo = co.id_conteudo 
                        JOIN conteudo_plataforma cp ON co.id_conteudo = cp.id_conteudo
                        JOIN plataforma p ON cp.id_plataforma = p.id_plataforma
                        JOIN tipo_interacao t ON i.id_tipo_interacao = t.id_tipo_interacao
                        WHERE t.nome_tipo = 'comment' AND i.id_usuario = %s 
                    """, (id_usuario,))


                else:
                    # Mostrar top_n usuários por tipo de interação
                    print(f"Top {top_n} usuários por {tipo_interacao}:")
                    usuarios = self.db.fetch_all("""
                        SELECT u.id_usuario, COUNT(*) AS total_interacoes
                        FROM interacao i 
                        JOIN usuario u ON i.id_usuario = u.id_usuario 
                        JOIN tipo_interacao t ON i.id_tipo_interacao = t.id_tipo_interacao
                        WHERE t.nome_tipo = %s
                        GROUP BY u.id_usuario 
                        ORDER BY total_interacoes DESC 
                        LIMIT %s
                    """, (tipo_interacao, top_n))
                    print(usuario)
                    for usuario in usuarios:
                        print(f"Usuário {usuario[0]}: {usuario[1]} interações")
                print()


    def top_usuarios_por_tempo_consumo_bd(self, top_n=10):
        query = """
            SELECT u.id_usuario, SUM(i.watch_duration_seconds) AS tempo_total
            FROM interacao i
            JOIN usuario u ON i.id_usuario = u.id_usuario
            GROUP BY u.id_usuario
            ORDER BY tempo_total DESC
            LIMIT %s
        """
        resultados = self.db.fetch_all(query, (top_n,))
        
        print(f"\nTop {top_n} usuários por tempo total de consumo:\n")
        for usuario in resultados:
            print(f"Usuário {usuario[0]}: {usuario[1]} segundos assistidos")

    def top_usuarios_por_tempo_medio_consumo_bd(self, top_n=10):
        query = """
            SELECT 
                u.id_usuario,
                COUNT(i.id_interacao) AS total_interacoes,
                SUM(i.watch_duration_seconds) AS tempo_total,
                AVG(i.watch_duration_seconds) AS tempo_medio
            FROM interacao i
            JOIN usuario u ON i.id_usuario = u.id_usuario
            WHERE i.watch_duration_seconds IS NOT NULL
            GROUP BY u.id_usuario
            HAVING total_interacoes > 0
            ORDER BY tempo_medio DESC
            LIMIT %s
        """
        resultados = self.db.fetch_all(query, (top_n,))
        
        print(f"\nTop {top_n} usuários por tempo **médio** de consumo:\n")
        for usuario in resultados:
            print(f"Usuário {usuario[0]} — {usuario[3]:.2f} segundos (média) em {usuario[1]} interações")

    
    def listar_plataformas_melhor_media_tempo_interacao_bd2(self, top_n=10):
        query = """
            SELECT 
                p.nome_plataforma, 
                AVG(i.watch_duration_seconds) AS media_tempo_interacao
            FROM interacao i
            JOIN conteudo_plataforma cp ON i.id_conteudo = cp.id_conteudo
            JOIN plataforma p ON cp.id_plataforma = p.id_plataforma
            WHERE i.watch_duration_seconds IS NOT NULL
            GROUP BY p.nome_plataforma
            ORDER BY media_tempo_interacao DESC
            LIMIT %s;
        """
        result = self.db.fetch_all(query, (top_n,))
        print(f"Top {top_n} plataformas com melhor média de tempo de interação:")
        for i, row in enumerate(result, start=1):
            print(f"{i}. Plataforma: {row[0]}, Média de tempo de interação: {float(row[1]):.2f} segundos")
        return result
    
    def listar_conteudos_melhor_media_tempo_interacao_bd2(self, top_n=10):
        query = """
            SELECT 
                c.nome_conteudo, 
                ROUND(AVG(i.watch_duration_seconds), 2) AS media_tempo_interacao
            FROM interacao i
            JOIN conteudo c ON i.id_conteudo = c.id_conteudo
            WHERE i.watch_duration_seconds IS NOT NULL
            GROUP BY c.nome_conteudo
            ORDER BY media_tempo_interacao DESC
            LIMIT %s;
        """
        result = self.db.fetch_all(query, (top_n,))
        print(f"Top {top_n} conteúdos com melhor média de tempo de interação:")
        for i, row in enumerate(result, start=1):
            print(f"{i}. Conteúdo: {row[0]}, Média de tempo de interação: {float(row[1]):.2f} segundos")
        return result

    def menu_principal(self):

        while True:
            print("\n" + ("-" * 30))
            print("Bem-vindo ao Sistema de Análise de Engajamento!")
            print(f"Versão: {self.VERSAO_ANALISE}")
            print("Selecione uma opção:")
            print("1. Cadastrar Plataforma")
            print("2. Listar Plataformas")
            print("3. Gerar Relatório de Engajamento de Conteúdos")
            print("4. Gerar Relatório de Atividade de Usuários")
            print("5. Identificar Top Conteúdos")
            print("0. Sair")
            opcao = input("Digite a opção desejada: ")
            print(("-" * 30))
            print()
            if opcao == '1':
                nome_plataforma = input("Digite o nome da plataforma: ")
                plataforma = self.cadastrar_plataforma(nome_plataforma)
                print(f"Plataforma '{plataforma.nome_plataforma}' cadastrada com sucesso!")
            elif opcao == '2':
                plataformas = self.listar_plataformas()
                if plataformas:
                    print("Plataformas registradas:")
                    for plataforma in plataformas:
                        print(f"- {plataforma.nome_plataforma} (ID: {plataforma.id_plataforma})")
                else:
                    print("Nenhuma plataforma registrada.")
            
            elif opcao == '3':
                top_n = input("Deseja ver os top N conteúdos? (Digite um número ou deixe em branco para ver todos): ")
                top_n = int(top_n) if top_n.isdigit() else None
                self.gerar_relatorio_engajamento_conteudos(top_n)
            elif opcao == '4':
                top_n = input("Deseja ver os top N usuários? (Digite um número ou deixe em branco para ver todos): ")
                top_n = int(top_n) if top_n.isdigit() else None
                self.gerar_relatorio_atividade_usuarios(top_n)
            elif opcao == '5':
                metrica = input("Digite a métrica (tempo_total_consumo ou total_interacoes_engajamento): ")
                n = input("Quantos conteúdos deseja ver? (Digite um número): ")
                n = int(n) if n.isdigit() else 5
                self.identificar_top_conteudos(metrica, n)
            elif opcao == '0':
                print("Saindo do sistema...")
                break
            else:
                print("Opção inválida. Tente novamente.")

    
    def __str__(self):
        return f"Sistema de Análise de Engajamento (Versão: {self.VERSAO_ANALISE})"
    def __repr__(self):
        return f"SistemaAnaliseEngajamento()"