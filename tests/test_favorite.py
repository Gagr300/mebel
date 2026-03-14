# tests/test_favorite.py
import allure
import pytest
from pages.header_component import HeaderComponent


@allure.feature("Избранное")
@allure.story("Добавление и проверка товара в избранном")
def test_add_to_favorite(catalog_page, favorite_page, page):
    """
    Тест проверяет добавление товара в избранное:
    1. Открыть каталог диванов
    2. У первого товара нажать иконку избранного
    3. Перейти в раздел избранного через шапку сайта
    4. Проверить, что товар отображается в избранном (по href)
    """
    header = HeaderComponent(page)

    # Шаг 1: Открываем каталог
    catalog_page.open_catalog()

    # Шаг 2: Получаем информацию о первом товаре и добавляем в избранное
    with allure.step("Получить информацию о первом товаре и добавить в избранное"):
        # Получаем href первого товара (более надежно, чем название)
        expected_href = catalog_page.get_first_product_href()
        expected_name = catalog_page.get_first_product_name()  # для информации

        allure.attach(
            f"Первый товар в каталоге:\n"
            f"Название: {expected_name}\n"
            f"href: {expected_href}\n"
            f"ID: {favorite_page.get_product_id_from_href(expected_href)}",
            name="Информация о товаре"
        )

        # Проверяем состояние иконки избранного до клика (опционально)
        icon_state_before = catalog_page.get_first_favorite_icon_state()
        allure.attach(f"Состояние иконки ДО клика: {icon_state_before}", name="Отладка")

        # Добавляем в избранное
        catalog_page.click_first_product_favorite()

        # Небольшая пауза для обновления счетчика
        page.wait_for_timeout(2000)

    # Шаг 3: Проверяем счетчик избранного в шапке (опционально)
    with allure.step("Проверить счетчик избранного в шапке"):
        favorite_count = header.get_favorite_count()
        allure.attach(f"Значение счетчика избранного: {favorite_count}", name="Информация")

    # Шаг 4: Переходим в избранное через шапку
    with allure.step("Перейти в раздел Избранное через шапку сайта"):
        header.go_to_favorite()

        # Проверяем, что мы действительно на странице избранного
        current_url = page.url
        allure.attach(f"URL после перехода в избранное: {current_url}", name="Информация")
        assert "favorite" in current_url, f"Не удалось перейти в избранное. Текущий URL: {current_url}"

    # Шаг 5: Проверяем, что в избранном есть товары
    with allure.step("Проверить наличие товаров в избранном"):
        # Даем дополнительное время на загрузку контента
        page.wait_for_timeout(2000)

        has_items = favorite_page.is_favorite_has_items()
        allure.attach(f"Есть ли товары в избранном: {has_items}", name="Информация")

        if not has_items:
            # Делаем скриншот для отладки
            from utils.allure_attach import attach_screenshot
            attach_screenshot(page, "Пустое избранное")

            # Проверяем HTML страницы
            page_html = page.content()
            allure.attach(page_html[:5000], name="HTML страницы (первые 5000 символов)",
                          attachment_type=allure.attachment_type.HTML)

        assert has_items, "Список избранного пуст"

        items_count = favorite_page.get_favorite_items_count()
        allure.attach(f"Количество товаров в избранном: {items_count}", name="Информация")

    # Шаг 6: Проверяем, что добавленный товар отображается в избранном (по href)
    with allure.step("Проверить, что добавленный товар отображается в избранном"):
        actual_href = favorite_page.get_first_product_href()
        actual_name = favorite_page.get_first_product_name()  # для информации

        allure.attach(
            f"Товар в избранном:\n"
            f"Название: {actual_name}\n"
            f"href: {actual_href}\n"
            f"ID: {favorite_page.get_product_id_from_href(actual_href)}",
            name="Информация о товаре в избранном"
        )

        # Проверяем, что href не пустые
        assert expected_href, "Не удалось получить href товара из каталога"
        assert actual_href, "Не удалось получить href товара из избранного"

        # Нормализуем href (убираем домен, если есть)
        expected_href_norm = expected_href.split('/')[-1] if '/' in expected_href else expected_href
        actual_href_norm = actual_href.split('/')[-1] if '/' in actual_href else actual_href

        allure.attach(
            f"Сравнение href (нормализованные):\n"
            f"Ожидаемый: {expected_href_norm}\n"
            f"Фактический: {actual_href_norm}",
            name="Сравнение"
        )

        # Проверяем, что href совпадают (или один содержится в другом)
        assert (expected_href_norm in actual_href_norm) or (actual_href_norm in expected_href_norm), \
            f"href не совпадают: ожидалось '{expected_href}', получено '{actual_href}'"

        # Дополнительно проверяем ID товара
        expected_id = favorite_page.get_product_id_from_href(expected_href)
        actual_id = favorite_page.get_product_id_from_href(actual_href)

        if expected_id and actual_id:
            assert expected_id == actual_id, f"ID товаров не совпадают: {expected_id} vs {actual_id}"
            allure.attach(f"ID товаров совпадают: {expected_id}", name="Успех")

        allure.attach("Товар успешно найден в избранном (проверка по href)", name="Успех")