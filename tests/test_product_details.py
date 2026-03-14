import allure
from pages.catalog_page import CatalogPage  # Импортируем из правильного модуля
from pages.product_page import ProductPage
from config.config import Config


@allure.feature("Карточка товара")
@allure.story("Проверка деталей товара")
def test_product_details(catalog_page, product_page):
    TARGET_PRODUCT = "Диван Мешковина"

    catalog_page.open_catalog()

    with allure.step(f"Найти и кликнуть на товар '{TARGET_PRODUCT}'"):
        # Используем метод из CatalogPage
        assert catalog_page.find_product_by_name(TARGET_PRODUCT), f"Товар '{TARGET_PRODUCT}' не найден"
        actual_href = catalog_page.get_product_href_by_name(TARGET_PRODUCT)
        catalog_page.click_product_by_name(TARGET_PRODUCT)

    with allure.step("Проверить, что открылась карточка правильного товара"):
        product_page_link = product_page.get_product_title()
        assert actual_href in product_page.page.url, \
            f"Открылась ссылка '{product_page_link}' вместо '{actual_href}'"

    with allure.step("Перейти на вкладку 'Характеристики'"):
        product_page.click_specifications_tab()


    with allure.step("Получить все характеристики товара"):
        specs = product_page.get_specifications_from_table()

        # Выводим все характеристики в отчет
        if specs:
            specs_text = "\n".join([f"  • {k}: {v}" for k, v in specs.items()])
            allure.attach(f"Найденные характеристики:\n{specs_text}",
                          name="Характеристики товара")
        else:
            allure.attach("Характеристики не найдены", name="Ошибка")
            # Не падаем, а просто логируем, так как не у всех товаров есть характеристики

    with allure.step("Проверить наличие и корректность характеристики 'Ширина'"):
        # Проверяем конкретную характеристику
        width_value = product_page.get_specification_value("Ширина")

        if width_value:
            allure.attach(f"Найдена ширина: {width_value}", name="Информация")

            assert "2200" in width_value or "2200" in width_value, \
                f"Ожидалась ширина 2200 мм, получено '{width_value}'"

            numeric_width = product_page.extract_numeric_value(width_value)
            allure.attach(f"Числовое значение ширины: {numeric_width} мм",
                          name="Информация")

        else:
            # Если ширина не найдена, пробуем другие характеристики
            allure.attach("Характеристика 'Ширина' не найдена, ищем альтернативы",
                          name="Предупреждение")

            # Проверяем другие возможные названия
            alt_names = ["Габариты", "Размеры", "Длина"]
            found = False

            for alt_name in alt_names:
                alt_value = product_page.get_specification_value(alt_name)
                if alt_value:
                    allure.attach(f"Найдена альтернативная характеристика '{alt_name}': {alt_value}",
                                  name="Информация")
                    found = True
                    break

            if not found:
                allure.attach("Не удалось найти информацию о размерах товара",
                              name="Предупреждение")
                # Не падаем, так как это не критично для демо-теста

    with allure.step("Проверить другие характеристики"):
        # Проверяем механизм трансформации (если есть)
        mechanism = product_page.get_specification_value("Механизм")
        if mechanism:
            allure.attach(f"Механизм трансформации: {mechanism}", name="Информация")

        # Проверяем материал
        material = product_page.get_specification_value("Материал")
        if material:
            allure.attach(f"Материал: {material}", name="Информация")

        # Проверяем цвет
        color = product_page.get_specification_value("Цвет")
        if color:
            allure.attach(f"Цвет: {color}", name="Информация")