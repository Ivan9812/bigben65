"""Integration checks against the running demo. Uses synthetic data only."""
import json
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright, expect

base = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:3000'
artifacts = Path(os.environ.get('BIGBEN_ARTIFACTS', '/workspace/artifacts'))
artifacts.mkdir(parents=True, exist_ok=True)
errors = []
routes = ['/', '/catalog', '/catalog/men', '/catalog/women', '/catalog/unisex',
          '/brands', '/brands/TISSOT', '/catalog/tissot-prx', '/search?q=Seiko',
          '/favorites', '/compare', '/cart', '/checkout', '/checkout/success',
          '/account/login', '/account/register', '/account/reset-password', '/account',
          '/account/profile', '/account/orders', '/account/addresses', '/account/bonuses',
          '/stores', '/stores/bigben', '/service', '/service/request', '/delivery',
          '/payment', '/returns', '/warranty', '/about', '/journal',
          '/journal/your-first-watch', '/contacts', '/faq', '/legal/privacy',
          '/legal/terms', '/legal/consent', '/missing-page', '/ui', '/appointment']

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    context = browser.new_context(viewport={'width': 1440, 'height': 1000})
    page = context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(base, wait_until='networkidle')

    def visit(route):
        page.evaluate('(route) => location.hash = route', route)
        page.locator('[data-page]').filter(has=page.locator('h1')).last.wait_for()
        page.wait_for_function('(route) => !!document.querySelector(`[data-page="${route}"] h1`)', arg=route)

    def no_overflow(label):
        result = page.evaluate('''() => ({viewport: innerWidth, width: document.documentElement.scrollWidth,
          elements: [...document.querySelectorAll('main *')].map(e => ({tag:e.tagName, cls:e.className,
          right:Math.round(e.getBoundingClientRect().right)})).filter(e=>e.right>innerWidth+1).slice(0,8)})''')
        assert result['width'] <= result['viewport'], (label, result)

    # Real shopping flow, persistence, gallery and filters.
    visit('/catalog')
    expect(page.locator('.product-card')).to_have_count(8)
    page.get_by_role('button', name='Фильтры').click()
    page.get_by_label('Бренд', exact=True).select_option('TISSOT')
    expect(page.locator('.product-card')).to_have_count(2)
    page.get_by_role('button', name='Сбросить фильтры').click()
    expect(page.locator('.product-card')).to_have_count(8)
    page.locator('.sort-label select').select_option('asc')
    assert 'Petite Sheffield' in page.locator('.product-card').first.inner_text()
    page.locator('.product-card').first.get_by_role('button', name='В избранное').click()
    page.locator('.product-card').first.get_by_role('button', name='Сравнить', exact=True).click()
    page.locator('.product-card').nth(1).get_by_role('button', name='Сравнить', exact=True).click()
    visit('/favorites')
    expect(page.locator('.product-card')).to_have_count(1)
    page.reload(wait_until='networkidle')
    expect(page.locator('.product-card')).to_have_count(1)
    visit('/compare')
    expect(page.locator('.compare-table tr').first.locator('td')).to_have_count(2)
    visit('/catalog/tissot-prx')
    page.get_by_role('button', name='Увеличить изображение часов').click()
    expect(page.get_by_role('dialog', name='PRX Powermatic 80')).to_be_visible()
    page.keyboard.press('Escape')
    expect(page.get_by_role('dialog', name='PRX Powermatic 80')).not_to_be_visible()
    page.get_by_role('button', name='Добавить в корзину').click()
    visit('/cart')
    expect(page.locator('.cart-item')).to_have_count(1)
    page.get_by_role('button', name='Увеличить количество PRX Powermatic 80').click()
    expect(page.locator('.quantity span')).to_have_text('2')
    page.get_by_role('button', name='Удалить', exact=True).click()
    expect(page.locator('.cart-item')).to_have_count(0)
    page.get_by_role('button', name='Отменить', exact=True).click()
    expect(page.locator('.cart-item')).to_have_count(1)
    page.reload(wait_until='networkidle')
    expect(page.locator('.quantity span')).to_have_text('2')
    visit('/checkout')
    page.get_by_label('Имя', exact=True).fill('Тестовый покупатель')
    page.get_by_label('Телефон', exact=True).fill('+79990000000')
    page.get_by_label('Электронная почта', exact=True).fill('browser-test@example.com')
    page.locator('input[name=consent]').check()
    page.route('**/api/orders', lambda route: route.fulfill(status=503, content_type='application/json', body=json.dumps({'error': 'Не удалось сохранить данные. Попробуйте ещё раз.'})))
    page.get_by_role('button', name='Создать демозаказ').click()
    expect(page.get_by_role('alert')).to_have_text('Не удалось сохранить данные. Попробуйте ещё раз.')
    assert page.evaluate('JSON.parse(localStorage.getItem("bigben-cart"))[0].quantity') == 2
    page.unroute('**/api/orders')
    with page.expect_response(lambda r: r.url.endswith('/api/orders') and r.request.method == 'POST') as response:
        page.get_by_role('button', name='Создать демозаказ').click()
    order = response.value.json()
    assert response.value.status == 201, order
    assert order['total'] == 159800, order
    expect(page.get_by_role('heading', name='Ваш выбор сохранён')).to_be_visible()
    assert page.evaluate('JSON.parse(localStorage.getItem("bigben-cart")).length') == 0
    visit('/account/orders/' + order['id'])
    expect(page.get_by_role('heading', name=order['number'], exact=True)).to_be_visible()
    Path('/tmp/bigben-browser-order.json').write_text(json.dumps({'id': order['id'], 'total': order['total']}))
    routes.append('/account/orders/' + order['id'])

    visit('/contacts')
    page.get_by_label('Имя', exact=True).fill('Тестовая заявка')
    page.get_by_label('Электронная почта', exact=True).fill('browser-test@example.com')
    page.get_by_label('Ваш вопрос', exact=True).fill('Учебное обращение для проверки формы.')
    page.locator('input[name=consent]').check()
    with page.expect_response(lambda r: r.url.endswith('/api/requests') and r.request.method == 'POST') as response:
        page.get_by_role('button', name='Сохранить демозаявку').click()
    assert response.value.status == 201
    request = response.value.json()
    expect(page.get_by_role('heading', name='Демозаявка сохранена')).to_be_visible()
    Path('/tmp/bigben-browser-request.json').write_text(json.dumps({'id': request['id']}))

    for width in [1440, 390]:
        page.set_viewport_size({'width': width, 'height': 1000 if width == 1440 else 844})
        for route in routes:
            visit(route)
            no_overflow(f'{width}px {route}')
            assert 'Не удалось открыть страницу' not in page.locator('main').inner_text()
    print(f'PASS: {len(routes)} routes on desktop and mobile; no horizontal overflow.')

    # Native dialog focus and keyboard behavior, search and mobile navigation.
    page.get_by_role('button', name='Поиск', exact=True).click()
    page.get_by_label('Название модели или бренд').fill('Seiko')
    page.get_by_role('button', name='Найти', exact=True).click()
    page.wait_for_function('location.hash.includes("/search?q=Seiko")')
    expect(page.locator('.product-card')).to_have_count(2)
    page.get_by_role('button', name='Открыть меню').click()
    expect(page.get_by_role('dialog', name='Меню', exact=True)).to_be_visible()
    page.get_by_role('dialog', name='Меню', exact=True).get_by_role('link', name='Бренды', exact=True).click()
    expect(page.get_by_role('heading', name='Бренды', exact=True)).to_be_visible()
    expect(page.get_by_role('dialog', name='Меню', exact=True)).not_to_be_visible()

    # Full-page screenshots after all reveal sections have entered the viewport.
    for width, name in [(1440, 'desktop'), (390, 'mobile')]:
        page.set_viewport_size({'width': width, 'height': 1000 if width == 1440 else 844})
        visit('/')
        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        page.wait_for_timeout(450)
        for position in range(0, page.evaluate('document.body.scrollHeight'), 500):
            page.evaluate('(position) => window.scrollTo(0, position)', position)
            page.wait_for_timeout(100)
        page.evaluate('window.scrollTo(0, 0)')
        page.wait_for_timeout(500)
        page.screenshot(path=str(artifacts / f'bigben-home-{name}.png'), full_page=True)
    assert not errors, errors
    print('PASS: shopping, price recalculation, undo, reload persistence, failed checkout retains cart and retries, PostgreSQL order and request submission, product gallery, search, mobile menu, no JavaScript errors.')
    browser.close()

# Cloud Chromium blocks file:// by managed policy. Test the identical exported
# standalone file via HTTP, with its explicit local-only mode and no API calls.
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    page = browser.new_page(viewport={'width': 390, 'height': 844})
    file_errors = []
    page.on('pageerror', lambda error: file_errors.append(str(error)))
    unexpected_api = []
    page.route('**/api/**', lambda route: (unexpected_api.append(route.request.url), route.abort()))
    standalone = base.rstrip('/') + '/bigben-preview.html'
    page.goto(standalone, wait_until='load')
    expect(page.get_by_role('heading', name='Время быть собой.', exact=True)).to_be_visible()
    page.evaluate('location.hash = "/catalog/tissot-prx"')
    page.get_by_role('button', name='Добавить в корзину').click()
    page.evaluate('location.hash = "/checkout"')
    page.get_by_label('Имя', exact=True).fill('Офлайн тест')
    page.get_by_label('Телефон', exact=True).fill('+79990000000')
    page.get_by_label('Электронная почта', exact=True).fill('offline-test@example.com')
    page.locator('input[name=consent]').check()
    page.get_by_role('button', name='Создать демозаказ').click()
    expect(page.get_by_role('heading', name='Ваш выбор сохранён')).to_be_visible()
    assert page.evaluate('JSON.parse(localStorage.getItem("bigben-orders"))[0].total') == 79900
    assert not file_errors, file_errors
    assert not unexpected_api, unexpected_api
    browser.close()
print('PASS: exported standalone HTML completes local-only checkout without any API calls (tested via HTTP; file:// blocked by cloud browser policy).')
