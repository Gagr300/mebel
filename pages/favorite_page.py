import allure
from pages.base_page import BasePage
from config.config import Config

class FavoritePage(BasePage):
    # Избранное может быть пустым или с товарами
    FAVORITE_CONTAINER = ".favorite-page, .favorite-list"  # Нужно уточнить
    PRODUCT_CARD = ".product-card"
    EMPTY_FAVORITE_MESSAGE = ".empty-message, .favorite-empty"  # Сообщение о пустом избранном
    FIRST_PRODUCT_NAME = f"{PRODUCT_CARD}:first-child .product-card__name a"

    def open_favorite(self):
        with allure.step("Открыть раздел Избранное"):
            self.open(Config.FAVORITE_URL)
            self.page.wait_for_load_state("networkidle")

    def is_favorite_has_items(self) -> bool:
        """Проверить, есть ли товары в избранном"""
        # Ждем либо карточки товара, либо сообщения о пустом избранном
        try:
            self.page.wait_for_selector(self.PRODUCT_CARD, timeout=5000)
            return True
        except:
            return False

    def get_first_product_name(self) -> str:
        if self.is_favorite_has_items():
            name = self.get_text(self.FIRST_PRODUCT_NAME)
            allure.attach(f"Первый товар в избранном: {name}", name="Информация")
            return name
        return ""

    def get_first_product_price(self) -> str:
        """Получить цену первого товара в избранном"""
        with allure.step("Получить цену первого товара в избранном"):
            first_card = self.page.locator(self.PRODUCT_CARD).first

            # Пробуем найти цену
            price_now = first_card.locator(".product-card__now_price span").first
            if price_now.is_visible():
                price = price_now.text_content()
                allure.attach(f"Цена товара: {price}", name="Информация")
                return price or ""

            price_old = first_card.locator(".product-card__old_price span").first
            if price_old.is_visible():
                price = price_old.text_content()
                allure.attach(f"Цена товара (старая): {price}", name="Информация")
                return price or ""

            return ""

    def get_favorite_items_count(self) -> int:
        """Получить количество товаров в избранном"""
        with allure.step("Получить количество товаров в избранном"):
            # Сначала пробуем найти счетчик
            count_element = self.page.locator(".w-100.pl-3.pr-3").first
            if count_element.is_visible():
                count_text = count_element.text_content()
                import re
                match = re.search(r'из\s+(\d+)', count_text)
                if match:
                    count = int(match.group(1))
                    allure.attach(f"Всего товаров в избранном: {count}", name="Информация")
                    return count

            # Если счетчика нет, считаем карточки
            cards = self.page.locator(self.PRODUCT_CARD).all()
            count = len(cards)
            allure.attach(f"Товаров на странице: {count}", name="Информация")
            return count