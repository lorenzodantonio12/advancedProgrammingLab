from nicegui import ui
from pages.dashboard_page import setup_dashboard_page
from pages.rules_page import setup_rules_page


# --- SHARED NAVBAR BETWEEN PAGES ---
def navigation_bar():
    with ui.header().classes('w-full justify-between items-center bg-slate-900 text-white p-4'):
        ui.label('SpaceY - Mars Automation').classes('text-2xl font-bold')
        with ui.row().classes('gap-6'):
            ui.link('Dashboard', '/').classes('text-gray-300 hover:text-white')
            ui.link('Rules Engine', '/rules').classes('text-gray-300 hover:text-white')


setup_dashboard_page(navigation_bar)
setup_rules_page(navigation_bar)

ui.run(host='0.0.0.0', port=8081, reload=True, title="Mars Control")