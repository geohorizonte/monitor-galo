import os
import datetime
import urllib.parse
import feedparser
import google.generativeai as genai

def buscar_noticias():
    # 1. Busca Geral (Google News)
    query = '("Atlético Mineiro" OR "Galo") when:1d'
    encoded_query = urllib.parse.quote(query)
    urls = [
        f"https://news.google.com/rss/search?q={encoded_query}&hl=pt-BR&gl=BR&ceid=BR:pt-BR",
        # 2. Feeds Prioritários (Sites de Notícias)
        "https://www.otempo.com.br/sports/atletico/rss.xml",
        # 3. Feeds YouTube (Convertidos para formato RSS)
        "https://www.youtube.com/feeds/videos.xml?channel_id=UC2Zzj4636i_mqvSdOJddbbQ", # Fala Galo
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCT-l3gJ3kK2VnE888pC225g", # FalaGalo13
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCrB_rN8B0e052c93d9S8lCg", # Canal do Frossard
        "https://www.youtube.com/feeds/videos.xml?channel_id=UC52JjXbW_lJpD2YfN5gK5kA", # Canal Eu Acredito
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCe19eP55X2u0FqjVn7y4U8A"  # Itatiaia Esporte
    ]
    
    todas_noticias = []
    links_visitados = set()

    for url in urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            # Filtro básico: apenas notícias recentes e relevantes
            if entry.link not in links_visitados:
                todas_noticias.append(entry)
                links_visitados.add(entry.link)
    
    return todas_noticias

def analisar_com_ia(noticias):
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    
    # Destaque das fontes prioritárias para a IA
    texto_noticias = "FONTES PRIORITÁRIAS (Favor dar peso extra a estas notícias):\n"
    for i, n in enumerate(noticias[:30], 1):
        texto_noticias += f"Notícia {i}: {n.title} (Link: {n.link})\n"

    prompt = f"""
    Você é um analista esportivo de alto nível e inteligência de dados focado no Clube Atlético Mineiro.
    Abaixo estão as manchetes e notícias coletadas. Dê prioridade analítica às fontes indicadas no topo da lista.
    
    {texto_noticias}
    
    Analise profundamente esse material e escreva um relatório profissional em Markdown seguindo RIGOROSAMENTE esta estrutura:
    
    # 🐔 Dossiê Analítico do Atlético Mineiro - {datetime.datetime.now().strftime("%d/%m/%Y")}
    
    ## 📊 Resumo Quantitativo & Qualitativo
    - **Total por Tipo de Notícia / Assunto:** (Contagem absoluta).
    - **Índice de Tom / Clima da Cobertura:** (Positivo, Neutro, Tenso/Crítico).
    - **Matriz de Foco Temático com Proporção:** (Distribuição percentual).
    - **Raio-X dos Veículos:** (Destaque o que veio das fontes prioritárias: Itatiaia, O Tempo, Canais YouTube).
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
    - **O Termômetro da Imprensa:** (Consenso e narrativa do confronto).
    - **A Prancheta Tática:** (Escalações e desfalques).
    - **Previsões e Tendências Esportivas:** (Palpites e visão de mercado).
    - **O Fator Adversário:** (Momentos do rival).
    
    ## 📰 Principais Notícias (Top 5 - Dê preferência às fontes prioritárias)
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
