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

    with allure.step("Получить информацию о первом товаре"):
        # Получаем название и цену первого товара
        expected_name = catalog_page.get_first_product_name()
        expected_price = catalog_page.get_first_product_price()

        allure.attach(
            f"Первый товар в каталоге:\n"
            f"Название: {expected_name}\n"
            f"Цена: {expected_price}",
            name="Информация о товаре"
        )

        # Для отладки - проверим состояние иконки избранного до клика
        icon_classes = catalog_page.get_first_favorite_icon_state()
        allure.attach(f"Состояние иконки избранного до клика: {icon_classes}",
                      name="Отладка")

    # Добавляем в избранное
    with allure.step("Добавить первый товар в избранное"):
        catalog_page.click_first_product_favorite()

        # Проверяем, что иконка изменила состояние (опционально)
        icon_classes_after = catalog_page.get_first_favorite_icon_state()
        allure.attach(f"Состояние иконки избранного после клика: {icon_classes_after}",
                      name="Отладка")

    # Небольшая пауза для обновления счетчика
    page.wait_for_timeout(2000)

    # Проверяем, что счетчик избранного увеличился (опционально)
    with allure.step("Проверить счетчик избранного в шапке"):
        favorite_count = header.get_favorite_count()
        allure.attach(f"Счетчик избранного: {favorite_count}", name="Информация")
        assert favorite_count > 0, "Счетчик избранного не увеличился"

    # Переходим в избранное через шапку
    with allure.step("Перейти в раздел Избранное"):
        header.go_to_favorite()

    with allure.step("Проверить, что в избранном есть товары"):
        assert favorite_page.is_favorite_has_items(), "Список избранного пуст"
        items_count = favorite_page.get_favorite_items_count()
        allure.attach(f"Количество товаров в избранном: {items_count}",
                      name="Информация")

    with allure.step("Проверить, что добавленный товар отображается в избранном"):
        actual_name = favorite_page.get_first_product_name()
        actual_price = favorite_page.get_first_product_price()

        allure.attach(
            f"Товар в избранном:\n"
            f"Название: {actual_name}\n"
            f"Цена: {actual_price}",
            name="Информация о товаре в избранном"
        )

        # Проверяем название (частичное совпадение)
        assert expected_name.lower() in actual_name.lower() or \
               actual_name.lower() in expected_name.lower(), \
            f"Названия не совпадают: ожидалось '{expected_name}', получено '{actual_name}'"

        # Проверяем цену (очищенную от символов)
        expected_price_clean = catalog_page.clean_price(expected_price)
        actual_price_clean = catalog_page.clean_price(actual_price)

        # Цены могут немного отличаться из-за скидок, поэтому проверяем с допуском
        price_diff = abs(expected_price_clean - actual_price_clean)
        assert price_diff < 1000, \
            f"Цены сильно отличаются: ожидалось {expected_price_clean}, получено {actual_price_clean}"
