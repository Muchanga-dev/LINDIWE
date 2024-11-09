
# Lindiwe: Ferramenta de Análise de Fraturas Geológicas, com base na Tecnica de scanline

## Visão Geral

Indiwe oferece uma interface web para análise de fraturas geológicas usando dados de scanline. 
Desenvolvida em Python com Streamlit, essa ferramenta permite que geólogos façam upload de dados, selecionem 
parâmetros de fraturas relevantes e realizem análises estatísticas detalhadas. Com recursos avançados para ajustes 
de orientação, visualizações e exportação de resultados, a ferramenta facilita estudos geológicos completos.

## Instalação

1. **Clone o Repositório**:
   ```bash
   git clone <url_do_repositorio>
   cd lindiwe_tool
   ```

2. **Instale as Dependências**:
   Utilize um ambiente virtual (recomendado) para manter as dependências isoladas.
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # No Windows, use venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Estrutura de Diretórios**:
   - **app.py**: Ponto de entrada principal para execução da aplicação Streamlit.
   - **src/utils**:
     - `conf.py`: Contém funções de configuração e gerenciamento de sessão.
     - `translations.py`: Gerencia traduções para suporte multilíngue.
   - **assets/image**: Diretório contendo o logo da aplicação e outras imagens necessárias.

4. **Configuração dos Arquivos de Tradução e Configuração**:
   Certifique-se de que `translations.py` inclui mapeamentos de dicionário para todas as strings de texto usadas na aplicação, 
   cobrindo os idiomas suportados (por exemplo, Português e Inglês). 
   Use `conf.py` para configurar as configurações de sessão ou modificar tags HTML, se necessário.

## Uso

1. **Execute a Aplicação**:
   No diretório principal (onde o `app.py` está localizado), inicie o aplicativo Streamlit:
   ```bash
   streamlit run app.py
   ```

2. **Interface de Usuário**:
   - Abra uma janela do navegador para acessar a interface Streamlit (geralmente em `http://localhost:8501`).
   - **Seleção de Idioma**: Escolha entre Português e Inglês na barra lateral.
   - **Carregamento de Dados**: Faça o upload de um arquivo (CSV, Excel ou TXT) contendo os dados de fraturas de scanline.
   - **Seleção de Parâmetros**: Escolha as colunas para abertura, espaçamento, orientação e dip (se disponíveis).
   - **Especificar Detalhes da Scanline**:
     - Insira o comprimento da scanline e o ângulo de orientação (se aplicável).
     - Defina as unidades para abertura e espaçamento (por exemplo, mm, cm, m).
   - **Confirmar Configurações**: Confirme ou saia para prosseguir com a análise ou redefinir as seleções.

3. **Análise e Visualização**:
   - A ferramenta oferece:
     - Estatísticas descritivas e histogramas para os parâmetros de fraturas.
     - Diagramas de roseta e estereográficos para orientação de fraturas.
     - Cálculos de intensidade de fratura, espaçamento médio e distribuições de tamanho.
   - **Exportar Resultados**: Baixe os resultados estatísticos em formato Excel.

## Solução de Problemas

- **Erros de Carregamento de Dados**: Certifique-se de que os arquivos carregados estão no formato correto e que as colunas estão nomeadas adequadamente.
- **Conversões de Unidade**: Verifique se as unidades são consistentes em toda a aplicação para evitar discrepâncias na análise.

Para quaisquer dúvidas ou documentação adicional, consulte as dicas de ajuda dentro do aplicativo ou entre em contato com a equipe de suporte.

---

Este README fornece os passos necessários para configurar, executar e utilizar a Ferramenta Lindiwe para análise de fraturas geológicas.
