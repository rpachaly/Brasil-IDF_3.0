# -*- coding: utf-8 -*-
"""
/***************************************************************************
 BrasilIDF
                                 A QGIS plugin
 FAZER A DESCRIÇÃO
                              -------------------
        begin                : 2016-10-03
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Ecotecnologias
        email                : robsonleopachaly@yahoo.com.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from __future__ import absolute_import
from builtins import zip
from builtins import str
from builtins import range
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QSettings, QCoreApplication, QTranslator, qVersion, Qt, QEvent
from PyQt5.QtGui import QIcon, QCursor, QMouseEvent
from PyQt5.QtWidgets import QAction, QRadioButton
from .brasil_IDF_dialog import BrasilIDFDialog
from qgis.gui import QgsMapTool, QgsMapToolEmitPoint, QgsMapMouseEvent, QgsMessageBar
from qgis.core import QgsPointXY, QgsVectorLayer, QgsFeature, QgsGeometry, QgsProject, QgsFeatureRequest, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProcessing
from qgis.utils import *
import os
import processing
from processing.tools import *
from . import resources
import matplotlib.pyplot as plt
from scipy import interpolate
import numpy as np
from .interpolar import interpolador
from .desacumular import desacumulador
from .plotar import plotarLinha
from .plotar import plotarBarra
from . import getCoord
from osgeo import ogr

class BrasilIDF(QgsMapTool):
    
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        QgsMapTool.__init__(self, iface.mapCanvas())

        """Constructor.
	
        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """

 # Create the dialog (after translation) and keep reference
        
        self.dlg = BrasilIDFDialog()


        #############################################
        # Save reference to the QGIS interface
        self.iface = iface 
        self.canvas = self.iface.mapCanvas()
        self.clickTool = QgsMapToolEmitPoint(self.canvas)
        self.mapTool = getCoord.PointTool(self.iface, self.dlg)

        #############################################
                             

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'BrasilIDF_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

       
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Brasil IDF')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'BrasilIDF')
        self.toolbar.setObjectName(u'BrasilIDF')
        
        #======================================================================#
                
        #Limpa o texto que ja foi escrito e conecta ao select_output_file1
        self.dlg.caminhoTexto.clear()
        self.dlg.botaoTexto.clicked.connect(self.select_output_file)  
        
        #DURACAO - Pega o clique do botão rodar e conecta ao rodarDurEspecifica
        self.dlg.rodarDuracao.clicked.connect(self.rodarDurEspecifica)
        
        #BLOCOS_ALTERNADOS - Pega o clique do botão rodar e conecta ao rodarChuvaProjeto
        self.dlg.rodarBlocos.clicked.connect(self.rodarChuvaProjeto)
        
        #CURVA_I-D-F - Pega o clique do botão rodar e conecta ao rodarIDF
        self.dlg.rodarIDF.clicked.connect(self.rodarIDF)
        
        #CURVA_P-D-F - Pega o clique do botão rodar e conecta ao rodarPDF
        self.dlg.rodarPDF.clicked.connect(self.rodarPDF)
        
        #Pega o clique do botão fechar e conect a função fechar
        self.dlg.fechar.clicked.connect(self.fechar)        
                        
        #Se clica no + seleciona coordenada no mapa
        self.dlg.getCoord.clicked.connect(self.selButton)
        
        #Deixa selecionado o radioButton das coordenadas
        self.dlg.radioMap.setChecked(True)
        
        #Se muda o index do comboBox do estado conecta a select coord !!!ARRUMAR!!!
        self.dlg.comboCidade.currentIndexChanged.connect(self.escCidade)
                                                
        #======================================================================#   
		
    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('BrasilIDF', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/BrasilIDF/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Brasil IDF'),
            callback=self.open,
            parent=self.iface.mainWindow())
            
    #============================================================      
    
    #Abre o file browser e colocar o widget do line edit com o caminho do arquivo
    def select_output_file(self):
        
        filename = QtWidgets.QFileDialog.getExistingDirectory(self.dlg, 'Selecione uma pasta de saida:', 'C:\\', QtWidgets.QFileDialog.ShowDirsOnly)   
        self.dlg.caminhoTexto.setText(filename) 
                                                                                                        	
    #Fecha a janela depois de clicar em fechar   
    def fechar(self):
        self.dlg.close()
                
    def aplicar_BlocosAlternados(self, precipitacao_desacumulada, numero_intervalos_tempo_chuva, posicao_pico):
        """
Aplica o metodo dos blocos alternados a partir de uma serie de dados de chuva desacumulada e retorna a precipitacao ordenada.
No metodo dos blocos alternados, os valores incrementais sao reorganizados 
de forma que o maximo incremento ocorra, aproximadamente, no meio da duracao 
da chuva total. Os incrementos (ou blocos de chuva) seguintes sao organizados 
a direita e a esquerda alternadamente, ate preencher toda a duracao, segundo 
Collischonn e Tassi, 2013.

Esta funcao retorna a chuva ordenada em uma variavel do tipo lista
        precipitacao_ordenada = [...]

    Parametros para uso:
            -> precipitacao_desacumulada: Lista que contem os dados de chuva desacumulada.
                * precipitacao_desacumulada = [...] -> Dados de chuva desacumulada [em mm/s].
                OBS: A variável precipitacao_desacumulada DEVE estar em ordem DECRESCENTE.
                
            -> numero_intervalos_tempo_chuva: Variavel do tipo inteiro que armazena o numero de intervalos de tempo COM CHUVA da operacao.
                * numero_intervalos_tempo_chuva = 1440
                
            -> posicao_pico: Variavel do tipo float que armazena a posicao da maior precipitacao desacumulada em porcentagem decimal.
                * Exemplos: posicao_pico = 0.5 -> Pico em 50 porcento do tempo da simulacao
                posicao_pico = 0.2 -> Pico em 20 porcento do tempo da simulacao"""

    #  Algoritmo original escrito por Daniel Allasia, revisado e otimizado por Vitor Geller.
    # Ordena a chuva pelo metodo dos blocos alternados
    
    #   Se o posicao_pico nao esta no range correto
        if (float(posicao_pico) < 0 or float(posicao_pico) > 1):
            self.errorMes("Erro", "O valor do pico de chuvas (posicao_pico) deve estar entre zero e um (0 <= posicao_pico <= 1)")
            return None

    #   Se o tamanho de precipitacao_desacumulada nao e' igual ao numero de intervalos de tempo com chuva
        if len(precipitacao_desacumulada) != numero_intervalos_tempo_chuva:
            self.errorMes("Erro", "O numero de intervalos de tempo com chuva deve ser igual ao tamanho da série de precipitacoes desacumuladas")
            return None

    #   Se nao parou ate aqui, continue...
    
    #   Se posicao_pico for zero
        if (float(posicao_pico) == 0.0):
            indice_pico = 0

    #   Se numero_intervalos_tempo_chuva for par
        elif numero_intervalos_tempo_chuva % 2 == 0:
            indice_pico = (int(posicao_pico*numero_intervalos_tempo_chuva)-1)   #estimo a localizacao do pico em numero de intervalos de tempo com relacao a duracao da chuva
        
    #   Se numero_intervalos_tempo_chuva for impar
        elif numero_intervalos_tempo_chuva % 2 == 1:
            indice_pico = int(posicao_pico*numero_intervalos_tempo_chuva)   #estimo a localizacao do pico em numero de intervalos de tempo com relacao a duracao da chuva
        
        precipitacao_ordenada = [0. for x in range(len(precipitacao_desacumulada))] # armazenar os valores. Variavel retornada no final da funcao.
        indice_pdes           = 0 #variavel de posicao
        indice_ordenacao      = 1 #variavel de posicao
    
        precipitacao_ordenada[indice_pico] = precipitacao_desacumulada[indice_pdes] #(Valor central se impar.... se par: arredondado para baixo) correspondente ao primeiro valor da chuva desacumulada (maior valor)
    
    #   Fazer o loop N vezes ate' que o bloco caia "fora" nos dois extremos
        while ( ((indice_pico - indice_ordenacao) >= 0) or ((indice_pico + indice_ordenacao) <= (len(precipitacao_desacumulada))) ):
        
        #   Comeco loop sempre verificando se e' possivel colocar um valor na direita do pico
            if (indice_pico + indice_ordenacao) < len(precipitacao_ordenada): # se for == ele nao entra
                indice_pdes += 1  # aumentar o indice de pdes em uma unidade para poder copiar o proximo valor de pdes
                precipitacao_ordenada[(indice_pico + indice_ordenacao)] = precipitacao_desacumulada[indice_pdes] # Entro com o valor na direita se for possivel
            
        #   Verifico se e' possivel colocar um valor a esquerda do pico
            if (indice_pico - indice_ordenacao) >= 0: # aqui pode ser igual, porque trata-se de indice (o primeiro e' zero)
                indice_pdes += 1 # Aumentar o indice de pdes em uma unidade para poder copiar o proximo valor de pdes
                precipitacao_ordenada[(indice_pico - indice_ordenacao)] = precipitacao_desacumulada[indice_pdes]   #valor abaixo se o indice nao for menor que zero

            indice_ordenacao += 1 # preparar para o proximo loop
    
    #   Retornar variavel ordenada
        return precipitacao_ordenada
        
    #=========================================================================================

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Brasil IDF'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
        
    #==============================================================
 
    def selButton(self):
        
        if self.dlg.radioMap.isChecked():
        
            tool = getCoord.PointTool(self.iface, self.dlg)
            self.canvas.setMapTool(tool)
            tool.afterClick.connect(self.pasteCoord)
        
    def pasteCoord(self):      
        pass   
    
    def open(self):
        
        #Adiciona a layer da geometria das isozonas quando abre o plugin
        plugin_path = self.getCam()
        isozonas_geometria = QgsVectorLayer(plugin_path + '\\layer2',  "isozonas_brasil", "ogr")
        layerMap = QgsProject.instance().mapLayers()
        QgsProject.instance().addMapLayer(isozonas_geometria)
        for name, layer in layerMap.items():
            if 'isozonas_brasil' in name:
                QgsProject.instance().removeMapLayer(layer)
         
        arquivoCidades = plugin_path + '\\layer3\\Cidade.txt'        
        listaCidades = open(arquivoCidades, 'r', encoding="latin-1")
        listaCidades = listaCidades.read().split('\n')
        self.dlg.comboCidade.clear()
        self.dlg.comboCidade.addItems(listaCidades)
                
        self.dlg.show()
        
    def escCidade(self):
#        
        if self.dlg.radioCidade.isChecked():
            plugin_path = self.getCam()   
            arquivoLatitude = plugin_path + '\\layer3\\Latitude.txt' 
            arquivoLongitude = plugin_path + '\\layer3\\Longitude.txt' 
            indexMun = self.dlg.comboCidade.currentIndex()
            
            listaLatitude = open(arquivoLatitude, 'r')
            listaLatitude = listaLatitude.read().split('\n')
            listaLongitude = open(arquivoLongitude, 'r')
            listaLongitude = listaLongitude.read().split('\n')

            latitude = listaLatitude[indexMun]
            longitude = listaLongitude[indexMun]
            
            self.dlg.lat_line.setText(str(round(float(latitude),2)))    
            self.dlg.long_line.setText(str(round(float(longitude),2)))
    
    def errorMes(self, tipo, mensagem):
        #Função de mostrar erro
        self.iface.messageBar().pushMessage(tipo, mensagem, level=Qgis.Critical)
    
    def getCam(self):
        #Pega o caminho do plugin
        plugin_path = os.path.dirname(os.path.realpath(__file__))
        return plugin_path
    
    def getPre(self):
        #Pega o valor da precipitação diária colocado pelo usuário
        prec_line = self.dlg.prec_line.text()
        if prec_line == '':
            return None
        #return prec_line
        else:
            return prec_line
        
    def getRet(self):
        #Pega o valor do tempo de retorno colocado pelo usuário
        ret_line = self.dlg.ret_line.text()
        if ret_line == '':
            return None
        else:
            return ret_line        
                
    def getLat(self):
        #Pega valor de latitude  
        lat_line = self.dlg.lat_line.text() 
        if lat_line == '':
            return None
        else:
            return lat_line
    
    def getLon(self):
        #Pega valor de longitude
        long_line = self.dlg.long_line.text()
        if long_line == '':
            return None
        else:
            return long_line 
 
    def getDir(self):      
        #Pega o diretorio colocado pelo usuario
        diretorio = self.dlg.caminhoTexto.text()
        if diretorio == '':
            return None
        else:
            return diretorio              
        
    def listaTempo(self):
        
        #Cria a variável da relação tempo em minutos
        relacaoTempo = [10.0, 15.0, 20.0, 30.0, 45.0, 60.0, 120.0, 240.0, 360.0, 720.0, 1440.0]
        return relacaoTempo       
    
    def extractLocation(self, layer1, layer2):
        
        #Extrai a feição do shape das Isozonas e cruza com o shape do ponto das coordenadas 
        #Como resultado a variável Isozona_zone_layer com a zona extraída
        ebl_out = processing.run("qgis:extractbylocation", {'INPUT': layer1,'PREDICATE': 0, 'INTERSECT': layer2, 'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT})
        #ebl_out = processing.run('qgis:extractbylocation', layer1, layer2, u'intersects')#, 0, None)
        if ebl_out is None:
            ebl_out = processing.run('qgis:extractbylocation', layer1, layer2, u'intersects')#, None)
        Isozona_zone = ebl_out['OUTPUT']
        #Isozona_zone_layer = QgsVectorLayer(Isozona_zone,"Isozona_zone", "ogr")
        return Isozona_zone#_layer
        
    def porcentagemChuva(self):
        
        #Cria a lista da relacão tempo em horas
        relacaoTempo = self.listaTempo()
        prec_line = self.getPre()
        if prec_line is None:
            return None
        lat_line = self.getLon()
        if lat_line is None:
            return None
        long_line = self.getLat()
        if long_line is None:
            return None
        plugin_path = self.getCam()
        diretorio = self.getDir()
        if diretorio is None:
            return None
        transformacaoHoras = []
        for i in relacaoTempo:
            transformacaoHoras.append(i/60)
            
        #prec_line = float(prec_line)*1.14
        
        # Cria uma layer tipo ponto, já em WGS84
        point_layer = QgsVectorLayer("Point?crs=EPSG:4326", "coordenada", "memory")
        provider = point_layer.dataProvider()
        # Adiciona primeiro ponto
        pt = QgsFeature()
        point = QgsPointXY(float(lat_line), float(long_line))
        pt.setGeometry(QgsGeometry.fromPointXY(point))
        provider.addFeatures([pt])
        # Diz para o vetor ponto para buscar mudanças com o provedor
        point_layer.updateExtents()
        #Adiciona o ponto ao mapa 
        layerMap = QgsProject.instance().mapLayers()
        for name, layer in layerMap.items():
            if "coordenada" in name:
                QgsProject.instance().removeMapLayer(layer)    
        
        QgsProject.instance().addMapLayer(point_layer)        
        #point_layer é o ponto criado
        
        #Abrir o shape das Isozona que está na pasta do plugin
        pol_layer = QgsVectorLayer(plugin_path + "\\layer1", "isozonas", "ogr")

        Isozona_zone_layer = self.extractLocation(pol_layer, point_layer)
        if Isozona_zone_layer is None:
            return None
        #Adiciona a Layer Isozona_zone_layer ao mapa
        for name, layer in layerMap.items():
            if "Isozona_zone" in name:
                QgsProject.instance().removeMapLayer(layer)  
            
        QgsProject.instance().addMapLayer(Isozona_zone_layer)     
                    
        #Salva em txt os campos da layer extraída separado por vírgula
        filename = diretorio + r"\dadosIsozona.txt"            
        output_file = open(filename, 'w')
        #Escreve o valor de precipitação e duração inseridos pelo usuário
        output_file.write("%s\n" %(prec_line))
        #Escreve os valores da feição do shape das isozonas
        Isozona_fields = Isozona_zone_layer.fields()
        Isozona_fieldnames = [field.name() for field in Isozona_fields]
        for f in Isozona_zone_layer.getFeatures():
            line = '\n'.join(str(f[x]) for x in Isozona_fieldnames)
            #unicode_line = line.encode('utf-8')
            output_file.write(line)
            output_file.close()
            
        #Abre o arquivo txt para leitura
        output_file = open(filename, 'r')
        #Separa os valores em lista
        porcentagemChuva = output_file.read().split('\n')
        
        #Verifica se o ponto realizou a interseção com as isozonas
        if len(porcentagemChuva) == 2:
             return None
        else:
             return porcentagemChuva
    
    def chuvaFinal(self):
        
        prec_line = self.getPre()
        if prec_line == '':
            return None
        prec_line = float(prec_line)*(1.14)
        porcentagemChuva = self.porcentagemChuva()
        if porcentagemChuva is None:
            return None
        #Remove os primeiros valores da lista
        del porcentagemChuva[0:3]
        #Transforma a lista em float
        floatChuva = []
        for i in porcentagemChuva:
            floatChuva.append(float(i))
        #Multiplica a precipitação inserida pelo usuário pelos valores da porcentagem da chuva
        chuvaFinal = []
        for i in floatChuva:
            chuvaFinal.append(i*(float(prec_line)/100))
            
        return chuvaFinal

    def intensidade(self):
        
        chuvaFinal = self.chuvaFinal()
        if chuvaFinal is None:
            return None
        relacaoTempo = self.listaTempo()
        transformacaoHoras = []
        for i in relacaoTempo:
            transformacaoHoras.append(i/60)
        #Cria a lista da intensidade dividindo a precipitação pela relacaoTempo em horas
        intensidade = [chuvaFinali/transformacaoHorasi for chuvaFinali,transformacaoHorasi in zip(chuvaFinal,transformacaoHoras)]

        return intensidade
    def verDadosIniciais(self):
             
        prec_line = self.getPre()
        if prec_line is None:
            self.errorMes("Error", "Dados de entrada: Insira valor para precipitacao")
            return False
        ret_line = self.getRet()
        if ret_line is None:
            self.errorMes("Error", "Dados de entrada: Insira valor para tempo de retorno")
            return False
        lat_line = self.getLon()
        if lat_line is None:
            self.errorMes("Error", "Dados de entrada: Insira valor para longitude")
            return False
        long_line = self.getLat()
        if long_line is None:
            self.errorMes("Error", "Dados de entrada: Insira valor para latitude")
            return False
        diretorio = self.getDir()
        if diretorio is None:
            self.errorMes("Error", "Diretorio: Insira o diretorio de saida")
            return False   
        
    def rodarDurEspecifica(self):

        #Verifição dados iniciais
        dadosIniciais = self.verDadosIniciais()
        if dadosIniciais is False:
            return None

        #Verificação dados modelo
        duracao = self.dlg.duracao.text()
        if duracao == '':
            self.errorMes("Error", "Chuva para duracao especifica: Insira valor para duracao")
            return None
        elif float(duracao) < 10:
            self.errorMes("Error", "Chuva para duracao especifica: Insira valor maior que o mínimo (10 minutos)")
            return None
        chuvaFinal = self.chuvaFinal()
        if chuvaFinal is None:
            self.errorMes("Error", "Insira coordenadas localizadas no Brasil ou em WGS84")
            return None
        intensidade = self.intensidade()
        if intensidade is None:
            self.errorMes("Error", "Insira coordenadas localizadas no Brasil ou em WGS84")
            return None    
        listaTempo = self.listaTempo()
        
        #torna PorcentagemChuva e RelacaoTempo array
        arrayPorcentagemChuva = np.asarray(chuvaFinal)
        arrayRelacaoTempo = np.asarray(listaTempo)
        arrayIntensidade = np.asarray(intensidade)
            
        #transforma a duracao em float
        duracao = float(duracao)    
            
        #realiza a interpolacao para precipitacao e para a intensidade
        interPrec = interpolate.interp1d(arrayRelacaoTempo, arrayPorcentagemChuva)
        interInt = interpolate.interp1d(arrayRelacaoTempo, arrayIntensidade)        

        precUsuario = str(np.round(interPrec(duracao),2))
        intUsuario = str(np.round(interInt(duracao),2))
        
        self.dlg.prec_final.setText(precUsuario)
        self.dlg.int_final.setText(intUsuario)
            
            
    def rodarChuvaProjeto(self):
                        
        #Verifição dados iniciais
        dadosIniciais = self.verDadosIniciais()
        if dadosIniciais is False:
            return None
            
        #Verificação dados modelo
        ret_line = self.getRet()
        diretorio = self.getDir()
        relacaoTempo = self.listaTempo()
        chuvaFinal = self.chuvaFinal()
        if chuvaFinal is None:
            self.errorMes("Error", "Insira coordenadas localizadas no Brasil ou em WGS84")
            return None    
        intervaloTempo = self.dlg.intTempo.text()
        if intervaloTempo == '':
            self.errorMes("Error", "Chuva de projeto: Insira valor para intervalo de tempo")
            return None              
        if float(intervaloTempo) < 10:
            self.errorMes("Error", "Chuva de projeto: Valor de intervalo de tempo menor que o minimo (10 min)")
            return None  
        intervaloTempo = float(intervaloTempo)
        durChuva = self.dlg.durChuva.text()
        if durChuva == '':
            self.errorMes("Error", "Chuva de projeto: Insira valor para duracao da chuva")
            return None  
        if float(durChuva) > 24:
            self.errorMes("Error", "Chuva de projeto: Valor de duracao da chuva maior que o maximo (24 horas)")
            return None 
        durChuva = float(durChuva) 
        posicaoPico = self.dlg.posPico.text()
        if posicaoPico == '':
            self.errorMes("Error", "Chuva de projeto: Insira valor para posicao do pico")
            return None  
        elif float(posicaoPico) < 1 or float(posicaoPico) > 100:
            self.errorMes("Error", "Chuva de projeto: Insira valor em porcentagem para posicao do pico") 
            return None 
        posicaoPico = (float(posicaoPico)/100)

        direBlocos = diretorio + '\\blocos_alternados_' + ret_line + 'anos_' + str(int(intervaloTempo)) + '.pdf'
        
        chuvaEntrada = interpolador(chuvaFinal, relacaoTempo, intervaloTempo, durChuva)[1]
        tempo = interpolador(chuvaFinal, relacaoTempo, intervaloTempo, durChuva)[0]
        chuvaDesacumulada = desacumulador(chuvaEntrada)
        
        if intervaloTempo == 5:
            numero_intervalos = (((durChuva*60)/intervaloTempo)-1)
        else:
            numero_intervalos = ((durChuva*60)/intervaloTempo)
                        
        blocosAlternados = self.aplicar_BlocosAlternados(chuvaDesacumulada, numero_intervalos, posicaoPico)
        titulo = 'Metodo dos Blocos Alternados para TR = ' + ret_line
        plotarBarra(tempo, blocosAlternados, titulo, 'Tempo (min)', 'Precipitacao (mm)', direBlocos)
        
        self.dlg.valorPico.setText(str(round(max(blocosAlternados), 2)))
        
        #Salva em txt
        filename = diretorio + '\\BlocosAlternados_' + str(intervaloTempo) + '.txt'            
        output_file = open(filename, 'w')
        #Escreve o valor de precipitação e duração inseridos pelo usuário
        for i in range(len(blocosAlternados)):
            output_file.write(str(round(blocosAlternados[i],2)) + " " + str(int(tempo[i])) + "\n")
        output_file.close()
                
    def rodarIDF(self):
            
       #Verifição dados iniciais
        dadosIniciais = self.verDadosIniciais()
        if dadosIniciais is False:
            return None 

        #Verificação dados do modelo
        relacaoTempo = self.listaTempo()
        ret_line = self.getRet()
        diretorio = self.getDir()
        intensidade = self.intensidade()
        if intensidade is None:
            self.errorMes("Error", "Insira coordenadas localizadas no Brasil ou em WGS84")
            return None

        #Chama a função plotagem para configurar o gráfico de precipitação x duração
        direGrafico2 = diretorio + '\\int_dur_' + ret_line + '.pdf'
        titulo2 = 'Grafico da Intensidade (mm/h) x Duracao (min) para TR = ' + ret_line
        plotarLinha(relacaoTempo, intensidade, titulo2 , 'Duracao (min)' , 'Intensidade (mm/h)', direGrafico2)
        
        #Salva em txt
        filename = diretorio + '\\dadosIDF_' + ret_line + '.txt'            
        output_file = open(filename, 'w')
        #Escreve o valor de precipitação e duração inseridos pelo usuário
        for i in range(len(intensidade)):
            output_file.write(str(round(intensidade[i],2)) + " " + str(int(relacaoTempo[i])) + "\n")
        output_file.close()
                
    def rodarPDF(self):
                        
        #Verifição dados iniciais
        dadosIniciais = self.verDadosIniciais()
        if dadosIniciais is False:
            return None     
         
        #Verificação dados modelo
        relacaoTempo = self.listaTempo()
        ret_line = self.getRet()
        diretorio = self.getDir()
        chuvaFinal = self.chuvaFinal()
        if chuvaFinal is None:
            self.errorMes("Error", "Insira coordenadas localizadas no Brasil ou em WGS84")
            return None
        
        #Chama a função plotagem para configurar o gráfico de precipitação x duração
        direGrafico1 = diretorio + '\\prec_dur_' + ret_line + '.pdf'
        titulo1 = 'Grafico da Precipitacao (mm) x Duracao (min) para TR = ' + ret_line
        plotarLinha(relacaoTempo, chuvaFinal, titulo1, 'Duracao (min)', 'Precipitacao (mm)', direGrafico1)
        
        #Salva em txt
        filename = diretorio + '\\dadosPDF_' + ret_line + '.txt'            
        output_file = open(filename, 'w')
        #Escreve o valor de precipitação e duração inseridos pelo usuário
        for i in range(len(chuvaFinal)):
            output_file.write(str(round(chuvaFinal[i],2)) + " " + str(int(relacaoTempo[i])) + "\n")
        output_file.close()
            
        