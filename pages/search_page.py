import allure
from pages.base_page import BasePage
from config.config import Config


class SearchPage(BasePage):
    SEARCH_RESULTS_GRID = ".product-card"
    FIRST_SEARCH_RESULT_TITLE = f"{SEARCH_RESULTS_GRID}:first-child .product-card__name a"
    SEARCH_RESULTS_COUNT = ".w-100.pl-3.pr-3"

    def open_search_page(self):
        with allure.step("Открыть главную страницу"):
            self.open(Config.BASE_URL)
            self.page.wait_for_load_state("domcontentloaded")

    def search(self, query: str):
        with allure.step(f"Выполнить поиск по запросу: '{query}'"):
            # Прямой переход на страницу поиска
            search_url = f"{Config.BASE_URL}/search/{query}"
            allure.attach(f"Переход по URL: {search_url}", name="Информация")

            # Переходим на страницу поиска
            self.page.goto(search_url, wait_until="domcontentloaded")
            self.page.wait_for_timeout(2000)

            # Проверяем результаты
            try:
                self.wait_for_selector(self.SEARCH_RESULTS_GRID)
                results_count = self.page.locator(self.SEARCH_RESULTS_GRID).count()
                allure.attach(f"Найдено результатов: {results_count}", name="Информация")

                # Выводим заголовки всех найденных товаров
                titles = []
                for card in self.page.locator(self.SEARCH_RESULTS_GRID).all()[:5]:  # Первые 5
                    title_elem = card.locator(".product-card__name a").first
                    if title_elem.is_visible():
                        titles.append(title_elem.text_content())

                if titles:
                    allure.attach("Первые результаты:\n" + "\n".join(titles), name="Результаты поиска")

            except Exception as e:
                allure.attach(f"Результаты поиска не найдены: {str(e)}", name="Предупреждение")

    def get_first_result_title(self) -> str:
        with allure.step("Получить название первого результата поиска"):
            try:
                self.page.wait_for_selector(self.SEARCH_RESULTS_GRID, timeout=5000)
                first_result = self.page.locator(self.FIRST_SEARCH_RESULT_TITLE).first

                if first_result.is_visible():
                    title = first_result.text_content()
                    allure.attach(f"Первый результат: {title}", name="Информация")
                    return title.strip() if title else ""
            except Exception as e:
                allure.attach(f"Ошибка: {str(e)}", name="Ошибка")

            return ""