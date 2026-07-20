import numpy as np
from PIL import Image
from scipy.signal import correlate, find_peaks
from sklearn.cluster import KMeans
import streamlit as st
from io import BytesIO

st.set_page_config(
    page_title="Pixel Art to Cross-Stitch Converter", layout="centered"
)

st.title("Востановление Pixel Art")
st.write(
    "Загрузи пиксель-арт, чтобы автоматически определить сетку, очистить палитру и получить точную схему."
)

uploaded_file = st.file_uploader(
    "Выберите изображение...", type=["png", "jpg", "jpeg"]
)


def detect_grid_size(img_gray):
  """Аналитическое определение размера сетки через градиенты и автокорреляцию."""
  img_np = np.array(img_gray, dtype=float)

  # Считаем разницу соседних пикселей (градиент) по строкам и столбцам
  grad_x = np.abs(np.diff(img_np, axis=1))
  grad_y = np.abs(np.diff(img_np, axis=0))

  # Проекции градиентов на оси (суммируем по строкам/столбцам)
  profile_x = np.sum(grad_x, axis=0)
  profile_y = np.sum(grad_y, axis=1)


  def find_period(profile):
    if len(profile) < 4:
      return 1
    # Автокорреляция профиля для поиска повторяющегося шага сетки
    corr = correlate(profile - np.mean(profile), profile - np.mean(profile), mode='full')
    # Оставляем только правую часть (положительные лаги)
    corr = corr[len(corr) // 2 :]

    if len(corr) < 3:
      return 1

    # Ищем пики автокорреляции (игнорируем нулевой лаг)
    peaks, _ = find_peaks(corr, distance=2)
    if len(peaks) > 0:
      return int(peaks[0])

    return max(1, int(np.argmax(corr[1:]) + 1))


  step_x = find_period(profile_x)
  step_y = find_period(profile_y)

  # Усредняем шаг по осям и приводим к разумному целому
  estimated_step = int(round((step_x + step_y) / 2))
  estimated_step = max(1, estimated_step)

  orig_w, orig_h = img_gray.size

  # Размеры сетки
  grid_w = max(1, round(orig_w / estimated_step))
  grid_h = max(1, round(orig_h / estimated_step))

  return estimated_step, grid_w, grid_h


def optimize_palette_with_guard(img_rgb, target_w, target_h, max_k=32):
  """Даунскейл методом box-фильтра и подбор K-Means палитры с защитой от потери мелких деталей."""
  img_small = img_rgb.resize((target_w, target_h), Image.Resampling.BOX)
  pixels = np.array(img_small, dtype=float).reshape(-1, 3)

  best_labels = None
  best_centers = None
  chosen_k = 6
  mean_err = 0.0
  max_err = 0.0

  unique_colors_count = len(np.unique(pixels, axis=0))
  limit_k = min(max_k + 1, unique_colors_count + 1)

  for k in range(6, max(7, limit_k), 2):
    kmeans = KMeans(n_clusters=k, n_init=15, random_state=42)
    labels = kmeans.fit_predict(pixels)
    centers = kmeans.cluster_centers_

    quantized_pixels = centers[labels]
    errors = np.linalg.norm(pixels - quantized_pixels, axis=1)

    max_err = np.max(errors)
    mean_err = np.mean(errors)

    chosen_k = k
    best_labels = labels
    best_centers = centers

    if mean_err < 3.5 and max_err < 22:
      break

  final_pixels_rgb = np.clip(best_centers[best_labels], 0, 255).astype(np.uint8)
  result_small_np = final_pixels_rgb.reshape((target_h, target_w, 3))
  result_small_img = Image.fromarray(result_small_np, mode="RGB")

  return result_small_img, chosen_k, mean_err, max_err


if uploaded_file is not None:
  original_image = Image.open(uploaded_file).convert("RGB")
  st.image(
      original_image,
      caption="Исходное загруженное изображение",
      use_container_width=True,
  )

  if st.button("🚀 Запустить аналитический анализ и конвертацию"):
    with st.spinner("Анализируем сетку и подбираем палитру..."):
      gray_image = original_image.convert("L")
      step, grid_w, grid_h = detect_grid_size(gray_image)

      st.success(
          f"✅ **Анализ завершен:** найден шаг сетки **{step} px**, размер"
          f" сетки: **{grid_w} × {grid_h} крестиков**."
      )

      palette_img, final_k, mean_err, max_err = optimize_palette_with_guard(
          original_image, grid_w, grid_h
      )

      st.info(
          f"🎨 **Палитра:** подобрано цветов ($k$): **{final_k}**. Средняя"
          f" ошибка квантования: **{mean_err:.2f}**, максимальная:"
          f" **{max_err:.2f}**."
      )

      scale_preview = max(6, min(8, 1000 // max(grid_w, grid_h)))
      preview_img = palette_img.resize(
          (grid_w * scale_preview, grid_h * scale_preview),
          Image.Resampling.NEAREST,
      )

      col1, col2 = st.columns(2)

      with col1:
        st.image(
            palette_img,
            caption=f"Схема в исходном размере ({grid_w}x{grid_h})",
            use_container_width=True,
        )
        buf_small = BytesIO()
        palette_img.save(buf_small, format="PNG")
        byte_small = buf_small.getvalue()

        st.download_button(
            label="📥 Скачать схему (оригинальный размер)",
            data=byte_small,
            file_name="cross_stitch_grid.png",
            mime="image/png",
        )

      with col2:
        st.image(
            preview_img,
            caption=f"Превью для просмотра (×{scale_preview})",
            use_container_width=True,
        )
        buf_large = BytesIO()
        preview_img.save(buf_large, format="PNG")
        byte_large = buf_large.getvalue()

        st.download_button(
            label="📥 Скачать превью (для просмотра)",
            data=byte_large,
            file_name="cross_stitch_preview.png",
            mime="image/png",
        )