import allure


@allure.feature("Поиск")
@allure.story("Поиск товара по названию")
def test_search_product(search_page):
    search_query = "Бостон"

    # Используем метод open_search_page или просто вызываем search, который сам перейдет куда нужно
    search_page.open_search_page()  # Теперь этот метод существует
    search_page.search(search_query)

    with allure.step("Проверить, что первый результат содержит искомое слово"):
        first_result_title = search_page.get_first_result_title()
        # В предоставленном HTML первые результаты - это полки и шкафы, но они содержат "Бостон"
        assert search_query.lower() in first_result_title.lower(), \
            f"Название первого результата '{first_result_title}' не содержит '{search_query}'"
