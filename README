# 🔋 Analyseur de Consommation Électrique (Electrical Consumption Analyzer)

This project provides a complete system for monitoring, analyzing, and diagnosing the power consumption of electronic devices. It consists of an Arduino-based hardware component for data acquisition and a Python-based desktop application for visualization and analysis.

The application's user interface is in French.

<!-- Add a screenshot of the application here -->
<!-- ![Application Screenshot](path/to/screenshot.png) -->

## Features

- **Real-time Data Acquisition**: Reads voltage, current, and power data from an INA219 sensor via a serial connection.
- **Data Smoothing**: Applies a Kalman filter to the raw sensor data to reduce noise and improve accuracy.
- **Rich Data Analysis**:
    - Calculates average power and current consumption.
    - Estimates total consumption over a 24-hour period (in Wh and mAh).
    - Recommends a suitable battery capacity based on desired autonomy and a safety margin.
    - Provides detailed statistics (min, max, median, standard deviation) for all metrics.
    - Predicts short-term future consumption trends.
- **Data Export**:
    - Saves all raw and filtered measurements to a CSV file.
    - Generates a summary text file with key results and alerts.
- **Visualization**:
    - Plots graphs of voltage, current, and power over time.
    - Displays both raw and filtered data for comparison.
    - Saves the plots as a PNG image.
- **User-Friendly GUI**: A desktop application built with Flet allows for easy configuration and displays results in a clear, organized manner.

## Hardware Requirements

- **Microcontroller**: An Arduino board (e.g., Arduino Uno, Nano).
- **Sensor**: An Adafruit INA219 current sensor breakout board.
- **Display (Optional)**: A 20x4 I2C LCD screen for local display of readings.
- **Wiring**: Jumper wires to connect the components.

## Arduino Setup

1.  **Install Arduino IDE**: If you don't have it, download and install the [Arduino IDE](https://www.arduino.cc/en/software).
2.  **Install Libraries**: In the Arduino IDE, go to **Sketch > Include Library > Manage Libraries...** and install the following libraries:
    *   `Adafruit INA219` by Adafruit
    *   `LiquidCrystal I2C` by Frank de Brabander
3.  **Connect Hardware**: Wire the INA219 sensor and the optional LCD to your Arduino according to their documentation.
4.  **Upload the Sketch**:
    *   Open the `arduino/main.ino` file in the Arduino IDE.
    *   Select your board and port from the **Tools** menu.
    *   Click the "Upload" button.

## Software & Installation

This project uses [Poetry](https://python-poetry.org/) for dependency management.

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```
2.  **Install Poetry**: Follow the instructions on the [official Poetry website](https://python-poetry.org/docs/#installation) to install it.
3.  **Install Dependencies**: Run the following command in the project's root directory. This will create a virtual environment and install all necessary packages (`flet`, `pyserial`, `numpy`, `matplotlib`, etc.).
    ```bash
    poetry install
    ```

## Usage

1.  Connect the Arduino to your computer via USB.
2.  Activate the Poetry virtual environment:
    ```bash
    poetry shell
    ```
3.  Run the application:
    ```bash
    python src/main.py
    ```
4.  The "Analyseur de Consommation Électrique" window will open. Configure the settings and click "Démarrer la mesure" to begin.

## Application UI

The user interface allows you to configure the following parameters:

| Field | Description | Default |
| --- | --- | --- |
| **Port série** | The serial port your Arduino is connected to (e.g., `COM3` on Windows, `/dev/ttyUSB0` on Linux). | `COM3` |
| **Baudrate** | The serial communication speed. Must match the value in the Arduino sketch. | `9600` |
| **Durée d'enregistrement (s)** | The number of seconds to record data for. | `10` |
| **Nom du fichier CSV** | The name of the CSV file to save the detailed measurements. | `mesures.csv` |
| **Nom de l'image de la courbe**| The name of the PNG file to save the generated graph. | `courbe.png` |
| **Tension batterie (V)** | The voltage of the battery you plan to use (e.g., 3.7V for LiPo, 12V for lead-acid). | `12.0` |
| **Marge de sécurité (float)** | The safety margin percentage to add to the battery capacity calculation. | `20` |
| **Jours d'autonomie cible** | The desired number of days the device should run on the battery. | `2` |

## Outputs

The application generates three files:

1.  **CSV File** (`mesures.csv` by default): Contains the timestamped raw and Kalman-filtered data for voltage, current, and power.
2.  **Image File** (`courbe.png` by default): A PNG image containing plots of the measurements over time.
3.  **Results File** (`mesures_results.txt` by default): A text file summarizing the analysis, including 24-hour consumption estimates, recommended battery capacity, and statistics.

## Project Structure

```
.
├── arduino/
│   └── main.ino            # Arduino sketch for the INA219 sensor
├── src/
│   ├── main.py             # Main Flet application entry point and UI
│   ├── consol.py           # Core logic for data logging, filtering, and analysis (ConsoLogger class)
│   └── tests/              # Unit tests
├── .gitignore
├── pyproject.toml          # Project metadata and dependencies for Poetry
└── README.md               # This file
```
=======
# ConsoLogger

## Overview

ConsoLogger is a Python-based tool for analyzing and diagnosing electrical consumption. It reads data from the INA219 sensor and records it in a CSV file. The tool provides various features, including Kalman filtering to reduce noise and predictions for future consumption.

## Features

- Serial communication with INA219 sensor
- Data logging to a CSV file
- Kalman filtering for voltage, current, and power
- Statistical analysis of consumption data
- Graph plotting with predicted values
- Battery autonomy estimation

## Installation

1. Clone this repository.
2. Ensure you have Python 3.x installed.
3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Configure the serial port, baud rate, and other parameters in the `ConsoLogger` class or via the Flet UI.
2. Run the main application:
   ```bash
   python src/main.py
   ```
3. Follow on-screen instructions to start measurements and view results.

## Components

- **ConsoLogger**: The main class responsible for reading data, filtering, and analysis.
- **Flet UI**: Provides a graphical interface to configure parameters and view results.
- **Kalman Filter**: Used for smoothing the data.

## Testing

Unit tests are available in the `src/tests` directory. Run tests using:
```bash
python -m unittest discover -s src/tests
```

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.
