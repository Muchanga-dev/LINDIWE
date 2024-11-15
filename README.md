
# Lindiwe: Ferramenta de Análise de Fraturas Geológicas, com base na Tecnica de scanline

## Visão Geral

Indiwe oferece uma interface web para análise de fraturas geológicas usando dados de scanline. 
Desenvolvida em Python com Streamlit, essa ferramenta permite que geólogos façam upload de dados, selecionem 
parâmetros de fraturas relevantes e realizem análises estatísticas detalhadas. Com recursos avançados para ajustes 
de orientação, visualizações e exportação de resultados, a ferramenta facilita estudos geológicos completos.

![LINDIWE](assets/output/image_0.png)

## Pré-Requisitos

- Certifique-se de que **Python** (versão 3.10 ou superior) esteja instalado em sua máquina. 
  - Para verificar, execute:
    ```bash
    python3 --version
    ```
  - Se não estiver instalado, faça o download e a instalação em [python.org](https://www.python.org/downloads/).

## Instalação

1. **Clone o Repositório**:
   ```bash
   git clone https://github.com/Muchanga-dev/LINDIWE.git
   cd LINDIWE
   ```

2. **Instale as Dependências**:
   Utilize um ambiente virtual (recomendado) para manter as dependências isoladas.
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # No Windows, use venv\Scripts\activate
   pip install -r requirements.txt
   ```

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
     - Distribuição do tamanho das fraturas Lei de Potência (Power Law)
       ![LINDIWE](assets/output/image_4.png)
     - Diagramas de roseta e estereográficos para orientação de fraturas.
       ![LINDIWE](assets/output/image_2.png)
     - Cálculos de intensidade de fratura, espaçamento médio e distribuições de tamanho.
       ![LINDIWE](assets/output/image_6.png)
  - **Exportar Resultados**: Baixe os resultados estatísticos em formato Excel.
  

## Solução de Problemas

- **Erros de Carregamento de Dados**: Certifique-se de que os arquivos carregados estão no formato correto e que as colunas estão nomeadas adequadamente.
- **Conversões de Unidade**: Verifique se as unidades são consistentes em toda a aplicação para evitar discrepâncias na análise.

### Contribuindo com LINDIWE
Contribuições são essenciais para o desenvolvimento contínuo do LINDIWE. Se você deseja contribuir, faça um fork do repositório, aplique suas mudanças e abra um pull request para revisão.

### Licença
O LINDIWE é disponibilizado sob a Licença Apache 2.0, oferecendo flexibilidade para uso pessoal e comercial, garantindo ao mesmo tempo a proteção dos direitos autorais. Consulte o arquivo [LICENSE](https://github.com/Muchanga-dev/FRAMFRAT/blob/main/LICENSE.txt) para obter detalhes completos.

