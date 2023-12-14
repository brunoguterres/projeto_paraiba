import requests
from qgis.core import QgsVectorLayer, QgsVectorLayerJoinInfo

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

    def importar_camada_fundo(self):
        #   método de carregamento da camada de plano de fundo
        self.service_url = 'mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}'
        self.service_uri = 'type=xyz&zmin=0&zmax=21&url=https://'+requests.utils.quote(self.service_url)
        iface.addRasterLayer(self.service_uri, 'Google_Road', 'wms')
        pass

    def definir_extensao(self, camada):
        #   método de definição da extensão da camada de interesse
        self.camada = camada
        self.canvas = qgis.utils.iface.mapCanvas()
        self.canvas.setExtent(self.camada.extent())
        self.canvas.refresh()
        pass

    def importar_camada_ottobacias(self, nome_bd, senha_bd, schema_bd, nome_camada_ottobacias):
        #   método de carregamento de camadas vetorial de ottobacias do banco
        self.uri = QgsDataSourceUri()
        self.uri.setConnection('localhost', '5432', nome_bd, 'postgres', senha_bd)
        self.uri.setDataSource(schema_bd, nome_camada_ottobacias, 'geom')
        self.ottobacias = QgsVectorLayer(self.uri.uri(False), 'camada_ottobacias', 'postgres')
        self.ottobacias.renderer().symbol().setColor(QColor(200, 200, 200, 10))
        QgsProject.instance().addMapLayer(self.ottobacias)
        print('\n''-> Importação da camada de ottobacias realizada.')
        return self.ottobacias

    def importar_camada_ottotrechos(self, nome_bd, senha_bd, schema_bd, nome_camada_ottotrechos):
        #   método de carregamento de camadas vetorial de ottotrechos do banco
        self.uri = QgsDataSourceUri()
        self.uri.setConnection('localhost', '5432', nome_bd, 'postgres', senha_bd)
        self.uri.setDataSource(schema_bd, nome_camada_ottotrechos, "geom")
        self.ottotrechos = QgsVectorLayer(self.uri.uri(False), 'camada_ottotrechos', 'postgres')
        self.ottotrechos.renderer().symbol().setColor(QColor(0, 150, 255))
        QgsProject.instance().addMapLayer(self.ottotrechos)
        print('\n''-> Importação da camada de ottotrechos realizada.')
        return self.ottotrechos
    
    def importar_disponibilidade_hidrica(self, nome_bd, senha_bd, nome_camada_disp):
        self.uri = QgsDataSourceUri()
        self.uri.setConnection('localhost', '5432', nome_bd, 'postgres', senha_bd)
        self.uri.setDataSource('public', nome_camada_disp, 'geom')
        self.disponibilidade_hidrica = QgsVectorLayer(self.uri.uri(False), 'camada_disp_hid', 'postgres')
        QgsProject.instance().addMapLayer(self.disponibilidade_hidrica, False)  # Camada adicionada, mas não visível.
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

class Processamentos:
    #   classe que realiza as etapas de processamento e apresentação de resultados

    def obter_populacao_montante(self, ottobacias_montante, setores): #NÃO É UTILIZADO MAIS. MANTIDO PARA CONSULTA DE AGREGAÇÃO
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
    
    def unir_ottobacias_com_disponibilidade(self): #NÃO ESTÁ FUNCIONANDO AINDA
        # método que realiza operação de união entre tabelas de população a montante e disponibilidade hídrica a montante
        camada_alvo = ottobacias
        camada_fonte = disponibilidade_hidrica

        info_uniao = QgsVectorLayerJoinInfo()
        info_uniao.setJoinFieldName('cobacia')
        info_uniao.setJoinLayerId(camada_fonte.id())
        info_uniao.setJoinFieldName('cobacia')

        camada_alvo.addJoin(info_uniao)
        pass

    def gerar_tabela_para_balanco(self, ottobacias):
        # método para preparação da tabela para cálculo do balanço
        campos = ottobacias.fields()

        dados_tabela = []

        # Adicione os nomes dos campos como a primeira linha da matriz
        linha_campos = [campo.name() for campo in campos]
        dados_tabela.append(linha_campos)

        # Itere sobre os recursos da camada
        for feature in camada_ativa.getFeatures():
            # Obtenha os valores dos atributos como uma lista
            valores_atributos = [feature[campo.name()] for campo in campos]
            
            dados_tabela.append(valores_atributos)



####################    INÍCIO DA EXECUÇÃO DO ALGORITMO     ####################


# PARÂMETROS DE ENTRADA DO BDG #
host_bd = 'localhost'
nome_bd = 'bdg_prh_rpb'
usuario_bd = 'postgres'
senha_bd = 'cobrape'
schema_bd = 'public'
print('-> Parâmetros de entrada definidos.')

# LIMPEZA DE CAMADAS RESIDUAIS #
mensagem_saida_limpeza = Camadas().limpeza_residuos()
print('\n''-> Limpeza de camadas realizada.')
print(mensagem_saida_limpeza)

# IMPORTAÇÃO DE CAMADA DE FUNDO #
Camadas().importar_camada_fundo()
print('\n''-> Camada de fundo adicionada.')

# IMPORTAÇÃO CAMADAS DA BACIA DE INTERESSE #
nome_camada_ottobacias = 'ottobacias_pb_5k'
nome_camada_ottotrechos = 'ottotrechos_pb_5k'
ottobacias = Camadas().importar_camada_ottobacias(nome_bd, senha_bd, schema_bd, nome_camada_ottobacias)
ottotrechos = Camadas().importar_camada_ottotrechos(nome_bd, senha_bd, schema_bd, nome_camada_ottotrechos)
print('\n''-> Seleção das camadas da bacia realizada.')

# IMPORTAÇÃO DA CAMADA DE DISPONIBILIDADE HIDRICA #
nome_camada_disp = 'disp_hid_pb_5k'
disponibilidade_hidrica = Camadas().importar_disponibilidade_hidrica(nome_bd, senha_bd, nome_camada_disp)
print('\n''-> Importação da camada de disponibilidade realizada.')

# UNIÃO DE OTTOBACIAS E DISPONIBILIDADE HÍDRICA #
Processamentos().unir_ottobacias_com_disponibilidade()
print('\n''-> União de ottobacias e disponibilidade realizada.')

# CRIAR TABELA PARA CÁLCULO DE BALANÇO #
Processamentos().gerar_tabela_para_balanco(ottobacias)

print('\n','FIM DA EXECUÇÃO DA FERRAMENTA!!!','\n')
