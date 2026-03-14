import allure
from playwright.sync_api import Page, expect
from config.config import Config
from utils import allure_attach


class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.timeout = Config.DEFAULT_TIMEOUT

    def open(self, url: str = ""):
        with allure.step(f"Открыть страницу {url if url else Config.BASE_URL}"):
            self.page.goto(url if url else Config.BASE_URL)

    def wait_for_selector(self, selector: str, state: str = "visible"):
        """Явное ожидание элемента."""
        self.page.locator(selector).first.wait_for(state=state, timeout=self.timeout)

    def click(self, selector: str, description: str = ""):
        """Клик по элементу с описанием для шага Allure."""
        step_name = f"Кликнуть на элемент {description if description else selector}"
        with allure.step(step_name):
            self.wait_for_selector(selector)
            self.page.locator(selector).first.click()

    def fill(self, selector: str, value: str, description: str = ""):
        """Заполнить поле текстом."""
        step_name = f"Заполнить поле {description if description else selector} значением '{value}'"
        with allure.step(step_name):
            self.wait_for_selector(selector)
            self.page.locator(selector).first.fill(value)

    def get_text(self, selector: str) -> str:
        """Получить текст элемента."""
        self.wait_for_selector(selector)
        return self.page.locator(selector).first.text_content()

    def get_attribute(self, selector: str, attribute: str) -> str:
        """Получить атрибут элемента."""
        self.wait_for_selector(selector)
        return self.page.locator(selector).first.get_attribute(attribute)

    def is_visible(self, selector: str) -> bool:
        """Проверить, виден ли элемент."""
        try:
            self.wait_for_selector(selector)
            return True
        except:
            return False

    # Для скриншотов при падении (будет вызвано из conftest.py)
    def make_screenshot_on_failure(self):
        allure_attach.attach_screenshot(self.page, name="Скриншот в момент ошибки")

    def debug_element(self, selector: str, description: str = ""):
        """Отладочный метод для проверки наличия элемента"""
        try:
            element = self.page.locator(selector).first
            is_visible = element.is_visible()
            is_enabled = element.is_enabled()
            text = element.text_content()

            debug_info = f"""
            Элемент: {description or selector}
            Видим: {is_visible}
            Доступен: {is_enabled}
            Текст: {text}
            HTML: {element.inner_html() if is_visible else 'Недоступен'}
            """

            allure.attach(debug_info, name=f"Отладка: {description or selector}")
            return is_visible
        except Exception as e:
            allure.attach(f"Ошибка при проверке элемента: {str(e)}",
                          name=f"Ошибка: {description or selector}")
            return False

    def wait_and_click(self, selector: str, description: str = "", timeout: int = 30000):
        """Более надежный клик с ожиданием"""
        with allure.step(f"Кликнуть на элемент {description if description else selector}"):
            try:
                element = self.page.locator(selector).first
                element.wait_for(state="visible", timeout=timeout)
                element.wait_for(state="attached", timeout=timeout)
                element.scroll_into_view_if_needed()
                element.click()
            except Exception as e:
                allure.attach(f"Ошибка клика: {str(e)}\nURL: {self.page.url}",
                              name="Ошибка клика")
                raise

    def safe_goto(self, url: str, wait_until: str = "domcontentloaded", timeout: int = 30000):
        """
        Безопасный переход по URL с возможностью выбора состояния загрузки.
        По умолчанию ждет только загрузки DOM, не networkidle.
        """
        with allure.step(f"Перейти на страницу {url}"):
            try:
                self.page.goto(url, wait_until=wait_until, timeout=timeout)
                # Небольшая пауза для стабилизации
                self.page.wait_for_timeout(1000)
            except Exception as e:
                allure.attach(f"Ошибка при переходе на {url}: {str(e)}", name="Ошибка навигации")
                # Пробуем еще раз с меньшими требованиями
                self.page.goto(url, wait_until="commit", timeout=timeout)
                self.page.wait_for_timeout(2000)
