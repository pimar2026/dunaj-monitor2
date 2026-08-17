from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivy.clock import Clock
import urllib.request
import re

try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

class DunajMonitorScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.stations = ["Devín", "Bratislava", "Medveďov"]
        self.selected_station = "Bratislava"
        self.warning_limit = None
        
        layout = MDBoxLayout(orientation='vertical', padding=20, spacing=15)
        
        title = MDLabel(
            text="Sledovanie toku Dunaj",
            font_style="H4",
            halign="center",
            size_hint_y=None,
            height=40
        )
        layout.add_widget(title)

        self.btn_select_station = MDFlatButton(
            text=f"Stanica: {self.selected_station} - Dunaj",
            pos_hint={'center_x': 0.5},
            font_style="Button"
        )
        self.btn_select_station.bind(on_release=self.open_station_menu)
        layout.add_widget(self.btn_select_station)

        self.card = MDCard(
            orientation='vertical',
            padding=20,
            spacing=10,
            size_hint=(1, None),
            height=180,
            elevation=4
        )
        
        self.station_label = MDLabel(
            text=f"Stanica: {self.selected_station} - Dunaj", 
            font_style="Subtitle1"
        )
        self.level_label = MDLabel(text="Výška hladiny: načítavam...", font_style="H5")
        self.temp_label = MDLabel(text="Teplota vody: načítavam...", font_style="Body1")
        self.status_label = MDLabel(text="Stav: --", font_style="Caption")

        self.card.add_widget(self.station_label)
        self.card.add_widget(self.level_label)
        self.card.add_widget(self.temp_label)
        self.card.add_widget(self.status_label)
        
        layout.add_widget(self.card)

        self.limit_input = MDTextField(
            hint_text="Výstražný limit hladiny (cm)",
            input_filter="int",
            size_hint_x=0.8,
            pos_hint={'center_x': 0.5}
        )
        self.limit_input.bind(text=self.on_limit_change)
        layout.add_widget(self.limit_input)

        btn_refresh = MDRaisedButton(
            text="Obnoviť dáta",
            pos_hint={'center_x': 0.5},
            on_release=lambda x: self.fetch_data()
        )
        layout.add_widget(btn_refresh)
        
        self.add_widget(layout)
        
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": station,
                "on_release": lambda x=station: self.set_station(x),
            } for station in self.stations
        ]
        self.menu = MDDropdownMenu(
            caller=self.btn_select_station,
            items=menu_items,
            width_mult=4,
        )

        Clock.schedule_once(lambda dt: self.fetch_data(), 1)

    def open_station_menu(self, instance):
        self.menu.open()

    def set_station(self, station_name):
        self.selected_station = station_name
        self.btn_select_station.text = f"Stanica: {self.selected_station} - Dunaj"
        self.station_label.text = f"Stanica: {self.selected_station} - Dunaj"
        self.menu.dismiss()
        self.fetch_data()

    def on_limit_change(self, instance, text):
        if text.strip().isdigit():
            self.warning_limit = int(text.strip())
        else:
            self.warning_limit = None

    def send_notification(self, current_level):
        msg = f"Hladina na stanici {self.selected_station} dosiahla {current_level} cm! (Limit: {self.warning_limit} cm)"
        if PLYER_AVAILABLE:
            try:
                notification.notify(
                    title="⚠️ Výstraha - Vysoká hladina Dunaja",
                    message=msg,
                    app_name="Dunaj Monitor",
                    timeout=10
                )
            except Exception as e:
                print(f"Chyba: {e}")

    def fetch_data(self):
        self.status_label.text = "Stav: Aktualizujem..."
        try:
            url = "https://www.shmu.sk/sk/?page=1&id=ran_sprav"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            html = urllib.request.urlopen(req).read().decode('utf-8')

            pattern = re.escape(self.selected_station) + r'\s*-\s*Dunaj.*?<td>(\d+)</td>.*?<td>([\d\.,]+)</td>'
            match = re.search(pattern, html, re.DOTALL)

            if match:
                hladina = int(match.group(1))
                teplota = match.group(2)
                
                self.level_label.text = f"Výška hladiny: {hladina} cm"
                self.temp_label.text = f"Teplota vody: {teplota} °C"
                self.status_label.text = "Stav: Dáta sú aktuálne"

                if self.warning_limit is not None and hladina >= self.warning_limit:
                    self.send_notification(hladina)
            else:
                self.level_label.text = "Výška hladiny: N/A"
                self.temp_label.text = "Teplota vody: N/A"
                self.status_label.text = "Stav: Nepodarilo sa spracovať dáta"
        except Exception:
            self.status_label.text = "Stav: Chyba pripojenia"

class DunajApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        return DunajMonitorScreen()

if __name__ == '__main__':
    DunajApp().run()
