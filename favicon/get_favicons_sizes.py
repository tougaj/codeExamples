from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


def get_favicons_from_html(base_url, soup):
    """Знаходить іконки через <link> теги."""
    favicons = []
    for link in soup.find_all('link', rel=lambda x: x and 'icon' in x):
        href = link.get('href')
        sizes = link.get('sizes', '')  # Наприклад: "16x16", "32x32"
        if href:
            favicons.append({
                'url': urljoin(base_url, href),
                'sizes': sizes
            })
    return favicons


def get_favicons_from_manifest(base_url, soup):
    """Знаходить іконки з маніфесту."""
    manifest_link = soup.find('link', rel='manifest')
    if not manifest_link or not manifest_link.get('href'):
        print("Маніфест не знайдено.")
        return []

    manifest_url = urljoin(base_url, manifest_link['href'])
    print(f"Завантаження маніфесту: {manifest_url}")
    response = requests.get(manifest_url)

    if response.status_code != 200:
        print(f"Не вдалося завантажити маніфест: {manifest_url}")
        return []

    try:
        manifest = response.json()
        favicons = []
        for icon in manifest.get('icons', []):
            url = urljoin(base_url, icon.get('src', ''))
            sizes = icon.get('sizes', '')  # Наприклад: "192x192"
            favicons.append({'url': url, 'sizes': sizes})
        return favicons
    except Exception as e:
        print(f"Помилка обробки маніфесту: {e}")
        return []


def parse_size(size_str):
    """Парсить розмір (наприклад, '192x192') і повертає кортеж (192, 192)."""
    try:
        width, height = map(int, size_str.split('x'))
        return width, height
    except ValueError:
        return None


def find_best_favicon(favicons, target_size=(192, 192)):
    """Знаходить іконку з розміром, найближчим до цільового, але не меншого."""
    target_width, target_height = target_size
    best_favicon = None
    best_distance = float('inf')

    for favicon in favicons:
        size_str = favicon.get('sizes')
        size = parse_size(size_str)
        if size:
            width, height = size
            # Перевірка: іконка не менша за цільовий розмір
            if width >= target_width and height >= target_height:
                # Обчислення відстані між поточним розміром і 192x192
                distance = abs(target_width - width) + abs(target_height - height)
                if distance < best_distance:
                    best_distance = distance
                    best_favicon = favicon

    return best_favicon


# Основний код
url = 'https://www.unian.ua/'  # Замініть на потрібний сайт
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# 1. Знайти favicon у тегах <link>
favicons_html = get_favicons_from_html(url, soup)

# 2. Спробувати завантажити favicon із маніфесту
favicons_manifest = get_favicons_from_manifest(url, soup)

# 3. Об'єднати всі знайдені favicon
all_favicons = favicons_html + favicons_manifest
print("Усі знайдені favicon:", all_favicons)

# 4. Знайти найкращу іконку за розміром
best_favicon = find_best_favicon(all_favicons)
if best_favicon:
    print("\nНайкраща іконка:", best_favicon)
    try:
        # Завантажити і зберегти
        r = requests.get(best_favicon['url'])
        filename = best_favicon['url'].split("/")[-1]
        with open(filename, 'wb') as f:
            f.write(r.content)
        print(f"Збережено {filename} (Розмір: {best_favicon['sizes']})")
    except Exception as e:
        print(f"Помилка завантаження {best_favicon['url']}: {e}")
else:
    print("\nНе вдалося знайти підходящу іконку.")
