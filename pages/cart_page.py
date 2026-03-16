import allure
import re
from pages.base_page import BasePage
from config.config import Config


class CartPage(BasePage):
    # Локаторы для корзины
    CART_CONTAINER = "#cartWidget"
    CART_ITEM = ".list-group-item"
    CART_ITEM_NAME = f"{CART_ITEM} a.font-weight-bold"
    CART_ITEM_PRICE = f"{CART_ITEM} .col-md-2.py-2"  # Это дает несколько элементов
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
        """Получить цену первого товара в корзине"""
        if self.is_cart_not_empty():
            with allure.step("Получить цену первого товара в корзине"):
                # Находим первый товар в корзине
                first_item = self.page.locator(self.CART_ITEM).first

                price_elements = first_item.locator(".col-md-2.py-2").all()

                allure.attach(f"Найдено элементов с ценой: {len(price_elements)}", name="Отладка")

                for i, elem in enumerate(price_elements):
                    if elem.is_visible():
                        text = elem.text_content() or ""
                        allure.attach(f"Элемент {i}: '{text}'", name="Отладка")

                        # Проверяем, содержит ли элемент символ ₽
                        if '₽' in text:
                            # Очищаем цену от символов валюты и пробелов
                            price_clean = re.sub(r'[^\d]', '', text)
                            allure.attach(f"Найдена цена: {price_clean}", name="Информация")
                            return price_clean

                item_text = first_item.text_content() or ""
                allure.attach(f"Весь текст товара: {item_text}", name="Отладка")

                match = re.search(r'(\d[\d\s]*)₽', item_text)
                if match:
                    price_clean = re.sub(r'[^\d]', '', match.group(1))
                    allure.attach(f"Цена найдена через regex: {price_clean}", name="Информация")
                    return price_clean

                numbers = re.findall(r'(\d[\d\s]*)', item_text)
                if len(numbers) >= 2:
                    price_clean = re.sub(r'[^\d]', '', numbers[1])
                    allure.attach(f"Цена предположительно: {price_clean}", name="Информация")
                    return price_clean

                allure.attach("Цена не найдена", name="Ошибка")
        return "0"

    def get_total_price(self) -> str:
        """Получить общую стоимость корзины"""
        with allure.step("Получить общую стоимость корзины"):
            total_element = self.page.locator(self.TOTAL_PRICE).first
            if total_element.is_visible():
                total_text = total_element.text_content() or ""
                match = re.search(r'([\d\s]+)₽', total_text)
                if match:
                    total_clean = re.sub(r'[^\d]', '', match.group(1))
                    allure.attach(f"Общая стоимость: {total_clean}", name="Информация")
                    return total_clean
            return "0"
