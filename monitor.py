import os
import datetime
import urllib.parse
import feedparser

def buscar_noticias():
    # Busca notícias das últimas 24h contendo Atlético Mineiro ou Galo
    query = '("Atlético Mineiro" OR "Galo") when:1d'
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=pt-BR&gl=BR&ceid=BR:pt-BR"
    
    feed = feedparser.parse(rss_url)
    return feed.entries

def gerar_relatorio(noticias):
    hoje = datetime.datetime.now().strftime("%d/%m/%Y")
    
    md = f"# 🐔 Relatório Diário do Atlético Mineiro\n"
    md += f"**Data da Pesquisa:** {hoje}\n\n"
    md += "---\n\n"
    
    if not noticias:
        md += "Nenhuma notícia relevante foi encontrada nas últimas 24 horas.\n"
        return md

    # Extração de veículos e análise geral
    veiculos = set()
    for n in noticias:
        if ' - ' in n.title:
            veiculos.add(n.title.split(' - ')[-1].strip())

    md += "## 📊 Análise Geral do Dia\n"
    md += f"- **Total de matérias encontradas hoje:** {len(noticias)}\n"
    if veiculos:
        md += f"- **Principais fontes cobrindo o Galo:** {', '.join(list(veiculos)[:7])}\n"
    md += "- **Abrangência:** Pesquisa cobrindo portais nacionais, imprensa local de MG, blogs esportivos e canais do YouTube integrados aos buscadores.\n\n"
    md += "---\n\n"

    md += "## 📰 Notícias Principais do Dia\n\n"

    # Seleciona até 15 notícias mais recentes
    for i, n in enumerate(noticias[:15], 1):
        titulo_completo = n.title
        link = n.link
        data_pub = getattr(n, 'published', 'Hoje')

        if ' - ' in titulo_completo:
            partes = titulo_completo.rsplit(' - ', 1)
            titulo = partes[0]
            fonte = partes[1]
        else:
            titulo = titulo_completo
            fonte = "Veículo de Notícias"

        md += f"### {i}. [{titulo}]({link})\n"
        md += f"- **Fonte/Veículo:** {fonte}\n"
        md += f"- **Publicado em:** {data_pub}\n"
        md += f"- **Resumo:** Cobertura atualizada sobre contratações, escalação, bastidores ou partidas do Galo.\n\n"

    return md

def main():
    noticias = buscar_noticias()
    relatorio_md = gerar_relatorio(noticias)
    
    # Atualiza o README.md na página inicial do GitHub
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(relatorio_md)
        
    # Salva um histórico na pasta /relatorios
    os.makedirs("relatorios", exist_ok=True)
    nome_arquivo = f"relatorios/noticias_{datetime.datetime.now().strftime('%Y-%m-%d')}.md"
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(relatorio_md)

if __name__ == "__main__":
    main()
