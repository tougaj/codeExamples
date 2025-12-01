from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # ← показує вікно браузера
        page = browser.new_page()

        # page.goto("https://example.com")
        # page.goto("https://thehill.com/homenews/administration/5625565-trump-immigration-pause-third-world-countries/", wait_until="networkidle")
        page.goto("https://thehill.com/homenews/administration/5625565-trump-immigration-pause-third-world-countries/", timeout=30000, wait_until="networkidle")
        # page.wait_for_timeout(5000)
        selector = ".article__text"
        page.wait_for_selector(selector, state="visible", timeout=30000)
        # page.wait_for_function("selector => !!document.querySelector(selector)", selector)
        # page.wait_for_timeout(1000)
        # print(page.title())

        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1000)  # або краще — чекати конкретний елемент

        # html = page.content()
        # print(html)
        content = page.inner_html(selector)
        # content = page.inner_html("xpath=//div[contains(@class, \"article__text\")]")
        print(content)

        # Браузер залишиться відкритим
        # input("Натисни Enter, щоб закрити браузер...")

        browser.close()


if __name__ == "__main__":
    main()
