import requests

class BancoDados:
    #   classe responsável pela conexão com o banco de dados geográficos
    
    def verificacao_parametros_conexao_bd(self, nome_bd, senha_bd, schema_bd):
        #   método que verifica os dados da conexão com o BDG
        print('> VERIFICAÇÃO DA CONEXÃO POSTGIS:')
        self.verify_postgis = QInputDialog().getText(None,
                                                     'Dados de conexão do PostGIS',
                                                     '\n Verifique os dados de conexão do Banco de Dados PostGIS:'
                                                     '\n'
                                                     '\n NOME: '+nome_bd+
                                                     '\n SENHA: '+senha_bd+
                                                     '\n SCHEMA: '+schema_bd+
                                                     '\n'
                                                     '\n Deseja alterar os dados de conexão?'
                                                     '\n (1) SIM     (2) NÃO')

        if self.verify_postgis[1] == True:
            if self.verify_postgis[0] == '1':
                self.switch_connection = True   #o usuário deseja trocar a conexão
            elif self.verify_postgis[0] == '2':
                self.switch_connection = False  #o usuário deseja permanecer na conexão
            else:
                iface.messageBar().pushCritical('Valor de entrada inválido: ',
                                                'Entre com valor (1)SIM ou (2)Não. Tente novamente.')
                self.verify_parameters_connection(nome_bd, senha_bd, schema_bd)
        else:
            self.switch_connection = False
        pass

    def executa_consulta_bd (self, host_bd, nome_bd, usuario_bd, senha_bd, schema_bd, cod_otto_interesse):
        #   método que executa consultas sql no banco de dados
        #   as consultas são realizadas em substituição aos processamentos QGIS
        self.cod_otto_processado = '86652191'
        conexao = psycopg2.connect(host = host_bd,
                                   database = nome_bd,
                                   user = usuario_bd,
                                   password = senha_bd)
        cursor = conexao.cursor()
        consulta_sql =  'SELECT COUNT(*) '\
                        'FROM camada_ottobacias '\
                        'WHERE camada_ottobacias.cobacia LIKE \''+self.cod_otto_processado+'%\' AND camada_ottobacias.cobacia >= \''+cod_otto_interesse+'\''
        cursor.execute(consulta_sql)
        resultados = cursor.fetchall()
        for linha in resultados:
            print(linha)
        cursor.close()
        conexao.close()
        pass

class Camadas:
    #   classe que realiza a preparação das camadas no projeto

    def limpeza_residuos(self):
        #   método de exclusao de camadas residuais do projeto
        self.camada_residual = QgsProject.instance().mapLayers().values()
        lista_camadas_residuais = [l for l in self.camada_residual]
        if len(lista_camadas_residuais) > 0:
            for camada in lista_camadas_residuais:
                QgsProject.instance().removeMapLayer(camada)
            self.mensagem_saida_limpeza = '--> Limpeza de camadas residuais de execuções anteriores realizada!'
        else:
            self.mensagem_saida_limpeza = '--> Não existem camadas residuais de execuções anteriores.'
        self.canvas = qgis.utils.iface.mapCanvas()
        self.canvas.refresh()
        return self.mensagem_saida_limpeza

    def escolher_bacia(self):
        #   método de escolha da bacia de interesse
        self.escolher_bacia = QInputDialog().getText(None, 'Selecione uma Bacia',
                                                           ' Selecione a bacia de interesse:'
                                                           '\n'
                                                           '\n (1) Tiete')
        iface.messageBar().pushSuccess('Definição da Bacia: ',
                                       'A bacia de interesse foi definida.')
        self.bacia_escolhida = self.escolher_bacia[0]
        return self.bacia_escolhida

    def importar_camada_fundo(self):
        #   método de carregamento da camada de plano de fundo
        self.service_url = 'mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}'
        self.service_uri = 'type=xyz&zmin=0&zmax=21&url=https://'+requests.utils.quote(self.service_url)
        iface.addRasterLayer(self.service_uri, 'Google_Road', 'wms')
        pass

    def selecionar_camadas_bacia(self, bacia_escolhida, nome_bd, senha_bd, schema_bd):
        #   método de definição dos nomes das cmadas da bacia selecionada pelo usuário
        self.bacia = bacia_escolhida
        self.lista_ottobacias = ['ottobacias_tiete_bho_2017_5k']
        self.lista_ottotrechos = ['ottotrechos_tiete_bho_2017_5k']
        if self.bacia == '1':
            self.ottobacias = self.importar_camada_ottobacias(nome_bd, senha_bd, schema_bd, self.lista_ottobacias[0])
            self.ottotrechos = self.importar_camada_ottotrechos(nome_bd, senha_bd, schema_bd, self.lista_ottotrechos[0])
        elif self.bacia == '2':
            self.ottobacias = self.importar_camada_ottobacias(nome_bd, senha_bd, schema_bd, self.lista_ottobacias[1])
            self.ottotrechos = self.importar_camada_ottotrechos(nome_bd, senha_bd, schema_bd, self.lista_ottotrechos[1])
        elif self.bacia == '3':
            self.ottobacias = self.importar_camada_ottobacias(nome_bd, senha_bd, schema_bd, self.lista_ottobacias[2])
            self.ottotrechos = self.importar_camada_ottotrechos(nome_bd, senha_bd, schema_bd, self.lista_ottotrechos[2])
        return self.ottobacias, self.ottotrechos

    def definir_extensao(self, camada):
        #   método de definição da extensão da camada de interesse
        self.camada = camada
        self.canvas = qgis.utils.iface.mapCanvas()
        self.canvas.setExtent(self.camada.extent())
        self.canvas.refresh()
        pass

    def importar_camada_ottobacias(self, nome_bd, senha_bd, schema_bd, nome_camada):
        #   método de carregamento de camadas vetorial de ottobacias do banco
        self.uri = QgsDataSourceUri()
        self.uri.setConnection('localhost', '5432', nome_bd, 'postgres', senha_bd)
        self.uri.setDataSource(schema_bd, nome_camada, 'geom')
        self.ottobacias = QgsVectorLayer(self.uri.uri(False), 'camada_ottobacias', 'postgres')
        self.ottobacias.renderer().symbol().setColor(QColor(200, 200, 200, 10))
        QgsProject.instance().addMapLayer(self.ottobacias, False)
        print('\n''-> Importação da camada de ottobacias realizada.')
        return self.ottobacias

    def importar_camada_ottotrechos(self, nome_bd, senha_bd, schema_bd, nome_camada):
        #   método de carregamento de camadas vetorial de ottotrechos do banco
        self.uri = QgsDataSourceUri()
        self.uri.setConnection('localhost', '5432', nome_bd, 'postgres', senha_bd)
        self.uri.setDataSource(schema_bd, nome_camada, "geom")
        self.ottotrechos = QgsVectorLayer(self.uri.uri(False), 'camada_ottotrechos', 'postgres')
        self.ottotrechos.renderer().symbol().setColor(QColor(0, 150, 255))
        QgsProject.instance().addMapLayer(self.ottotrechos)
        print('\n''-> Importação da camada de ottotrechos realizada.')
        return self.ottotrechos

    def importar_setores_censitarios(self, nome_bd, senha_bd):
        #   método de carregamento de camadas vetorial de ottobacias do banco
        self.uri = QgsDataSourceUri()
        self.uri.setConnection('localhost', '5432', nome_bd, 'postgres', senha_bd)
        self.uri.setDataSource('public', 'setores_censitarios_ibge_2010', 'geom')
        self.setores = QgsVectorLayer(self.uri.uri(False), 'camada_setores', 'postgres')
        QgsProject.instance().addMapLayer(self.setores, False)  # Camada adiciona, mas não visível.
        return self.setores
    
    def importar_disponibilidade_hidrica(self, nome_bd, senha_bd, bacia_escolhida):
        if bacia_escolhida == '1':
            self.bacia_disponibilidade = 'DispH_v27nov20_Snirh_Tiete'
        elif bacia_escolhida == '2':
            self.bacia_disponibilidade = 'DispH_v27nov20_Snirh_Paranapanema'
        elif bacia_escolhida == '3':
            self.bacia_disponibilidade = 'DispH_v27nov20_Snirh_Iguacu'
        self.uri = QgsDataSourceUri()
        self.uri.setConnection('localhost', '5432', nome_bd, 'postgres', senha_bd)
        self.uri.setDataSource('public', self.bacia_disponibilidade, 'geom')
        self.disponibilidade_hidrica = QgsVectorLayer(self.uri.uri(False), 'camada_disp_hid', 'postgres')
        QgsProject.instance().addMapLayer(self.disponibilidade_hidrica, False)  # Camada adiciona, mas não visível.
        return self.disponibilidade_hidrica
    
    def importar_outorgas(self, nome_bd, senha_bd, bacia_escolhida):
        if bacia_escolhida == '1':
            self.filtro_bacia_outorga = 'tietê'
        elif bacia_escolhida == '2':
            self.filtro_bacia_outorga = 'paranapanema'
        elif bacia_escolhida == '3':
            self.filtro_bacia_outorga = 'iguaçu'
        # Importa outorgas estaduais
        self.uri = QgsDataSourceUri()
        self.uri.setConnection('localhost', '5432', nome_bd, 'postgres', senha_bd)
        self.uri.setDataSource('public', 'CNARH_Estadual_ANA_2022', 'geom')
        self.outorgas_estaduais = QgsVectorLayer(self.uri.uri(False), 'camada_outorgas_estaduais', 'postgres')
        QgsProject.instance().addMapLayer(self.outorgas_estaduais, True)  # Camada adiciona, mas não visível.
        '''
        # Filtro para bacia
        self.query_outorgas_estaduais = '?query=SELECT camada_outorgas_estaduais.* '\
                                        'FROM camada_outorgas_estaduais '\
                                        'WHERE camada_outorgas_estaduais.bacia = \''+self.filtro_bacia_outorga+'\''
        self.outorgas_estaduais_bacia = QgsVectorLayer(self.query_outorgas_estaduais, 'outorgas_estaduais_bacia', 'virtual')
        QgsProject.instance().addMapLayer(self.outorgas_estaduais_bacia, True)  # Camada adiciona, mas não visível.
        # Importa outorgas federais
        self.uri = QgsDataSourceUri()
        self.uri.setConnection('localhost', '5432', nome_bd, 'postgres', senha_bd)
        self.uri.setDataSource('public', 'CNARH_Federal_ANA_2022', 'geom')
        self.outorgas_federais = QgsVectorLayer(self.uri.uri(False), 'camada_outorgas_federais', 'postgres')
        QgsProject.instance().addMapLayer(self.outorgas_federais, False)  # Camada adiciona, mas não visível.
        return self.outorgas_estaduais, self.outorgas_federais
        '''

class Ponto:
    #   classe que cria o ponto de interesse para análise

    def ponto_interesse(self, bacia):
        self.tipo_ponto = QInputDialog().getText(None, 'Ponto de interesse',
                                                       ' Como deseja criar um ponto de interesse:'
                                                       '\n'
                                                       '\n (1) - Pontos predefinidos'
                                                       '\n (2) - Entrar com novas coordenadas')
        if self.tipo_ponto[1] == True:
            if self.tipo_ponto[0] == '1':
                Ponto().escolher_pontos_listados(bacia)
            elif self.tipo_ponto[0] == '2':
                Ponto().definir_coordenadas_ponto()
        else:
            iface.messageBar().pushCritical('ATENÇÃO: ',
                                            'O usuário precisar escolher entre as opções (1) ou (2)!')
        pass

    def escolher_pontos_listados(self, bacia):
        self.tiete = [-47.5982, -23.1851,
                      -47.1160, -22.6998,
                      -48.4400, -22.1020]
        self.paranapanema = [-50.3579, -25.1052,
                             -50.4208, -22.9439,
                             -49.4060, -22.8790]
        self.iguacu = [-49.3386, -25.5492,
                       -51.0178, -26.3169,
                       -50.2299, -25.7713]
        self.escolher_ponto = QInputDialog().getText(None, 'Ponto de interesse',
                                                            ' Escolha um ponto de interesse na bacia:'
                                                            '\n'
                                                            '\n (1) (2) (3)')
        if bacia == '1':
            if self.escolher_ponto[0] == '1':
                self.x = self.tiete[0]
                self.y = self.tiete[1]
            elif self.escolher_ponto[0] == '2':
                self.x = self.tiete[2]
                self.y = self.tiete[3]
            elif self.escolher_ponto[0] == '3':
                self.x = self.tiete[4]
                self.y = self.tiete[5]
        elif bacia == '2':
            if self.escolher_ponto[0] == '1':
                self.x = self.paranapanema[0]
                self.y = self.paranapanema[1]
            elif self.escolher_ponto[0] == '2':
                self.x = self.paranapanema[2]
                self.y = self.paranapanema[3]
            elif self.escolher_ponto[0] == '3':
                self.x = self.paranapanema[4]
                self.y = self.paranapanema[5]
        elif bacia == '3':
            if self.escolher_ponto[0] == '1':
                self.x = self.iguacu[0]
                self.y = self.iguacu[1]
            elif self.escolher_ponto[0] == '2':
                self.x = self.iguacu[2]
                self.y = self.iguacu[3]
            elif self.escolher_ponto[0] == '3':
                self.x = self.iguacu[4]
                self.y = self.iguacu[5]
        self.gerar_ponto(self.x, self.y)
        pass

    def definir_coordenadas_ponto(self):
        self.mb = QMessageBox()
        self.mb.setText('ATENÇÃO: Tenha certeza que o ponto está contido na bacia!')
        self.mb.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        self.valor_retornado = self.mb.exec()
        if self.valor_retornado == QMessageBox.Ok:
            self.coord_lat = QInputDialog().getText(None,
                                                    'Coordenadas do ponto de interesse',
                                                    ' Digite a coordenada de LONGITUDE:')
            self.y = self.coord_lat[0]
            self.coord_long = QInputDialog().getText(None,
                                                    'Coordenadas do ponto de interesse',
                                                    ' Digite a coordenada de LATITUDE:')
            self.x = self.coord_long[0]
        self.gerar_ponto(self.x, self.y)
        pass

    def gerar_ponto(self, x, y):
        self.ponto_interesse = QgsVectorLayer('Point?crs=epsg:4674', 'ponto_interesse' , 'memory')
        prov = self.ponto_interesse.dataProvider()
        ponto = QgsPointXY(x, y)
        feat = QgsFeature()
        feat.setGeometry(QgsGeometry.fromPointXY(ponto))
        prov.addFeatures([feat])
        QgsProject.instance().addMapLayers([self.ponto_interesse])
        pass

class Processamentos:
    #   classe que realiza as etapas de processamento e apresentação de resultados

    def selecionar_cod_bacia_interesse(self):
        #   método que obtém o código otto da bacia que contém o ponto de interesse
        self.query_bacia_interesse = '?query=SELECT camada_ottobacias.cobacia, camada_ottobacias.geometry '\
                                     'FROM camada_ottobacias, ponto_interesse '\
                                     'WHERE st_intersects(camada_ottobacias.geometry, ponto_interesse.geometry)'
        self.bacia_interesse = QgsVectorLayer(self.query_bacia_interesse, 'bacia_interesse', 'virtual')
        for feature in self.bacia_interesse.getFeatures():          # tentar arrumara este trecho, para eliminara o "for"
            self.cod_otto_interesse = feature['cobacia']
        return self.cod_otto_interesse, self.bacia_interesse

    def processamento_cod_otto(self, cod_otto_interesse):
        #   método que realiza o tratamento do código otto original da bacia selecionada
        if (int(cod_otto_interesse) % 2) == 0:
            self.cod_otto_processado = cod_otto_interesse
        else:
            for self.caractere in range(len(cod_otto_interesse)):
                self.index_analysis = (self.caractere + 1) * -1
                self.value_analysis = int(cod_otto_interesse[self.index_analysis])
                if (self.value_analysis % 2) == 0:
                    self.cod_otto_processado = cod_otto_interesse[:(self.index_analysis + 1)]
                    break
        return self.cod_otto_processado

    def selecao_ottoottobacias_montante(self, cod_otto_interesse):
        #   método que criará a camada de bacias a montante
        self.cod_otto_processado = self.processamento_cod_otto(cod_otto_interesse)
        self.query_ottobacias_montante = '?query=SELECT * '\
                                         'FROM camada_ottobacias '\
                                         'WHERE camada_ottobacias.cobacia LIKE \''+self.cod_otto_processado+'%\' AND camada_ottobacias.cobacia >= \''+cod_otto_interesse+'\''
        self.ottobacias_montante = QgsVectorLayer(self.query_ottobacias_montante, 'ottobacias_montante', 'virtual')
        return self.ottobacias_montante

    def selecionar_ottotrechos_montante(self, cod_otto_interesse):
        #   método que criará a camada de bacias a montante
        self.cod_otto_processado = self.processamento_cod_otto(cod_otto_interesse)
        self.query_ottotrechos_montante = '?query=SELECT camada_ottotrechos.cobacia, camada_ottotrechos.geometry '\
                                          'FROM camada_ottotrechos '\
                                          'WHERE camada_ottotrechos.cobacia LIKE \''+self.cod_otto_processado+'%\' AND camada_ottotrechos.cobacia >= \''+cod_otto_interesse+'\''
        self.ottotrechos_montante = QgsVectorLayer(self.query_ottotrechos_montante, 'trechos_montante', 'virtual')
        self.ottotrechos_montante.renderer().symbol().setColor(QColor(255, 130, 0,))
        self.ottotrechos_montante.renderer().symbol().setWidth(0.4)
        QgsProject.instance().addMapLayer(self.ottotrechos_montante)
        return self.ottotrechos_montante

    def selecionar_ottotrechos_jusante(self, cod_otto_interesse):
        #   método que seleciona os trechos a jusante do ponto de interesse
        self.rio = ['','','','','','']
        self.rios = 0
        # seleção dos rios a jusante
        for self.valor in range(len(cod_otto_interesse)):

            self.index_analise = (self.valor + 1) * -1
            self.algarismo = int(cod_otto_interesse[self.index_analise])
            self.impar = self.algarismo % 2
            self.codf = cod_otto_interesse[:(len(cod_otto_interesse)-self.valor)]


            # fiz o teste para final par, pois do contrário dá erro, não entendi
            if self.impar == 0:
                self.codfim = cod_otto_interesse[:(len(cod_otto_interesse)-self.valor)]
                self.rio[self.rios] = self.codfim
                self.rios = self.rios + 1
                self.compri = len(self.codfim)
                if self.compri <= 3:    # teste para ver se é um dos inícios em branco e se já chegou na foz do iguaçu (rio 862, por 4 para o Paraopeba)
                    break

        print(self.rios)
        print(self.rio)

        self.selecao = ''
        for self.elementos in self.rio:
            if self.elementos != '':
                self.selecao = self.selecao + 'camada_ottotrechos.cocursodag LIKE \''+ self.elementos +'\' OR '
            else:
                break
        self.comp = len(self.selecao)
        self.comp2 = self.comp - 3
        print(self.comp2)
        print(self.selecao)
        self.sele2 = self.selecao [:self.comp2]
        print(self.sele2)
        self.query_ottotrechos_jusante = '?query=SELECT camada_ottotrechos.cocursodag, camada_ottotrechos.geometry '\
                                         'FROM camada_ottotrechos '\
                                         'WHERE ('+ self.sele2 +')AND camada_ottotrechos.cobacia < \''+cod_otto_interesse+'\''
        self.ottotrechos_jusante = QgsVectorLayer(self.query_ottotrechos_jusante, "trechos_jusante_1", "virtual")
        self.ottotrechos_jusante.renderer().symbol().setColor(QColor(20, 0, 255,))
        self.ottotrechos_jusante.renderer().symbol().setWidth(0.8)
        QgsProject.instance().addMapLayer(self.ottotrechos_jusante)
        return self.ottotrechos_jusante

    def numero_bacias_montante(self):
        #   método que apresenta o número de bacias a montante
        self.n_otto_trechos = 0
        for feature in QgsProject.instance().mapLayersByName('trechos_montante')[0].getFeatures():
            self.n_otto_trechos += 1
        print('número de ottotrechos à montante:', self.n_otto_trechos)
        message_box = QMessageBox()
        message_box.setWindowTitle('RESULTADOS')
        self.texto = str('O número de bacias à montante é:'+self.n_otto_trechos)
        message_box.setText(self.texto)
        message_box.exec_()
        pass
    
    def area_acumulada_montante(self):
        #   método que soma o valor das áreas das bacias a montante do ponto de interesse

        '''
        #   apresentação do valor de área acumulada à montante
        self.soma_area_otto_bacias = 0.0
        for feature in QgsProject.instance().mapCamadasByName('ottobacias_montante')[0].getFeatures():
            self.soma_area_otto_bacias += feature['nuareacont']
        print('soma das áreas das ottobacias à montante (km²):', self.soma_area_otto_bacias)
        '''
        pass

    def obter_populacao_montante(self, ottobacias_montante, setores):
        # método que realiza operações para obter o valor da população nas ottobacias a montante da bacia de interesse
        self.processo_bacias_setores = processing.run("native:intersection",{
                                                        'INPUT':ottobacias_montante,
                                                        'OVERLAY':setores,
                                                        'OUTPUT':'memory: setores_cesitarios_e_ottobacias_montante'})
        self.intersecao_bacias_setores = self.processo_bacias_setores['OUTPUT']

        self.intersecao_bacias_setores.startEditing()                                       # COMANDO PARA HABILITAR MODO DE EDIÇÃO
        self.intersecao_bacias_setores.addAttribute(QgsField('nova_area', QVariant.Double))    # INSERE UMA COLUNA CHAMADA "nova_area" NA TABELA DE ATRIBUTOS
        self.intersecao_bacias_setores.addAttribute(QgsField('nova_pop', QVariant.Double))
        self.intersecao_bacias_setores.commitChanges()                                      # COMANDO PARA ENCERRAR MODO DE EDIÇÃO E SALVAR EDIÇÕES
        
        self.expressao_area = QgsExpression('$area')  # Expressão do cálculo de área
        self.expressao_pop = QgsExpression('"densidade_demografica_inicial_sirgas" * "nova_area"')  # Expressão do cálculo de população
        
        self.context = QgsExpressionContext()
        self.context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(self.intersecao_bacias_setores))
        
        with edit(self.intersecao_bacias_setores):
            for f in self.intersecao_bacias_setores.getFeatures():
                self.context.setFeature(f)
                f['nova_area'] = self.expressao_area.evaluate(self.context)
                self.intersecao_bacias_setores.updateFeature(f)
        
        with edit(self.intersecao_bacias_setores):
            for f in self.intersecao_bacias_setores.getFeatures():
                self.context.setFeature(f)
                f['nova_pop'] = self.expressao_pop.evaluate(self.context)
                self.intersecao_bacias_setores.updateFeature(f)
        

        self.processo_de_agrupamento_por_ottobacias = processing.run("native:aggregate", {
                    'INPUT': self.intersecao_bacias_setores,
		            'GROUP_BY':'"cobacia"',
		            'AGGREGATES':[{'aggregate': 'first_value','delimiter': ',','input': '"cobacia"','length': 0,'name': 'cobacia','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                  {'aggregate': 'sum','delimiter': ',','input': '"nova_pop"','length': 0,'name': 'nova_pop','precision': 0,'sub_type': 0,'type': 6,'type_name': 'double precision'}],
		            'OUTPUT':'memory: ottobacias_montante_populacao'})
        self.agrupamento_por_ottobacias = self.processo_de_agrupamento_por_ottobacias['OUTPUT']
        return self.intersecao_bacias_setores, self.agrupamento_por_ottobacias
    
    def obter_disponibilidade_montante(self, cod_otto_interesse):
        # método que realiza operação para obter disponibilidade hídrica nas ottobacias a montante da bacia de interesse
        self.cod_otto_processado = self.processamento_cod_otto(cod_otto_interesse)
        self.query_disponibilidade_montante = '?query=SELECT * '\
                                              'FROM camada_disp_hid '\
                                              'WHERE camada_disp_hid.cobacia LIKE \''+self.cod_otto_processado+'%\' AND camada_disp_hid.cobacia >= \''+cod_otto_interesse+'\''
        self.disp_hid_montante = QgsVectorLayer(self.query_disponibilidade_montante, 'disp_hid_montante', 'virtual')
        return self.disp_hid_montante
    
    def unir_populacao_e_disponibilidade(self):
        # método que realiza operação de união entre tabelas de população a montante e disponibilidade hídrica a montante
        self.query_uniao_pop_disp = '?query=SELECT * '\
                                    'FROM ottobacias_montante_populacao '\
                                    'INER JOIN disp_hid_montante ON disp_hid_montante.bacia = ottobacias_montante_populacao.bacia '
        self.uniao_populacao_disponibilidade = QgsVectorLayer(self.query_uniao_pop_disp, 'uniao_pop_disp', 'virtual')
        return self.uniao_populacao_disponibilidade


####################    INÍCIO DA EXECUÇÃO DO ALGORITMO     ####################


# PARÂMETROS DE ENTRADA DO BDG #
host_bd = 'localhost'
nome_bd = 'dev_bacias'
usuario_bd = 'postgres'
senha_bd = 'cobrape'
schema_bd = 'public'
print('-> Parâmetros de entrada definidos.')

# LIMPEZA DE CAMADAS RESIDUAIS #
mensagem_saida_limpeza = Camadas().limpeza_residuos()
print('\n''-> Limpeza de camadas realizada.')
print(mensagem_saida_limpeza)

# ESCOLHA DA BACIA DE INTERESSE PARA TRABALHAR #
bacia_escolhida = Camadas().escolher_bacia()
print('\n''-> Escolha da bacia realizada.')
#print('\n''bacia_escolhida:', bacia_escolhida)

# IMPORTAÇÃO DE CAMADA DE FUNDO #
Camadas().importar_camada_fundo()
print('\n''-> Camada de fundo adicionada.')

# SELEÇÃO DAS CAMADAS DA BACIA DE INTERESSE #
ottobacias, ottotrechos = Camadas().selecionar_camadas_bacia(bacia_escolhida, nome_bd, senha_bd, schema_bd)
print('\n''-> Seleção das camadas da bacia realizada.')

# DEFINIÇÃO DO PONTO DE INTERESSE NA BACIA #
Ponto().ponto_interesse(bacia_escolhida)
print('\n''-> Ponto de interesse criado.')

# SELEÇÃO DO CÓDIGO DA BACIA DE INTERESSE #
cod_otto_interesse, bacia_interesse = Processamentos().selecionar_cod_bacia_interesse()
print('\n''-> Código da bacia de interesse obtido.')
print('-->Código da Bacia Selecionada:', cod_otto_interesse)

# SELEÇÃO DE OTTOBACIAS A MONTANTE #
ottobacias_montante = Processamentos().selecao_ottoottobacias_montante(cod_otto_interesse)
print('\n''-> Seleção de ottobacias a montante realizado.')

# SELEÇÃO DE OTTOTRECHOS A MONTANTE #
ottotrechos_montante = Processamentos().selecionar_ottotrechos_montante(cod_otto_interesse)
print('\n''-> Seleção de ottorechos a montante realizado.')

# SELEÇÃO DE OTTOTRECHOS A JUSANTE #
ottotrechos_jusante = Processamentos().selecionar_ottotrechos_jusante(cod_otto_interesse)
print('\n''-> Seleção de ottorechos a jusante realizado.')

# APRESENTA NÚMERO DE BACIAS A MONTANTE #
Processamentos().numero_bacias_montante()
print('\n''-> Apresentação de informações realizada.')

'''
# REALIZA CONSULTA SQL DE TESTE #
BancoDados().executa_consulta_bd(host_bd, nome_bd, usuario_bd, senha_bd, schema_bd, cod_otto_interesse)
print('\n''-> Apresentação de consulta SQL realizada.')


# IMPORTAÇÃO DA CAMADA DE SETORES CENSITARIOS #
setores = Camadas().importar_setores_censitarios(nome_bd, senha_bd)

# OBTER POPULAÇÃO DAS OTTOBACIAS A MONTANTE #
intersecao_bacias_setores, agrupamento_por_ottobacias = Processamentos().obter_populacao_montante(ottobacias_montante, setores)

# IMPORTAÇÃO DA CAMADA DE DISPONIBILIDADE HIDRICA #
disponibilidade_hidrica = Camadas().importar_disponibilidade_hidrica(nome_bd, senha_bd, bacia_escolhida)

# OBTER DISPONIBILIDADE HÍDRICA DAS OTTOBACIAS A MONTANTE #
disponilidade_montante = Processamentos().obter_disponibilidade_montante(cod_otto_interesse)

# IMPORTAÇÃO DE CAMADAS DE OUTORGAS #
#outorgas_estaduais, outorgas_federais = Camadas().importar_outorgas(nome_bd, senha_bd, bacia_escolhida)
outorgas_estaduais = Camadas().importar_outorgas(nome_bd, senha_bd, bacia_escolhida)

# UNIÃO DE POPULAÇÃO E DISPONIBILIDADE HÍDRICA #
#uniao_populacao_disponibilidade = Processamentos().unir_populacao_e_disponibilidade()
'''

ottobacias_montante.renderer().symbol().setColor(QColor(255, 0, 0, 50))
QgsProject.instance().addMapLayer(ottobacias_montante)
Camadas().definir_extensao(ottobacias_montante)

bacia_interesse.renderer().symbol().setColor(QColor(0, 255, 0, 70))
QgsProject.instance().addMapLayer(bacia_interesse)

'''
intersecao_bacias_setores.renderer().symbol().setColor(QColor(150, 150, 150))
QgsProject.instance().addMapLayer(intersecao_bacias_setores)

QgsProject.instance().addMapLayer(agrupamento_por_ottobacias)

QgsProject.instance().addMapLayer(disponilidade_montante)
'''

print('\n','FIM DA EXECUÇÃO DA FERRAMENTA!!!','\n')
