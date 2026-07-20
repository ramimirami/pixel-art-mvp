# Pixel Refiner Studio

Локальная версия Streamlit-приложения для восстановления и очистки палитры пиксель-арта.

## Кратко
Инструмент автоматически детектирует сетку пиксель-арта, оптимизирует палитру и генерирует результат для скачивания.

## Требования
- Python 3.9+ (минимум)
- Рекомендуется виртуальное окружение (venv)

Установите зависимости:

```bash
python3 -m venv venv
source venv/bin/activate
pip install streamlit numpy pillow scikit-learn scipy
```

## Запуск

```bash
source venv/bin/activate
streamlit run restorer_app.py
```

Откройте в браузере адрес, который выведет Streamlit (обычно http://localhost:8501).

## Файловая структура (важные файлы)
- `restorer_app.py` — Streamlit UI, загрузка файлов, показ превью и кнопка скачивания.
- `pixel_core.py` — логика обнаружения сетки и оптимизации палитры (ядро обработки).

## Быстрая отладка
- При изменениях UI или логики перезапустите Streamlit или используйте `st.experimental_rerun()` в коде для ускорения цикла разработки.
- Для проверки синтаксиса:

```bash
python -m py_compile restorer_app.py
```

## Примечания
- Интерфейс использует кастомные CSS-правила, внедряемые через `st.markdown(..., unsafe_allow_html=True)`.
- Если появятся ошибки с ключами виджетов (duplicate key), убедитесь, что в коде каждому виджету назначен уникальный `key`.

Если хотите, могу также создать `requirements.txt` и короткий `CONTRIBUTING.md`.