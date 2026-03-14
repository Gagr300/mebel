# pages/favorite_page.py
import allure
from pages.base_page import BasePage
from config.config import Config


class FavoritePage(BasePage):
    # Избранное может быть пустым или с товарами
    PRODUCT_CARD = ".product-card"
    EMPTY_FAVORITE_MESSAGE = ".empty-message, .favorite-empty, .lead:has-text('пуст')"  # Сообщение о пустом избранном
    FIRST_PRODUCT_NAME = f"{PRODUCT_CARD}:first-child .product-card__name a"
    FAVORITE_CONTAINER = ".page-favorite"

    def open_favorite(self):
        """Открыть раздел Избранное с ожиданием только загрузки DOM"""
        with allure.step("Открыть раздел Избранное"):
            # Используем безопасный переход без ожидания networkidle
            self.safe_goto(Config.FAVORITE_URL, wait_until="domcontentloaded")

            # Проверяем, что мы на странице избранного
            assert "favorite" in self.page.url, f"Не удалось открыть избранное. Текущий URL: {self.page.url}"

            # Делаем скриншот для отчета
            from utils.allure_attach import attach_screenshot
            attach_screenshot(self.page, "Страница избранного")

    def is_favorite_has_items(self) -> bool:
        """Проверить, есть ли товары в избранном"""
        with allure.step("Проверить наличие товаров в избранном"):
            # Ждем либо карточки товара, либо сообщения о пустом избранном
            try:
                # Сначала проверим, нет ли сообщения о пустом избранном
                empty_message = self.page.locator(self.EMPTY_FAVORITE_MESSAGE).first
                if empty_message.is_visible():
                    allure.attach("Избранное пусто (найдено сообщение о пустоте)", name="Информация")
                    return False

                # Ждем появления карточек товаров
                self.page.wait_for_selector(self.PRODUCT_CARD, timeout=10000)
                card_count = self.page.locator(self.PRODUCT_CARD).count()
                allure.attach(f"Найдено карточек товаров: {card_count}", name="Информация")
                return card_count > 0
            except Exception as e:
                allure.attach(f"Товары в избранном не найдены: {str(e)}", name="Информация")
                return False

    def get_first_product_name(self) -> str:
        """Получить название первого товара в избранном"""
        with allure.step("Получить название первого товара в избранном"):
            if not self.is_favorite_has_items():
                allure.attach("В избранном нет товаров", name="Ошибка")
                return ""

            # Пробуем разные локаторы для названия
            name_selectors = [
                self.FIRST_PRODUCT_NAME,
                f"{self.PRODUCT_CARD}:first-child a.font-weight-bold",
                f"{self.PRODUCT_CARD}:first-child .product-card__name a",
                f"{self.PRODUCT_CARD}:first-child a[href*='/id']"
            ]

            for selector in name_selectors:
                name_element = self.page.locator(selector).first
                if name_element.is_visible():
                    name = name_element.text_content()
                    if name and name.strip():
                        allure.attach(f"Первый товар в избранном: {name}", name="Информация")
                        return name.strip()

            # Если не нашли по селекторам, попробуем извлечь из HTML
            first_card = self.page.locator(self.PRODUCT_CARD).first
            card_html = first_card.inner_html()

            # Ищем текст между тегами <a>
            import re
            match = re.search(r'<a[^>]*>(.*?)</a>', card_html)
            if match:
                name = match.group(1).strip()
                allure.attach(f"Название извлечено из HTML: {name}", name="Информация")
                return name

            allure.attach("Не удалось найти название товара", name="Ошибка")
            return ""

    def get_first_product_price(self) -> str:
        """Получить цену первого товара в избранном"""
        with allure.step("Получить цену первого товара в избранном"):
            if not self.is_favorite_has_items():
                return ""

            first_card = self.page.locator(self.PRODUCT_CARD).first

            # Пробуем найти цену
            price_selectors = [
                ".product-card__now_price span",
                ".product-card__old_price span",
                ".product-card__price span"
            ]

            for selector in price_selectors:
                price_element = first_card.locator(selector).first
                if price_element.is_visible():
                    price = price_element.text_content()
                    if price:
                        allure.attach(f"Цена товара: {price}", name="Информация")
                        return price.strip()

            return ""

    def get_favorite_items_count(self) -> int:
        """Получить количество товаров в избранном"""
        with allure.step("Получить количество товаров в избранном"):
            # Сначала пробуем найти счетчик
            count_selectors = [
                ".w-100.pl-3.pr-3",
                ".page-favorite .w-100",
                ".col-sm-12 .w-100"
            ]

            for selector in count_selectors:
                count_element = self.page.locator(selector).first
                if count_element.is_visible():
                    count_text = count_element.text_content()
                    import re
                    match = re.search(r'из\s+(\d+)', count_text)
                    if match:
                        count = int(match.group(1))
                        allure.attach(f"Всего товаров в избранном (из счетчика): {count}", name="Информация")
                        return count

            # Если счетчика нет, считаем карточки
            cards = self.page.locator(self.PRODUCT_CARD).all()
            count = len(cards)
            allure.attach(f"Товаров на странице: {count}", name="Информация")
            return count

    def get_first_product_href(self) -> str:
        """Получить href (ссылку) первого товара в избранном"""
        with allure.step("Получить href первого товара в избранном"):
            if not self.is_favorite_has_items():
                allure.attach("В избранном нет товаров", name="Ошибка")
                return ""

            first_card = self.page.locator(self.PRODUCT_CARD).first

            # Пробуем найти ссылку в названии товара
            name_link = first_card.locator(".product-card__name a").first
            if name_link.is_visible():
                href = name_link.get_attribute('href')
                allure.attach(f"href первого товара в избранном: {href}", name="Информация")
                return href or ""

            # Если не нашли через название, ищем любую ссылку с href на товар
            all_links = first_card.locator("a").all()
            for link in all_links:
                href = link.get_attribute('href')
                if href and ('/id' in href or '/product' in href or '/divan' in href):
                    allure.attach(f"href первого товара (найдено по паттерну): {href}", name="Информация")
                    return href

            # Последний вариант - берем любую ссылку
            any_link = first_card.locator("a").first
            if any_link.is_visible():
                href = any_link.get_attribute('href')
                allure.attach(f"href первого товара (любая ссылка): {href}", name="Информация")
                return href or ""

            allure.attach("Не удалось найти href первого товара в избранном", name="Ошибка")
            return ""

    def get_product_id_from_href(self, href: str) -> str:
        """Извлечь ID товара из href"""
        if not href:
            return ""

        import re
        # Ищем паттерны вида /id123456 или /product/123456
        match = re.search(r'/id(\d+)', href)
        if match:
            return match.group(1)

        match = re.search(r'/product/([^/]+)', href)
        if match:
            return match.group(1)

        # Если не нашли ID, возвращаем последнюю часть URL
        parts = href.split('/')
        return parts[-1] if parts else ""
