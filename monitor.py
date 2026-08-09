import os
import datetime
import urllib.parse
import feedparser
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

def buscar_itatiaia_direto():
    # Acessa diretamente a editoria do Atlético na Itatiaia para garantir 100% de captura
    noticias_itatiaia = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        url = 'https://www.itatiaia.com.br/esportes/futebol/futebol-nacional/futebol-mineiro/atletico/'
        resposta = requests.get(url, headers=headers, timeout=10)
        
        if resposta.status_code == 200:
            soup = BeautifulSoup(resposta.text, 'html.parser')
            # Procura por links de matérias no site
            for a in soup.find_all('a', href=True):
                href = a['href']
                titulo = a.get_text().strip()
                # Filtra apenas links que parecem notícias de esportes e possuem títulos válidos
                if ('/esportes/' in href or '/noticia/' in href) and len(titulo) > 20:
                    link_completo = href if href.startswith('http') else 'https://www.itatiaia.com.br' + href
                    # Padroniza no formato que o código espera
                    class Entidade:
                        def __init__(self, title, link):
                            self.title = f"{titulo} - Itatiaia"
                            self.link = link
                    noticias_itatiaia.append(Entidade(titulo, link_completo))
    except Exception as e:
        print(f"Erro ao buscar direto na Itatiaia: {e}")
        
    return noticias_itatiaia

def buscar_noticias():
    # 1. Busca ampla via Google News (Galo, O Tempo, etc.)
    queries = [
        '("Atlético Mineiro" OR "Galo") when:1d',
        '("O Tempo" AND ("Atlético Mineiro" OR "Galo")) when:1d'
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

    # 2. Insere diretamente as notícias raspadas da Itatiaia
    noticias_ita = buscar_itatiaia_direto()
    for item in noticias_ita:
        if item.link not in links_visitados:
            todas_noticias.insert(0, item) # Joga a Itatiaia para o topo da lista (prioridade)
            links_visitados.add(item.link)
            
    return todas_noticias

def analisar_com_ia(noticias):
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    
    texto_noticias = "NOTÍCIAS COLETADAS (Dê prioridade máxima analítica e de citação para a Rádio Itatiaia e O Tempo):\n"
    for i, n in enumerate(noticias[:35], 1):
        texto_noticias += f"Notícia {i}: {n.title} (Link: {n.link})\n"

    prompt = f"""
    Você é um analista esportivo de alto nível e inteligência de dados focado no Clube Atlético Mineiro.
    Abaixo estão as manchetes coletadas. Dê prioridade e destaque explícito às matérias da Itatiaia e do O Tempo que constam na lista.
    
    {texto_noticias}
    
    Analise profundamente esse material e escreva um relatório profissional em Markdown seguindo RIGOROSAMENTE esta estrutura:
    
    # 🐔 Dossiê Analítico do Atlético Mineiro - {datetime.datetime.now().strftime("%d/%m/%Y")}
    
    ## 📊 Resumo Quantitativo & Qualitativo
    - **Total por Tipo de Notícia / Assunto:** (Contagem absoluta por categoria).
    - **Índice de Tom / Clima da Cobertura:** (Positivo, Neutro, Tenso/Crítico).
    - **Matriz de Foco Temático com Proporção:** (Distribuição percentual dos temas).
    - **Raio-X dos Veículos:** (Destaque expressivo para a cobertura da Itatiaia e O Tempo).
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
    
    ## 📰 Principais Notícias (Top 5 - Dê preferência absoluta à Itatiaia e O Tempo)
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
