import asyncio
import threading
from nicegui import ui, app

from pages.dashboard_page import setup_dashboard_page
from pages.rules_page import setup_rules_page

from services.api import start_telemetry_consumer

# --- SHARED NAVBAR BETWEEN PAGES ---
def navigation_bar():
    with ui.header().classes('w-full justify-between items-center bg-slate-900 text-white p-4 shadow-md'):
        ui.label('SpaceY - Mars Automation').classes('text-2xl font-bold tracking-widest')
        with ui.row().classes('gap-6'):
            ui.link('Dashboard', '/').classes('text-lg font-semibold text-gray-300 hover:text-white transition')
            ui.link('Rules Engine', '/rules').classes('text-lg font-semibold text-gray-300 hover:text-white transition')
            

setup_dashboard_page(navigation_bar)
setup_rules_page(navigation_bar)

# --- AVVIO LOGICA MULTI-THREAD (ActiveMQ + NiceGUI) ---
def start_background_workers():
    try:
        loop = asyncio.get_running_loop()
        
        t = threading.Thread(
            target=start_telemetry_consumer, 
            args=(loop,), 
            daemon=True
        )
        t.start()
        print("🚀 [SISTEMA] Thread di ascolto ActiveMQ avviato con successo sul loop principale.", flush=True)
    except Exception as e:
        print(f"❌ [ERRORE FATALE] Impossibile avviare i worker: {e}", flush=True)

app.on_startup(start_background_workers)

app.add_static_files('/assets', './assets')  # Per servire eventuali file statici

# Avvio del server NiceGUI
ui.run(
    host='0.0.0.0', 
    port= 8081, 
    reload= False, # per evitare task zombie
    title= "Mars Control System",
    favicon = './assets/mars.png'
)