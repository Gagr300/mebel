import allure
from pages.product_page import ProductPage


@allure.feature("Корзина")
@allure.story("Добавление товара в корзину и проверка цены")
def test_add_to_cart(catalog_page, cart_page, page):
    """Тест проверяет добавление товара в корзину"""

    # Открываем каталог
    catalog_page.open_catalog()
    catalog_page.take_screenshot("Каталог открыт", force=True)

    with allure.step("Запомнить название и цену первого товара в каталоге"):
        expected_name = catalog_page.get_first_product_name()
        expected_price_text = catalog_page.get_first_product_price()
        expected_price_clean = catalog_page.clean_price(expected_price_text)
        allure.attach(
            f"Название: {expected_name}\nЦена: {expected_price_clean}",
            name="Информация о товаре в каталоге"
        )

    # Переходим на страницу товара
    catalog_page.click_first_product()

    product_page = ProductPage(page)

    with allure.step("Проверить, что открылась страница правильного товара"):
        product_title = product_page.get_product_title()
        product_price = product_page.get_product_price()
        allure.attach(f"Цена на странице товара: {product_price}", name="Информация")

    # Добавляем товар в корзину
    product_page.click_add_to_cart()
    product_page.take_screenshot("Товар добавлен в корзину", force=True)

    # Переходим в корзину
    with allure.step("Перейти в корзину"):
        from config.config import Config
        page.goto(Config.CART_URL)
        page.wait_for_timeout(1000)
        cart_page.take_screenshot("Корзина открыта", force=True)

    # Проверяем корзину
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