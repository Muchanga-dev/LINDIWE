import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import mplstereonet
import xlsxwriter
import numpy as np
from io import BytesIO
from scipy import stats
from src.utils.translations import translations
from src.utils.conf import conf
conf()


def translate(key, lang):
    """
    Função para traduzir chaves de texto com base no idioma selecionado.
    Verifica se a chave e o idioma estão disponíveis, caso contrário, retorna a chave original.
    """
    if key in translations and lang in translations[key]:
        return translations[key][lang]
    else:
        return key

def main():
    """
    Função principal que controla o fluxo da aplicação.
    """
    # Seleção de idioma
    st.sidebar.image("assets/image/logo.png")
    lang = st.sidebar.radio("Selecione o idioma / Select language", ["Português", "English"], horizontal=True)
    lang = "pt" if lang == "Português" else "en"

    # Carregar os dados
    data = upload_data(lang)

    if data is not None:
        initialize_session_state()
        unit_measurement = select_units(lang)

        # Inserir o comprimento da scanline aqui
        scanline_length = st.sidebar.number_input(
            translate("input_scanline_length", lang),
            min_value=0.0,
            value=0.0,
            format="%f"
        )

        if scanline_length <= 0:
            st.warning(translate("invalid_scanline_length", lang))
            return  # Interrompe a execução até que um valor válido seja inserido

        # Armazenar o comprimento da scanline no estado de sessão
        st.session_state['scanline_length'] = scanline_length

        # Opção para incluir orientação
        include_orientation = st.sidebar.checkbox(translate("include_orientation", lang))
        scanline_angle = 0.0

        if include_orientation:
            # Solicitar o ângulo da scanline em relação ao norte geográfico
            scanline_angle = st.sidebar.number_input(
                translate("input_scanline_orientation", lang),
                min_value=0.0,
                max_value=360.0,
                value=0.0,
                help=translate("help_input_scanline_orientation", lang)
            )

        # Selecionar as colunas
        selected_columns = select_columns(data, include_orientation, lang)
        if selected_columns:
            st.sidebar.info(translate("confirm_column_selection", lang))

            # Adicionar botões "Confirmar" e "Sair" usando estado de sessão
            if 'confirmed' not in st.session_state:
                st.session_state['confirmed'] = None

                   

            col1, col2 = st.sidebar.columns(2)
            with col1:
                if st.button(translate("confirm", lang)):
                    st.session_state['confirmed'] = True
            with col2:
                if st.button(translate("exit", lang)):
                    st.session_state['confirmed'] = False

            # Verificar o estado e agir de acordo
            if st.session_state['confirmed'] == True:
                process_data(data, selected_columns, include_orientation, lang, scanline_angle, unit_measurement)
            elif st.session_state['confirmed'] == False:
                st.warning(translate("processing_canceled", lang))
                if st.button(translate("restart_application", lang)):
                    st.session_state.clear()
                    st.rerun()
        else:
            st.warning(translate("select_columns_warning", lang))
              
    else:
        c1, c2, c3 = st.columns([1, 10, 1])
        c2.title("")
        c2.title("")
        c2.title(translate("title", lang))
        c2.write(translate("welcome_message", lang))
        #c2.image("assets/image/fraturas.png")
        st.sidebar.warning(translate("no_file_uploaded", lang))


def upload_data(lang):
    """
    Função para realizar o upload dos dados.
    Suporta arquivos nos formatos CSV, Excel e TXT.
    """
    uploaded_file = st.sidebar.file_uploader(
        translate("upload_data", lang), type=["csv", "xlsx", "txt"]
    )
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                data = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                data = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.txt'):
                data = pd.read_csv(uploaded_file, delimiter='\t')
            st.sidebar.success(translate("data_loaded_success", lang))
            return data
        except Exception as e:
            st.error(translate("data_loading_error", lang) + str(e))
            return None
    else:
        return None

def initialize_session_state():
    """
    Inicializa o estado de sessão para unidades de medida.
    """
    if 'abertura_unit' not in st.session_state:
        st.session_state['abertura_unit'] = 'Milímetro'
    if 'distancia_unit' not in st.session_state:
        st.session_state['distancia_unit'] = 'Milímetro'

def select_units(lang):
    """
    Permite ao usuário selecionar as unidades de medida para abertura e distância.
    """
    st.sidebar.subheader(translate("select_units", lang))
    unit_options = ['Milímetro', 'Centímetro', 'Metro', 'Quilômetro']

    st.session_state['abertura_unit'] = st.sidebar.selectbox(
        translate("select_abertura_unit", lang), unit_options
    )
    st.session_state['distancia_unit'] = st.sidebar.selectbox(
        translate("select_distancia_unit", lang), unit_options
    )

    default_unit = st.sidebar.selectbox(translate("select_default_unit", lang), unit_options)

    return default_unit


def select_columns(data, include_orientation, lang):
    """
    Permite ao usuário selecionar as colunas relevantes dos dados carregados.
    """
    st.sidebar.subheader(translate("select_columns", lang))
    all_columns = data.columns.tolist()

    abertura_col = st.sidebar.selectbox(translate("select_abertura", lang), all_columns)
    distancia_col = st.sidebar.selectbox(translate("select_distancia", lang), all_columns)
    orientacao_col = None
    dip_col = None

    if include_orientation:
        orientacao_col = st.sidebar.selectbox(
            translate("select_orientacao", lang), [None] + all_columns
        )
        dip_col = st.sidebar.selectbox(
            translate("select_dip", lang), [None] + all_columns
        )

    if abertura_col and distancia_col and (not include_orientation or orientacao_col):
        selected_columns = {
            'abertura_atual': abertura_col,
            'distancia_proxima_abertura': distancia_col,
            'orientacao': orientacao_col if orientacao_col else None,
            'dip': dip_col if dip_col else None
        }
        return selected_columns
    else:
        return None


def process_data(data, selected_columns, include_orientation, lang, scanline_angle, unit_measurement):
    """
    Processa os dados selecionados e executa as análises necessárias.
    """
    columns_to_select = [
        selected_columns['abertura_atual'],
        selected_columns['distancia_proxima_abertura']
    ]
    if include_orientation and selected_columns['orientacao']:
        columns_to_select.append(selected_columns['orientacao'])
    if include_orientation and selected_columns.get('dip'):
        columns_to_select.append(selected_columns['dip'])

    filtered_data = data[columns_to_select].copy()
    new_columns = ['abertura_atual', 'distancia_proxima_abertura']
    if include_orientation and selected_columns['orientacao']:
        new_columns.append('orientacao')
    if include_orientation and selected_columns.get('dip'):
        new_columns.append('dip')

    filtered_data.columns = new_columns

    validate_data(filtered_data, lang)
    convert_units(filtered_data, unit_measurement, lang)

    # Calcular abertura ajustada usando a orientação em relação ao norte
    if include_orientation:
        filtered_data['abertura_ajustada'] = correct_openings_with_orientation(
            filtered_data, 'orientacao', scanline_angle
        )
    else:
        filtered_data['abertura_ajustada'] = filtered_data['abertura_atual']

    if 'abertura_ajustada' not in filtered_data.columns:
        st.error(translate("error_creating_adjusted_opening", lang))
        return

    # Define translated_columns based on include_orientation
    if include_orientation:
        translated_columns = [
            translate('current_opening', lang),
            translate('distance_next_opening', lang),
            translate('orientation', lang),
            translate('adjusted_opening', lang)
        ]
        if 'dip' in filtered_data.columns:
            translated_columns.insert(3, translate('dip', lang))
    else:
        translated_columns = [
            translate('current_opening', lang),
            translate('distance_next_opening', lang)
        ]

    show_data(filtered_data, unit_measurement, lang, translated_columns, include_orientation)

    # Set aperture_column based on include_orientation
    if include_orientation:
        aperture_column = 'abertura_ajustada'
    else:
        aperture_column = 'abertura_atual'

    # Análises e visualizações
    analyze_data(filtered_data, unit_measurement, lang, include_orientation, aperture_column)
    visualize_geography(filtered_data, unit_measurement, lang)
    if include_orientation and selected_columns['orientacao']:
        visualize_orientation(filtered_data, 'orientacao', lang)
        plot_stereogram(filtered_data, 'orientacao', selected_columns.get('dip'), lang)

    fracture_intensity = calculate_fracture_intensity(filtered_data, lang)
    average_spacing = calculate_average_spacing(filtered_data, lang)
    regression_results = analyze_fracture_size_distribution(filtered_data, lang, unit_measurement, aperture_column)
    log_normal_results = fit_log_normal_distribution(filtered_data, lang, aperture_column)

    display_results_table(fracture_intensity, regression_results, log_normal_results, average_spacing, lang)
    plot_fracture_histogram_and_cumulative(filtered_data, unit_measurement, lang)

    
def validate_data(data, lang):
    """
    Valida os dados, convertendo para numérico e removendo valores nulos.
    """
    for column in data.columns:
        data[column] = pd.to_numeric(data[column], errors='coerce')
    if data.isnull().values.any():
        st.warning(translate("null_values_warning", lang))
        data.dropna(inplace=True)


def convert_units(data, default_unit, lang):
    """
    Converte as unidades de medida para a unidade padrão selecionada.
    """
    unit_conversion_to_mm = {
        'Milímetro': 1,
        'Centímetro': 10,
        'Metro': 1000,
        'Quilômetro': 1000000
    }
    unit_conversion_from_mm = {
        'Milímetro': 1,
        'Centímetro': 0.1,
        'Metro': 0.001,
        'Quilômetro': 0.000001
    }

    # Converte para milímetros
    data['abertura_atual_mm'] = data['abertura_atual'] * unit_conversion_to_mm[st.session_state['abertura_unit']]
    data['distancia_proxima_abertura_mm'] = data['distancia_proxima_abertura'] * unit_conversion_to_mm[st.session_state['distancia_unit']]

    # Converte de milímetros para a unidade padrão selecionada
    data['abertura_atual'] = data['abertura_atual_mm'] * unit_conversion_from_mm[default_unit]
    data['distancia_proxima_abertura'] = data['distancia_proxima_abertura_mm'] * unit_conversion_from_mm[default_unit]

    # Remove colunas temporárias
    data.drop(['abertura_atual_mm', 'distancia_proxima_abertura_mm'], axis=1, inplace=True)


def correct_openings_with_orientation(data, orientation_column, scanline_angle):
    """
    Ajusta as aberturas com base na orientação em relação à scanline.
    """
    # Converter ângulos para radianos
    scanline_orientation_rad = np.radians(scanline_angle)
    fracture_orientation_rad = np.radians(data[orientation_column])

    # Calcular o ângulo relativo e ajustar para o primeiro quadrante
    relative_angle_rad = np.abs(fracture_orientation_rad - scanline_orientation_rad)
    relative_angle_rad = np.where(relative_angle_rad > np.pi/2, np.pi - relative_angle_rad, relative_angle_rad)

    # Correção: garantir que o cosseno não seja zero
    abertura_ajustada = data['abertura_atual'] / np.cos(relative_angle_rad)

    # Aproximação para 6 casas decimais e garantir que abertura ajustada seja positiva
    abertura_ajustada = np.round(abertura_ajustada, 6)
    abertura_ajustada = abertura_ajustada.replace([np.inf, -np.inf], np.nan).dropna()
    return abertura_ajustada


def show_data(data, unit_measurement, lang, translated_columns, include_orientation):
    """
    Exibe os dados processados na interface.
    """
    if include_orientation:
        columns_to_display = ['abertura_atual', 'distancia_proxima_abertura', 'orientacao']
        if 'dip' in data.columns:
            columns_to_display.append('dip')
        columns_to_display.append('abertura_ajustada')
    else:
        columns_to_display = ['abertura_atual', 'distancia_proxima_abertura']

    translated_data = data[columns_to_display].copy()
    translated_data.columns = translated_columns

    st.write(translate("data_loaded", lang).format(unit=unit_measurement))
    st.dataframe(translated_data)

def analyze_data(data, unit_measurement, lang, include_orientation, aperture_column):
    """
    Realiza análises estatísticas descritivas e plota histograma.
    """
    st.subheader(translate("descriptive_statistics", lang).format(unit=unit_measurement))

    translated_data = data[[aperture_column, 'distancia_proxima_abertura']].copy()
    if include_orientation:
        translated_data.columns = [
            translate('adjusted_opening', lang),
            translate('distance_next_opening', lang)
        ]
    else:
        translated_data.columns = [
            translate('current_opening', lang),
            translate('distance_next_opening', lang)
        ]

    st.write(translated_data.describe().transpose())

    st.write(translate("histogram_aberturas", lang).format(unit=unit_measurement))
    fig, ax = plt.subplots()
    ax.hist(data[aperture_column], bins=30, color='blue', alpha=0.7)
    ax.set_xlabel(translate('opening', lang))
    ax.set_ylabel(translate('fracture_count', lang))
    ax.set_title(translate('histogram_aberturas', lang).format(unit=unit_measurement))
    st.pyplot(fig)

def visualize_geography(data, unit_measurement, lang):
    """
    Plota o mapa de fraturas ao longo da scanline.
    """
    st.subheader(translate("fracture_map", lang))

    data['posicao_scanline'] = data['distancia_proxima_abertura'].cumsum() - data['distancia_proxima_abertura'].iloc[0] + data['abertura_atual'].cumsum()

    fig, ax = plt.subplots(figsize=(10, 6))
    if 'orientacao' in data.columns:
        sc = ax.scatter(
            data['posicao_scanline'],
            data['abertura_ajustada'],
            c=data['orientacao'],
            cmap='viridis',
            alpha=0.6,
            edgecolors='w',
            linewidth=0.5
        )
        plt.colorbar(sc, label=translate("orientation", lang))
    else:
        sc = ax.scatter(
            data['posicao_scanline'],
            data['abertura_ajustada'],
            color='blue',
            alpha=0.6,
            edgecolors='w',
            linewidth=0.5
        )

    ax.set_xlabel(translate("along_scanline", lang).format(unit=unit_measurement))
    ax.set_ylabel(translate("opening", lang).format(unit=unit_measurement))
    ax.set_title(translate("fracture_map", lang))

    st.pyplot(fig)

def visualize_orientation(data, orientacao_col, lang):
    """
    Plota o diagrama de roseta das orientações.
    """
    st.subheader(translate("orientation_rose_diagram", lang))

    orientations = data[orientacao_col].dropna()
    num_bins = 36  # Número de bins no diagrama de roseta

    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    counts, bins = np.histogram(orientations, bins=num_bins, range=(0, 360))
    bins = np.deg2rad(bins)  # Converte para radianos

    ax.bar(bins[:-1], counts, width=bins[1] - bins[0], align='edge', edgecolor='k')
    ax.set_theta_direction(-1)
    ax.set_theta_zero_location('N')

    ax.set_title(translate("orientation_rose_diagram", lang))
    st.pyplot(fig)

def plot_stereogram(data, orientation_col, dip_col=None, lang="en"):
    """
    Plota o estereograma das fraturas.
    """
    st.subheader(translate("stereogram_plot", lang))

    orientations = data[orientation_col].dropna()
    if len(orientations) == 0:
        st.warning(translate("no_orientation_data", lang))
        return

    strikes = orientations % 360

    if dip_col and dip_col in data.columns:
        dips = data[dip_col].dropna()
        
        # Combinar strikes e dips, removendo valores nulos
        orientations = pd.concat([strikes, dips], axis=1).dropna()
        strikes = orientations[orientation_col]
        dips = orientations[dip_col]
    else:
        dips = np.full_like(strikes, 90)  # Assumindo fraturas verticais

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection='stereonet')

    # Plotar os planos das fraturas sem rótulo
    plane_lines = ax.plane(strikes, dips, color='blue', linewidth=0.5)

    # Plotar os polos das fraturas com rótulo
    poles = ax.pole(strikes, dips, 'o', markersize=5, color='red', label=translate("fracture_poles", lang))

    # Adicionar contornos de densidade para os polos
    ax.density_contourf(strikes, dips, measurement='poles', cmap='Reds', alpha=0.3)

    ax.grid()

    # Criar handles personalizados para a legenda
    custom_handles = [
        Line2D([0], [0], color='blue', linewidth=1.5, label=translate("fracture_planes", lang)),
        Line2D([0], [0], marker='o', color='red', linestyle='None', markersize=8, label=translate("fracture_poles", lang))
    ]

    # Adicionar a legenda com os handles personalizados
    ax.legend(handles=custom_handles, loc='best')

    st.pyplot(fig)

def calculate_fracture_intensity(data, lang):
    """
    Calcula a intensidade de fraturas.
    """
    st.subheader(translate("fracture_intensity", lang))
    num_fractures = len(data)

    # Obter o comprimento da scanline do estado de sessão
    scanline_length = st.session_state.get('scanline_length', None)

    if scanline_length is None or scanline_length <= 0:
        st.warning(translate("invalid_scanline_length", lang))
        return None

    fracture_intensity = num_fractures / scanline_length

    st.write(translate("fracture_intensity_result", lang).format(intensity=fracture_intensity))
    return fracture_intensity

    
    if scanline_length <= 0:
        st.warning(translate("invalid_scanline_length", lang))
        return None

    fracture_intensity = num_fractures / scanline_length

    st.write(translate("fracture_intensity_result", lang).format(intensity=fracture_intensity))
    return fracture_intensity

def analyze_fracture_size_distribution(data, lang, unit_measurement, aperture_column):
    """
    Analisa a distribuição do tamanho das fraturas e plota o gráfico de regressão linear com a equação e R².
    """
    st.subheader(translate("fracture_size_distribution", lang))
    apertures = data[aperture_column]
    sorted_apertures = apertures[apertures > 0].sort_values(ascending=False).reset_index(drop=True)
    cumulative_count = np.arange(1, len(sorted_apertures) + 1)
    
    log_apertures = np.log10(sorted_apertures)
    log_cumulative_count = np.log10(cumulative_count)
    slope, intercept, r_value, p_value, std_err = stats.linregress(log_apertures, log_cumulative_count)
    
    # Cálculo dos intervalos de confiança para slope e intercept
    n = len(log_apertures)
    alpha = 0.05  # Nível de confiança de 95%
    t_value = stats.t.ppf(1 - alpha/2, df=n - 2)
    
    # Intervalos de confiança para slope
    slope_conf_interval = t_value * std_err
    slope_lower = slope - slope_conf_interval
    slope_upper = slope + slope_conf_interval
    
    # Erro padrão do intercept
    s_yx = np.sqrt(np.sum((log_cumulative_count - (slope * log_apertures + intercept))**2) / (n - 2))
    intercept_std_err = s_yx * np.sqrt(np.sum(log_apertures**2) / (n * np.sum((log_apertures - np.mean(log_apertures))**2)))
    
    # Intervalos de confiança para intercept
    intercept_conf_interval = t_value * intercept_std_err
    intercept_lower = intercept - intercept_conf_interval
    intercept_upper = intercept + intercept_conf_interval
    
    # Preparar os dados para plotagem
    fit_line = slope * log_apertures + intercept
    r_squared = r_value ** 2

    # Formatar a equação da regressão linear
    intercept_formatted = f"{intercept:.2f}"
    slope_formatted = f"{slope:.2f}"
    equation = f"y = {slope_formatted}x + {intercept_formatted}"
    
    fig, ax = plt.subplots()
    ax.loglog(sorted_apertures, cumulative_count, marker='o', linestyle='none', label=translate("data", lang))
    ax.loglog(
        sorted_apertures,
        10**fit_line,
        'b-',
        label=f"{translate('linear_regression', lang)}: {equation}\n$R^2$ = {r_squared:.4f}"
    )
    
    ax.set_xlabel(translate("opening", lang).format(unit=unit_measurement))
    ax.set_ylabel(translate("cumulative_fractures", lang))
    ax.set_title(translate("fracture_size_distribution", lang))
    ax.legend()
    
    st.pyplot(fig)
    
    regression_results = {
        'slope': slope,
        'slope_lower': slope_lower,
        'slope_upper': slope_upper,
        'intercept': intercept,
        'intercept_lower': intercept_lower,
        'intercept_upper': intercept_upper,
        'r_value': r_squared,
        'p_value': p_value,
        'std_err': std_err
    }
    
    return regression_results





def fit_log_normal_distribution(data, lang, aperture_column):
    """
    Ajusta uma distribuição log-normal aos dados.
    """
    st.subheader(translate("fit_log_normal_distribution", lang))

    apertures = data[aperture_column]
    apertures = apertures[apertures > 0]

    # Ajuste dos parâmetros mu e sigma da distribuição log-normal
    shape, loc, scale = stats.lognorm.fit(apertures, floc=0)

    mu = np.log(scale)
    sigma = shape

    # Erros padrão (aproximação)
    n = len(apertures)
    sigma_std_err = sigma / np.sqrt(2 * n)
    mu_std_err = sigma / np.sqrt(n)

    # Intervalos de confiança para mu e sigma
    alpha = 0.05  # Nível de confiança de 95%
    z_value = stats.norm.ppf(1 - alpha/2)

    mu_lower = mu - z_value * mu_std_err
    mu_upper = mu + z_value * mu_std_err

    sigma_lower = sigma - z_value * sigma_std_err
    sigma_upper = sigma + z_value * sigma_std_err

    # Gerar dados teóricos da distribuição log-normal
    x = np.linspace(min(apertures), max(apertures), 100)
    pdf_fitted = stats.lognorm.pdf(x, s=sigma, scale=np.exp(mu))

    # Plotar o histograma das aberturas e a distribuição ajustada
    fig, ax = plt.subplots()
    ax.hist(apertures, bins=30, density=True, alpha=0.6, color='g', label=translate("data", lang))
    ax.plot(x, pdf_fitted, 'r-', label=f'Log-Normal PDF')

    ax.set_xlabel(translate("opening", lang))
    ax.set_ylabel(translate("density", lang))
    ax.set_title(translate("fit_log_normal_distribution", lang))
    ax.legend()

    st.pyplot(fig)

    # Realizar o teste de Kolmogorov-Smirnov
    ks_statistic, ks_p_value = stats.kstest(apertures, 'lognorm', args=(sigma, 0, np.exp(mu)))

    st.write(translate("log_normal_parameters", lang))
    st.write(f"Mu (μ): {mu:.4f} [{mu_lower:.4f}, {mu_upper:.4f}]")
    st.write(f"Sigma (σ): {sigma:.4f} [{sigma_lower:.4f}, {sigma_upper:.4f}]")
    st.write(translate("ks_test", lang))
    st.write(f"{translate('ks_statistic', lang)}: {ks_statistic:.4f}")
    st.write(f"{translate('ks_p_value', lang)}: {ks_p_value:.4f}")

    log_normal_results = {
        'mu': mu,
        'mu_lower': mu_lower,
        'mu_upper': mu_upper,
        'sigma': sigma,
        'sigma_lower': sigma_lower,
        'sigma_upper': sigma_upper,
        'ks_statistic': ks_statistic,
        'ks_p_value': ks_p_value
    }

    return log_normal_results

def calculate_average_spacing(data, lang):
    """
    Calcula o espaçamento médio entre fraturas.
    """
    st.subheader(translate("average_spacing", lang))
    num_fractures = len(data)

    # Obter o comprimento da scanline do estado de sessão
    scanline_length = st.session_state.get('scanline_length', None)

    if scanline_length is None or scanline_length <= 0:
        st.warning(translate("invalid_scanline_length", lang))
        return None

    average_spacing = scanline_length / num_fractures

    st.write(translate("average_spacing_result", lang).format(spacing=average_spacing))
    return average_spacing


def display_results_table(fracture_intensity, regression_results, log_normal_results, average_spacing, lang):
    """
    Exibe uma tabela com os resultados estatísticos.
    """
    st.subheader(translate("statistical_results", lang))
    
    results = {}
    
    # Intensidade de fraturas
    if fracture_intensity is not None:
        results[translate("fracture_intensity", lang)] = f"{fracture_intensity:.6f}"
    else:
        results[translate("fracture_intensity", lang)] = translate("not_available", lang)
    
    # Espaçamento médio
    if average_spacing is not None:
        results[translate("average_spacing", lang)] = f"{average_spacing:.4f}"
    else:
        results[translate("average_spacing", lang)] = translate("not_available", lang)
    
    # Resultados da regressão linear (Lei de Potência)
    if regression_results is not None:
        results[translate("slope", lang)] = f"{regression_results['slope']:.4f}"
        results[translate("slope_conf_interval", lang)] = f"[{regression_results['slope_lower']:.4f}, {regression_results['slope_upper']:.4f}]"
        results[translate("intercept", lang)] = f"{regression_results['intercept']:.4f}"
        results[translate("intercept_conf_interval", lang)] = f"[{regression_results['intercept_lower']:.4f}, {regression_results['intercept_upper']:.4f}]"
        results[translate("r_squared", lang)] = f"{regression_results['r_value']:.4f}"
        results[translate("p_value", lang)] = f"{regression_results['p_value']:.4f}"
    else:
        # Caso os resultados não estejam disponíveis
        results[translate("slope", lang)] = translate("not_available", lang)
        results[translate("slope_conf_interval", lang)] = translate("not_available", lang)
        results[translate("intercept", lang)] = translate("not_available", lang)
        results[translate("intercept_conf_interval", lang)] = translate("not_available", lang)
        results[translate("r_squared", lang)] = translate("not_available", lang)
        results[translate("p_value", lang)] = translate("not_available", lang)
    
    # Resultados do ajuste Log-Normal
    if log_normal_results is not None:
        results[translate("mu", lang)] = f"{log_normal_results['mu']:.4f}"
        results[translate("mu_conf_interval", lang)] = f"[{log_normal_results['mu_lower']:.4f}, {log_normal_results['mu_upper']:.4f}]"
        results[translate("sigma", lang)] = f"{log_normal_results['sigma']:.4f}"
        results[translate("sigma_conf_interval", lang)] = f"[{log_normal_results['sigma_lower']:.4f}, {log_normal_results['sigma_upper']:.4f}]"
        results[translate("ks_statistic", lang)] = f"{log_normal_results['ks_statistic']:.4f}"
        results[translate("ks_p_value", lang)] = f"{log_normal_results['ks_p_value']:.4f}"
    else:
        # Caso os resultados não estejam disponíveis
        results[translate("mu", lang)] = translate("not_available", lang)
        results[translate("mu_conf_interval", lang)] = translate("not_available", lang)
        results[translate("sigma", lang)] = translate("not_available", lang)
        results[translate("sigma_conf_interval", lang)] = translate("not_available", lang)
        results[translate("ks_statistic", lang)] = translate("not_available", lang)
        results[translate("ks_p_value", lang)] = translate("not_available", lang)
    
    # Converter o dicionário de resultados em DataFrame
    df_results = pd.DataFrame(list(results.items()), columns=[translate("parameter", lang), translate("value", lang)])
    
    # Exibir a tabela de resultados
    st.table(df_results)
    
    # Chamar a função para permitir o download
    export_statistical_results(df_results, lang)

def export_statistical_results(results_df, lang):
    """
    Permite ao usuário baixar os resultados estatísticos como um arquivo Excel.
    """
    output = BytesIO()
    try:
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        results_df.to_excel(writer, index=False, sheet_name='Resultados')
        writer.close()
        processed_data = output.getvalue()

        st.download_button(
            label=translate("download_excel", lang),
            data=processed_data,
            file_name='statistical_results.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        st.error(f"{translate('error_generating_excel', lang)}: {e}")

def plot_fracture_histogram_and_cumulative(data, unit_measurement, lang):
    """
    Plota o histograma de fraturas e a frequência acumulada.
    """
    st.subheader(translate("fracture_histogram_cumulative", lang))

    data['posicao_scanline'] = data['distancia_proxima_abertura'].cumsum() - data['distancia_proxima_abertura'].iloc[0] + data['abertura_atual'].cumsum()
    data_filtered = data[data['posicao_scanline'] > 0]

    fig, ax1 = plt.subplots(figsize=(10, 6))

    n, bins, patches = ax1.hist(data_filtered['posicao_scanline'], bins=30, alpha=0.6, color='blue', label=translate("histogram", lang))

    ax1.set_xlabel(translate("along_scanline", lang).format(unit=unit_measurement))
    ax1.set_ylabel(translate("fracture_count", lang), color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')

    ax2 = ax1.twinx()
    cumulative = np.cumsum(n)
    ax2.plot(bins[:-1], cumulative, 'r-', label=translate("cumulative_frequency", lang))
    ax2.set_ylabel(translate("cumulative_fracture_count", lang), color='red')
    ax2.tick_params(axis='y', labelcolor='red')

    fig.tight_layout()
    st.pyplot(fig)

if __name__ == "__main__":
    main()
