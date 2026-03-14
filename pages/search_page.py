# pages/cart_page.py
import allure
import re
from pages.base_page import BasePage
from config.config import Config


class CartPage(BasePage):
    # Локаторы для корзины
    CART_CONTAINER = "#cartWidget"
    CART_ITEM = ".list-group-item"
    CART_ITEM_NAME = f"{CART_ITEM} a.font-weight-bold"
    CART_ITEM_PRICE = f"{CART_ITEM} .col-md-2.py-2"  # Цена товара
    EMPTY_CART_MESSAGE = ".lead:has-text('Корзина пуста')"
    TOTAL_PRICE = "h2:has-text('Итого:')"

    def open_cart(self):
        with allure.step("Открыть корзину"):
            self.open(Config.CART_URL)
            self.page.wait_for_load_state("networkidle")

    def is_cart_not_empty(self) -> bool:
        """Проверить, не пуста ли корзина"""
        try:
            self.page.wait_for_selector(self.CART_ITEM, timeout=5000)
            return True
        except:
            return False

    def get_first_item_name(self) -> str:
        """Получить название первого товара в корзине"""
        if self.is_cart_not_empty():
            name_element = self.page.locator(self.CART_ITEM_NAME).first
            if name_element.is_visible():
                name = name_element.text_content()
                allure.attach(f"Первый товар в корзине: {name}", name="Информация")
                return name or ""
        return ""

    def get_first_item_price(self) -> str:
        """
        Получить цену первого товара в корзине

        Из структуры HTML:
        <div class="col-md-2 py-2">12,405 ₽</div>

        Returns:
            str: Цена товара в виде числа (12405)
        """
        if not self.is_cart_not_empty():
            return "0"

        with allure.step("Получить цену первого товара в корзине"):
            # Находим первый товар в корзине
            first_item = self.page.locator(self.CART_ITEM).first

            # Ищем элемент с ценой внутри первого товара
            price_element = first_item.locator(self.CART_ITEM_PRICE).first

            if price_element.is_visible():
                price_text = price_element.text_content() or ""
                allure.attach(f"Текст цены: '{price_text}'", name="Информация")

                # Очищаем цену от символов (оставляем только цифры)
                # Убираем пробелы, запятые, символ валюты
                price_clean = re.sub(r'[^\d]', '', price_text)

                allure.attach(f"Очищенная цена: {price_clean}", name="Результат")
                return price_clean

            allure.attach("Элемент с ценой не найден", name="Ошибка")
            return "0"

    def get_total_price(self) -> str:
        """Получить общую стоимость корзины"""
        with allure.step("Получить общую стоимость корзины"):
            total_element = self.page.locator(self.TOTAL_PRICE).first
            if total_element.is_visible():
                total_text = total_element.text_content() or ""
                # Извлекаем число из текста "Итого: 12 015 ₽"
                match = re.search(r'([\d\s,]+)₽', total_text)
                if match:
                    total_clean = re.sub(r'[^\d]', '', match.group(1))
                    allure.attach(f"Общая стоимость: {total_clean}", name="Информация")
                    return total_clean
            return "0"