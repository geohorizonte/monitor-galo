import os
import datetime
import urllib.parse
import feedparser
import google.generativeai as genai

def buscar_noticias():
    query = '("Atlético Mineiro" OR "Galo") when:1d'
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=pt-BR&gl=BR&ceid=BR:pt-BR"
    feed = feedparser.parse(rss_url)
    return feed.entries

def analisar_com_ia(noticias):
    # Puxa a chave de segurança armazenada nos Secrets do GitHub de forma segura
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    
    texto_noticias = ""
    for i, n in enumerate(noticias[:25], 1):
        texto_noticias += f"Notícia {i}: {n.title} (Link: {n.link})\n"

    prompt = f"""
    Você é um analista esportivo de alto nível focado no Clube Atlético Mineiro.
    Abaixo estão as manchetes das últimas 24 horas sobre o time:
    
    {texto_noticias}
    
    Escreva um relatório profissional em Markdown seguindo EXATAMENTE esta estrutura:
    
    # 🐔 Relatório Analítico do Atlético Mineiro - {datetime.datetime.now().strftime("%d/%m/%Y")}
    
    ## 📊 Resumo Quantitativo
    [Faça uma lista agrupando quantas notícias falaram sobre Mercado da Bola, Problemas Táticos/Lesões, Diretoria/Bastidores, etc.]
    
    ## ⚽ Análise Técnica
    [Analise se há problemas recorrentes citados nas matérias, desfalques, pressão sobre comissão técnica ou jogadores específicos]
    
    ## 🏢 Bastidores e Diretoria
    [Resuma o que está acontecendo fora de campo: SAF, finanças, declarações de dirigentes, polêmicas]
    
    ## 📰 Principais Notícias (Top 5)
    [Faça uma lista com as 5 notícias mais importantes, com seus respectivos links, e 2 linhas de resumo para cada uma. Tente diversificar os temas.]
    """

    # Atualizado para a versão clássica e super estável (gemini-pro)
    modelo = genai.GenerativeModel('gemini-pro')
    resposta = modelo.generate_content(prompt)
    
    return resposta.text

def main():
    noticias = buscar_noticias()
    
    if not noticias:
        relatorio = f"# 🐔 Relatório do Galo ({datetime.datetime.now().strftime('%d/%m/%Y')})\nNenhuma notícia encontrada nas últimas 24 horas."
    else:
        try:
            relatorio = analisar_com_ia(noticias)
        except Exception as e:
            relatorio = f"# Erro na IA\nNão foi possível gerar a análise inteligente. Erro: {e}"

    # Salva na página inicial do repositório (README)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(relatorio)
        
    # Salva o histórico na pasta relatorios para você ter o arquivo de cada dia
    os.makedirs("relatorios", exist_ok=True)
    nome_arquivo = f"relatorios/noticias_{datetime.datetime.now().strftime('%Y-%m-%d')}.md"
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(relatorio)

if __name__ == "__main__":
    main()
