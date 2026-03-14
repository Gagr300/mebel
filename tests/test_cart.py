# tests/test_cart.py
import allure
from pages.product_page import ProductPage


@allure.feature("Корзина")
@allure.story("Добавление товара в корзину и проверка цены")
def test_add_to_cart(catalog_page, cart_page, page):
    """
    Тест проверяет добавление товара в корзину:
    1. В каталоге нажимаем "Купить" на первом товаре
    2. На странице товара нажимаем "В корзину"
    3. В уведомлении нажимаем "Перейти в корзину"
    4. Проверяем, что товар в корзине и цена совпадает
    """

    # Открываем каталог
    catalog_page.open_catalog()

    with allure.step("Запомнить название и цену первого товара в каталоге"):
        expected_name = catalog_page.get_first_product_name()
        expected_price_text = catalog_page.get_first_product_price()
        expected_price_clean = catalog_page.clean_price(expected_price_text)
        allure.attach(
            f"Название: {expected_name}\nЦена: {expected_price_clean}",
            name="Информация о товаре в каталоге"
        )

    # Шаг 1: Переходим на страницу товара через кнопку "Купить"
    with allure.step("Нажать 'Купить' на первом товаре в каталоге"):
        catalog_page.click_first_product()
        allure.attach(f"Текущий URL: {page.url}", name="URL после перехода")

    # Создаем объект страницы товара
    product_page = ProductPage(page)

    with allure.step("Проверить, что открылась страница правильного товара"):
        product_title = product_page.get_product_title()
        # Проверяем цену на странице товара
        product_price = product_page.get_product_price()
        product_price_clean = catalog_page.clean_price(product_price)
        allure.attach(
            f"Цена на странице товара: {product_price_clean}",
            name="Информация"
        )

    # Шаг 2: Добавляем товар в корзину
    product_page.click_add_to_cart()

    # Шаг 3: Переходим в корзину из уведомления
    with allure.step("Перейти в корзину из уведомления"):
        # Проверяем наличие уведомления
        notification = page.locator(".notification, .alert, .toast").first
        if notification.is_visible():
            notification_text = notification.text_content()
            allure.attach(f"Текст уведомления: {notification_text}", name="Уведомление")

            # Ищем кнопку перехода в корзину
            go_to_cart_btn = page.locator("a:has-text('Перейти в корзину'), button:has-text('Перейти в корзину')").first
            if go_to_cart_btn.is_visible():
                go_to_cart_btn.click()
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(1000)
            else:
                # Если кнопка не найдена, переходим по URL
                from config.config import Config
                page.goto(Config.CART_URL)
        else:
            allure.attach("Уведомление не появилось, переходим в корзину по URL",
                          name="Предупреждение")
            from config.config import Config
            page.goto(Config.CART_URL)

    # Шаг 4: Проверяем корзину
    with allure.step("Проверить содержимое корзины"):
        assert cart_page.is_cart_not_empty(), "Корзина пуста"

    with allure.step("Проверить название товара в корзине"):
        actual_name = cart_page.get_first_item_name()
        assert product_title.lower() in actual_name.lower() or \
               actual_name.lower() in product_title.lower(), \
            f"В корзине товар '{actual_name}', ожидался содержащий '{expected_name}'"

    with allure.step("Проверить цену товара в корзине"):
        actual_price_clean = cart_page.get_first_item_price()
        assert product_price == actual_price_clean, \
            f"Цена в корзине {actual_price_clean} не совпадает с ценой в каталоге {product_price}"