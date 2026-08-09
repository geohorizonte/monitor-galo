import os
import datetime
import urllib.parse
import feedparser
import google.generativeai as genai

def buscar_noticias():
    # Busca notícias das últimas 24h contendo Atlético Mineiro ou Galo
    query = '("Atlético Mineiro" OR "Galo") when:1d'
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=pt-BR&gl=BR&ceid=BR:pt-BR"
    
    feed = feedparser.parse(rss_url)
    return feed.entries

def analisar_com_ia(noticias):
    # Configura a chave utilizando o cofre do GitHub Secrets
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    
    texto_noticias = ""
    for i, n in enumerate(noticias[:25], 1):
        texto_noticias += f"Notícia {i}: {n.title} (Link: {n.link})\n"

    # Prompt estruturado com o Resumo Quantitativo Qualificado e Seções Especializadas
    prompt = f"""
    Você é um analista esportivo de alto nível e inteligência de dados focado no Clube Atlético Mineiro.
    Abaixo estão as manchetes e notícias coletadas nas últimas 24 horas sobre o time:
    
    {texto_noticias}
    
    Analise profundamente esse material e escreva um relatório profissional em Markdown seguindo RIGOROSAMENTE esta estrutura:
    
    # 🐔 Dossiê Analítico do Atlético Mineiro - {datetime.datetime.now().strftime("%d/%m/%Y")}
    
    ## 📊 Resumo Quantitativo & Qualitativo
    - **Índice de Tom / Clima da Cobertura:** (Classifique o clima midiático do dia, ex: Positivo, Neutro, Tenso/Crítico, com uma breve justificativa baseada nas matérias).
    - **Matriz de Foco Temático com Proporção:** (Estime a distribuição percentual dos assuntos do dia, ex: Mercado da Bola %, Tática/Treinos %, Gestão/SAF %, DM/Lesões %, Bastidores %).
    - **Raio-X dos Veículos:** (Aponte quais fontes ou tipos de veículos — imprensa nacional vs. portais locais/influenciadores de MG — estão puxando o noticiário).
    - **Indicador de "Ruído vs. Fato":** (Analise se há muita repetição requentada da mesma notícia gerando efeito eco ou se há furos reais e informações novas).
    
    ## 🌡️ Termômetro da Torcida e Ambiente
    [Analise o clima geral do clube, o nível de pressão sobre a diretoria ou comissão técnica, e a repercussão do momento entre os torcedores].
    
    ## 💰 Lupa nas Finanças e Gestão da SAF
    [Resuma atualizações econômicas, balanços, negociações da SAF, acordos judiciais ou declarações de dirigentes sobre o aspecto financeiro].
    
    ## ⚽ Visão Clínica de Campo (Foco Técnico)
    [Análise tática, boletim do Departamento Médico/lesões, desempenho recente e alternativas de escalação do treinador].
    
    ## 🏟️ Logística de Jogo e "Galo na Veia"
    [Informações práticas sobre venda de ingressos, novidades da Arena MRV e atualizações do programa de sócio-torcedor Galo na Veia].
    
    ## ⚔️ Seção Especial de Jogo (Preencha apenas se houver partida hoje ou nos próximos dias; caso contrário, indique que é uma semana de treinos/transição)
    - **O Termômetro da Imprensa:** (Consenso dos jornalistas, favoritismo apontado e a narrativa principal do confronto).
    - **A Prancheta Tática:** (Prováveis escalações, desfalques confirmados e o encaixe estratégico esperado).
    - **Previsões e Tendências Esportivas:** (Palpites da mídia, projeções de desempenho e visão do mercado/odds).
    - **O Fator Adversário:** (Momento do rival, eventuais ex-jogadores do Galo no time oposto e pontos de atenção).
    
    ## 📰 Principais Notícias e Links (Top 5)
    [Faça uma lista com as 5 notícias mais importantes, contendo seus respectivos links em formato Markdown e um resumo analítico de 2 linhas para cada uma].
    """

    # Lista de modelos seguros com fallback para garantir o funcionamento
    modelos_seguros = [
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'gemini-pro'
    ]

    resposta_texto = None
    ultimo_erro = None

    for nome_modelo in modelos_seguros:
        try:
            modelo = genai.GenerativeModel(nome_modelo)
            resposta = modelo.generate_content(prompt)
            resposta_texto = resposta.text
            break
        except Exception as e:
            ultimo_erro = e
            continue

    if resposta_texto:
        return resposta_texto
    else:
        raise Exception(f"Todos os modelos falharam. Último erro: {ultimo_erro}")

def main():
    noticias = buscar_noticias()
    
    if not noticias:
        relatorio = f"# 🐔 Dossiê do Galo ({datetime.datetime.now().strftime('%d/%m/%Y')})\nNenhuma notícia encontrada nas últimas 24 horas."
    else:
        try:
            relatorio = analisar_com_ia(noticias)
        except Exception as e:
            relatorio = f"# Erro na IA\nNão foi possível gerar a análise. Detalhes: {e}"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(relatorio)
        
    os.makedirs("relatorios", exist_ok=True)
    nome_arquivo = f"relatorios/noticias_{datetime.datetime.now().strftime('%Y-%m-%d')}.md"
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(relatorio)

if __name__ == "__main__":
    main()
