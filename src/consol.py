import csv
import time
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import serial
from filterpy.kalman import KalmanFilter


class ConsoLogger:

    def __init__(
        self,
        port="COM12",
        baudrate=9600,
        duration=60,
        csv_file="./data/donnees_conso.csv",
        img_file="./data/courbes_conso.png",
        battery_voltage=3.7,
        safety_margin=1.3,
        target_days=2,
        voltage_max=5.08,
        voltage_min=5.0,
        current_max=1000,
    ):
        self.voltage_min = voltage_min
        self.voltage_max = voltage_max
        self.current_max = current_max
        self.port = port
        self.baudrate = baudrate
        self.duration = duration
        self.csv_file = csv_file
        self.img_file = img_file
        self.battery_voltage = battery_voltage
        self.safety_margin = safety_margin
        self.target_days = target_days
        self.timestamps = []
        self.voltages = []
        self.currents = []
        self.powers = []
        self.voltages_kalman = []
        self.currents_kalman = []
        self.powers_kalman = []
        self.total_energy_mWh_raw = 0
        self.total_charge_mAh_raw = 0
        self.total_energy_mWh_filtered = 0
        self.total_charge_mAh_filtered = 0
        self.stats = {}
        self.setup_kalman_filter()

    def setup_kalman_filter(self):
        def create_filter():
            kf = KalmanFilter(dim_x=2, dim_z=1)
            kf.x = np.array([[0.0], [0.0]])
            kf.F = np.array([[1.0, 1.0], [0.0, 1.0]])
            kf.H = np.array([[1.0, 0.0]])
            kf.P *= 1000.0
            kf.R = 10
            kf.Q = np.eye(2) * 0.001
            return kf

        self.kf_voltage = create_filter()
        self.kf_current = create_filter()
        self.kf_power = create_filter()

    def read_serial_data(self):
        print("⏳ Lecture des données INA219...")
        ser = serial.Serial(self.port, self.baudrate, timeout=1)
        start_time = time.time()

        # Initialiser des listes pour les valeurs supplémentaires
        self.bus_voltages = []
        self.shunt_voltages = []

        try:
            while time.time() - start_time < self.duration:
                line = ser.readline().decode("utf-8").strip()
                try:
                    # Récupérer toutes les valeurs
                    data = list(map(float, line.split(",")))

                    if len(data) < 5:
                        continue  # Ignorer les lignes incomplètes

                    # Extraire toutes les valeurs
                    loadvoltage = data[0]  # Tension de charge
                    current = data[1]  # Courant
                    power = data[2]  # Puissance
                    busvoltage = data[3]  # Tension du bus
                    shuntvoltage = data[4]  # Tension de shunt

                    now = datetime.now()
                    self.timestamps.append(now)
                    self.voltages.append(loadvoltage)
                    self.currents.append(current)
                    self.powers.append(power)
                    self.bus_voltages.append(busvoltage)
                    self.shunt_voltages.append(shuntvoltage)

                    # Filtrage Kalman
                    self.kf_voltage.predict()
                    self.kf_voltage.update(loadvoltage)
                    voltage_k = float(self.kf_voltage.x[0])

                    self.kf_current.predict()
                    self.kf_current.update(current)
                    current_k = float(self.kf_current.x[0])

                    self.kf_power.predict()
                    self.kf_power.update(power)
                    power_k = float(self.kf_power.x[0])

                    self.voltages_kalman.append(voltage_k)
                    self.currents_kalman.append(current_k)
                    self.powers_kalman.append(power_k)

                    # Calcul de l'énergie et charge accumulées
                    if len(self.timestamps) > 1:
                        delta_t = (
                            self.timestamps[-1] - self.timestamps[-2]
                        ).total_seconds() / 3600

                        self.total_energy_mWh_raw += power * delta_t
                        self.total_energy_mWh_filtered += power_k * delta_t
                        self.total_charge_mAh_raw += current * delta_t
                        self.total_charge_mAh_filtered += current_k * delta_t

                    print(
                        f"{now.strftime('%H:%M:%S')} | "
                        f"Load: {loadvoltage:.2f}V | "
                        f"Bus: {busvoltage:.2f}V | "
                        f"Shunt: {shuntvoltage:.2f}mV | "
                        f"Current: {current:.2f}mA | "
                        f"Power: {power:.2f}mW"
                    )
                except ValueError:
                    continue
        finally:
            ser.close()

    def compute_averages(self):
        if not self.powers:
            print("❌ Aucune donnée reçue.")
            return False
        self.avg_power_raw = sum(self.powers) / len(self.powers)
        self.avg_current_raw = sum(self.currents) / len(self.currents)
        self.avg_power_kalman = sum(self.powers_kalman) / len(self.powers_kalman)
        self.avg_current_kalman = sum(self.currents_kalman) / len(self.currents_kalman)
        return True

    def estimate_24h(self, power_mW):
        # Correction : suppression des doubles affectations
        wh = (power_mW * 24) / 1000  # mW * h / 1000 = Wh
        mah = (wh * 1000) / self.battery_voltage  # Wh * 1000 / V = mAh
        return wh, mah

    def estimate_required_battery(self, avg_power):
        # Calcul plus clair et précis
        wh_per_day = (avg_power * 24) / 1000  # Consommation journalière en Wh
        wh_total = wh_per_day * self.target_days  # Consommation totale sur la période
        mah = (wh_total * 1000) / self.battery_voltage  # Capacité nécessaire en mAh
        return mah * self.safety_margin  # Avec marge de sécurité

    def predict_next(self, n_steps=5):
        predictions = {"voltage": [], "current": [], "power": []}
        for name, series in {
            "voltage": self.voltages_kalman,
            "current": self.currents_kalman,
            "power": self.powers_kalman,
        }.items():
            if len(series) < 2:
                continue
            delta = series[-1] - series[-2]
            last = series[-1]
            predictions[name] = [last + delta * i for i in range(1, n_steps + 1)]
        return predictions

    def export_csv(self):
        with open(self.csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "timestamp",
                    "voltage_V",
                    "current_mA",
                    "power_mW",
                    "voltage_kalman",
                    "current_kalman",
                    "power_kalman",
                ]
            )
            for i in range(len(self.timestamps)):
                writer.writerow(
                    [
                        self.timestamps[i],
                        self.voltages[i],
                        self.currents[i],
                        self.powers[i],
                        self.voltages_kalman[i],
                        self.currents_kalman[i],
                        self.powers_kalman[i],
                    ]
                )
        print(f"✅ Données sauvegardées dans {self.csv_file}")

    def plot_graph(self):
        pred = self.predict_next()
        time_interval = (
            (self.timestamps[-1] - self.timestamps[-2])
            if len(self.timestamps) >= 2
            else 1
        )
        future_times = [
            self.timestamps[-1] + time_interval * (i + 1)
            for i in range(len(pred["voltage"]))
        ]
        plt.figure(figsize=(12, 6))

        def plot_subplot(index, raw, filtered, predicted, title, ylabel, color):
            plt.subplot(3, 1, index)
            plt.plot(
                self.timestamps, raw, label=f"{title} brute", alpha=0.4, linestyle="--"
            )
            plt.plot(
                self.timestamps,
                filtered,
                label=f"{title} filtrée",
                color=color,
                linewidth=2,
            )
            if predicted:
                plt.plot(future_times, predicted, "r--", label="Prédiction")
            plt.ylabel(ylabel)
            plt.grid()
            plt.legend()

        plot_subplot(
            1,
            self.voltages,
            self.voltages_kalman,
            pred["voltage"],
            "Tension",
            "V",
            "blue",
        )
        plot_subplot(
            2,
            self.currents,
            self.currents_kalman,
            pred["current"],
            "Courant",
            "mA",
            "orange",
        )
        plot_subplot(
            3,
            self.powers,
            self.powers_kalman,
            pred["power"],
            "Puissance",
            "mW",
            "green",
        )

        # Utilisation des valeurs calculées dans run() pour la cohérence
        plt.suptitle(
            f"Conso estimée 24h (filtrée) : {self.wh_kal:.2f} Wh / {self.mah_kal:.0f} mAh"
        )
        plt.tight_layout()
        plt.savefig(self.img_file, dpi=150)
        print(f"📈 Graphe sauvegardé dans {self.img_file}")

    def compute_statistics(self):
        """Calcule les statistiques détaillées"""
        if not self.powers:
            return False

        self.stats = {
            "power": {
                "raw": {
                    "min": min(self.powers),
                    "max": max(self.powers),
                    "std": np.std(self.powers),
                    "median": np.median(self.powers),
                },
                "kalman": {
                    "min": min(self.powers_kalman),
                    "max": max(self.powers_kalman),
                    "std": np.std(self.powers_kalman),
                    "median": np.median(self.powers_kalman),
                },
            },
            "current": {
                "raw": {
                    "min": min(self.currents),
                    "max": max(self.currents),
                    "std": np.std(self.currents),
                    "median": np.median(self.currents),
                },
                "kalman": {
                    "min": min(self.currents_kalman),
                    "max": max(self.currents_kalman),
                    "std": np.std(self.currents_kalman),
                    "median": np.median(self.currents_kalman),
                },
            },
            "voltage": {
                "raw": {
                    "min": min(self.voltages),
                    "max": max(self.voltages),
                    "std": np.std(self.voltages),
                    "median": np.median(self.voltages),
                },
                "kalman": {
                    "min": min(self.voltages_kalman),
                    "max": max(self.voltages_kalman),
                    "std": np.std(self.voltages_kalman),
                    "median": np.median(self.voltages_kalman),
                },
            },
        }
        return True

    def save_results(self):
        """Sauvegarde les résultats dans un fichier texte"""
        results_file = self.csv_file.replace(".csv", "_results.txt")

        with open(results_file, "w", encoding="utf-8") as f:
            f.write("====== RÉSULTATS DE L'ANALYSE DE CONSOMMATION ======\n\n")
            f.write(
                f"Date de l'analyse: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            f.write(f"Durée d'acquisition: {self.duration} secondes\n")
            f.write(f"Tension batterie: {self.battery_voltage} V\n")
            f.write(f"Marge de sécurité: {self.safety_margin}\n\n")

            f.write("CONSOMMATION ESTIMÉE SUR 24H:\n")
            f.write(
                f"  - Données brutes: {self.wh_raw:.2f} Wh / {self.mah_raw:.0f} mAh\n"
            )
            f.write(
                f"  - Données filtrées: {self.wh_kal:.2f} Wh / {self.mah_kal:.0f} mAh\n\n"
            )

            f.write("BATTERIE RECOMMANDÉE:\n")
            f.write(f"  - Basée sur les données brutes: {self.battery_raw:.0f} mAh\n")
            f.write(
                f"  - Basée sur les données filtrées: {self.battery_kal:.0f} mAh\n\n"
            )

            f.write("STATISTIQUES:\n")
            f.write(
                f"  - Puissance brute: min={self.stats['power']['raw']['min']:.2f} mW, "
                f"max={self.stats['power']['raw']['max']:.2f} mW, "
                f"std={self.stats['power']['raw']['std']:.2f} mW\n"
            )
            f.write(
                f"  - Puissance filtrée: min={self.stats['power']['kalman']['min']:.2f} mW, "
                f"max={self.stats['power']['kalman']['max']:.2f} mW, "
                f"std={self.stats['power']['kalman']['std']:.2f} mW\n"
            )

            # Ajout des alertes
            alerts = self.check_thresholds()
            if alerts:
                f.write("\nALERTES:\n")
                for alert in alerts:
                    f.write(f"  - {alert}\n")

        print(f"✅ Résultats sauvegardés dans {results_file}")

    def check_thresholds(self):
        """Vérifie les seuils et retourne les alertes"""
        alerts = []

        if self.voltages_kalman:
            last_voltage = self.voltages_kalman[-1]
            if last_voltage < self.voltage_min:
                alerts.append(
                    f"⚠️ Tension basse: {last_voltage:.2f}V < {self.voltage_min}V"
                )
            elif last_voltage > self.voltage_max:
                alerts.append(
                    f"⚠️ Tension élevée: {last_voltage:.2f}V > {self.voltage_max}V"
                )

        if self.currents_kalman:
            last_current = self.currents_kalman[-1]
            if last_current > self.current_max:
                alerts.append(
                    f"⚠️ Courant élevé: {last_current:.2f}mA > {self.current_max}mA"
                )

        return alerts

    def estimate_autonomy(self, battery_capacity_mah):
        """Estime l'autonomie en jours"""
        avg_current = self.avg_current_kalman
        if avg_current > 0:
            autonomy_hours = battery_capacity_mah / avg_current
            return autonomy_hours / 24
        return float("inf")

    def run(self):
        self.read_serial_data()
        if not self.compute_averages():
            return

        # Calcul de la durée réelle d'acquisition en heures
        self.duration_hours = (
            self.timestamps[-1] - self.timestamps[0]
        ).total_seconds() / 3600

        # Méthode 1: Utilisation des données accumulées (plus précise)
        # Conversion mWh -> Wh pour l'énergie
        real_wh_raw = self.total_energy_mWh_raw / 1000
        real_wh_filtered = self.total_energy_mWh_filtered / 1000

        # Extrapolation à 24h
        self.wh_raw = real_wh_raw * (24 / self.duration_hours)
        self.wh_kal = real_wh_filtered * (24 / self.duration_hours)

        # Conversion en mAh
        self.mah_raw = (self.wh_raw * 1000) / self.battery_voltage
        self.mah_kal = (self.wh_kal * 1000) / self.battery_voltage

        # Méthode 2: Utilisation de la puissance moyenne (alternative)
        # wh_raw_alt, mah_raw_alt = self.estimate_24h(self.avg_power_raw)
        # wh_kal_alt, mah_kal_alt = self.estimate_24h(self.avg_power_kalman)

        # Estimation de la batterie requise
        self.battery_raw = self.estimate_required_battery(self.avg_power_raw)
        self.battery_kal = self.estimate_required_battery(self.avg_power_kalman)

        self.export_csv()
        self.plot_graph()

        margin_percent = int(self.safety_margin * 100)
        print("\n====== 🔎 RÉCAPITULATIF DEBUG ======")
        print(f"📏 Durée d'acquisition : {self.duration_hours:.2f} heures")
        print(f"🔋 Tension batterie : {self.battery_voltage:.2f} V")
        print(f"📆 Jours cibles : {self.target_days} j")
        print(f"⚠️ Marge de sécurité : {self.safety_margin:.2f} ({margin_percent}%)")
        print("-----")
        print(f"📉 Moyenne puissance brute : {self.avg_power_raw:.2f} mW")
        print(f"📉 Moyenne puissance filtrée (Kalman) : {self.avg_power_kalman:.2f} mW")
        print("-----")
        print(f"🕒 Conso brute sur 24h : {self.wh_raw:.2f} Wh / {self.mah_raw:.0f} mAh")
        print(
            f"🕒 Conso filtrée sur 24h : {self.wh_kal:.2f} Wh / {self.mah_kal:.0f} mAh"
        )
        print("-----")
        print(
            f"📦 Batterie brute recommandée (marge incluse) : {self.battery_raw:.0f} mAh"
        )
        print(
            f"📦 Batterie filtrée recommandée (marge incluse) : {self.battery_kal:.0f} mAh"
        )
        print("-------------")
        print("=-> estimation de l'autonomie ...")
        print(
            f"baterie estimate autonomie brute  : {self.estimate_autonomy(self.battery_raw)} jrs"
        )
        print(
            f"baterie estimate autonomie kalman : {self.estimate_autonomy(self.battery_kal)} jrs"
        )
        print("-----------------")
        print("calcul statistiques ...")
        self.compute_statistics()
        print(self.stats)
        print("=-> alertes:")
        for alert in self.check_thresholds():
            print(alert)
        print("-------------")
        print("=-> sauvegarde:")
        self.save_results()
        print("====================================\n")
