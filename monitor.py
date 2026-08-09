import os
import datetime
import urllib.parse
import feedparser
import google.generativeai as genai

def buscar_noticias():
    # Consultas baseadas em palavras-chave inteligentes (substituindo o 'site:' que falha no RSS)
    queries = [
        '("Atlético Mineiro" OR "Galo") when:1d',
        '(Itatiaia AND ("Atlético Mineiro" OR "Galo")) when:1d',
        '("O Tempo" AND ("Atlético Mineiro" OR "Galo")) when:1d',
        '(("Fala Galo" OR "Frossard" OR "Eu Acredito" OR "Itatiaia Esporte") AND ("Atlético Mineiro" OR "Galo")) when:1d'
    ]
    
    todas_noticias = []
    links_visitados = set()

    for q in queries:
        encoded_query = urllib.parse.quote(q)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=pt-BR&gl=BR&ceid=BR:pt-BR"
        
        feed = feedparser.parse(rss_url)
        for entry in feed.entries:
            if entry.link not in links_visitados:
                todas_noticias.append(entry)
                links_visitados.add(entry.link)
    
    return todas_noticias

def analisar_com_ia(noticias):
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    
    texto_noticias = "NOTÍCIAS COLETADAS:\n"
    for i, n in enumerate(noticias[:35], 1):
        texto_noticias += f"Notícia {i}: {n.title} (Link: {n.link})\n"

    prompt = f"""
    Você é um analista esportivo de alto nível e inteligência de dados focado no Clube Atlético Mineiro.
    Abaixo estão as manchetes coletadas. Dê prioridade e destaque explícito às matérias e análises das fontes prioritárias (Itatiaia, O Tempo, Fala Galo, Frossard e Eu Acredito) que aparecem no conjunto de dados.
    
    {texto_noticias}
    
    Analise profundamente esse material e escreva um relatório profissional em Markdown seguindo RIGOROSAMENTE esta estrutura:
    
    # 🐔 Dossiê Analítico do Atlético Mineiro - {datetime.datetime.now().strftime("%d/%m/%Y")}
    
    ## 📊 Resumo Quantitativo & Qualitativo
    - **Total por Tipo de Notícia / Assunto:** (Contagem absoluta por categoria).
    - **Índice de Tom / Clima da Cobertura:** (Positivo, Neutro, Tenso/Crítico).
    - **Matriz de Foco Temático com Proporção:** (Distribuição percentual dos temas).
    - **Raio-X dos Veículos:** (Destaque expressivo para a cobertura da Itatiaia, O Tempo e dos influenciadores/blogs citados).
    - **Indicador de "Ruído vs. Fato":** (Análise de furos vs. repetições).
    
    ## 🌡️ Termômetro da Torcida e Ambiente
    [Analise o clima geral do clube e a pressão atual].
    
    ## 💰 Lupa nas Finanças e Gestão da SAF
    [Resuma atualizações econômicas e de gestão].
    
    ## ⚽ Visão Clínica de Campo (Foco Técnico)
    [Análise tática, boletim do DM e escalação].
    
    ## 🏟️ Logística de Jogo e "Galo na Veia"
    [Ingressos, Arena MRV e Sócio-Torcedor].
    
    ## ⚔️ Seção Especial de Jogo (Se houver partida)
    - **O Termômetro da Imprensa:** (Consenso dos jornalistas locais e nacionais).
    - **A Prancheta Tática:** (Escalações e desfalques).
    - **Previsões e Tendências Esportivas:** (Palpites e visão de mercado).
    - **O Fator Adversário:** (Momentos do rival).
    
    ## 📰 Principais Notícias (Top 5 - Dê preferência absoluta às fontes prioritárias)
    """

    modelo_escolhido = None
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                modelo_escolhido = m.name
                break
    except:
        modelo_escolhido = 'gemini-1.5-flash'

    modelo = genai.GenerativeModel(modelo_escolhido)
    resposta = modelo.generate_content(prompt)
    return resposta.text

def main():
    noticias = buscar_noticias()
    
    if not noticias:
        relatorio = f"# 🐔 Dossiê do Galo ({datetime.datetime.now().strftime('%d/%m/%Y')})\nNenhuma notícia encontrada."
    else:
        try:
            relatorio = analisar_com_ia(noticias)
        except Exception as e:
            relatorio = f"# Erro na IA\nDetalhes: {e}"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(relatorio)
        
    os.makedirs("relatorios", exist_ok=True)
    with open(f"relatorios/noticias_{datetime.datetime.now().strftime('%Y-%m-%d')}.md", "w", encoding="utf-8") as f:
        f.write(relatorio)

if __name__ == "__main__":
    main()
