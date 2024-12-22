import dearpygui.dearpygui as dpg
import json
import pandas as pd

# Хранилище операций
operations = []

big_let_start = 0x00C0
big_let_end = 0x00DF
small_let_end = 0x00FF
remap_big_let = 0x0410
alph_len = big_let_end - big_let_start + 1
alph_shift = remap_big_let - big_let_start


def add_operation(sender, app_data, user_data):
    category = dpg.get_value("category_input")
    amount = float(dpg.get_value("amount_input"))
    description = dpg.get_value("description_input")
    operations.append({"category": category, "amount": amount, "description": description})
    dpg.add_row(user_data, [category, amount, description])
    dpg.set_value("category_input", "")
    dpg.set_value("amount_input", "0.0")
    dpg.set_value("description_input", "")


# Сохранение операций в JSON
def save_operations(sender, app_data, user_data):
    with open("operations.json", "w", encoding="utf-8") as file:
        json.dump(operations, file, indent=4, ensure_ascii=False)
    dpg.set_value("status_text", "Операции сохранены в operations.json")


# Загрузка операций из JSON
def load_operations(sender, app_data, user_data):
    global operations
    try:
        with open("operations.json", "r", encoding="utf-8") as file:
            operations = json.load(file)
        dpg.delete_item("operations_table", children_only=True)
        for op in operations:
            dpg.add_row("operations_table", [op["category"], op["amount"], op["description"]])
        dpg.set_value("status_text", "Операции загружены из operations.json")
    except Exception as e:
        dpg.set_value("status_text", f"Ошибка загрузки: {str(e)}")


# Загрузка операций из XLSX
def load_from_xlsx(sender, app_data, user_data):
    global operations
    file_path = dpg.get_value("xlsx_file_input")
    try:
        df = pd.read_excel(file_path)
        for _, row in df.iterrows():
            category = row.get("Category", "Неизвестно")
            amount = row.get("Amount", 0.0)
            description = row.get("Description", "")
            operations.append({"category": category, "amount": amount, "description": description})
            dpg.add_row("operations_table", [category, amount, description])
        dpg.set_value("status_text", "Операции загружены из XLSX")
    except Exception as e:
        dpg.set_value("status_text", f"Ошибка загрузки: {str(e)}")


# Интерфейс приложения
dpg.create_context()
dpg.create_viewport(title="Финансовый учёт", width=800, height=600)
with dpg.font_registry():
    with dpg.font("EpilepsySans.ttf", 13, default_font=True) as font1:
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
        biglet = remap_big_let
        for i1 in range(big_let_start, big_let_end + 1):
            dpg.add_char_remap(i1, biglet)
            dpg.add_char_remap(i1 + alph_len, biglet + alph_len)
            biglet += 1
        dpg.add_char_remap(0x00A8, 0x0401)
        dpg.add_char_remap(0x00B8, 0x0451)
        dpg.add_font_chars([0x0451, 0x2116])

dpg.bind_font(font1)
with dpg.window(label="Финансовый учёт", width=800, height=600):
    dpg.add_text("Добавить операцию")
    dpg.add_input_text(label="Категория", tag="category_input")
    dpg.add_input_text(label="Сумма", tag="amount_input", default_value="0.0")
    dpg.add_input_text(label="Описание", tag="description_input")
    dpg.add_button(label="Добавить", callback=add_operation, user_data="operations_table")

    dpg.add_separator()

    dpg.add_text("Операции")
    with dpg.table(label="Таблица операций", header_row=True, tag="operations_table"):
        dpg.add_table_column(label="Категория")
        dpg.add_table_column(label="Сумма")
        dpg.add_table_column(label="Описание")

    dpg.add_separator()

    dpg.add_text("Функции")
    dpg.add_button(label="Сохранить операции", callback=save_operations)
    dpg.add_button(label="Загрузить операции", callback=load_operations)

    dpg.add_separator()

    dpg.add_text("Загрузка из XLSX")
    dpg.add_input_text(label="Путь к файлу", tag="xlsx_file_input", default_value="bank_report.xlsx")
    dpg.add_button(label="Загрузить", callback=load_from_xlsx)

    dpg.add_separator()
    dpg.add_text("", tag="status_text")

dpg.create_viewport()
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
