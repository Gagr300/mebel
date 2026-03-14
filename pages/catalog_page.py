# pages/catalog_page.py
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
        """Применить фильтр по цене через URL (без ожидания networkidle)"""
        with allure.step(f"Применить фильтр по цене: от {price_from} до {price_to}"):
            # Получаем базовый URL без параметров
            current_url = self.page.url
            if '?' in current_url:
                base_url = current_url.split('?')[0]
            else:
                base_url = current_url

            # Формируем URL с фильтром
            filter_url = f"{base_url}?price={price_from}-{price_to}"

            allure.attach(f"URL для фильтрации: {filter_url}", name="Информация")

            # Переходим по URL с фильтром, ожидаем только загрузку DOM
            try:
                # Используем goto с wait_until="domcontentloaded" вместо "networkidle"
                self.page.goto(filter_url, wait_until="domcontentloaded", timeout=30000)

                # Даем время на рендеринг контента
                self.page.wait_for_timeout(2000)

                # Ждем появления карточек товаров
                self.page.wait_for_selector(self.PRODUCT_CARD, timeout=10000)

                # Дополнительная пауза для стабилизации
                self.page.wait_for_timeout(1000)

            except Exception as e:
                allure.attach(f"Ошибка при применении фильтра: {str(e)}", name="Ошибка")

                # Пробуем альтернативный способ - через клик по кнопке фильтра
                allure.attach("Пробуем альтернативный способ фильтрации", name="Информация")

                # Возвращаемся на исходную страницу
                self.page.goto(base_url, wait_until="domcontentloaded")
                self.page.wait_for_timeout(2000)

                # Пытаемся найти и нажать кнопку применения фильтра
                filter_button = self.page.locator(self.FILTER_APPLY_BTN).first
                if filter_button.is_visible():
                    # Здесь нужно было бы установить значения фильтра,
                    # но это сложнее, поэтому пока просто логируем
                    allure.attach("Кнопка фильтра найдена, но установка значений не реализована",
                                  name="Предупреждение")

                raise

            # Проверяем, что фильтр применился (в URL есть параметры)
            assert f"price={price_from}-{price_to}" in self.page.url, \
                f"Фильтр не применился. Текущий URL: {self.page.url}"

            # Получаем количество товаров после фильтрации
            try:
                products_count = self.get_total_products_count()
                allure.attach(f"Найдено товаров после фильтрации: {products_count}", name="Информация")
            except:
                pass

    def find_product_by_name(self, product_name: str) -> bool:
        """Найти товар по названию (частичному совпадению)"""
        with allure.step(f"Поиск товара с названием '{product_name}'"):
            # Ждем загрузки всех товаров
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
                            allure.attach(f"Найден товар #{i}: {name}", name="Информация")
                            return True

            # Если товар не найден, прикладываем список всех товаров для отладки
            allure.attach(
                f"Поиск '{product_name}'\n\nВсе товары на странице:\n" + "\n".join(found_products),
                name="Детальная информация"
            )
            return False

    def add_to_cart_by_name(self, product_name: str):
        """Добавить товар в корзину по названию"""
        with allure.step(f"Добавить товар '{product_name}' в корзину"):
            self.page.wait_for_selector(self.PRODUCT_CARD)
            product_cards = self.page.locator(self.PRODUCT_CARD).all()

            for card in product_cards:
                # Находим название товара в карточке
                name_element = card.locator(self.PRODUCT_LINK).first
                if not name_element.is_visible():
                    continue

                name = name_element.text_content()
                if not name:
                    continue

                if product_name.lower() in name.lower():
                    allure.attach(f"Найден товар: {name}", name="Информация")

                    # Ищем кнопку добавления в корзину
                    add_to_cart_btn = card.locator(self.PRODUCT_ADD_TO_CART_BTN).first
                    if add_to_cart_btn.is_visible():
                        # Прокручиваем к кнопке
                        add_to_cart_btn.scroll_into_view_if_needed()
                        self.page.wait_for_timeout(500)
                        add_to_cart_btn.click()
                        allure.attach("Товар добавлен в корзину", name="Успешно")
                        self.page.wait_for_timeout(2000)  # Ждем обновления корзины
                        return
                    else:
                        # Если нет прямой кнопки, переходим на страницу товара
                        allure.attach("Кнопка 'В корзину' не найдена в карточке, переходим на страницу товара",
                                      name="Предупреждение")
                        name_element.click()
                        self.page.wait_for_load_state("networkidle")

                        # На странице товара ищем кнопку добавления в корзину
                        from pages.product_page import ProductPage
                        product_page = ProductPage(self.page)
                        product_page.click_add_to_cart()
                        return

            raise AssertionError(f"Не удалось добавить товар '{product_name}' в корзину")

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
            result = int(cleaned)
            allure.attach(f"Очистка цены: '{price_text}' -> {result}", name="Отладка")
            return result
        except ValueError:
            allure.attach(f"Ошибка преобразования цены: '{price_text}'", name="Ошибка")
            return 0

    def get_all_prices_on_page(self) -> List[str]:
        """Получить все цены товаров на текущей странице"""
        prices = []
        product_cards = self.page.locator(self.PRODUCT_CARD).all()

        for card in product_cards:
            price = self._extract_price_from_card(card)
            if price:
                prices.append(price)

        allure.attach(f"Найдено цен: {len(prices)}", name="Информация")
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

                    # Альтернативный паттерн
                    numbers = re.findall(r'\d+', count_text)
                    if len(numbers) >= 3:
                        return int(numbers[2])
        except Exception as e:
            allure.attach(f"Ошибка получения количества: {str(e)}", name="Ошибка")

        # Если не нашли счетчик, считаем товары на странице
        return len(self.page.locator(self.PRODUCT_CARD).all())

    def get_first_favorite_icon_state(self) -> str:
        """Получить состояние иконки избранного первого товара (возвращает классы)"""
        with allure.step("Получить состояние иконки избранного"):
            self.page.wait_for_selector(self.PRODUCT_CARD, state="visible")
            first_card = self.page.locator(self.PRODUCT_CARD).first
            favorite_icon = first_card.locator(".product-card__favorites .favorite-icon").first

            if favorite_icon.is_visible():
                classes = favorite_icon.get_attribute('class') or ""
                is_active = 'active' in classes
                allure.attach(
                    f"Иконка видима: {favorite_icon.is_visible()}\n"
                    f"Классы: {classes}\n"
                    f"Активна (есть класс 'active'): {is_active}",
                    name="Состояние иконки"
                )
                return classes
            else:
                # Попробуем найти альтернативный элемент
                alt_icon = first_card.locator("a.favorite-icon").first
                if alt_icon.is_visible():
                    classes = alt_icon.get_attribute('class') or ""
                    allure.attach(f"Иконка найдена по альтернативному пути. Классы: {classes}",
                                  name="Информация")
                    return classes

                allure.attach("Иконка избранного не найдена в первой карточке", name="Ошибка")
                return ""

    def verify_prices_in_range(self, price_from: int, price_to: int):
        """Проверить, что все цены на странице в заданном диапазоне"""
        with allure.step(f"Проверить, что цены в диапазоне {price_from}-{price_to}"):
            prices_in_range = []
            prices_out_of_range = []

            # Получаем все цены на странице
            price_texts = self.get_all_prices_on_page()

            allure.attach(f"Найдено цен для проверки: {len(price_texts)}", name="Информация")

            for i, price_text in enumerate(price_texts, 1):
                price_num = self.clean_price(price_text)
                if price_num > 0:  # Игнорируем нулевые цены
                    if price_from <= price_num <= price_to:
                        prices_in_range.append((i, price_text, price_num))
                    else:
                        prices_out_of_range.append((i, price_text, price_num))

            # Формируем отчет
            if prices_in_range:
                in_range_info = "\n".join([f"  Товар #{i}: {text} ({num} руб.)"
                                           for i, text, num in prices_in_range])
                allure.attach(f"Товары в диапазоне:\n{in_range_info}",
                              name="Цены в диапазоне")

            if prices_out_of_range:
                out_range_info = "\n".join([f"  Товар #{i}: {text} ({num} руб.)"
                                            for i, text, num in prices_out_of_range])
                allure.attach(f"Товары вне диапазона:\n{out_range_info}",
                              name="⚠Цены вне диапазона")

            # Проверяем, что все цены в диапазоне
            assert len(prices_out_of_range) == 0, \
                f"Найдено {len(prices_out_of_range)} товаров с ценой вне диапазона {price_from}-{price_to}"

            allure.attach(f"Все {len(prices_in_range)} товаров имеют цены в диапазоне {price_from}-{price_to}",
                          name="Успех")

            return prices_in_range

    def get_first_product_name(self) -> str:
        """Получить название первого товара в каталоге"""
        with allure.step("Получить название первого товара"):
            self.wait_for_selector(self.PRODUCT_CARD)
            first_product_link = self.page.locator(self.PRODUCT_LINK).first

            if first_product_link.is_visible():
                name = first_product_link.text_content()
                allure.attach(f"Название первого товара: {name}", name="Информация")
                return name or ""
            else:
                allure.attach("Первый товар не найден", name="Ошибка")
                return ""

    def get_first_product_price(self) -> str:
        """Получить цену первого товара в каталоге"""
        with allure.step("Получить цену первого товара"):
            self.wait_for_selector(self.PRODUCT_CARD)
            first_card = self.page.locator(self.PRODUCT_CARD).first
            price = self._extract_price_from_card(first_card)

            if price:
                allure.attach(f"Цена первого товара: {price}", name="Информация")
                return price
            else:
                allure.attach("Не удалось найти цену первого товара", name="Ошибка")
                return "0"

    def get_first_product_href(self) -> str:
        """Получить href (ссылку) первого товара в каталоге"""
        with allure.step("Получить href первого товара в каталоге"):
            self.wait_for_selector(self.PRODUCT_CARD)

            # Пробуем найти ссылку в названии товара
            product_link = self.page.locator(self.PRODUCT_LINK).first

            if product_link.is_visible():
                href = product_link.get_attribute('href')
                allure.attach(f"href первого товара: {href}", name="Информация")
                return href or ""

            # Если не нашли через PRODUCT_LINK, ищем любую ссылку внутри карточки
            first_card = self.page.locator(self.PRODUCT_CARD).first
            any_link = first_card.locator("a").first

            if any_link.is_visible():
                href = any_link.get_attribute('href')
                allure.attach(f"href первого товара (альтернативный): {href}", name="Информация")
                return href or ""

            allure.attach("Не удалось найти href первого товара", name="Ошибка")
            return ""

    def click_first_product_favorite(self):
        """Нажать на иконку избранного у первого товара (более надежный способ)"""
        with allure.step("Добавить первый товар в избранное"):
            # Ждем появления хотя бы одной карточки товара
            self.page.wait_for_selector(self.PRODUCT_CARD, state="visible", timeout=10000)

            # Берем первую карточку
            first_card = self.page.locator(self.PRODUCT_CARD).first

            # Прокручиваем к карточке, чтобы она была в зоне видимости
            first_card.scroll_into_view_if_needed()
            self.page.wait_for_timeout(500)

            # Ищем иконку избранного внутри первой карточки
            # Используем более конкретный локатор
            favorite_icon = first_card.locator(".product-card__favorites .favorite-icon").first

            # Проверяем видимость и кликаем
            if favorite_icon.is_visible():
                # Дополнительно логируем состояние до клика
                class_before = favorite_icon.get_attribute("class")
                allure.attach(f"Классы иконки ДО клика: {class_before}", name="Отладка")

                # Пробуем кликнуть через JavaScript на случай, если элемент перекрыт
                try:
                    favorite_icon.click(timeout=5000)
                except:
                    # Если обычный клик не сработал, пробуем JS
                    self.page.evaluate("(element) => element.click()", favorite_icon)

                self.page.wait_for_timeout(1000)  # Ждем обновления состояния

                # Проверяем состояние после клика
                class_after = favorite_icon.get_attribute("class")
                allure.attach(f"Классы иконки ПОСЛЕ клика: {class_after}", name="Отладка")

                # Проверяем, добавился ли класс 'active' (признак успешного добавления)
                if 'active' in class_after:
                    allure.attach("Товар успешно добавлен в избранное (появился класс 'active')", name="Успешно")
                else:
                    # Если класс не появился, но ошибки не было, возможно, сайт работает иначе
                    allure.attach("Класс 'active' не обнаружен после клика, но клик прошел. Проверяем счетчик...",
                                  name="Предупреждение")
            else:
                # Если иконка не видна, сохраняем HTML для отладки
                card_html = first_card.inner_html()
                allure.attach(card_html, name="HTML первой карточки",
                              attachment_type=allure.attachment_type.HTML)

                # Попробуем найти иконку по другому пути (на случай изменения верстки)
                alt_icon = first_card.locator("a.favorite-icon").first
                if alt_icon.is_visible():
                    alt_icon.click()
                    allure.attach("Иконка найдена по альтернативному пути и кликнута", name="Успешно")
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
                card_html = first_card.inner_html()
                allure.attach(card_html, name="HTML первой карточки",
                              attachment_type=allure.attachment_type.HTML)
                raise AssertionError("Кнопка 'Купить' не найдена у первого товара")

    def click_first_product(self):
        """Кликнуть на первый товар в каталоге для перехода на его страницу"""
        with allure.step("Перейти на страницу первого товара"):
            self.wait_for_selector(self.PRODUCT_CARD)

            # Запоминаем название товара
            product_name = self.get_first_product_name()
            allure.attach(f"Переход на страницу товара: {product_name}", name="Информация")

            # Ищем ссылку "Купить" у первого товара
            first_card = self.page.locator(self.PRODUCT_CARD).first
            buy_link = first_card.locator("a.btn-primary:has-text('Купить')").first

            if buy_link.is_visible():
                # Получаем URL из href перед кликом
                href = buy_link.get_attribute('href')
                allure.attach(f"URL товара: {href}", name="Информация")

                # Кликаем и ждем загрузки страницы
                with self.page.expect_navigation(wait_until="domcontentloaded", timeout=30000):
                    buy_link.click()

                # Дополнительная задержка для полной загрузки
                self.page.wait_for_timeout(2000)
            else:
                # Если нет прямой ссылки "Купить", кликаем по названию
                product_link = first_card.locator(self.PRODUCT_LINK).first
                if product_link.is_visible():
                    with self.page.expect_navigation(wait_until="domcontentloaded", timeout=30000):
                        product_link.click()
                    self.page.wait_for_timeout(2000)
                else:
                    raise AssertionError("Не удалось найти способ перехода на страницу товара")

            # Проверяем, что мы действительно на странице товара
            assert "product" in self.page.url or "id" in self.page.url, \
                f"Не удалось перейти на страницу товара. Текущий URL: {self.page.url}"

    def click_product_by_name(self, product_name: str):
        """
        Кликнуть на товар по названию и перейти на его страницу

        Args:
            product_name: Название товара (полное или частичное)
        """
        with allure.step(f"Кликнуть на товар '{product_name}'"):
            self.page.wait_for_selector(self.PRODUCT_CARD, timeout=10000)

            # Получаем все ссылки на товары
            product_links = self.page.locator(self.PRODUCT_LINK).all()

            found = False
            for link in product_links:
                if link.is_visible():
                    name = link.text_content()
                    if name and product_name.lower() in name.lower():
                        # Прокручиваем к ссылке
                        link.scroll_into_view_if_needed()
                        self.page.wait_for_timeout(500)

                        # Запоминаем URL до клика для отладки
                        before_url = self.page.url
                        allure.attach(f"URL до клика: {before_url}", name="Информация")

                        # Получаем href для проверки после перехода
                        href = link.get_attribute('href')
                        allure.attach(f"href товара: {href}", name="Информация")

                        try:
                            # Используем expect_navigation с wait_until="domcontentloaded"
                            with self.page.expect_navigation(wait_until="domcontentloaded", timeout=30000):
                                link.click()

                            # Даем время на рендеринг
                            self.page.wait_for_timeout(2000)

                        except Exception as e:
                            allure.attach(f"Ошибка при навигации: {str(e)}", name="Ошибка")
                            # Пробуем прямой переход по href
                            if href:
                                if href.startswith('/'):
                                    from config.config import Config
                                    full_url = Config.BASE_URL + href
                                else:
                                    full_url = href

                                allure.attach(f"Пробуем прямой переход: {full_url}", name="Информация")
                                self.page.goto(full_url, wait_until="domcontentloaded")
                                self.page.wait_for_timeout(2000)

                        # Проверяем, что перешли на страницу товара
                        after_url = self.page.url
                        allure.attach(f"URL после клика: {after_url}", name="Информация")

                        # Проверяем, что URL изменился и содержит признаки страницы товара
                        assert after_url != before_url, "URL не изменился после клика"

                        # Проверяем наличие признаков страницы товара
                        product_indicators = [
                            "h1",  # Заголовок товара
                            ".productPrice",  # Цена
                            ".btnToCart",  # Кнопка в корзину
                        ]

                        for indicator in product_indicators:
                            try:
                                self.page.wait_for_selector(indicator, timeout=5000)
                                allure.attach(f"Найден индикатор страницы товара: {indicator}",
                                              name="Успех")
                                break
                            except:
                                continue

                        found = True
                        break

                if found:
                    break

            if not found:
                # Если товар не найден, собираем все названия для отладки
                all_names = []
                for link in product_links:
                    if link.is_visible():
                        name = link.text_content()
                        if name:
                            all_names.append(name.strip())

                names_text = "\n".join([f"  {i + 1}. {name}" for i, name in enumerate(all_names[:20])])
                if len(all_names) > 20:
                    names_text += f"\n  ... и еще {len(all_names) - 20} товаров"

                allure.attach(
                    f"Товар '{product_name}' не найден.\n\nДоступные товары:\n{names_text}",
                    name="Ошибка"
                )

                # Делаем скриншот для отладки
                from utils.allure_attach import attach_screenshot
                attach_screenshot(self.page, "Страница каталога")

                raise AssertionError(f"Товар с названием '{product_name}' не найден")

    def get_first_favorite_icon_state(self) -> str:
        """Получить состояние иконки избранного первого товара"""
        with allure.step("Получить состояние иконки избранного"):
            first_card = self.page.locator(self.PRODUCT_CARD).first
            favorite_icon = first_card.locator(self.PRODUCT_FAVORITE_ICON).first

            if favorite_icon.is_visible():
                classes = favorite_icon.get_attribute('class') or ""
                is_active = 'active' in classes
                allure.attach(
                    f"Иконка видима: {favorite_icon.is_visible()}\n"
                    f"Классы: {classes}\n"
                    f"Активна: {is_active}",
                    name="Состояние иконки"
                )
                return classes
            else:
                allure.attach("Иконка избранного не найдена", name="Ошибка")
                return ""

    def get_product_href_by_name(self, product_name: str) -> str:
        """
        Получить href (ссылку) товара по его названию

        Args:
            product_name: Название товара (полное или частичное)

        Returns:
            str: href товара или пустая строка, если товар не найден
        """
        with allure.step(f"Получить href товара по названию: '{product_name}'"):
            # Ждем загрузки карточек товаров
            self.page.wait_for_selector(self.PRODUCT_CARD, timeout=10000)

            # Получаем все карточки товаров
            product_cards = self.page.locator(self.PRODUCT_CARD).all()

            allure.attach(f"Всего карточек товаров на странице: {len(product_cards)}",
                          name="Информация")

            # Перебираем карточки в поисках нужного товара
            for card_index, card in enumerate(product_cards, 1):
                try:
                    # Ищем ссылку с названием товара
                    name_link = card.locator(self.PRODUCT_LINK).first

                    if not name_link.is_visible():
                        continue

                    # Получаем текст названия
                    name_text = name_link.text_content()
                    if not name_text:
                        continue

                    # Проверяем, содержит ли название искомый текст
                    if product_name.lower() in name_text.lower():
                        # Получаем href
                        href = name_link.get_attribute('href')

                        allure.attach(
                            f"Найден товар #{card_index}:\n"
                            f"Название: {name_text}\n"
                            f"href: {href}",
                            name="Товар найден"
                        )

                        return href or ""

                except Exception as e:
                    # Логируем ошибку, но продолжаем поиск
                    allure.attach(f"Ошибка при обработке карточки #{card_index}: {str(e)}",
                                  name="Предупреждение")
                    continue

            # Если товар не найден, собираем все названия для отладки
            all_names = []
            for card in product_cards:
                try:
                    name_link = card.locator(self.PRODUCT_LINK).first
                    if name_link.is_visible():
                        name = name_link.text_content()
                        if name:
                            all_names.append(name.strip())
                except:
                    pass

            # Формируем подробный отчет
            if all_names:
                names_list = "\n".join([f"  {i + 1}. {name}" for i, name in enumerate(all_names[:20])])
                if len(all_names) > 20:
                    names_list += f"\n  ... и еще {len(all_names) - 20} товаров"

                allure.attach(
                    f"Товар '{product_name}' не найден.\n\n"
                    f"Все товары на странице (первые 20):\n{names_list}",
                    name="Товар не найден"
                )
            else:
                allure.attach(
                    f"Товар '{product_name}' не найден. На странице нет товаров.",
                    name="Товар не найден"
                )

            # Делаем скриншот для отладки
            from utils.allure_attach import attach_screenshot
            attach_screenshot(self.page, "Страница каталога при поиске товара")

            return ""

    def get_product_href_by_name_all_pages(self, product_name: str, max_pages: int = 5) -> str:
        """
        Получить href товара по названию с поиском по нескольким страницам каталога
        """
        with allure.step(f"Поиск href товара '{product_name}' по страницам каталога"):
            current_page = 1
            base_url = self.page.url.split('?')[0]  # Базовый URL без параметров

            while current_page <= max_pages:
                allure.attach(f"Поиск на странице {current_page}", name="Информация")

                # Ищем на текущей странице
                href = self.get_product_href_by_name(product_name)

                if href:
                    allure.attach(f"Товар найден на странице {current_page}", name="Успех")
                    return href

                # Проверяем, есть ли следующая страница
                next_page_link = self.page.locator("a.next, .pagination .next a, .pagination a:has-text('»')").first

                if not next_page_link.is_visible():
                    allure.attach("Достигнут конец пагинации", name="Информация")
                    break

                # Переходим на следующую страницу
                next_page_link.click()
                self.page.wait_for_load_state("domcontentloaded")
                self.page.wait_for_timeout(2000)
                self.wait_for_selector(self.PRODUCT_CARD)

                current_page += 1

            allure.attach(f"Товар '{product_name}' не найден после проверки {current_page - 1} страниц",
                          name="Результат")
            return ""
