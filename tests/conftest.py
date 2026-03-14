# conftest.py
import allure
import pytest
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


@pytest.fixture(scope="function")
def browser(request):
    browser_name = request.config.getoption("--test-browser")
    with sync_playwright() as p:
        if browser_name == "chromium":
            browser = p.chromium.launch(headless=False, slow_mo=500)
        elif browser_name == "firefox":
            browser = p.firefox.launch(headless=False, slow_mo=500)
        else:
            browser = p.chromium.launch()
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def page(browser):
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()

    # Добавляем обработчик для логирования консольных ошибок с фильтрацией
    def handle_console(msg):
        # Игнорируем ошибки JivoSite
        if "jivosite" in msg.text.lower() or "widget" in msg.text.lower():
            return
        # Игнорируем другие известные сторонние ошибки
        ignored_patterns = [
            r"widget.*removed",
            r"jivo",
            r"yandex",
            r"metrika",
            r"favicon\.ico"
        ]

        for pattern in ignored_patterns:
            if re.search(pattern, msg.text, re.IGNORECASE):
                return

        # Печатаем остальные сообщения
        print(f"CONSOLE: {msg.text}")

    page.on("console", handle_console)

    yield page
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
    if rep.when == "call" and rep.failed:
        if "page" in item.funcargs:
            page = item.funcargs["page"]
            # Добавляем больше информации при падении
            allure_attach.attach_screenshot(page, name="Скриншот при падении теста")
            allure_attach.attach_page_source(page, name="HTML код страницы при падении")

            # Добавляем информацию о текущем URL
            allure.attach(page.url, name="URL при падении", attachment_type=allure.attachment_type.TEXT)
