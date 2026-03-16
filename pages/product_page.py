import allure
import re
from pages.base_page import BasePage


class ProductPage(BasePage):
    TITLE = "h1"
    PRICE = ".productPrice"
    FAVORITE_ICON = ".favorite-icon"
    ADD_TO_CART_BTN = ".btnToCart"

    # Локаторы для уведомления после добавления в корзину
    NOTIFICATION = ".notification, .alert, .toast"
    NOTIFICATION_GO_TO_CART = "a:has-text('Перейти в корзину'), button:has-text('Перейти в корзину')"

    # Локаторы для таблицы характеристик
    SPEC_TAB = "a[href='#singleProdParam'], a:has-text('Характеристики')"
    SPEC_TABLE = "div.tab-pane#singleProdParam table.table"

    def get_product_title(self) -> str:
        title = self.get_text(self.TITLE)
        allure.attach(f"Заголовок товара: {title}", name="Информация")
        return title

    def get_product_price(self) -> str:
        price = self.get_text(self.PRICE)
        allure.attach(f"Цена товара: {price}", name="Информация")
        return price.replace(' ', '')

    def click_add_to_cart(self):
        """Нажать кнопку добавления в корзину"""
        with allure.step("Нажать кнопку 'В корзину'"):
            self.page.wait_for_selector(self.ADD_TO_CART_BTN, timeout=10000)

            add_btn = self.page.locator("a.btnToCart.btn-primary:has-text('В корзину')").first

            if not add_btn.is_visible():
                add_btn = self.page.locator(self.ADD_TO_CART_BTN).first

            if add_btn.is_visible():
                add_btn.scroll_into_view_if_needed()
                self.page.wait_for_timeout(500)
                add_btn.click()
                self.page.wait_for_timeout(2000)
            else:
                raise AssertionError("Кнопка 'В корзину' не найдена на странице")

    def click_specifications_tab(self):
        """Нажать на вкладку 'Характеристики'"""
        with allure.step("Перейти на вкладку 'Характеристики'"):
            spec_tab = self.page.locator(self.SPEC_TAB).first

            if spec_tab.is_visible():
                spec_tab.scroll_into_view_if_needed()
                self.page.wait_for_timeout(1000)

                is_active = spec_tab.get_attribute('aria-selected') == 'true' or 'active' in (
                            spec_tab.get_attribute('class') or '')

                if not is_active:
                    spec_tab.click()
                    self.page.wait_for_timeout(1000)

                self.page.wait_for_selector(self.SPEC_TABLE, timeout=5000)
            else:
                raise AssertionError("Вкладка 'Характеристики' не найдена")

    def get_specifications_from_table(self) -> dict:
        """Получить все характеристики товара из таблицы"""
        with allure.step("Получить характеристики из таблицы"):
            specs = {}

            try:
                self.click_specifications_tab()
            except:
                allure.attach("Не удалось активировать вкладку характеристик", name="Предупреждение")

            table = self.page.locator(self.SPEC_TABLE).first

            if table.is_visible():
                rows = table.locator("tbody tr").all()

                for row in rows:
                    cells = row.locator("td").all()
                    if len(cells) >= 2:
                        spec_name = cells[0].text_content()
                        spec_value = cells[1].text_content()
                        if spec_name and spec_value:
                            spec_name = spec_name.strip().rstrip(':').strip()
                            spec_value = spec_value.strip()
                            specs[spec_name] = spec_value

                allure.attach(f"Получено характеристик: {len(specs)}", name="Информация")
            else:
                allure.attach("Таблица характеристик не найдена", name="Ошибка")

            return specs

    def get_specification_value(self, spec_name: str) -> str:
        """Получить значение конкретной характеристики"""
        specs = self.get_specifications_from_table()

        # Поиск точного совпадения
        if spec_name in specs:
            return specs[spec_name]

        # Поиск частичного совпадения
        for key, value in specs.items():
            if spec_name.lower() in key.lower():
                return value

        return ""

    def extract_numeric_value(self, text: str) -> int:
        """Извлечь числовое значение из текста"""
        match = re.search(r'(\d+)', text)
        if match:
            return int(match.group(1))
        return 0