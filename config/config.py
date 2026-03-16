class Config:
    BASE_URL = "https://mebelmart-saratov.ru"
    CATALOG_URL = f"{BASE_URL}/myagkaya_mebel_v_saratove/divanyi_v_saratove"
    SEARCH_URL = f"{BASE_URL}/search/"
    FAVORITE_URL = f"{BASE_URL}/favorite"
    CART_URL = f"{BASE_URL}/cart"

    DEFAULT_TIMEOUT = 5000

    BROWSERS = ["chromium", "firefox"]
