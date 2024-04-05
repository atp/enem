# funções de utilidade 
import pandas as pd
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr

mirt = importr('mirt')
mirtcat = importr("mirtCAT")

def to_rdf(df):
    with (robjects.default_converter + pandas2ri.converter).context():
        rdf = robjects.conversion.get_conversion().py2rpy(df)
    return rdf

def to_df(rdf):
    with (robjects.default_converter + pandas2ri.converter).context():
        df = robjects.conversion.get_conversion().rpy2py(rdf)

    return df

summary = rpy2.robjects.r['summary']
coef = rpy2.robjects.r['coef']
rprint = rpy2.robjects.r['print']

def load_sample(ano,n):
    '''Retorna dataframe com n linhas da prova ENEM do ano e area (MT,LC,CH,CN).

    Depende da amostra gerada no notebook 00-PrepareData
    '''
    perc = 1 # usar amostra de 1% por agora
    fn = f'data/enem_{perc}_{ano}.csv'
    df = pd.read_csv(fn)
    return df.sample(n)

def load_acertos(ano,area,n,remove_abandonados=True,prova=None):
    assert ano in range(2009,2023)
    assert area in ['CN','CH','MT']
    perc = 1 #TODO: generalizar para quando temos outras porcentagens
    fn = f'data/ac_{perc}_{ano}_{area}.csv'
    resp = pd.read_csv(fn,index_col='candidato')
    if prova:
        assert prova in resp['caderno'].unique()
        resp = resp.query('caderno == @prova')
    if remove_abandonados:
        removed_columns = [col for col in resp.columns if col.endswith('-aban')]
        resp = resp.drop(columns=removed_columns)
    return resp.sample(n)

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
        item = str(item)
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


def objurl(ano,pos,gab):
    primdia = segdia = False
    if ano >=2017:
        if pos > 90:
            segdia = True
        if ano >= 2018:
           if pos <= 90:
               primdia = True
    pos = str(pos).zfill(3)
    gab = gab.lower()
    if ano in [2017]:
        gab = gab.upper()
    if ano == 2009:
        return f'https://www.curso-objetivo.br/vestibular/resolucao_comentada/enem/{ano}/{pos}.gif'
    if ano == 2020:
        if primdia:
            url = f'https://www.curso-objetivo.br/vestibular/resolucao_comentada/enem/{ano}/presencial/1dia/{pos}{gab}.gif'
        elif segdia:
            url = f'https://www.curso-objetivo.br/vestibular/resolucao_comentada/enem/{ano}/presencial/2dia/{pos}{gab}.gif'
    else:
        if primdia:
            url = f'https://www.curso-objetivo.br/vestibular/resolucao_comentada/enem/{ano}/1dia/{pos}{gab}.gif'
        elif segdia:
            url = f'https://www.curso-objetivo.br/vestibular/resolucao_comentada/enem/{ano}/2dia/{pos}{gab}.gif'
        else:
            url = f'https://www.curso-objetivo.br/vestibular/resolucao_comentada/enem/{ano}/{pos}{gab}.gif'
        
    return url

def item_url(item):
    try:
        ano,pos,gab = item_info_inep(item=item).query("TX_COR == 'AMARELA'")[['ano','CO_POSICAO','TX_GABARITO']].iloc[0]
    except IndexError:
        return f'{item} not found'
    if ano == 2016:
        pos = pos - 45
    if ano == 2017:
        ano,pos,gab = item_info_inep(item=item).query("TX_COR == 'AZUL'")[['ano','CO_POSICAO','TX_GABARITO']].iloc[0]
        pos = pos + 90
    return objurl(ano,pos,gab)

def rename_aban(itemname):
    return itemname.strip('-aban')


def item_stats(ano,area,cor='AMARELA'):
    acertos  = load_acertos(ano, area, n=10000,remove_abandonados=False)
    resp = acertos.iloc[:,:-3]
    resp.rename(columns=rename_aban,inplace=True)
    istats = mirt.itemstats(to_rdf(resp))
    istats = to_df(istats[1])
    #istats.index = istats.index.astype(int)
    #istats.index = istats.index
    item_info = item_info_inep(ano,area)
    if cor:
        item_info = item_info.query("TX_COR == @cor")
    else:
        item_info = item_info.drop_duplicates(subset=['CO_ITEM'],keep='first')
    item_info.insert(0,'url',item_info['CO_ITEM'].apply(item_url))
    item_info = item_info.set_index('CO_ITEM')
    #item_info.index = item_info.index.astype(str)
    istats = pd.merge(istats,item_info,how='left',left_index=True,right_index=True,validate='1:m')
    istats = istats.drop(columns=['total.r_if_rm','alpha_if_rm'])
    return istats

def provas(ano,area):
    'retorna as provas (cadernos) em nossas amostras de um determinado ano / area'
    
    amostra = load_acertos(ano,area,10000)
    return amostra['caderno'].unique()

def params_inep(prova):
    params = item_info_inep(prova=prova)
    params = params[["CO_ITEM","NU_PARAM_A","NU_PARAM_B","NU_PARAM_C"]]
    params['CO_ITEM'] = params['CO_ITEM'].astype(int)
    params = params.set_index("CO_ITEM")
    params.columns = ["a_inep","b_inep","c_inep"]
    params['u'] = 1
    return params.dropna().sort_index()

def load_padr(prova,n=1,nota_inep=False):
    'Carrega um padrão de resposta aleatório. Retorna padrões de resposta'
    perc = 1 #TODO: generalizar para quando temos outras porcentagens
    ano = item_info_inep(prova=prova)['ano'].iloc[0]
    area = item_info_inep(prova=prova)['SG_AREA'].iloc[0]
    fn = f'data/ac_{perc}_{ano}_{area}.csv'
    resp = pd.read_csv(fn,index_col='candidato')
    assert prova in resp['caderno'].unique()
    resp = resp.query('caderno == @prova')
    resp = resp.sample(n)
    removed_columns = [col for col in resp.columns if col.endswith('-aban')]
    # em 2011 o inep não deu os parámetros do item 73678 (mas não indicou que era abandonado)
    resp = resp.drop(columns=removed_columns)
    resp1 = resp.iloc[:,:-3]
    if nota_inep:
        notas = resp.iloc[:,-3:]
    resp1.columns = resp1.columns.astype(int)
    resp1 = resp1.sort_index(axis=1) # se não fizer isso, os itens (colunas nestas padrões de resposta) não correspondem ao modelo mod_inep acima
    if nota_inep:
        return resp1,notas
        
    return resp1

def score_inep(padr,prova = None,params = None, method="EAP"):
    if prova is None:
        assert params is not None
    if params is None:
        params = params_inep(prova)
    # transformar os parâmetros de discriminação /  dificuldade de IRT para "slope / intercept" do mirt.
    params = mirt.traditional2mirt(to_rdf(params),"3PL")
    mod_inep = mirtcat.generate_mirt_object(to_rdf(params),itemtype = '3PL')
    score = mirt.fscores(mod_inep,method=method,full_scores=True,returnER=False,verbose=True ,response_pattern = to_rdf(padr))
    nota = to_df(score)[:,0]
    se = to_df(score)[:,1]
    return pd.DataFrame({'nota':nota, 'se':se},index=padr.index)