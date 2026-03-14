import allure
from pages.base_page import BasePage
from config.config import Config


class HeaderComponent(BasePage):
    # Более точные локаторы на основе HTML
    CART_LINK = ".header-laptop__link_cart a[href='/cart']"
    FAVORITE_LINK = ".header-laptop__link_favorite a[href='/favorite']"
    # Для мобильной версии
    CART_LINK_MOBILE = ".mobile-header__cart a[href='/cart']"
    FAVORITE_LINK_MOBILE = ".mobile-header__favorite a[href='/favorite']"

    def go_to_cart(self):
        with allure.step("Перейти в корзину через шапку сайта"):
            if self.is_visible(self.CART_LINK):
                self.click(self.CART_LINK, "Иконка корзины")
            elif self.is_visible(self.CART_LINK_MOBILE):
                self.click(self.CART_LINK_MOBILE, "Иконка корзины (моб.)")
            else:
                self.page.goto(Config.CART_URL)
            self.page.wait_for_load_state("networkidle")

    def go_to_favorite(self):
        with allure.step("Перейти в избранное через шапку сайта"):
            if self.is_visible(self.FAVORITE_LINK):
                self.click(self.FAVORITE_LINK, "Иконка избранного")
            elif self.is_visible(self.FAVORITE_LINK_MOBILE):
                self.click(self.FAVORITE_LINK_MOBILE, "Иконка избранного (моб.)")
            else:
                self.page.goto(Config.FAVORITE_URL)
            self.page.wait_for_load_state("networkidle")

    def get_favorite_count(self) -> int:
        """Получить количество товаров в избранном из счетчика в шапке"""
        with allure.step("Получить счетчик избранного"):
            # Пробуем найти счетчик в разных местах
            favorite_counter = None

            # Для десктопной версии
            desktop_counter = self.page.locator(".header-laptop__favorite .favorite-informer b small").first
            if desktop_counter.is_visible():
                favorite_counter = desktop_counter

            # Для мобильной версии
            if not favorite_counter:
                mobile_counter = self.page.locator(".mobile-header__favorite .favorite-informer b small").first
                if mobile_counter.is_visible():
                    favorite_counter = mobile_counter

            if favorite_counter and favorite_counter.is_visible():
                count_text = favorite_counter.text_content()
                try:
                    count = int(count_text.strip()) if count_text else 0
                    allure.attach(f"Товаров в избранном: {count}", name="Информация")
                    return count
                except ValueError:
                    pass

            allure.attach("Счетчик избранного не найден или пуст", name="Информация")
            return 0
