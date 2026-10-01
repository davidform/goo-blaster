"""Shared book navigation for bounded game screens; all eleven languages."""
import json
from pathlib import Path
DATA={
'en':['Previous page','Next page','{0} / {1}'],
'zh-Hant':['上一頁','下一頁','第 {0} / {1} 頁'],
'zh-Hans':['上一页','下一页','第 {0} / {1} 页'],
'ja':['前のページ','次のページ','{0} / {1} ページ'],
'ko':['이전 페이지','다음 페이지','{0} / {1} 페이지'],
'de':['Vorherige Seite','Nächste Seite','Seite {0} / {1}'],
'fr':['Page précédente','Page suivante','Page {0} / {1}'],
'es':['Página anterior','Página siguiente','Página {0} / {1}'],
'it':['Pagina precedente','Pagina successiva','Pagina {0} / {1}'],
'pt-BR':['Página anterior','Próxima página','Página {0} / {1}'],
'ru':['Предыдущая страница','Следующая страница','Страница {0} / {1}']}
HELP={'en':'Help','zh-Hant':'說明','zh-Hans':'说明','ja':'説明','ko':'도움말','de':'Hilfe','fr':'Aide','es':'Ayuda','it':'Aiuto','pt-BR':'Ajuda','ru':'Помощь'}
TABS={'en':['Grow','Cook','Orders','Decorate'],'zh-Hant':['種植','料理','委託','佈置'],'zh-Hans':['种植','料理','委托','布置'],'ja':['栽培','料理','依頼','配置'],'ko':['재배','요리','주문','꾸미기'],'de':['Anbau','Küche','Aufträge','Deko'],'fr':['Cultiver','Cuisine','Commandes','Décorer'],'es':['Cultivos','Cocina','Pedidos','Decorar'],'it':['Coltiva','Cucina','Ordini','Decora'],'pt-BR':['Cultivar','Cozinha','Pedidos','Decorar'],'ru':['Растения','Кухня','Заказы','Декор']}
if __name__=='__main__':
 p=Path(__file__).resolve().parents[1]/'index.html';s=p.read_text(encoding='utf-8')
 old=next(x for x in s.splitlines() if x.startswith('const L10N='));d=json.loads(old[11:-1]);assert set(d)==set(DATA)
 for lang,values in DATA.items():
  d[lang].update(zip(['pagePrevious','pageNext','pageCount'],values));d[lang]['uiHelp']=HELP[lang];d[lang].update(zip(['gardenTabFarm','gardenTabKitchen','gardenTabCommunity','gardenTabDecorate'],TABS[lang]))
 p.write_text(s.replace(old,'const L10N='+json.dumps(d,ensure_ascii=False)+';'),encoding='utf-8')
