# conftest.py
import allure
import pytest
import os
import re
from playwright.sync_api import sync_playwright
from config.config import Config
from utils import allure_attach


# Парсим аргументы командной строки для выбора браузера
def pytest_addoption(parser):
    parser.addoption(
        "--test-browser",
        action="store",
        default="chromium",
        choices=Config.BROWSERS,
        help="Choose browser: chromium or firefox"
    )
    parser.addoption(
        "--num-threads",
        action="store",
        default="auto",
        help="Number of threads for parallel execution (auto, 2, 4, etc.)"
    )


# Функция для определения количества потоков
def pytest_configure(config):
    """Регистрация кастомных маркеров"""
    config.addinivalue_line(
        "markers",
        "filter_test: тесты фильтрации"
    )
    config.addinivalue_line(
        "markers",
        "cart_test: тесты корзины"
    )
    config.addinivalue_line(
        "markers",
        "favorite_test: тесты избранного"
    )
    config.addinivalue_line(
        "markers",
        "search_test: тесты поиска"
    )
    config.addinivalue_line(
        "markers",
        "product_test: тесты карточки товара"
    )

    # Существующий код для параллельного запуска
    if not hasattr(config, 'workerinput'):
        num_threads = config.getoption("--num-threads")
        os.environ['PYTEST_XDIST_NUM_THREADS'] = num_threads

        if num_threads == "auto":
            import multiprocessing
            threads = multiprocessing.cpu_count()
            print(f"\nЗапуск тестов в {threads} потоков (автоопределение)")
        else:
            print(f"\nЗапуск тестов в {num_threads} потоков")


@pytest.fixture(scope="function")
def browser(request):
    """Фикстура браузера с поддержкой параллельного запуска"""
    browser_name = request.config.getoption("--test-browser")

    # Определяем уникальный порт для каждого worker'а (для изоляции)
    worker_id = getattr(request.config, 'workerinput', {}).get('workerid', 'master')

    with sync_playwright() as p:
        # Настройки запуска браузера
        launch_options = {
            "headless": False,  # Можно сделать параметром
            "slow_mo": 300,  # Уменьшаем для скорости
        }

        # Для firefox могут быть свои особенности
        if browser_name == "chromium":
            browser = p.chromium.launch(**launch_options)
        elif browser_name == "firefox":
            browser = p.firefox.launch(**launch_options)
        else:
            browser = p.chromium.launch(**launch_options)

        yield browser
        browser.close()


@pytest.fixture(scope="function")
def page(browser, request):
    """Фикстура страницы с уникальным контекстом для каждого теста"""
    # Создаем уникальный контекст для изоляции тестов
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent=f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (parallel-test-{request.node.name})"
    )

    # Устанавливаем таймаут
    context.set_default_timeout(10000)

    page = context.new_page()

    # Добавляем трассировку для отладки (опционально)
    worker_id = getattr(request.config, 'workerinput', {}).get('workerid', 'master')
    trace_path = f"traces/{worker_id}_{request.node.name}"


    yield page

    # Останавливаем трассировку при падении
    # if request.node.rep_call.failed:
    #     context.tracing.stop(path=f"{trace_path}.zip")

    context.close()


@pytest.fixture(scope="function")
def catalog_page(page):
    from pages.catalog_page import CatalogPage
    return CatalogPage(page)


@pytest.fixture(scope="function")
def product_page(page):
    from pages.product_page import ProductPage
    return ProductPage(page)


@pytest.fixture(scope="function")
def favorite_page(page):
    from pages.favorite_page import FavoritePage
    return FavoritePage(page)


@pytest.fixture(scope="function")
def search_page(page):
    from pages.search_page import SearchPage
    return SearchPage(page)


@pytest.fixture(scope="function")
def cart_page(page):
    from pages.cart_page import CartPage
    return CartPage(page)


# Хук для скриншота при падении теста
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    # Сохраняем результат для использования в фикстурах
    if rep.when == "call":
        setattr(item, "rep_call", rep)

    if rep.when == "call" and rep.failed:
        if "page" in item.funcargs:
            page = item.funcargs["page"]
            worker_id = getattr(item.config, 'workerinput', {}).get('workerid', 'master')

            # Добавляем информацию о worker'е в название скриншота
            allure_attach.attach_screenshot(
                page,
                name=f"Скриншот при падении (worker: {worker_id})"
            )
            allure_attach.attach_page_source(
                page,
                name=f"HTML код страницы при падении (worker: {worker_id})"
            )

            # Добавляем информацию о текущем URL
            allure.attach(
                page.url,
                name=f"URL при падении (worker: {worker_id})",
                attachment_type=allure.attachment_type.TEXT
            )


# Хук для логирования начала теста в параллельном режиме
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    worker_id = getattr(item.config, 'workerinput', {}).get('workerid', 'master')
    print(f"\n[Worker {worker_id}] Запуск теста: {item.name}")


# Функция для группировки тестов по категориям (опционально)
def pytest_collection_modifyitems(items):
    """Группируем тесты для более эффективного параллельного запуска"""
    for item in items:
        # Добавляем маркеры для группировки по фичам
        if "test_filter" in item.nodeid:
            item.add_marker(pytest.mark.filter_test)
        elif "test_cart" in item.nodeid:
            item.add_marker(pytest.mark.cart_test)
        elif "test_favorite" in item.nodeid:
            item.add_marker(pytest.mark.favorite_test)
        elif "test_search" in item.nodeid:
            item.add_marker(pytest.mark.search_test)
        elif "test_product_details" in item.nodeid:
            item.add_marker(pytest.mark.product_test)