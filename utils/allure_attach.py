import allure
from playwright.sync_api import Page


def attach_screenshot(page: Page, name: str = "Скриншот"):
    """Делает скриншот страницы и прикрепляет его к отчету Allure."""
    screenshot = page.screenshot(full_page=True)
    allure.attach(screenshot, name=name, attachment_type=allure.attachment_type.PNG)


def attach_page_source(page: Page, name: str = "HTML код страницы"):
    """Прикрепляет HTML код страницы к отчету Allure."""
    allure.attach(page.content(), name=name, attachment_type=allure.attachment_type.HTML)
