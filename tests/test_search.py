# tests/test_search.py
# tests/test_search.py
import allure


@allure.feature("Поиск")
@allure.story("Поиск товара по названию")
def test_search_product(search_page):
    search_query = "Чебурашка"

    search_page.open_search_page()
    search_page.take_screenshot("Главная страница")

    search_page.search(search_query)
    search_page.take_screenshot(f"Результаты поиска: {search_query}")

    with allure.step("Проверить, что первый результат содержит искомое слово"):
        first_result_title = search_page.get_first_result_title()
        search_page.take_screenshot(f"Первый результат: {first_result_title}")
        assert search_query.lower() in first_result_title.lower(), \
            f"Название первого результата '{first_result_title}' не содержит '{search_query}'"
