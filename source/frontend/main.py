import asyncio
import threading
from nicegui import ui, app

# Import delle setup function delle pagine
from pages.dashboard_page import setup_dashboard_page
from pages.rules_page import setup_rules_page

# Import del consumatore ActiveMQ da api.py
from services.api import start_telemetry_consumer

# --- SHARED NAVBAR BETWEEN PAGES ---
def navigation_bar():
    with ui.header().classes('w-full justify-between items-center bg-slate-900 text-white p-4 shadow-md'):
        ui.label('SpaceY - Mars Automation').classes('text-2xl font-bold tracking-widest')
        with ui.row().classes('gap-6'):
            ui.link('Dashboard', '/').classes('text-lg font-semibold text-gray-300 hover:text-white transition')
            ui.link('Rules Engine', '/rules').classes('text-lg font-semibold text-gray-300 hover:text-white transition')

# Inizializza le pagine passando la navbar
setup_dashboard_page(navigation_bar)
setup_rules_page(navigation_bar)

# --- AVVIO LOGICA MULTI-THREAD (ActiveMQ + NiceGUI) ---
def start_background_workers():
    """
    Questa funzione viene chiamata SOLO quando NiceGUI è completamente avviato.
    Ci garantisce di usare il loop asincrono corretto (quello di Uvicorn/NiceGUI).
    """
    try:
        # Recuperiamo il loop asincrono ATTIVO
        loop = asyncio.get_running_loop()
        
        # Avviamo il thread per ActiveMQ passandogli il loop "vivo"
        t = threading.Thread(
            target=start_telemetry_consumer, 
            args=(loop,), 
            daemon=True
        )
        t.start()
        print("🚀 [SISTEMA] Thread di ascolto ActiveMQ avviato con successo sul loop principale.", flush=True)
    except Exception as e:
        print(f"❌ [ERRORE FATALE] Impossibile avviare i worker: {e}", flush=True)

# Registriamo la funzione all'avvio dell'applicazione
app.on_startup(start_background_workers)

# Avvio del server NiceGUI
ui.run(
    host='0.0.0.0', 
    port=8081, 
    reload=False, # Fondamentale tenere False con Docker e Thread per evitare task zombie
    title="Mars Control System"
)