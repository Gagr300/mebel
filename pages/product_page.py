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