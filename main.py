from analise.sistema import SistemaAnaliseEngajamento


def main():
    
    sistema = SistemaAnaliseEngajamento(database='globo_tech', host='localhost', port=3306, user='root', password='')
    # sistema.criar_queries('interacoes_globo.csv')
    # sistema.criar_tabelas()
    # sistema.processar_interacoes_do_csv_bd('interacoes_globo.csv')
    # sistema.listar_plataformas_melhor_media_tempo_interacao_bd2(top_n=5)
    # sistema.listar_conteudos_melhor_media_tempo_interacao_bd2(top_n=5)
    
    # sistema.gerar_relatorio_engajamento_conteudos_bd(top_n=5)
    # sistema.gerar_relatorio_atividade_usuarios_bd(top_n=5)


    # sistema.identificar_top_conteudos_bd(metrica='tempo_total_consumo', n=5)
    # sistema.identificar_top_conteudos_bd(metrica='total_interacoes_engajamento', n=5)
    
    # sistema.obter_totais()

    # sistema.top_usuarios_por_interacao_bd(top_n=10)
    # sistema.top_usuarios_por_tempo_consumo_bd(top_n=5)
    # sistema.top_usuarios_por_tempo_medio_consumo_bd(top_n=5)
    
    
   
   
    
if __name__ == '__main__':
    main()