# tests/test_favorite.py
import allure
from pages.header_component import HeaderComponent


@allure.feature("Избранное")
@allure.story("Добавление и проверка товара в избранном")
def test_add_to_favorite(catalog_page, favorite_page, page):
    """Тест проверяет добавление товара в избранное"""
    header = HeaderComponent(page)

    # Открываем каталог
    catalog_page.open_catalog()
    catalog_page.take_screenshot("Каталог открыт", force=True)

    # Получаем информацию о первом товаре и добавляем в избранное
    with allure.step("Получить информацию о первом товаре и добавить в избранное"):
        expected_href = catalog_page.get_first_product_href()
        expected_name = catalog_page.get_first_product_name()

        allure.attach(
            f"Первый товар в каталоге:\nНазвание: {expected_name}\nhref: {expected_href}",
            name="Информация о товаре"
        )

        catalog_page.click_first_product_favorite()
        # Скриншот уже есть внутри метода click_first_product_favorite

    # Переходим в избранное
    with allure.step("Перейти в раздел Избранное через шапку сайта"):
        header.go_to_favorite()
        favorite_page.take_screenshot("Страница избранного", force=True)

    # Проверяем, что в избранном есть товары
    with allure.step("Проверить наличие товаров в избранном"):
        has_items = favorite_page.is_favorite_has_items()
        assert has_items, "Список избранного пуст"

    # Проверяем, что добавленный товар отображается в избранном
    with allure.step("Проверить, что добавленный товар отображается в избранном"):
        actual_href = favorite_page.get_first_product_href()

        assert expected_href, "Не удалось получить href товара из каталога"
        assert actual_href, "Не удалось получить href товара из избранного"

        expected_href_norm = expected_href.split('/')[-1]
        actual_href_norm = actual_href.split('/')[-1]

        assert (expected_href_norm in actual_href_norm) or (actual_href_norm in expected_href_norm), \
            f"href не совпадают: ожидалось '{expected_href}', получено '{actual_href}'"

        allure.attach("Товар успешно найден в избранном", name="Успех")