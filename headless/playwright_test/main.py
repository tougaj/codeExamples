from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # ← показує вікно браузера
        page = browser.new_page()

        url = "https://thehill.com/homenews/administration/5625565-trump-immigration-pause-third-world-countries/"
        selector = ".article__text"

        # url = "https://www.nytimes.com/2025/12/01/world/europe/zelensky-ukraine-paris-putin-witkoff.html"
        # selector = "#story > section[name='articleBody']"

        # url = "https://www.washingtonpost.com/politics/2025/12/01/speechnow-fec-citizens-united-super-pacs/?itid=hp-top-table-main_p001_f002"
        # selector = ".meteredContent"

        # page.goto(url, timeout=30000, wait_until="networkidle")
        page.goto(url, timeout=30000, wait_until="domcontentloaded")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.locator(selector).wait_for(state="visible")

        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        # page.locator('footer').wait_for(state="visible")
        page.wait_for_timeout(1000)  # або краще — чекати конкретний елемент

        # html = page.content()
        # print(html)
        content = page.locator(selector).inner_html()
        # content = page.inner_html("xpath=//div[contains(@class, \"article__text\")]")
        print(content)

        browser.close()


if __name__ == "__main__":
    main()
