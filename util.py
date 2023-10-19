# funções de utilidade 
import pandas as pd

def load_sample(ano,n):
    '''Retorna dataframe com n linhas da prova ENEM do ano e area (MT,LC,CH,CN).

    Depende da amostra gerada no notebook 00-PrepareData
    '''
    perc = 1 # usar amostra de 1% por agora
    fn = f'data/enem_{perc}_{ano}.csv'
    df = pd.read_csv(fn)
    return df.sample(n)

def load_acertos(ano,area,n):
    assert ano in range(2009,2023)
    assert area in ['CN','CH','MT']
    perc = 1
    fn = f'data/ac_{perc}_{ano}_{area}.csv'
    df = pd.read_csv(fn)
    return df.sample(n)

def item_info_inep(ano=None,area=None,cor=None,prova=None,item=None,list_criteria=False):
    '''Retorna as informações sobre itens do INEP, filtrando pelos critérios dados.

    Se prova ou item são dados, retorna os itens correspondentes.
    Se ano, area ou cor são dados, filtra com "E" lógico.
    '''
   
    itens = pd.read_csv('data/itens_inep.csv',dtype={'CO_ITEM':str})
    
    if list_criteria:
        anos = itens['ano'].unique()
        areas = itens['SG_AREA'].unique()
        cores = itens['TX_COR'].unique()
        #provas = itens['CO_PROVA'].unique()
        return {'Anos':anos,'Areas':areas,'Cores': cores}

    if prova:
        return itens.query('CO_PROVA == @prova')
    if item:
        return itens.query('CO_ITEM == @item')

    
    if ano:
        itens = itens.query('ano == @ano')
    if area:
        area = area.upper()
        itens = itens.query('SG_AREA == @area')
    if cor:
        cor = cor.upper()
        itens = itens.query('TX_COR == @cor')
        

    return itens