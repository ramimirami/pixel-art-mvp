import streamlit as st
from PIL import Image
from io import BytesIO
from pixel_core import detect_grid_size, optimize_palette

# Конфигурация страницы
st.set_page_config(
    page_title="Pixel Refiner Studio",
    page_icon="🎨",
    layout="wide"
)

# Точная дизайн-система из предоставленного макета Tailwind / Material Design
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=block');

    .stApp {
        background-color: #0b0f19;
        color: #dfe2f1;
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif;
    }

    /* Карточки метрик (Surface Container) */
    .metric-card {
        background: #1c1f2a;
        border: 1px solid #424754;
        padding: 16px;
        border-radius: 8px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .metric-title {
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.01em;
        color: #c2c6d6;
        margin-bottom: 4px;
        font-weight: 500;
    }
    .metric-value {
        font-size: 20px;
        font-weight: 600;
        color: #adc6ff;
    }

    /* Основные кнопки Streamlit */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background: #3b82f6;
        color: #ffffff !important;
        font-weight: 600;
        border: none;
        padding: 0.85rem 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.3);
        transition: all 0.2s ease;
        font-size: 16px;
    }
    .stButton>button:hover {
        background: #2563eb;
        transform: translateY(-1px);
        box-shadow: 0 15px 30px -5px rgba(59, 130, 246, 0.4);
        color: #ffffff !important;
    }

    /* Кастомная кнопка скачивания Streamlit */
    .stDownloadButton>button {
        width: 100%;
        border-radius: 8px;
        background: #3b82f6 !important;
        color: #ffffff !important;
        font-weight: 600;
        border: none;
        padding: 0.85rem 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.3);
        transition: all 0.2s ease;
        font-size: 16px;
    }
    .stDownloadButton>button:hover {
        background: #2563eb !important;
        transform: translateY(-1px);
        box-shadow: 0 15px 30px -5px rgba(59, 130, 246, 0.4);
        color: #ffffff !important;
    }

    /* Рамки картинок и контейнер пиксель-арта без сглаживания (nearest neighbor) */
    img {
        border-radius: 8px;
        border: 1px solid #424754;
        image-rendering: pixelated;
        image-rendering: crisp-edges;
    }

    /* Скрываем стандартный кривой лейбл Streamlit */
    div[data-testid="stFileUploader"] > label {
        display: none !important;
    }

    /* Превращаем uploader в кастомную зону Drag & Drop из макета */
    div[data-testid="stFileUploader"] {
        background: transparent;
        padding: 0;
        width: 100%;
        max-width: 896px;
        margin: 0 auto;
    }
    div[data-testid="stFileUploader"] section {
        background: #0f131d !important;
        border: 2px dashed #424754 !important;
        border-radius: 8px !important;
        padding: 32px !important;
        min-height: 180px !important;
        text-align: left !important;
        transition: all 0.3s ease;
    }
    div[data-testid="stFileUploader"] section:hover {
        border-color: rgba(59, 130, 246, 0.5) !important;
        background: rgba(23, 27, 38, 0.3) !important;
    }

    /* Тексты внутри загрузчика */
    div[data-testid="stFileUploader"] span {
        color: #dfe2f1 !important;
        font-size: 24px !important;
        font-weight: 600 !important;
    }
    div[data-testid="stFileUploader"] small {
        color: #c2c6d6 !important;
        font-size: 14px !important;
    }

    /* Кнопка Browse files в стиле макета */
    div[data-testid="stFileUploader"] button {
        background-color: #3b82f6 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.2) !important;
    }
    div[data-testid="stFileUploader"] button:hover {
        opacity: 0.9 !important;
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# TopNavBar
st.markdown("""
    <header style="background-color: #0f131d; border-bottom: 1px solid #424754; padding: 16px 24px; margin: -6rem -4rem 2rem -4rem; position: sticky; top: 0; z-index: 50;">
        <div style="max-width: 1280px; margin: 0 auto; display: flex; align-items: center; gap: 12px;">
            <span class="material-symbols-outlined" style="font-size: 28px; color: #3b82f6; font-variation-settings: 'FILL' 1;">auto_awesome</span>
            <span style="font-size: 18px; font-weight: 700; color: #ffffff; letter-spacing: -0.01em;">Pixel Refiner Studio</span>
        </div>
    </header>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
    <div style="max-width: 896px; margin: 0 auto 3rem auto; text-align: left;">
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
            <span class="material-symbols-outlined" style="font-size: 40px; color: #3b82f6; font-variation-settings: 'FILL' 1;">auto_awesome</span>
            <h1 style="font-size: 48px; font-weight: 700; margin: 0; letter-spacing: -0.02em; line-height: 56px;">Pixel Refiner Studio</h1>
        </div>
        <p style="font-size: 18px; color: #c2c6d6; line-height: 28px; margin: 0; max-width: 42rem;">
            Интеллектуальная коррекция сетки и очистка палитры пиксель-арта.
        </p>
    </div>
""", unsafe_allow_html=True)

# Зона загрузки (Drag & Drop) строго по макету
uploaded_file = st.file_uploader("Загрузите изображение для начала работы", type=["png", "jpg", "jpeg"])

# Отслеживание смены файла для сброса старого результата в сессии
if uploaded_file is None:
    if 'restored' in st.session_state:
        del st.session_state['restored']
    if 'last_file' in st.session_state:
        del st.session_state['last_file']
else:
    current_file_id = getattr(uploaded_file, "file_id", uploaded_file.name)
    if st.session_state.get('last_file') != current_file_id:
        st.session_state['last_file'] = current_file_id
        if 'restored' in st.session_state:
            del st.session_state['restored']

if uploaded_file:
    original = Image.open(uploaded_file).convert("RGB")
    
    st.markdown("<br><hr style='border-color: #424754;'><br>", unsafe_allow_html=True)
    
    # Основная сетка: слева оригинал, справа результат обработки
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.subheader("Исходное изображение")
        orig_w, orig_h = original.size
        st.image(original.resize((orig_w * 8, orig_h * 8), Image.Resampling.NEAREST), use_container_width=True)

    with col2:
        st.subheader("Результат восстановления")
        
        if 'restored' in st.session_state:
            restored_img = st.session_state['restored']
            res_w, res_h = restored_img.size
            st.image(restored_img.resize((res_w * 8, res_h * 8), Image.Resampling.NEAREST), use_container_width=True)
        else:
            # Заглушка, если обработка еще не запущена
            st.markdown("""
                <div style="text-align: center; padding: 60px 24px; color: #c2c6d6; border: 1px dashed #424754; border-radius: 8px; background: #171b26;">
                    <span class="material-symbols-outlined" style="font-size: 48px; color: #8c909f; margin-bottom: 12px;">image_search</span>
                    <p style="font-size: 16px; margin: 0; color: #dfe2f1;">Изображение загружено. Нажмите кнопку ниже для запуска обработки.</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Запустить обработку"):
                with st.spinner("Интеллектуальный анализ пиксель-арта..."):
                    step, w, h = detect_grid_size(original.convert("L"))
                    restored, k, *_ = optimize_palette(original, w, h)
                    st.session_state['restored'] = restored
                    st.session_state['grid_w'] = w
                    st.session_state['grid_h'] = h
                    st.session_state['colors_k'] = k
                    st.rerun()

    # Если обработка завершена, выносим Панель метрик и Кнопку скачивания на всю ширину под изображениями
    if 'restored' in st.session_state:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Контейнер результатов на всю ширину (3 колонки: Метрика 1, Метрика 2, Кнопка скачивания)
        res_col1, res_col2, res_col3 = st.columns([1, 1, 1.5], gap="medium")
        
        with res_col1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Определенная сетка</div>
                    <div class="metric-value">{st.session_state['grid_w']} × {st.session_state['grid_h']}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with res_col2:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Оптимизация палитры (K)</div>
                    <div class="metric-value">{st.session_state['colors_k']}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with res_col3:
            # Центрируем кнопку скачивания визуально на уровне карточек
            st.markdown("<div style='margin-top: 4px;'></div>", unsafe_allow_html=True)
            buf = BytesIO()
            st.session_state['restored'].save(buf, format="PNG")
            st.download_button(
                label="Скачать результат",
                data=buf.getvalue(),
                file_name="pixel_refined.png",
                mime="image/png"
            )