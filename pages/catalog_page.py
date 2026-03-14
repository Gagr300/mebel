import allure
import re
from typing import List, Tuple, Optional
from pages.base_page import BasePage
from config.config import Config


class CatalogPage(BasePage):
    # Локаторы
    TITLE = "h1"

    # Карточка товара
    PRODUCT_CARD = ".product-card"
    PRODUCT_LINK = f"{PRODUCT_CARD} .product-card__name a"
    PRODUCT_PRICE_NOW = f"{PRODUCT_CARD} .product-card__now_price span"
    PRODUCT_PRICE_OLD = f"{PRODUCT_CARD} .product-card__old_price span"
    PRODUCT_FAVORITE_ICON = f"{PRODUCT_CARD} .product-card__favorites .favorite-icon"
    PRODUCT_ADD_TO_CART_BTN = f"{PRODUCT_CARD} .btn-primary.btn-block"

    # Дополнительные локаторы для характеристик
    PRODUCT_DIMENSIONS = f"{PRODUCT_CARD} .text-center small"

    # Локаторы для фильтрации
    FILTER_APPLY_BTN = "a#filterLinkContainer, .filter__link"
    PRODUCTS_COUNT_TEXT = ".w-100.pl-3.pr-3"

    def open_catalog(self):
        with allure.step("Открыть раздел Диваны"):
            self.open(Config.CATALOG_URL)
            self.page.wait_for_timeout(500)
            self.wait_for_selector(self.PRODUCT_CARD)
            # Только один скриншот при открытии каталога
            self.take_screenshot("Каталог открыт", force=True)
            self.page.wait_for_timeout(500)

    def get_page_title(self) -> str:
        """Получить заголовок страницы"""
        title_element = self.page.locator("h1").first
        if title_element.is_visible():
            title = title_element.text_content()
            allure.attach(f"Заголовок страницы: {title}", name="Информация")
            return title or ""
        return ""

    def apply_price_filter(self, price_from: str, price_to: str):
        """Применить фильтр по цене через URL"""
        with allure.step(f"Применить фильтр по цене: от {price_from} до {price_to}"):
            # Скриншот ДО фильтрации
            self.take_screenshot("До применения фильтра", force=True)

            # Получаем базовый URL без параметров
            current_url = self.page.url
            if '?' in current_url:
                base_url = current_url.split('?')[0]
            else:
                base_url = current_url

            # Формируем URL с фильтром
            filter_url = f"{base_url}?price={price_from}-{price_to}"

            allure.attach(f"URL для фильтрации: {filter_url}", name="Информация")

            try:
                self.page.goto(filter_url, wait_until="domcontentloaded", timeout=30000)
                self.page.wait_for_timeout(2000)
                self.page.wait_for_selector(self.PRODUCT_CARD, timeout=10000)

                # Скриншот ПОСЛЕ фильтрации
                self.take_screenshot("После применения фильтра", force=True)

            except Exception as e:
                self.take_screenshot("Ошибка при применении фильтра", force=True)
                allure.attach(f"Ошибка при применении фильтра: {str(e)}", name="Ошибка")
                raise

            # Проверяем, что фильтр применился
            assert f"price={price_from}-{price_to}" in self.page.url, \
                f"Фильтр не применился. Текущий URL: {self.page.url}"

    def find_product_by_name(self, product_name: str) -> bool:
        """Найти товар по названию (частичному совпадению)"""
        with allure.step(f"Поиск товара с названием '{product_name}'"):
            self.page.wait_for_selector(self.PRODUCT_CARD)

            # Получаем все названия товаров
            product_links = self.page.locator(self.PRODUCT_LINK).all()

            found_products = []
            for i, link in enumerate(product_links, 1):
                if link.is_visible():
                    name = link.text_content()
                    if name:
                        found_products.append(f"{i}. {name}")
                        if product_name.lower() in name.lower():
                            # Скриншот только найденного товара
                            link.scroll_into_view_if_needed()
                            self.page.wait_for_timeout(500)
                            self.take_screenshot(f"Найден товар: {name}", force=True)
                            allure.attach(f"Найден товар #{i}: {name}", name="Информация")
                            return True

            # Если товар не найден, прикладываем список всех товаров для отладки
            allure.attach(
                f"Поиск '{product_name}'\n\nВсе товары на странице:\n" + "\n".join(found_products),
                name="Детальная информация"
            )
            return False

    def get_product_price_by_name(self, product_name: str) -> str:
        """Получить цену товара по названию"""
        with allure.step(f"Получить цену товара '{product_name}'"):
            product_cards = self.page.locator(self.PRODUCT_CARD).all()

            for card_index, card in enumerate(product_cards, 1):
                name_element = card.locator(self.PRODUCT_LINK).first
                if not name_element.is_visible():
                    continue

                name = name_element.text_content()
                if not name:
                    continue

                if product_name.lower() in name.lower():
                    allure.attach(f"Найдена карточка #{card_index}: {name}", name="Информация")
                    price = self._extract_price_from_card(card)

                    if price:
                        allure.attach(f"Цена товара '{name}': {price}", name="Информация")
                        return price

            raise AssertionError(f"Не удалось найти цену для товара '{product_name}'")

    def _extract_price_from_card(self, card) -> Optional[str]:
        """Извлечь цену из карточки товара различными способами"""
        # Способ 1: текущая цена
        price_now = card.locator(self.PRODUCT_PRICE_NOW).first
        if price_now.is_visible():
            price_text = price_now.text_content()
            if price_text:
                return price_text.strip()

        # Способ 2: старая цена (если нет текущей)
        price_old = card.locator(self.PRODUCT_PRICE_OLD).first
        if price_old.is_visible():
            price_text = price_old.text_content()
            if price_text:
                return price_text.strip()

        # Способ 3: ищем любые числа с символом ₽
        all_text = card.text_content()
        if all_text:
            match = re.search(r'(\d[\d\s]*)\s*₽', all_text)
            if match:
                return match.group(1).strip()

        return None

    def clean_price(self, price_text: str) -> int:
        """Очистить цену от символов и преобразовать в число"""
        if not price_text:
            return 0

        cleaned = re.sub(r'[^\d]', '', price_text)
        try:
            return int(cleaned)
        except ValueError:
            return 0

    def get_all_prices_on_page(self) -> List[str]:
        """Получить все цены товаров на текущей странице"""
        prices = []
        product_cards = self.page.locator(self.PRODUCT_CARD).all()

        for card in product_cards:
            price = self._extract_price_from_card(card)
            if price:
                prices.append(price)

        return prices

    def get_total_products_count(self) -> int:
        """Получить общее количество товаров в выдаче"""
        try:
            count_element = self.page.locator(self.PRODUCTS_COUNT_TEXT).first
            if count_element.is_visible():
                count_text = count_element.text_content()
                if count_text:
                    # Ищем паттерн "из X"
                    match = re.search(r'из\s+(\d+)', count_text)
                    if match:
                        return int(match.group(1))
        except:
            pass

        # Если не нашли счетчик, считаем товары на странице
        return len(self.page.locator(self.PRODUCT_CARD).all())

    def verify_prices_in_range(self, price_from: int, price_to: int):
        """Проверить, что все цены на странице в заданном диапазоне"""
        with allure.step(f"Проверить, что цены в диапазоне {price_from}-{price_to}"):
            prices_in_range = []
            prices_out_of_range = []

            # Получаем все цены на странице
            price_texts = self.get_all_prices_on_page()

            for i, price_text in enumerate(price_texts, 1):
                price_num = self.clean_price(price_text)
                if price_num > 0:
                    if price_from <= price_num <= price_to:
                        prices_in_range.append((i, price_text, price_num))
                    else:
                        prices_out_of_range.append((i, price_text, price_num))

            if prices_out_of_range:
                out_range_info = "\n".join([f"  Товар #{i}: {text} ({num} руб.)"
                                            for i, text, num in prices_out_of_range])
                allure.attach(f"Товары вне диапазона:\n{out_range_info}",
                              name="⚠Цены вне диапазона")
                # Скриншот только если есть проблемы
                self.take_screenshot(f"Обнаружены цены вне диапазона", force=True)

            assert len(prices_out_of_range) == 0, \
                f"Найдено {len(prices_out_of_range)} товаров с ценой вне диапазона {price_from}-{price_to}"

    def get_first_product_name(self) -> str:
        """Получить название первого товара в каталоге"""
        self.wait_for_selector(self.PRODUCT_CARD)
        first_product_link = self.page.locator(self.PRODUCT_LINK).first

        if first_product_link.is_visible():
            name = first_product_link.text_content()
            return name or ""
        return ""

    def get_first_product_price(self) -> str:
        """Получить цену первого товара в каталоге"""
        self.wait_for_selector(self.PRODUCT_CARD)
        first_card = self.page.locator(self.PRODUCT_CARD).first
        price = self._extract_price_from_card(first_card)
        return price or "0"

    def get_first_product_href(self) -> str:
        """Получить href (ссылку) первого товара в каталоге"""
        self.wait_for_selector(self.PRODUCT_CARD)

        product_link = self.page.locator(self.PRODUCT_LINK).first
        if product_link.is_visible():
            href = product_link.get_attribute('href')
            return href or ""

        return ""

    def click_first_product_favorite(self):
        """Нажать на иконку избранного у первого товара"""
        with allure.step("Добавить первый товар в избранное"):
            self.page.wait_for_selector(self.PRODUCT_CARD, state="visible", timeout=10000)

            # Скриншот до клика
            self.take_screenshot("До добавления в избранное", force=True)

            first_card = self.page.locator(self.PRODUCT_CARD).first
            first_card.scroll_into_view_if_needed()
            self.page.wait_for_timeout(500)

            favorite_icon = first_card.locator(".product-card__favorites .favorite-icon").first

            if favorite_icon.is_visible():
                favorite_icon.click()
                self.page.wait_for_timeout(1000)

                # Скриншот после клика
                self.take_screenshot("После добавления в избранное", force=True)
            else:
                raise AssertionError("Иконка избранного не найдена у первого товара")

    def click_first_product_add_to_cart(self):
        """Нажать кнопку 'Купить' у первого товара"""
        with allure.step("Добавить первый товар в корзину"):
            self.wait_for_selector(self.PRODUCT_CARD)
            first_card = self.page.locator(self.PRODUCT_CARD).first
            buy_button = first_card.locator(self.PRODUCT_ADD_TO_CART_BTN).first

            if buy_button.is_visible():
                product_name = self.get_first_product_name()
                allure.attach(f"Добавляем товар: {product_name}", name="Информация")

                buy_button.scroll_into_view_if_needed()
                self.page.wait_for_timeout(500)
                buy_button.click()
                self.page.wait_for_timeout(2000)
            else:
                raise AssertionError("Кнопка 'Купить' не найдена у первого товара")

    def click_first_product(self):
        """Кликнуть на первый товар в каталоге для перехода на его страницу"""
        with allure.step("Перейти на страницу первого товара"):
            self.wait_for_selector(self.PRODUCT_CARD)

            product_name = self.get_first_product_name()
            allure.attach(f"Переход на страницу товара: {product_name}", name="Информация")

            first_card = self.page.locator(self.PRODUCT_CARD).first
            buy_link = first_card.locator("a.btn-primary:has-text('Купить')").first

            if buy_link.is_visible():
                href = buy_link.get_attribute('href')
                allure.attach(f"URL товара: {href}", name="Информация")

                with self.page.expect_navigation(wait_until="domcontentloaded", timeout=30000):
                    buy_link.click()

                self.page.wait_for_timeout(2000)
            else:
                product_link = first_card.locator(self.PRODUCT_LINK).first
                if product_link.is_visible():
                    with self.page.expect_navigation(wait_until="domcontentloaded", timeout=30000):
                        product_link.click()
                    self.page.wait_for_timeout(2000)
                else:
                    raise AssertionError("Не удалось найти способ перехода на страницу товара")

    def click_product_by_name(self, product_name: str):
        """Кликнуть на товар по названию и перейти на его страницу"""
        with allure.step(f"Кликнуть на товар '{product_name}'"):
            self.page.wait_for_selector(self.PRODUCT_CARD, timeout=10000)

            product_links = self.page.locator(self.PRODUCT_LINK).all()

            found = False
            for link in product_links:
                if link.is_visible():
                    name = link.text_content()
                    if name and product_name.lower() in name.lower():
                        link.scroll_into_view_if_needed()
                        self.page.wait_for_timeout(500)

                        with self.page.expect_navigation(wait_until="domcontentloaded", timeout=30000):
                            link.click()

                        self.page.wait_for_timeout(2000)
                        found = True
                        break

            if not found:
                raise AssertionError(f"Товар с названием '{product_name}' не найден")

    def get_product_href_by_name(self, product_name: str) -> str:
        """Получить href (ссылку) товара по его названию"""
        with allure.step(f"Получить href товара по названию: '{product_name}'"):
            self.page.wait_for_selector(self.PRODUCT_CARD, timeout=10000)

            product_cards = self.page.locator(self.PRODUCT_CARD).all()

            for card in product_cards:
                name_link = card.locator(self.PRODUCT_LINK).first
                if not name_link.is_visible():
                    continue

                name_text = name_link.text_content()
                if not name_text:
                    continue

                if product_name.lower() in name_text.lower():
                    href = name_link.get_attribute('href')
                    return href or ""

            return ""