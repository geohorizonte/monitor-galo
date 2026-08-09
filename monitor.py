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
    # Puxa a chave de segurança armazenada nos Secrets do GitHub
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

    # Lista de modelos para testar (do mais rápido/recente para o mais antigo)
    modelos_disponiveveis = [
        'gemini-1.5-flash',
        'gemini-1.5-flash-latest',
        'gemini-1.5-pro',
        'gemini-1.5-pro-latest',
        'gemini-1.0-pro',
        'gemini-pro'
    ]

    resposta_texto = None
    ultimo_erro = None

    # Mecanismo de fallback: testa um por um até funcionar
    for nome_modelo in modelos_disponiveveis:
        try:
            print(f"Tentando usar o modelo: {nome_modelo}...")
            modelo = genai.GenerativeModel(nome_modelo)
            resposta = modelo.generate_content(prompt)
            resposta_texto = resposta.text
            print(f"Sucesso com o modelo: {nome_modelo}!")
            break  # Sai do loop assim que funcionar
        except Exception as e:
            ultimo_erro = e
            print(f"Falha no modelo {nome_modelo}: {e}")
            continue  # Pula para o próximo modelo da lista

    # Se percorreu toda a lista e não conseguiu, levanta o erro final
    if resposta_texto:
        return resposta_texto
    else:
        raise Exception(f"Todos os modelos falharam. Último erro: {ultimo_erro}")

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
        
    # Salva o histórico na pasta relatorios
    os.makedirs("relatorios", exist_ok=True)
    nome_arquivo = f"relatorios/noticias_{datetime.datetime.now().strftime('%Y-%m-%d')}.md"
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(relatorio)

if __name__ == "__main__":
    main()
