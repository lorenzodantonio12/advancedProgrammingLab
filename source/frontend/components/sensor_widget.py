from nicegui import ui

class SensorWidget:
    def __init__(self, name, icon, color):
        # h-40: Più alta per far respirare le 2 righe. justify-evenly: Spazia tutto perfettamente
        with ui.card().classes('p-4 shadow-lg items-center justify-evenly w-40 h-40 flex-col overflow-hidden shrink-0'):
            
            # shrink-0: L'icona mantiene i suoi 36px di grandezza cascasse il mondo
            ui.icon(icon, color=color).classes('text-4xl shrink-0')
            
            # Il testo al centro: va a capo, 2 righe max, se di più si taglia
            ui.label(name).classes('text-xs text-gray-500 uppercase tracking-wider text-center w-full whitespace-normal leading-tight line-clamp-2')
            
            # shrink-0: Anche il numerone in basso non si fa schiacciare
            self.value_label = ui.label('---').classes('text-2xl font-bold text-slate-800 w-full text-center truncate shrink-0')

    def __call__(self, data):
        if data is None:
            self.value_label.set_text('N/A')
            self.value_label.classes(replace='text-gray-400')
        else:
            self.value_label.set_text(str(data))
            self.value_label.classes(replace='text-slate-800')