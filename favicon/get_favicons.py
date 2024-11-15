from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


def get_favicons_from_manifest(base_url, bs):
    """Знаходить і завантажує favicon з маніфесту."""
    manifest_link = bs.find('link', rel='manifest')
    if not manifest_link or not manifest_link.get('href'):
        print("Маніфест не знайдено.")
        return []

    manifest_url = urljoin(base_url, manifest_link['href'])
    print(f"Завантаження маніфесту: {manifest_url}")
    response = requests.get(manifest_url, timeout=30)

    if response.status_code != 200:
        print(f"Не вдалося завантажити маніфест: {manifest_url}")
        return []

    try:
        manifest = response.json()
        icons = [urljoin(base_url, icon['src']) for icon in manifest.get('icons', [])]
        print("Знайдено іконки в маніфесті:", icons)
        return icons
    except Exception as e:
        print(f"Помилка обробки маніфесту: {e}")
        return []


# Основний код
url = 'https://www.unian.net/'  # Замініть на потрібний сайт
response = requests.get(url, timeout=30)
soup = BeautifulSoup(response.text, 'html.parser')

# 1. Знайти favicon у тегах <link>
favicons = [urljoin(url, link['href']) for link in soup.find_all('link', rel=lambda x: x and 'icon' in x)]
print("Знайдені іконки через <link>:", favicons)

# 2. Спробувати завантажити favicon із маніфесту
favicons_from_manifest = get_favicons_from_manifest(url, soup)

# Об'єднати всі знайдені favicon
all_favicons = set(favicons + favicons_from_manifest)
print("Усі знайдені favicon:", all_favicons)

# 3. Завантаження всіх favicon
for favicon in all_favicons:
    try:
        r = requests.get(favicon, timeout=30)
        filename = favicon.split("/")[-1]
        with open(filename, 'wb') as f:
            f.write(r.content)
        print(f"Збережено {filename}")
    except Exception as e:
        print(f"Помилка завантаження {favicon}: {e}")
