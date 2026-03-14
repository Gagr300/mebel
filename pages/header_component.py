# pages/header_component.py
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

            # Ждем только загрузки DOM, а не полной остановки сети
            self.page.wait_for_load_state("domcontentloaded")
            # Даем небольшую паузу для рендеринга
            self.page.wait_for_timeout(1000)

    def go_to_favorite(self):
        with allure.step("Перейти в избранное через шапку сайта"):
            # Пробуем найти ссылку на избранное в разных местах
            favorite_found = False

            # Для десктопной версии
            desktop_link = self.page.locator(self.FAVORITE_LINK).first
            if desktop_link.is_visible():
                desktop_link.click()
                favorite_found = True
                allure.attach("Клик по ссылке избранного (десктоп)", name="Успешно")

            # Для мобильной версии
            if not favorite_found:
                mobile_link = self.page.locator(self.FAVORITE_LINK_MOBILE).first
                if mobile_link.is_visible():
                    mobile_link.click()
                    favorite_found = True
                    allure.attach("Клик по ссылке избранного (мобильная)", name="Успешно")

            # Если не нашли через клик, переходим напрямую по URL
            if not favorite_found:
                self.page.goto(Config.FAVORITE_URL)
                allure.attach("Переход по прямому URL избранного", name="Информация")

            # Ждем только загрузки DOM, не networkidle
            self.page.wait_for_load_state("domcontentloaded")
            self.page.wait_for_timeout(2000)  # Даем время на рендеринг JS

            # Проверяем, что мы действительно на странице избранного
            current_url = self.page.url
            assert "favorite" in current_url, f"Не удалось перейти в избранное. Текущий URL: {current_url}"

            # Делаем скриншот для отчета
            from utils.allure_attach import attach_screenshot
            attach_screenshot(self.page, "Страница избранного после перехода")

    def get_favorite_count(self) -> int:
        """Получить количество товаров в избранном из счетчика в шапке"""
        with allure.step("Получить счетчик избранного"):
            # Пробуем найти счетчик в разных местах
            selectors = [
                ".header-laptop__favorite .favorite-informer b small",  # Десктоп
                ".mobile-header__favorite .favorite-informer b small",  # Мобильный
                ".favorite-informer b small",  # Общий
                ".header-laptop__favorite b small",  # Альтернативный
                ".mobile-header__favorite b small",  # Альтернативный
                ".header-laptop__favorite .favorite-informer b",  # Без small
                ".mobile-header__favorite .favorite-informer b"  # Без small
            ]

            for selector in selectors:
                counter_element = self.page.locator(selector).first
                if counter_element.is_visible():
                    count_text = counter_element.text_content()
                    try:
                        # Очищаем текст от возможных HTML-тегов и пробелов
                        if count_text:
                            # Убираем все, кроме цифр
                            import re
                            digits = re.sub(r'[^\d]', '', count_text)
                            if digits:
                                count = int(digits)
                                allure.attach(f"Счетчик избранного ({selector}): {count}", name="Информация")
                                return count
                    except (ValueError, AttributeError):
                        continue

            # Если не нашли счетчик, возможно, он пустой (скрыт)
            allure.attach("Счетчик избранного не найден или пуст (возвращаем 0)", name="Информация")
            return 0