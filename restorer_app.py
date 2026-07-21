import hashlib

import streamlit as st
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from pixel_core import detect_grid_size, optimize_palette, get_palette_stats

# Конфигурация страницы
st.set_page_config(
    page_title="Pixel Refiner Studio",
    page_icon="🎨",
    layout="wide"
)

# === РЕТРО-ПИКСЕЛЬНЫЙ ДИЗАЙН ===
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=block');

    .stApp {
        background-color: #0b0b10;
        color: #ffffff;
        font-family: 'Inter', sans-serif;
        padding-top: 2rem !important;
    }
    
    .retro-border {
        border: 2px solid #2e2e3a;
        box-shadow: 4px 4px 0 rgba(0,0,0,0.6);
    }
    .bg-surface-container {
        background-color: #0f1116;
    }
    .output-controls {
        display: flex;
        flex-direction: column;
        gap: 16px;
        width: 100%;
        align-items: stretch;
    }
    .control-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 16px;
        flex: 1;
        width: 100%;
    }
    .control-card {
        background: #0f1116;
        border: 2px solid #2e2e3a;
        padding: 16px;
        box-shadow: 4px 4px 0 rgba(0,0,0,0.6);
    }
    .control-card .label {
        font-family: 'Press Start 2P', monospace;
        font-size: 8px;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.02em;
        margin-bottom: 6px;
        display: block;
    }
    .control-card .value {
        font-family: 'Press Start 2P', monospace;
        font-size: 16px;
        color: #ffffff;
    }
    .download-column {
        width: 100%;
        display: flex;
        align-items: stretch;
    }
    @media (min-width: 768px) {
        .output-controls {
            flex-direction: row;
            align-items: stretch;
        }
        .download-column {
            flex: 0 0 50%;
            max-width: 50%;
        }
    }
    /* === ЗОНА ЗАГРУЗКИ === */
    div[data-testid="stFileUploader"] {
        background: transparent;
        padding: 0;
        width: 100%;
        max-width: 896px;
        margin: 0 auto;
    }

    div[data-testid="stFileUploader"] section {
        background: #0b0b10 !important;
        border: 2px solid #2e2e3a !important;
        border-radius: 0 !important;
        padding: 0 !important;
        min-height: 280px !important;
        box-shadow: 4px 4px 0 rgba(0,0,0,0.6);
        transition: border-color 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        background-image: 
            linear-gradient(45deg, #1a1a22 25%, transparent 25%),
            linear-gradient(-45deg, #1a1a22 25%, transparent 25%),
            linear-gradient(45deg, transparent 75%, #1a1a22 75%),
            linear-gradient(-45deg, transparent 75%, #1a1a22 75%);
        background-size: 20px 20px;
        background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
        background-color: #0b0b10;
    }

    div[data-testid="stFileUploader"] section:hover {
        border-color: #7dffb3 !important;
    }

    /* Декоративные уголки */
    div[data-testid="stFileUploader"] section::before {
        content: '';
        position: absolute;
        top: 8px;
        left: 8px;
        width: 16px;
        height: 16px;
        border-top: 2px solid #7dffb3;
        border-left: 2px solid #7dffb3;
        opacity: 0.3;
        pointer-events: none;
        z-index: 5;
    }
    div[data-testid="stFileUploader"] section::after {
        content: '';
        position: absolute;
        bottom: 8px;
        right: 8px;
        width: 16px;
        height: 16px;
        border-bottom: 2px solid #7dffb3;
        border-right: 2px solid #7dffb3;
        opacity: 0.3;
        pointer-events: none;
        z-index: 5;
    }

    /* Скрываем стандартные тексты и кнопку */
    div[data-testid="stFileUploader"] section span,
    div[data-testid="stFileUploader"] section small,
    div[data-testid="stFileUploader"] section .st-dz-drag-hint {
        display: none !important;
    }

    /* Кастомное содержимое через псевдоэлементы */
    div[data-testid="stFileUploader"] section > div {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 8px !important;
        padding: 2rem !important;
        text-align: center !important;
        width: 100% !important;
        min-height: 280px !important;
        background: transparent !important;
        position: relative;
        z-index: 2;
    }

    div[data-testid="stFileUploader"] section > div::before {
        content: "upload_file";
        font-family: 'Material Symbols Outlined';
        font-size: 48px;
        color: #7dffb3;
        display: block;
        margin-bottom: 4px;
    }
    div[data-testid="stFileUploader"] section > div::after {
        content: "ПЕРЕТАЩИТЕ ФАЙЛ СЮДА";
        font-family: 'Press Start 2P', monospace;
        font-size: 12px;
        color: #ffffff;
        display: block;
        margin-bottom: 4px;
        letter-spacing: 0.02em;
    }

    /* Стили для кнопки "Обзор файлов" */
    div[data-testid="stFileUploader"] button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #2e2e3a !important;
        border-radius: 0 !important;
        font-family: 'Press Start 2P', monospace !important;
        font-size: 10px !important;
        padding: 12px 24px !important;
        box-shadow: 4px 4px 0 rgba(0,0,0,0.6) !important;
        transition: all 0.1s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 0.02em !important;
        margin-top: 12px !important;
    }
    div[data-testid="stFileUploader"] button:hover {
        background-color: #7dffb3 !important;
        color: #000000 !important;
        transform: translateX(-2px) translateY(-2px);
        box-shadow: 6px 6px 0 rgba(0,0,0,0.6) !important;
    }

    /* === КНОПКА ВОССТАНОВЛЕНИЯ === */
    .stButton > button {
        width: 100% !important;
        max-width: 380px !important;
        background-color: #000000 !important;
        color: #7dffb3 !important;
        border: 2px solid #7dffb3 !important;
        border-radius: 0 !important;
        font-family: 'Press Start 2P', monospace !important;
        font-size: 14px !important;
        padding: 20px 32px !important;
        box-shadow: 4px 4px 0 #7dffb3 !important;
        transition: all 0.1s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 0.02em !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 12px !important;
        margin: 0 auto !important;
    }
    .stButton > button:hover:not(:disabled) {
        transform: translateX(-2px) translateY(-2px) !important;
        box-shadow: 6px 6px 0 #7dffb3 !important;
        background-color: #000000 !important;
        color: #7dffb3 !important;
    }
    .stButton > button:active:not(:disabled) {
        transform: translateX(2px) translateY(2px) !important;
        box-shadow: 2px 2px 0 #7dffb3 !important;
    }
    .stButton > button:disabled {
        opacity: 0.7;
        cursor: not-allowed;
        transform: none !important;
        box-shadow: 2px 2px 0 #7dffb3 !important;
    }        
            
    /* Статусная строка */
    .status-line {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 12px;
        font-family: 'Press Start 2P', monospace;
        font-size: 10px;
        color: #555;
        text-transform: uppercase;
        letter-spacing: 0.02em;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        background-color: #ff5da2;
        border-radius: 0;
        animation: pulse 1s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.2; }
        100% { opacity: 1; }
    }

    /* Изображения */
    img {
        border: 2px solid #2e2e3a;
        box-shadow: 4px 4px 0 rgba(0,0,0,0.6);
        image-rendering: pixelated;
        image-rendering: crisp-edges;
        border-radius: 0 !important;
    }

    /* Кнопка скачивания */
    .stDownloadButton > button {
        background-color: #000000 !important;
        color: #7dffb3 !important;
        border: 2px solid #7dffb3 !important;
        border-radius: 0 !important;
        font-family: 'Press Start 2P', monospace !important;
        font-size: 12px !important;
        padding: 16px 24px !important;
        box-shadow: 4px 4px 0 #7dffb3 !important;
        transition: all 0.1s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 0.02em !important;
        width: 100% !important;
    }
    .stDownloadButton > button:hover {
        transform: translateX(-2px) translateY(-2px) !important;
        box-shadow: 6px 6px 0 #7dffb3 !important;
        background-color: #000000 !important;
        color: #7dffb3 !important;
    }

    /* Разделитель */
    hr {
        border-color: #2e2e3a !important;
        margin: 24px 0 !important;
    }

    /* Hero */
    .hero-title {
        font-family: 'Press Start 2P', monospace;
        font-size: 20px;
        color: #7dffb3;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .hero-underline {
        width: 64px;
        height: 2px;
        background: #ff5da2;
        margin-bottom: 12px;
    }
    .hero-description {
        font-size: 14px;
        color: #888;
        max-width: 42rem;
        line-height: 1.6;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }

    @media (max-width: 640px) {
        .hero-title { font-size: 16px; }
        .stButton > button { font-size: 12px !important; padding: 16px 20px !important; min-width: unset !important; }
    }
    </style>
""", unsafe_allow_html=True)

# === HERO SECTION ===
st.markdown("""
    <div style="max-width: 896px; margin: 2rem auto 2rem auto; padding-top: 2rem; text-align: left;">
        <div class="hero-title">PIXEL_RESTORE_V1.0</div>
        <div class="hero-underline"></div>
        <div class="hero-description">Интеллектуальная коррекция сетки и очистка палитры пиксель-арта.</div>
    </div>
""", unsafe_allow_html=True)

# === ЗОНА ЗАГРУЗКИ ===
uploaded_file = st.file_uploader(
    "Загрузите изображение",
    type=["png", "jpg", "jpeg"],
    label_visibility="collapsed"
)

# Динамическая статусная строка
if uploaded_file is None:
    status_text = "СИСТЕМА ГОТОВА К ОБРАБОТКЕ"
else:
    if 'restored' in st.session_state:
        status_text = "ОБРАБОТКА ЗАВЕРШЕНА"
    else:
        status_text = "ФАЙЛ ЗАГРУЖЕН, НАЖМИТЕ КНОПКУ"

st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 12px; justify-content: center; margin: 16px 0 12px 0; max-width: 896px; margin-left: auto; margin-right: auto;">
        <div class="status-dot"></div>
        <span class="status-line" style="font-size: 10px; color: #555;">{status_text}</span>
    </div>
""", unsafe_allow_html=True)

# Отслеживание смены файла – сброс результата
if uploaded_file is None:
    if 'restored' in st.session_state:
        del st.session_state['restored']
    if 'last_file' in st.session_state:
        del st.session_state['last_file']
else:
    current_file_id = hashlib.md5(uploaded_file.getvalue()).hexdigest()
    if st.session_state.get('last_file') != current_file_id:
        st.session_state['last_file'] = current_file_id
        if 'restored' in st.session_state:
            del st.session_state['restored']

# === ОСНОВНОЙ ИНТЕРФЕЙС (при загруженном файле) ===
if uploaded_file:
    try:
        original = Image.open(uploaded_file).convert("RGB")
    except (UnidentifiedImageError, OSError):
        st.error("Не удалось открыть изображение. Проверьте, что файл не повреждён и имеет формат PNG/JPG.")
        st.stop()
    orig_w, orig_h = original.size

    st.markdown("<hr>", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

   # --- Левая колонка: Исходное изображение + ПАЛИТРА ---
    with col1:
        st.markdown("<p style='font-family: \"Press Start 2P\", monospace; font-size: 12px; color: #888;'>ИСХОДНОЕ</p>", unsafe_allow_html=True)
        st.image(original, use_container_width=True)
        
        # Блок ПАЛИТРЫ (Ретро-заголовок + Flexbox-галерея чипсов)
        if 'restored' in st.session_state:
            st.markdown("<p style='font-family: \"Press Start 2P\", monospace; font-size: 12px; color: #888; margin-top: 24px; margin-bottom: 8px;'>ПАЛИТРА</p>", unsafe_allow_html=True)
            palette = get_palette_stats(st.session_state['restored'])
            
            # Генерация карточек-чипсов для палитры
            chips_html = ""
            for item in palette:
                chips_html += f"""
                <div style="
                    background: #0f1116;
                    border: 2px solid #2e2e3a;
                    padding: 8px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 6px;
                    box-shadow: 2px 2px 0 rgba(0,0,0,0.6);
                ">
                    <div style="
                        width: 100%;
                        height: 32px;
                        background-color: {item['hex']};
                        border: 1px solid #ffffff;
                    "></div>
                    <div style="text-align: center;">
                        <span style="font-family: 'Press Start 2P', monospace; font-size: 8px; color: #ffffff; display: block; margin-bottom: 2px;">{item['hex']}</span>
                        <span style="font-family: 'Press Start 2P', monospace; font-size: 8px; color: #888; display: block;">{item['percentage']:.1f}%</span>
                    </div>
                </div>
                """
            
            # Контейнер-сетка для чипсов
            st.markdown(
                f"""
                <div style="
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
                    gap: 8px;
                    margin-top: 12px;
                    max-height: 320px;
                    overflow-y: auto;
                    padding-right: 4px;
                ">
                    {chips_html}
                </div>
                """,
                unsafe_allow_html=True,
            )
    # --- Правая колонка: Результат ---
    with col2:
        st.markdown("<p style='font-family: \"Press Start 2P\", monospace; font-size: 12px; color: #888;'>РЕЗУЛЬТАТ</p>", unsafe_allow_html=True)
        if 'restored' in st.session_state:
            restored = st.session_state['restored']
            grid_w = st.session_state['grid_w']
            grid_h = st.session_state['grid_h']
            colors_k = st.session_state.get('colors_k')
            if colors_k is None:
                initial_colors = st.session_state.get('initial_colors', [])
                colors_k = initial_colors if isinstance(initial_colors, int) else len(initial_colors)
            result_scale = max(6, min(16, 800 // max(grid_w, grid_h)))
            preview_img = restored.resize((grid_w * result_scale, grid_h * result_scale), Image.NEAREST)
            st.image(preview_img, caption=f"Превью ×{result_scale}", use_container_width=True)

            st.markdown(f"""
            <div class="output-controls">
                <div class="control-grid">
                    <div class="control-card retro-border bg-surface-container">
                        <span class="label">СЕТКА</span>
                        <div class="value">{grid_w}×{grid_h}</div>
                    </div>
                    <div class="control-card retro-border bg-surface-container">
                        <span class="label">ЦВЕТОВ</span>
                        <div class="value">{colors_k}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<div class='download-column'>", unsafe_allow_html=True)
            buf = BytesIO()
            restored.save(buf, format="PNG")
            st.download_button(
                label="СКАЧАТЬ РЕЗУЛЬТАТ",
                data=buf.getvalue(),
                file_name="pixel_grid.png",
                mime="image/png",
                key="download_result",
                help="",
                use_container_width=True
            )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            if st.button("ВОССТАНОВИТЬ ПИКСЕЛЬ-АРТ", key="restore_btn"):
                with st.spinner("Интеллектуальный анализ пиксель-арта..."):
                    step, w, h = detect_grid_size(original.convert("L"))
                    restored, k, mean_err, max_err, elbow_k, initial_mean, initial_max, initial_colors = optimize_palette(original, w, h)

                    st.session_state['restored'] = restored
                    st.session_state['grid_step'] = step
                    st.session_state['grid_w'] = w
                    st.session_state['grid_h'] = h
                    st.session_state['colors_k'] = k
                    st.session_state['elbow_k'] = elbow_k
                    st.session_state['initial_mean_err'] = initial_mean
                    st.session_state['initial_max_err'] = initial_max
                    st.session_state['mean_err'] = mean_err
                    st.session_state['max_err'] = max_err
                    st.session_state['initial_colors'] = initial_colors
                    st.session_state['result_scale'] = max(6, min(16, 800 // max(w, h)))
                    st.rerun()
else:
    # Ничего не выводим, если файл не загружен – чистая hero-секция
    pass