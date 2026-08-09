import os
import datetime
import urllib.parse
import feedparser
import requests
import glob
from bs4 import BeautifulSoup
import google.generativeai as genai

def buscar_itatiaia_direto():
    noticias_itatiaia = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        url = 'https://www.itatiaia.com.br/esportes/futebol/futebol-nacional/futebol-mineiro/atletico/'
        resposta = requests.get(url, headers=headers, timeout=10)
        
        if resposta.status_code == 200:
            soup = BeautifulSoup(resposta.text, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a['href']
                titulo = a.get_text().strip()
                if ('/esportes/' in href or '/noticia/' in href) and len(titulo) > 20:
                    link_completo = href if href.startswith('http') else 'https://www.itatiaia.com.br' + href
                    class Entidade:
                        def __init__(self, title, link):
                            self.title = f"{titulo} - Itatiaia"
                            self.link = link
                    noticias_itatiaia.append(Entidade(titulo, link_completo))
    except Exception as e:
        print(f"Erro ao buscar direto na Itatiaia: {e}")
        
    return noticias_itatiaia

def buscar_noticias():
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

    noticias_ita = buscar_itatiaia_direto()
    for item in noticias_ita:
        if item.link not in links_visitados:
            todas_noticias.insert(0, item) 
            links_visitados.add(item.link)
            
    return todas_noticias

def obter_historico_30_dias():
    historico_texto = ""
    if not os.path.exists("relatorios"):
        return historico_texto
        
    arquivos = glob.glob("relatorios/noticias_*.md")
    arquivos.sort(reverse=True)
    arquivos_30_dias = arquivos[:30]
    
    if not arquivos_30_dias:
        return "Nenhum histórico disponível ainda. Este é o primeiro dia de análise."
        
    for arq in arquivos_30_dias:
        try:
            with open(arq, "r", encoding="utf-8") as f:
                conteudo = f.read()
                historico_texto += f"\n\n--- Relatório Histórico: {arq} ---\n{conteudo}\n"
        except Exception:
            continue
            
    return historico_texto

def analisar_com_ia(noticias, historico):
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    
    texto_noticias = "NOTÍCIAS DE HOJE (Dê prioridade máxima analítica para Itatiaia e O Tempo):\n"
    for i, n in enumerate(noticias[:35], 1):
        texto_noticias += f"Notícia {i}: {n.title} (Link: {n.link})\n"

    prompt = f"""
    Você é um analista esportivo de alto nível focado no Clube Atlético Mineiro.
    
    Abaixo estão as manchetes coletadas HOJE:
    {texto_noticias}
    
    Abaixo está o HISTÓRICO dos últimos 30 dias:
    {historico}
    
    Sua missão é gerar um relatório de leitura RÁPIDA, OBJETIVA e DIRETA. 
    PROIBIDO usar parágrafos longos ou linguagem enrolada. Vá direto ao ponto, use frases curtas e bullet points.
    
    Escreva o relatório profissional em Markdown seguindo RIGOROSAMENTE esta estrutura:
    
    # 🐔 Dossiê do Galo - {datetime.datetime.now().strftime("%d/%m/%Y")}
    
    ## 📊 Resumo Rápido
    - **Total/Assunto:** (Ex: 5 Mercado, 3 SAF, 2 DM).
    - **Tom:** (Positivo, Neutro ou Tenso).
    - **Foco Temático:** (Ex: 50% Mercado, 30% Jogo).
    - **Raio-X:** (Destaque em 1 linha de Itatiaia/O Tempo).
    - **Ruído vs. Fato:** (1 frase sobre furos vs repetições).
    
    ## 🌡️ Termômetro e Ambiente
    - [1 ou 2 tópicos curtos e diretos sobre o clima e pressão do dia].
    
    ## 💰 Lupa na SAF e Finanças
    - [1 ou 2 tópicos diretos com novidades financeiras/gestão, se houver].
    
    ## ⚽ Foco Técnico e DM
    - [Tópicos ultra resumidos sobre Tática, Desempenho e atualizações médicas].
    
    ## 🏟️ Arena MRV e Ingressos
    - [Notas rápidas, se houver novidade].
    
    ## ⚔️ Especial de Jogo (Se houver partida próxima)
    - **Imprensa:** (1 frase de consenso/favoritismo).
    - **Prancheta:** (Escalação provável/desfalques).
    - **Tendências:** (1 frase sobre previsões/odds).
    - **Adversário:** (1 frase sobre o momento do rival).
    
    ## 📈 Radar de Tendências (Visão Macro dos Últimos 30 Dias)
    [Analisando o histórico dos últimos relatórios fornecidos, aponte os padrões do último mês:]
    - **Problemas Crônicos e Táticos:** (Ex: "A defesa tem sofrido críticas contínuas nos últimos 15 dias" ou "O problema da lateral direita persiste desde o início do mês").
    - **Evolução/Involução:** (Ex: "Houve uma melhora notável na aceitação do esquema tático nas últimas semanas" ou "O clima da torcida piorou significativamente após os últimos três empates").
    - **Movimentação Extracampo e SAF:** (Padrões de comportamento, finanças e contratações que se desenharam ao longo do último mês).
    
    ## 📰 Top 5 Notícias
    [Lista com as 5 principais notícias. Prioridade Itatiaia e O Tempo. Formato: Título com link e APENAS 1 LINHA de resumo direto por notícia].
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

def enviar_telegram(relatorio):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("Configurações do Telegram ausentes. Pulando envio.")
        return
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    partes = [relatorio[i:i+4000] for i in range(0, len(relatorio), 4000)]
    
    for parte in partes:
        payload = {
            "chat_id": chat_id,
            "text": parte,
            "parse_mode": "Markdown"
        }
        try:
            requests.post(url, json=payload)
        except Exception as e:
            print(f"Erro ao enviar para o Telegram: {e}")

def main():
    noticias = buscar_noticias()
    historico = obter_historico_30_dias()
    
    if not noticias:
        relatorio = f"# 🐔 Dossiê do Galo ({datetime.datetime.now().strftime('%d/%m/%Y')})\nNenhuma notícia encontrada."
    else:
        try:
            relatorio = analisar_com_ia(noticias, historico)
        except Exception as e:
            relatorio = f"# Erro na IA\nDetalhes: {e}"

    enviar_telegram(relatorio)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(relatorio)
        
    os.makedirs("relatorios", exist_ok=True)
    with open(f"relatorios/noticias_{datetime.datetime.now().strftime('%Y-%m-%d')}.md", "w", encoding="utf-8") as f:
        f.write(relatorio)

if __name__ == "__main__":
    main()
