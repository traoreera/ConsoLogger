import threading

import flet as ft
from flet import Colors as colors

from consol import ConsoLogger

"""
Analyseur de Consommation Électrique

Ce programme est un outil de diagnostic et d'analyse des consommations
électriques. Il lit les données de l'INA219 et les enregistre dans un fichier
CSV. Il est possible de configurer le port série, le baudrate, la durée
d'enregistrement, le fichier CSV et le fichier image.

Les données enregistrées sont :

- la tension de charge
- le courant
- la puissance

Les données sont filtrées avec un filtre de Kalman pour réduire les bruits.

L'outil permet également de faire des prévisions sur la consommation
électrique en fonction de la moyenne des données enregistrées.

"""


class AnalyseurConsommationApp:
    def __init__(self, page: ft.Page = None):
        # Champs de configuration
        self.page = page
        self.port_input = ft.TextField(label="Port série", value="COM3", width=300)
        self.baudrate_input = ft.TextField(label="Baudrate", value="9600", width=300)
        self.duration_input = ft.TextField(
            label="Durée d'enregistrement (s)", value="10", width=300
        )
        self.csv_file_input = ft.TextField(
            label="Nom du fichier CSV", value="mesures.csv", width=300
        )
        self.img_file_input = ft.TextField(
            label="Nom de l'image de la courbe", value="courbe.png", width=300
        )
        self.battery_voltage_input = ft.TextField(
            label="Tension batterie (V)", value="12.0", width=300
        )
        self.safety_margin_input = ft.TextField(
            label="Marge de sécurité (float )", value="20", width=300
        )
        self.target_days_input = ft.TextField(
            label="Jours d'autonomie cible", value="2", width=300
        )

        # Résultat et Image
        self.result_text = ft.Text(value="Résultat non disponible", selectable=True)
        self.image_display = ft.Image(
            src="", width=600, height=400, fit=ft.ImageFit.CONTAIN, visible=False
        )

        # Bouton
        self.config_button = ft.ElevatedButton(
            "Démarrer la mesure", on_click=self.start_measurement
        )
        # progress bar
        self.progress = ft.ProgressBar(width=400, visible=False)
        # result text
        self.estimation_results = ft.Text(
            size=14, expand=True, text_align=ft.TextAlign.LEFT
        )

    def build(
        self,
    ):
        self.page.title = "🔋 Analyseur de Consommation Électrique"
        self.page.scroll = "AUTO"
        self.page.theme_mode = ft.ThemeMode.SYSTEM  # 🌙 Thème sombre activé

        # Colonne gauche (formulaire config)
        left_column = ft.Column(
            controls=[
                ft.Column(
                    [
                        ft.Container(
                            ft.Column(
                                [
                                    ft.Text(
                                        "🔌 Configuration de Consommation Énergétique",
                                        size=24,
                                        weight="bold",
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                    self.port_input,
                                    self.baudrate_input,
                                    self.duration_input,
                                    self.csv_file_input,
                                    self.img_file_input,
                                    self.battery_voltage_input,
                                    self.safety_margin_input,
                                    self.target_days_input,
                                    self.config_button,
                                ],
                                width=320,
                            ),
                            padding=20,
                            border_radius=10,
                            border=ft.border.all(2, colors.BLUE_300),
                            width=320,
                        ),
                    ],
                    expand=True,
                )
            ],
            spacing=5,
            width=320,
            # border=ft.border.all(2, colors.BLUE_300),
        )

        # Colonne droite (résultats + image)
        right_column = ft.Container(
            ft.Column(
                controls=[
                    ft.Text("📊 Résultats", size=22, weight="bold"),
                    self.progress,
                    self.result_text,
                    self.estimation_results,
                    self.image_display,
                ],
            ),
            padding=20,
            border_radius=10,
            border=ft.border.all(2, colors.GREEN_300),
            visible=True,
            expand=True,
            alignment=ft.alignment.center,
            margin=ft.margin.only(left=20),
        )

        # Affichage final avec 2 colonnes
        self.page.add(
            ft.Row(
                controls=[left_column, right_column],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                expand=True,
            )
        )

    def start_measurement(self, e):

        try:
            self.port = self.port_input.value
            self.baudrate = int(self.baudrate_input.value)
            self.duration = int(self.duration_input.value)
            self.csv_file = self.csv_file_input.value
            self.img_file = self.img_file_input.value
            self.battery_voltage = float(self.battery_voltage_input.value)
            self.safety_margin = float(self.safety_margin_input.value)
            self.target_days = int(self.target_days_input.value)
            if self.duration <= 0 or self.target_days <= 0:
                raise ValueError("Durée et jours cibles doivent être positifs")
        except ValueError as ve:
            self.result_text.value = f"❌ Erreur de configuration: {str(ve)}"
            self.result_text.update()
            return
        self.result_text.value = "⏳ Mesure en cours..."
        self.progress.visible = True
        self.image_display.visible = False  # cacher l’image au départ
        self.result_text.update()
        self.progress.update()

        def run_messure():
            try:
                logger_instance = ConsoLogger(
                    port=self.port,
                    baudrate=self.baudrate,
                    duration=self.duration,
                    csv_file=self.csv_file,
                    img_file=self.img_file,
                    battery_voltage=self.battery_voltage,
                    safety_margin=self.safety_margin,
                    target_days=self.target_days,
                )
                margin_percent = self.safety_margin
                logger_instance.run()
                self.estimation_results.value = (
                    f"🔋 Tension batterie : {logger_instance.battery_voltage:.2f} V"
                    f"\n📆 Jours cibles : {logger_instance.target_days} j"
                    f"\n⚠️ Marge de sécurité : {logger_instance.safety_margin:.2f} ({margin_percent}%)"
                    f"\n📉 Moyenne puissance brute : {logger_instance.avg_power_raw:.2f} mW"
                    f"\n📉 Moyenne puissance filtrée (Kalman) : {logger_instance.avg_power_kalman:.2f} mW"
                    f"\n🕒 Conso brute sur 24h : {logger_instance.wh_raw:.2f} Wh / {logger_instance.mah_raw:.0f} mAh"
                    f"\n🕒 Conso filtrée sur 24h : {logger_instance.wh_kal:.2f} Wh / {logger_instance.mah_kal:.0f} mAh"
                    f"\n📦 Batterie brute recommandée (marge incluse) : {logger_instance.battery_raw:.0f} mAh"
                    f"\n📦 Batterie filtrée recommandée (marge incluse) : {logger_instance.battery_kal:.0f} mAh"
                    f"\nbaterie estimate autonomie brute  : {logger_instance.estimate_autonomy(logger_instance.battery_raw)} jrs"
                    f"\nbaterie estimate autonomie kalman : {logger_instance.estimate_autonomy(logger_instance.battery_kal)} jrs"
                )
                self.result_text.value = f"✅ Mesure terminée sur une durée d'acquisition  : {logger_instance.duration_hours} ! heures"
                self.image_display.src = ""

                self.image_display.update()
                self.image_display.visible = True  # afficher l’image
                self.progress.visible = False
                self.estimation_results.update()
                self.result_text.update()
                self.image_display.src = self.img_file
                self.image_display.update()
            except Exception as e:
                self.result_text.value = f"❌ Erreur de mesure: {str(e)}"
                self.progress.visible = False
                self.estimation_results.update()
                self.result_text.update()

            finally:
                self.progress.visible = False
                self.estimation_results.update()
                self.result_text.update()
                self.toggle_inputs(True)

        threading.Thread(target=run_messure, daemon=True).start()

    def toggle_inputs(self, enabled):
        for field in [
            self.port_input,
            self.baudrate_input,
            self.duration_input,
            self.csv_file_input,
            self.img_file_input,
            self.battery_voltage_input,
            self.safety_margin_input,
            self.target_days_input,
            self.config_button,
        ]:
            field.disabled = not enabled
        self.page.update()


# Point d’entrée Flet
def main(page: ft.Page):
    app = AnalyseurConsommationApp(page)
    app.build()


if __name__ == "__main__":
    try:
        ft.app(target=main)
    except Exception as e:
        print(f"Erreur lors du démarrage de l'application : {e}")
        raise e
# This code is part of the main application logic for the electrical consumption analyzer.
# It initializes the Flet page, sets up the UI components, and handles the measurement logic.
# The ConsoLogger class is used to handle the actual data logging and analysis.
