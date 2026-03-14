import allure
import re
from pages.base_page import BasePage
from config.config import Config


class SearchPage(BasePage):
    SEARCH_INPUT = ".searchInput"
    SEARCH_SUBMIT_BTN = ".submit"
    SEARCH_RESULTS_GRID = ".product-card"
    FIRST_SEARCH_RESULT_TITLE = f"{SEARCH_RESULTS_GRID}:first-child .product-card__name a"
    SEARCH_RESULTS_COUNT = ".w-100.pl-3.pr-3"  # Более точный локатор для счетчика

    def open_search_page(self):
        with allure.step("Открыть страницу поиска"):
            # Можно просто открыть базовый URL, т.к. поле поиска есть везде, либо отдельную страницу, если она есть.
            # Пока оставим переход на главную, откуда можно искать.
            self.open(Config.BASE_URL)

    def search(self, query: str):
        with allure.step(f"Выполнить поиск по запросу: '{query}'"):
            if self.is_visible(self.SEARCH_INPUT):
                self.fill(self.SEARCH_INPUT, query, description="Поле поиска")
                self.click(self.SEARCH_SUBMIT_BTN, description="Кнопка 'Найти'")
            else:
                self.page.goto(f"{Config.SEARCH_URL}{query}")
            self.page.wait_for_load_state("networkidle")
            try:
                self.wait_for_selector(self.SEARCH_RESULTS_GRID)
            except:
                allure.attach("Результаты поиска не найдены", name="Предупреждение")

    def get_first_result_title(self) -> str:
        if self.is_visible(self.FIRST_SEARCH_RESULT_TITLE):
            title = self.get_text(self.FIRST_SEARCH_RESULT_TITLE)
            allure.attach(f"Первый результат: {title}", name="Информация")
            return title
        return ""

    def get_results_count(self) -> int:
        if self.is_visible(self.SEARCH_RESULTS_COUNT):
            count_text = self.get_text(self.SEARCH_RESULTS_COUNT)
            # Извлекаем число из текста "Показаны записи 1-20 из 78"
            numbers = re.findall(r'\d+', count_text)
            if len(numbers) >= 3:
                return int(numbers[2])
        return 0
