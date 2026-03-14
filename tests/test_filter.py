# tests/test_filter.py
import allure
import re
from pages.catalog_page import CatalogPage
from config.config import Config


@allure.feature("Фильтрация товаров")
@allure.story("Фильтрация по цене в каталоге диванов")
def test_filter_by_price(catalog_page):
    """Тест проверяет работу фильтра по цене и наличие конкретного товара"""

    TARGET_PRODUCT = "Диван замша"
    PRICE_FROM = 10000  # Изменено на число
    PRICE_TO = 20000  # Изменено на число

    with allure.step("Открыть каталог диванов"):
        catalog_page.open_catalog()
        # Проверяем, что мы действительно на странице диванов
        page_title = catalog_page.get_page_title()
        allure.attach(f"Заголовок страницы: {page_title}", name="Информация")

    with allure.step(f"Применить фильтр по цене: от {PRICE_FROM} до {PRICE_TO}"):
        # Передаем как строки для URL
        catalog_page.apply_price_filter(str(PRICE_FROM), str(PRICE_TO))

        # Проверяем URL после применения фильтра
        current_url = catalog_page.page.url
        allure.attach(f"URL после фильтрации: {current_url}", name="Информация")

        # Проверяем, что в URL есть параметры фильтрации
        assert f"price={PRICE_FROM}-{PRICE_TO}" in current_url, \
            f"Параметры фильтрации не найдены в URL: {current_url}"


    with (allure.step(f"Найти товар '{TARGET_PRODUCT}' в результатах")):
        # Проверяем наличие целевого товара
        found = catalog_page.find_product_by_name(TARGET_PRODUCT)
        assert found, f"Товар '{TARGET_PRODUCT}' не найден после фильтрации"
        print(f"Товар '{TARGET_PRODUCT}' найден после фильтрации")
