import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from scipy.signal import correlate
import streamlit as st

def analyze_grid_step(img_gray):
    """Аналитическое определение размера сетки по градиентам яркости."""
    arr = np.array(img_gray, dtype=float)
    
    # Вычисляем градиент яркости по строкам и столбцам
    grad_x = np.abs(np.diff(arr, axis=1))
    grad_y = np.abs(np.diff(arr, axis=0))
    
    profile_x = np.mean(grad_x, axis=0)
    profile_y = np.mean(grad_y, axis=1)
    
    def find_period(profile):
        if len(profile) < 4:
            return 1
        corr = correlate(profile - np.mean(profile), profile - np.mean(profile), mode='full')
        corr = corr[len(corr)//2:]
        if len(corr) < 2:
            return 1
        peaks = []
        for i in range(1, len(corr) - 1):
            if corr[i] > corr[i-1] and corr[i] > corr[i+1]:
                peaks.append(i)
        return peaks[0] if peaks else 1

    step_x = find_period(profile_x)
    step_y = find_period(profile_y)
    
    estimated_step = int(round((step_x + step_y) / 2))
    return max(1, estimated_step)

def snap_to_convenient(val):
    """Корректировка к удобному числу, если оно близко."""
    convenient = [8, 16, 32, 64, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 150]
    for c in convenient:
        if abs(val - c) / c <= 0.15:
            return c
    return val

def process_pixel_art(img_orig):
    W, H = img_orig.size
    img_gray = img_orig.convert("L")
    
    # 1. Анализ шага сетки
    step = analyze_grid_step(img_gray)
    raw_grid_w = round(W / step)
    raw_grid_h = round(H / step)
    
    grid_w = snap_to_convenient(raw_grid_w)
    grid_h = snap_to_convenient(raw_grid_h)
    
    # 2. Масштабирование (усреднение блоков)
    img_small = img_orig.resize((grid_w, grid_h), Image.Resampling.BOX)
    
    # 3. Очистка палитры (K-Means с защитой от потери мелких деталей)
    pixels = np.array(img_small).reshape(-1, 3)
    
    inertias = []
    max_k_range = min(33, len(np.unique(pixels, axis=0)))
    if max_k_range < 6:
        max_k_range = max(2, len(np.unique(pixels, axis=0)))
    k_range = range(6, max_k_range) if max_k_range > 6 else range(2, max_k_range)
    
    for k in k_range:
        kmeans = KMeans(n_clusters=k, n_init=10, random_state=42).fit(pixels)
        inertias.append(kmeans.inertia_)
    
    best_k = list(k_range)[0]
    if len(inertias) > 2:
        diffs = np.diff(inertias)
        diffs_2 = np.diff(diffs)
        if len(diffs_2) > 0:
            best_k = list(k_range)[np.argmax(diffs_2) + 1]
            
    current_k = best_k
    max_iter_k = 64
    mean_err, max_err = 0.0, 0.0
    
    while current_k <= max_iter_k:
        kmeans = KMeans(n_clusters=current_k, n_init=15, random_state=42).fit(pixels)
        labels = kmeans.labels_
        centers = kmeans.cluster_centers_
        
        assigned_centers = centers[labels]
        distances = np.linalg.norm(pixels - assigned_centers, axis=1)
        
        mean_err = np.mean(distances)
        max_err = np.max(distances)
        
        if max_err > 22.0 and current_k + 4 <= max_iter_k:
            current_k += 4
        else:
            break
            
    quantized_arr = assigned_centers.clip(0, 255).astype(np.uint8).reshape((grid_h, grid_w, 3))
    img_quantized = Image.fromarray(quantized_arr, "RGB")
    
    # 4. Создание превью
    scale_factor = 8
    img_preview = img_quantized.resize((grid_w * scale_factor, grid_h * scale_factor), Image.Resampling.NEAREST)
    
    info = {
        "step": step,
        "grid_w": grid_w,
        "grid_h": grid_h,
        "elbow_k": best_k,
        "final_k": current_k,
        "mean_err": mean_err,
        "max_err": max_err
    }
    
    return img_quantized, img_preview, info

# --- INTERFACE (Streamlit) ---
st.title("🧵 Восстановление Pixel Art для схем вышивки")
st.write("Загрузите размытое изображение пиксель-арта, и алгоритм автоматически вернет ему исходную четкость и палитру.")

uploaded_file = st.file_uploader("Выберите файл изображения (PNG, JPG)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    img_orig = Image.open(uploaded_file).convert("RGB")
    
    st.subheader("Исходное изображение")
    st.image(img_orig, caption="Загруженный файл", use_container_width=True)
    
    if st.button("Создать схему"):
        with st.spinner("Анализируем сетку и очищаем палитру..."):
            img_quantized, img_preview, info = process_pixel_art(img_orig)
            
        st.success("Готово!")
        
        # Вывод аналитики
        st.info(
            f"**Результаты анализа:**\n"
            f"- Найденный шаг сетки: **{info['step']} px**\n"
            f"- Итоговый размер схемы: **{info['grid_w']} x {info['grid_h']} крестиков**\n"
            f"- Базовый 'локоть' палитры (k): **{info['elbow_k']}**\n"
            f"- Итоговое число цветов после проверки деталей: **{info['final_k']}**\n"
            f"- Ошибка квантования: средняя = **{info['mean_err']:.2f}**, максимальная = **{info['max_err']:.2f}**"
        )
        
        st.subheader("Результат обработки (увеличенная превьюшка)")
        st.image(img_preview, caption=f"Схема в разрешении сетки {info['grid_w']}x{info['grid_h']} (увеличено для просмотра)", use_container_width=True)
        
        # Подготовка файлов к скачиванию в байтовый формат
        import io
        
        # Файл 1: Точный размер сетки
        buf_small = io.BytesIO()
        img_quantized.save(buf_small, format="PNG")
        byte_small = buf_small.getvalue()
        
        # Файл 2: Увеличенное превью
        buf_large = io.BytesIO()
        img_preview.save(buf_large, format="PNG")
        byte_large = buf_large.getvalue()
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="⬇️ Скачать схему (оригинальный размер)",
                data=byte_small,
                file_name="pixel_art_grid.png",
                mime="image/png"
            )
        with col2:
            st.download_button(
                label="⬇️ Скачать превью (для просмотра)",
                data=byte_large,
                file_name="pixel_art_preview.png",
                mime="image/png"
            )
