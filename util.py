# funções de utilidade 
import numpy as np
import pandas as pd
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr
import os
from scipy.optimize import root_scalar

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

datadir = os.path.join(os.path.abspath(os.path.dirname(__file__)),'data')
sisudir = os.path.join(os.path.abspath(os.path.dirname(__file__)),'sisu')

def load_sample(ano,n=None,perc=1,orig=False):
    '''Retorna dataframe com n linhas da prova ENEM do ano.

    Depende da amostra gerada no notebook 00-PrepareData
    '''
    if orig:
        fn = os.path.join(datadir,f'enem_{perc}_{ano}_orig.csv')
    else:
        fn = os.path.join(datadir,f'enem_{perc}_{ano}.csv')
    df = pd.read_csv(fn)
    if n:
        return df.sample(n)
    else:
        return df

def load_acertos(ano,area,n=None,perc=1,remove_abandonados=True,prova=None,acertos=None,percentil=None):
    assert ano in range(2009,2024)
    assert area in ['CN','CH','MT','LC','LC_en','LC_esp']
    fn = os.path.join(datadir,f'ac_{perc}_{ano}_{area}.csv')
    resp = pd.read_csv(fn,index_col='candidato')
    if acertos:
        resp = resp.query("acertos == @acertos")
    if percentil:
        resp = resp[pd.qcut(resp['nota_inep'],100,labels=range(1,101)) == percentil]
    if prova:
        assert prova in resp['caderno'].unique()
        resp = resp.query('caderno == @prova')
    if remove_abandonados:
        removed_columns = [col for col in resp.columns if col.endswith('-aban')]
        resp = resp.drop(columns=removed_columns)
    if n:
        return resp.sample(n)
    else:
        return resp

def item_info_inep(ano=None,area=None,cor=None,prova=None,item=None,list_criteria=False):
    '''Retorna as informações sobre itens do INEP, filtrando pelos critérios dados.

    Se prova ou item são dados, retorna os itens correspondentes.
    Se ano, area ou cor são dados, filtra com "E" lógico.
    '''

    fn = os.path.join(datadir,'itens_inep.csv')
    itens = pd.read_csv(fn,dtype={'CO_ITEM':str})
    
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


def item_stats(ano,area,perc=1):
    acertos  = load_acertos(ano, area, n=None,perc=perc,remove_abandonados=False)
    resp = acertos.iloc[:,:-3]
    resp.rename(columns=rename_aban,inplace=True)
    istats = mirt.itemstats(to_rdf(resp))
    istats = to_df(istats[1])
    #istats.index = istats.index.astype(int)
    #istats.index = istats.index
    item_info = item_info_inep(ano,area)
    item_info = item_info.drop_duplicates(subset=['CO_ITEM'],keep='first')
    item_info.insert(0,'url',item_info['CO_ITEM'].apply(item_url))
    item_info = item_info.set_index('CO_ITEM')
    #item_info.index = item_info.index.astype(str)
    istats = pd.merge(istats,item_info,how='left',left_index=True,right_index=True,validate='1:m')
    #istats = istats.drop(columns=['total.r_if_rm','alpha_if_rm'])
    return istats

def provas(ano,area,pickone=False):
    'retorna as provas (cadernos) em nossas amostras de um determinado ano / area'
    
    amostra = load_acertos(ano,area,10000)
    provas = amostra['caderno'].unique()
    if pickone:
        return np.random.choice(provas)
    else:
        return provas

def params_inep(ano=None,area=None,prova=None,dropna=True):
    if prova:
        params = item_info_inep(prova=prova)
    else:
        prova = provas(ano,area,True)
        params = item_info_inep(prova=prova)
    params = params[["CO_ITEM","NU_PARAM_A","NU_PARAM_B","NU_PARAM_C"]]
    params['CO_ITEM'] = params['CO_ITEM']
    params = params.set_index("CO_ITEM")
    params.columns = ["a_inep","b_inep","c_inep"]
    params['u'] = 1
    if dropna:
        return params.dropna()
    else:
        return params

def load_padr(prova,n=None,nota_inep=False, percentil = None):
    'Carrega um padrão de resposta aleatório. Retorna padrões de resposta'
    perc = 1 #TODO: generalizar para quando temos outras porcentagens
    ano = item_info_inep(prova=prova)['ano'].iloc[0]
    area = item_info_inep(prova=prova)['SG_AREA'].iloc[0]
    fn = os.path.join(datadir,f'ac_{perc}_{ano}_{area}.csv')
    resp = pd.read_csv(fn,index_col='candidato')
    assert prova in resp['caderno'].unique()
    resp = resp.query('caderno == @prova')
    if percentil:
        resp = resp[pd.qcut(resp['nota_inep'],100,labels=range(1,101)) == percentil]
    if n:
        resp = resp.sample(n)
    removed_columns = [col for col in resp.columns if col.endswith('-aban')]
    # em 2011 o inep não deu os parámetros do item 73678 (mas não indicou que era abandonado)
    resp = resp.drop(columns=removed_columns)
    resp1 = resp.iloc[:,:-3]
    resp1.columns = resp1.columns.astype(int)
    resp1 = resp1.sort_index(axis=1) # se não fizer isso, os itens (colunas nestas padrões de resposta) não correspondem ao modelo mod_inep acima
    if nota_inep:
        notas = resp.iloc[:,-3:]
        return resp1,notas
        
    return resp1

def scalecalparams(area):        
    fn = os.path.join(datadir,f'scorecal-python-100.csv')
    df = pd.read_csv(fn)
    df = df[df['stderr'] < 0.01]
    df = df.query("area == @area")
    return df['slope'].mean(),df['intercept'].mean()
    
def notas_to_enem_scale(notas,area):
    slope,intercept = scalecalparams(area)
    return notas*slope + intercept

def irt_params_to_enem_scale(params,area):
    params = params.copy()
    slope,intercept = scalecalparams(area)
    params['b_inep'] = params['b_inep']*slope + intercept
    params['a_inep'] = params['a_inep']*slope
    return params
    
def score_inep(padr,ano,area,params = None, method="EAP",enemscale=False):
    if params is None:
        params = params_inep(ano,area,dropna=True)

    # padr pode conter colunas acertos, prova e nota_inep. Vamos tirar.
    if 'nota_inep' in padr.columns:
        padr = padr.iloc[:,:-3]

    # ter certeza que as colunas em padr são strings
    padr.columns = padr.columns.astype(str)
    
    assert len(params) == len(padr.columns), f"Length of params ({len(params)} is not equal to length of padr ({len(padr.columns)})"
    # transformar os parâmetros de discriminação /  dificuldade de IRT para "slope / intercept" do mirt.

    params = params.reindex(padr.columns)
    
    params = mirt.traditional2mirt(to_rdf(params),"3PL")
    mod_inep = mirtcat.generate_mirt_object(to_rdf(params),itemtype = '3PL')
    
    score = mirt.fscores(mod_inep,method=method,full_scores=False,verbose=True,response_pattern = to_rdf(padr))
    nota = to_df(score)[:,0]
    se = to_df(score)[:,1]
    
    if enemscale:
        slope, intercept = scalecalparams(area)
        nota = slope*nota + intercept
        se = slope*se
    return pd.DataFrame({'nota':nota, 'se':se},index=padr.index)

def notas_sisu(ano,edicao):
    
    arquivo = f"{sisudir}/orig/{ano}_{edicao}_sisu.csv"
    df = pd.read_csv(arquivo)
    if ano >= 2019:
        colunas = ['NO_IES','SG_IES','DS_CATEGORIA_ADM','SG_UF_CAMPUS','NO_CURSO','DS_TURNO','QT_VAGAS_CONCORRENCIA','QT_INSCRICAO','NU_NOTACORTE']
        if ano >= 2024:
            colunas = ['NO_IES','SG_IES','DS_CATEGORIA_ADM','SG_UF_CAMPUS','NO_CURSO','DS_TURNO','QT_VAGAS_OFERTADAS','QT_INSCRICAO','NU_NOTACORTE']
        novocols = ['ies','sg_ies','catadm','uf','curso','turno','vagas','inscricoes','notacorte']
        # TODO: generalizar para filtrar por cotas
        df = df[df['DS_MOD_CONCORRENCIA'] == 'Ampla concorrência']
        df = df[colunas]
        df.columns = novocols
    else:    
        colunas = ['NOME IES','SIGLA IES','NOME CURSO','TURNO','NOTA DE CORTE']
        novocols = ['ies','sg_ies','curso','turno','notacorte']
        df = df[df['TIPO MODALIDADE'] == 'Ampla Concorrência']
        df = df[colunas]
        df.columns = novocols
    return df

def PL3(theta,a=1,b=0,c=0):
    '3PL model likelihood'
    return c + (1-c)*1/(1+np.exp(a*(b-theta)))

def find_theta(a,b,c,prob=0.65):
    'Find the theta with RP (Response Probability) = prob, for the 3PL model with a,b and c'
    def fun(x,a,b,c):
        return PL3(x,a,b,c) - prob
    
    res = root_scalar(fun,x0=b,x1=b*1.2,bracket=[-abs(b)*4,abs(b)*4],args=(a,b,c))
    if res.converged:
        return res.root
    else:
        return np.NaN