import allure
import re
from pages.base_page import BasePage


class ProductPage(BasePage):
    TITLE = "h1"
    PRICE = ".productPrice"
    FAVORITE_ICON = ".favorite-icon"
    ADD_TO_CART_BTN = ".btnToCart"

    # Локаторы для уведомления после добавления в корзину
    NOTIFICATION = ".notification, .alert, .toast"  # Общий локатор для уведомления
    NOTIFICATION_GO_TO_CART = "a:has-text('Перейти в корзину'), button:has-text('Перейти в корзину'), .btn:has-text('Корзину')"
    NOTIFICATION_CONTINUE = "button:has-text('Продолжить'), .btn:has-text('Продолжить')"

    # Характеристики из HTML
    SPEC_CONTAINER = ".product-tab__block"  # Блок с характеристиками
    SPEC_ITEM = "p"  # Характеристики в параграфах

    DESCRIPTION_TAB = "a[href='#singleProdDesc'], a:has-text('Описание')"
    SPEC_TAB = "a[href='#singleProdParam'], a:has-text('Характеристики')"
    REVIEW_TAB = "a[href='#singleProdReview'], a:has-text('Отзывы')"

    # Локаторы для таблицы характеристик
    SPEC_TABLE = "div.tab-pane#singleProdParam table.table"
    SPEC_ROW = f"{SPEC_TABLE} tbody tr"
    SPEC_NAME = f"{SPEC_ROW} td:first-child"
    SPEC_VALUE = f"{SPEC_ROW} td:last-child"

    def get_product_title(self) -> str:
        title = self.get_text(self.TITLE)
        allure.attach(f"Заголовок товара: {title}", name="Информация")
        return title

    def get_product_price(self) -> str:
        price = self.get_text(self.PRICE)
        allure.attach(f"Цена товара: {price}", name="Информация")
        return price.replace(' ','')

    def get_specifications(self) -> dict:
        """Получить все характеристики товара в виде словаря"""
        with allure.step("Получить все характеристики товара"):
            specs = {}

            # Ждем загрузки блока с характеристиками
            if self.is_visible(self.SPEC_CONTAINER):
                # Ищем все параграфы в блоке характеристик
                paragraphs = self.page.locator(f"{self.SPEC_CONTAINER} {self.SPEC_ITEM}").all()

                for p in paragraphs:
                    text = p.text_content()
                    if text and ':' in text:
                        key, value = text.split(':', 1)
                        specs[key.strip()] = value.strip()

            allure.attach(str(specs), name="Характеристики")
            return specs

    def get_specification_value(self, spec_name: str) -> str:
        """Получить значение конкретной характеристики"""
        specs = self.get_specifications()
        return specs.get(spec_name, "")

    def click_add_to_favorite(self):
        self.click(self.FAVORITE_ICON, description="Добавить в избранное")

    def click_add_to_cart(self):
        """Нажать кнопку добавления в корзину"""
        with allure.step("Нажать кнопку 'В корзину'"):
            # Ждем появления кнопки
            self.page.wait_for_selector(self.ADD_TO_CART_BTN, timeout=10000)

            # Ищем кнопку по точному классу из HTML
            add_btn = self.page.locator("a.btnToCart.btn-primary:has-text('В корзину')").first

            if not add_btn.is_visible():
                # Альтернативный поиск
                add_btn = self.page.locator(self.ADD_TO_CART_BTN).first

            if add_btn.is_visible():
                # Прокручиваем к кнопке
                add_btn.scroll_into_view_if_needed()
                self.page.wait_for_timeout(500)

                # Получаем информацию о товаре перед кликом
                product_data = {
                    'title': add_btn.get_attribute('data-title'),
                    'price': add_btn.get_attribute('data-price'),
                    'id': add_btn.get_attribute('data-id')
                }
                allure.attach(f"Данные товара: {product_data}", name="Информация")

                # Кликаем по кнопке
                add_btn.click()
                allure.attach("Кнопка 'В корзину' нажата", name="Успешно")

                # Ждем появления уведомления
                self.page.wait_for_timeout(2000)
            else:
                # Сохраняем HTML для отладки
                page_html = self.page.content()
                allure.attach(page_html[:5000], name="HTML страницы (первые 5000 символов)",
                              attachment_type=allure.attachment_type.HTML)
                raise AssertionError("Кнопка 'В корзину' не найдена на странице")

    def click_specifications_tab(self):
        """Нажать на вкладку 'Характеристики'"""
        with allure.step("Перейти на вкладку 'Характеристики'"):
            # Ждем появления вкладки
            spec_tab = self.page.locator(self.SPEC_TAB).first

            if spec_tab.is_visible():
                # Прокручиваем к вкладке
                spec_tab.scroll_into_view_if_needed()
                self.page.wait_for_timeout(500)

                # Проверяем, не активна ли уже вкладка
                is_active = spec_tab.get_attribute('aria-selected') == 'true' or 'active' in (
                            spec_tab.get_attribute('class') or '')

                if not is_active:
                    # Кликаем по вкладке
                    spec_tab.click()
                    self.page.wait_for_timeout(1000)  # Ждем загрузки содержимого
                    allure.attach("Вкладка 'Характеристики' активирована", name="Успешно")
                else:
                    allure.attach("Вкладка 'Характеристики' уже активна", name="Информация")

                # Проверяем, что содержимое вкладки загрузилось
                self.page.wait_for_selector(self.SPEC_TABLE, timeout=5000)
            else:
                # Если вкладка не найдена, возможно характеристики в другом месте
                allure.attach("Вкладка 'Характеристики' не найдена, ищем таблицу характеристик на странице",
                              name="Предупреждение")

                # Пробуем найти таблицу характеристик вне вкладок
                alt_table = self.page.locator("table.table:has(td:has-text('Ширина'))").first
                if alt_table.is_visible():
                    allure.attach("Таблица характеристик найдена на основной странице",
                                  name="Информация")
                else:
                    # Сохраняем HTML для отладки
                    page_html = self.page.content()
                    allure.attach(page_html[:5000], name="HTML страницы (первые 5000 символов)",
                                  attachment_type=allure.attachment_type.HTML)
                    raise AssertionError("Вкладка 'Характеристики' не найдена")

    def go_to_cart_from_notification(self):
        """Перейти в корзину из всплывающего уведомления"""
        with allure.step("Перейти в корзину из уведомления"):
            # Ждем появления уведомления
            try:
                self.page.wait_for_selector(self.NOTIFICATION, timeout=5000)
                allure.attach("Уведомление появилось", name="Успешно")
            except:
                allure.attach("Уведомление не появилось, возможно товар уже был добавлен",
                              name="Предупреждение")
                return

            # Ищем кнопку перехода в корзину в уведомлении
            go_to_cart_btn = self.page.locator(self.NOTIFICATION_GO_TO_CART).first
            if go_to_cart_btn.is_visible():
                go_to_cart_btn.click()
                self.page.wait_for_load_state("networkidle")
                allure.attach("Клик по кнопке 'Перейти в корзину'", name="Успешно")
            else:
                # Если кнопка не найдена, возможно нужно искать в другом месте
                allure.attach("Кнопка перехода в корзину не найдена в уведомлении",
                              name="Предупреждение")
                # Пробуем найти любую ссылку на корзину
                cart_link = self.page.locator("a[href='/cart']").first
                if cart_link.is_visible():
                    cart_link.click()
                    self.page.wait_for_load_state("networkidle")
                else:
                    # Если ничего не нашли, просто переходим по URL
                    from config.config import Config
                    self.page.goto(Config.CART_URL)

    def get_specifications_from_table(self) -> dict:
        """
        Получить все характеристики товара из таблицы

        Returns:
            dict: Словарь с характеристиками {название: значение}
        """
        with allure.step("Получить характеристики из таблицы"):
            specs = {}

            # Сначала убедимся, что мы на вкладке с характеристиками
            try:
                self.click_specifications_tab()
            except:
                allure.attach("Не удалось активировать вкладку характеристик, пробуем найти таблицу",
                              name="Предупреждение")

            # Ищем таблицу характеристик
            table = self.page.locator(self.SPEC_TABLE).first

            if table.is_visible():
                # Получаем все строки таблицы
                rows = table.locator("tbody tr").all()

                allure.attach(f"Найдено строк с характеристиками: {len(rows)}",
                              name="Информация")

                for i, row in enumerate(rows, 1):
                    try:
                        # Получаем ячейки в строке
                        cells = row.locator("td").all()

                        if len(cells) >= 2:
                            spec_name = cells[0].text_content()
                            spec_value = cells[1].text_content()

                            if spec_name and spec_value:
                                # Очищаем от лишних пробелов
                                spec_name = spec_name.strip().rstrip(':').strip()
                                spec_value = spec_value.strip()

                                specs[spec_name] = spec_value
                                allure.attach(f"  {i}. {spec_name}: {spec_value}",
                                              name="Характеристика")
                    except Exception as e:
                        allure.attach(f"Ошибка при парсинге строки {i}: {str(e)}",
                                      name="Предупреждение")
                        continue

                allure.attach(f"Всего получено характеристик: {len(specs)}",
                              name="Итог")
            else:
                # Пробуем найти характеристики в другом формате
                allure.attach("Таблица характеристик не найдена, ищем в другом формате",
                              name="Предупреждение")

                # Поиск по параграфам (альтернативный формат)
                paragraphs = self.page.locator(".product-tab__block p, .characteristics p").all()
                for p in paragraphs:
                    text = p.text_content()
                    if text and ':' in text:
                        key, value = text.split(':', 1)
                        specs[key.strip()] = value.strip()

            if not specs:
                # Сохраняем HTML для отладки
                page_html = self.page.content()
                allure.attach(page_html[:5000], name="HTML страницы (первые 5000 символов)",
                              attachment_type=allure.attachment_type.HTML)
                allure.attach("Характеристики не найдены", name="Ошибка")

            return specs

    def get_specification_value(self, spec_name: str) -> str:
        """
        Получить значение конкретной характеристики

        Args:
            spec_name: Название характеристики (например, "Ширина, мм.")

        Returns:
            str: Значение характеристики или пустая строка
        """
        with allure.step(f"Получить значение характеристики: '{spec_name}'"):
            specs = self.get_specifications_from_table()

            # Поиск точного совпадения
            if spec_name in specs:
                value = specs[spec_name]
                allure.attach(f"Найдено точное совпадение: {value}",
                              name="Информация")
                return value

            # Поиск частичного совпадения
            for key, value in specs.items():
                if spec_name.lower() in key.lower():
                    allure.attach(f"Найдено частичное совпадение: '{key}' = '{value}'",
                                  name="Информация")
                    return value

            allure.attach(f"Характеристика '{spec_name}' не найдена",
                          name="Ошибка")
            return ""

    def verify_specification(self, spec_name: str, expected_value: str) -> bool:
        """
        Проверить, что характеристика соответствует ожидаемому значению

        Args:
            spec_name: Название характеристики
            expected_value: Ожидаемое значение

        Returns:
            bool: True если соответствует, иначе False
        """
        with allure.step(f"Проверить характеристику '{spec_name}': ожидается '{expected_value}'"):
            actual_value = self.get_specification_value(spec_name)

            if not actual_value:
                allure.attach(f"Характеристика '{spec_name}' не найдена",
                              name="Ошибка")
                return False

            # Нормализуем значения для сравнения
            actual_norm = actual_value.lower().strip()
            expected_norm = expected_value.lower().strip()

            # Проверяем на совпадение
            if expected_norm in actual_norm or actual_norm in expected_norm:
                allure.attach(f"Характеристика соответствует: '{actual_value}'",
                              name="Успех")
                return True
            else:
                allure.attach(f"Несоответствие: ожидалось '{expected_value}', получено '{actual_value}'",
                              name="Ошибка")
                return False

    def extract_numeric_value(self, text: str) -> int:
        """
        Извлечь числовое значение из текста (например, из "2200 мм" -> 2200)

        Args:
            text: Текст с числом

        Returns:
            int: Числовое значение или 0
        """
        import re
        match = re.search(r'(\d+)', text)
        if match:
            return int(match.group(1))
        return 0

    def verify_dimension(self, dimension_name: str, expected_min: int, expected_max: int = None) -> bool:
        """
        Проверить, что размер (ширина/высота/глубина) находится в допустимом диапазоне

        Args:
            dimension_name: Название размера ("Ширина", "Высота", "Глубина")
            expected_min: Минимальное ожидаемое значение
            expected_max: Максимальное ожидаемое значение (если None, то точное совпадение)

        Returns:
            bool: True если соответствует, иначе False
        """
        with allure.step(f"Проверить размер '{dimension_name}'"):
            # Ищем характеристики, содержащие название размера
            specs = self.get_specifications_from_table()

            for key, value in specs.items():
                if dimension_name.lower() in key.lower():
                    numeric_value = self.extract_numeric_value(value)

                    if expected_max is None:
                        # Точное совпадение
                        if numeric_value == expected_min:
                            allure.attach(f"{dimension_name} = {numeric_value} (ожидалось {expected_min})",
                                          name="Успех")
                            return True
                    else:
                        # Диапазон
                        if expected_min <= numeric_value <= expected_max:
                            allure.attach(
                                f"{dimension_name} = {numeric_value} в диапазоне [{expected_min}-{expected_max}]",
                                name="Успех")
                            return True

                    allure.attach(f"{dimension_name} = {numeric_value} не соответствует ожиданиям",
                                  name="Ошибка")
                    return False

            allure.attach(f"Размер '{dimension_name}' не найден", name="Ошибка")
            return False