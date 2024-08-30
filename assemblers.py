import pandas as pd
import utils
import channels
import os.path
import numpy as np
import assemblers

def sponsorship(source: str):
    coco = channels.coco(source=source)
    nascar = channels.nascar(source=source)
    raiders = channels.raiders(source=source)
    vgk = channels.vgk(source=source)
    wwe = channels.wwe(source=source)
    wso = channels.wso(source=source)
    collected = pd.concat([coco,nascar,raiders,vgk,wwe,wso])
    collected['DATE'] = pd.to_datetime(collected['DATE'])
    spend_file = pd.read_excel(source+r"\\Spend Record 2.xlsx")
    joined = pd.merge(collected,spend_file,on=['Format','Product'],how='left')
    filtered = joined[((joined['DATE']>=joined['START'])&(joined['DATE']<=joined['END']))|(joined['START'].isna())]
    grouped = filtered.groupby(['Format','Product','START','END','AMT SPEND'],as_index=False).agg({'IMPRESSIONS':"sum"})
    spon = pd.merge(collected,grouped,on=["Format","Product"],how='left')
    spon = spon[(spon['DATE']>=spon['START'])&(spon['DATE']<=spon['END'])|(spon['START'].isna())]
    spon = spon.rename(columns={'IMPRESSIONS_x':'IMPRESSIONS',
                                'IMPRESSIONS_y':'grouped_impressions',
                                'AMT SPEND':'SPEND_TOTAL'})
    spon = spon.assign(spend = (spon['IMPRESSIONS'] / spon['grouped_impressions']) * spon['SPEND_TOTAL'])
    spon = spon.rename(columns={'IMPRESSIONS':'TOTAL_IMPRESSIONS',
                                                                'SPEND_TOTAL':'grouped_spend',
                                                                'spend':'TOTAL_SPEND'})
    spon = spon.rename(columns={'Product':'PRODUCT',
                                'date':'DATE',
                                'Format':'FORMAT',
                                'Event':'EVENT',
                                'TOTAL_IMPRESSIONS':'IMPRESSIONS',
                                'TOTAL_SPEND':'SPEND'})
    spon = spon.assign(CLICKS=0)
    spon['CLICKS'] = spon['CLICKS'].astype('float64')
    spon['DATE'] = pd.to_datetime(spon['DATE'])
    spon = spon[[  'DATE'
                ,'FORMAT'
                ,'PRODUCT'
                ,'EVENT'
                ,'PLACEMENT'
                ,'IMPRESSIONS'
                ,'CLICKS'
                ,'SPEND']]
    return spon

def master():
    assumption = utils.assumptions()
    source = assumption['source']
    master = pd.concat([channels.tv(source=source).reset_index(drop=True)
                        ,channels.pr(source=source).reset_index(drop=True)
                        ,channels.social_no_api(source=source).reset_index(drop=True)
                        ,assemblers.sponsorship(source=source).reset_index(drop=True)
                        ,channels.digital(source=source).reset_index(drop=True)
                        ,channels.youtube(source=source).reset_index(drop=True)])
    master_raw = master
    master = master[~master['DATE'].isna()]
    master = master[master['DATE']!=0]
    master['DATE'] = pd.to_datetime(master['DATE'])
    master = master.assign(Year=master['DATE'].dt.year)
    imp = pd.read_excel(os.path.join(utils.assumptions()['source'],r'IMP FACTOR.xlsx'))
    mastera = master[master['FORMAT']=='Sponsorship']
    mastera = pd.merge(mastera,imp,how='left',on=['FORMAT','PRODUCT','Year'])
    masterb = master[master['FORMAT']!='Sponsorship']
    impb = imp[['Year','Weight','Exposure','Error Rate','Qi Score','Notes','Error Rate Platform','imp factor','FORMAT']]
    masterb = pd.merge(masterb,impb,how='left',on=['FORMAT','Year'])
    master = pd.concat([mastera,masterb])
    master['PRODUCT'] = master['PRODUCT'].str.upper()
    return (master,master_raw)

def budget_distribution(mas: pd.DataFrame):
    # Create list of all dates for each format
    formats = ['TV','Streaming','Social','Display','Audio','Radio','PR','Sponsorship']
    s_prods = [['Sponsorship','NASCAR'],['Sponsorship','COCO'],['Sponsorship','VGK'],['Sponsorship','WWE'],['Sponsorship','RAIDERS'],['Sponsorship','AVIATORS']]
    s_prods = pd.DataFrame(s_prods,columns = ['FORMAT','PRODUCT'])
    all_dates = pd.DataFrame()
    for i in formats:
        x = pd.DataFrame(pd.date_range(start='1/1/2020', end='1/01/2025'))
        x = x.rename(columns ={ 0: 'DATE'})
        x = x.assign(FORMAT = i)
        all_dates = pd.concat([all_dates,x])
    all_dates = pd.merge(all_dates,s_prods,on='FORMAT',how='left')
    all_dates = all_dates.fillna('blank')
    all_dates['quarter'] = 'Q'+pd.DatetimeIndex(all_dates['DATE']).quarter.astype('str')+' - '+pd.DatetimeIndex(all_dates['DATE']).year.astype('str')
    dc = all_dates.groupby(['quarter','FORMAT'],as_index=False).agg({'DATE':np.size})
    all_dates = pd.merge(all_dates,dc,how='left',on=['quarter','FORMAT'])
    all_dates = all_dates.rename(columns = {'DATE_x':'DATE',
                                                'DATE_y':'counter'})
    m = mas.assign(PRODUCT = np.where(mas['FORMAT']=='Sponsorship',mas['PRODUCT'],(np.where(mas['FORMAT']!='Sponsorship','blank','blank'))))
    m = m.groupby(['FORMAT','PRODUCT','DATE'],as_index=False).agg({'SPEND':"sum",'IMPRESSIONS':"sum"})
    m['quarter'] = 'Q'+pd.DatetimeIndex(m['DATE']).quarter.astype('str')+' - '+pd.DatetimeIndex(m['DATE']).year.astype('str')
    m['DATE'] = pd.to_datetime(m['DATE'])
    dist = pd.merge(all_dates,m,on=['DATE','FORMAT','PRODUCT'],how='left')
    dist = dist.rename(columns = {'quarter_x':'quarter'})
    budget = utils.assumptions()['budget']
    table = pd.merge(dist,budget,on=['quarter','FORMAT'],how='left')
    return table

def imp_assignment(table: pd.DataFrame):
    imp = utils.assumptions()['imp'] 
    imp = imp[['FORMAT','PRODUCT','Weight','Exposure','Error Rate Platform','Qi Score','imp factor','Year']]
    table['Year'] = table['DATE'].dt.year
    table = pd.merge(table,imp,how='left',on=['FORMAT','PRODUCT','Year'])
    table = table.rename(columns={'FORMAT_x':'FORMAT',
                                    'PRODUCT_x':'PRODUCT'})
    table = table.fillna(0)
    table = table.assign(daily_spend_target=table['Planned Spend']/table['counter'],
                            daily_net_imp_target=table['Planned Net Impressions']/table['counter'],
                            daily_gross_imp_target=table['Planned Gross Impressions']/table['counter'])
    table = table[['DATE'
                    ,'quarter'
                    ,'FORMAT'
                    ,'PRODUCT'
                    ,'SPEND'
                    ,'daily_spend_target'
                    ,'IMPRESSIONS'
                    ,'daily_net_imp_target'
                    ,'Planned Net CPM'
                    ,'daily_gross_imp_target'
                    ,'counter'
                    ,'imp factor']]
    table = table.assign(hasher=table['SPEND']+table['IMPRESSIONS']+table['daily_spend_target']+table['daily_net_imp_target'])
    table = table[table['hasher']>0]
    budget_dataset = table
    return budget_dataset

def output(budget_dataset: pd.DataFrame, master: pd.DataFrame):
    budget_dataset.to_csv(os.path.join(utils.assumptions()['target'],r'BrandBudget.csv'))
    master.to_csv(os.path.join(utils.assumptions()['target'],r'BrandSpendMaster.csv'))
    channels.adelaide(utils.assumptions()['source'],utils.assumptions()['target'])

def tableau_prep():
    m = master()
    addbudget = budget_distribution(mas=m[0])
    addimp = imp_assignment(table=addbudget)
    output(budget_dataset=addimp,master=m[0])
