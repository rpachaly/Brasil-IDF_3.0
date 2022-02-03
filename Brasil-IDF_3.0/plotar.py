# -*- coding: utf-8 -*-
""" Desenvolvido por PACHALY (2017) """

"""" Este algoritmo realizar plotagem de gráficos por linha ou por barras """

import matplotlib.pyplot as plt
import webbrowser

def plotarLinha(x, y, titulo, teixox, teixoy, diretorio):
    plt.close()
    plt.plot(x, y)
    plt.title(titulo)
    plt.xlabel(teixox)
    plt.ylabel(teixoy)
    plt.grid(True)
    plt.savefig(diretorio)
    plt.close()
    webbrowser.open(diretorio)
        
def plotarBarra(x, y, titulo, teixox, teixoy, diretorio):

    plt.close()
    plt.bar(x, y, align='center', alpha=1, width = 5)
    plt.title(titulo)
    plt.xlabel(teixox)
    plt.ylabel(teixoy)
    plt.grid(True)
    plt.savefig(diretorio)
    plt.close()
    webbrowser.open(diretorio)



#chuva = [0.81,1.51,1.51,1.51,2.89,4.84,16.17,7.43,3.34,2.43,1.51,1.51,1.51,0.81,0.81,0.81,0.81,0.81,0.81,0.81,0.81,0.81,0.81,0.81]
#tempo = [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240]
#plotarBarra(tempo, chuva, 'lalala', 'lelele', 'lilili', "barra.pdf")