import unittest
from unittest.mock import patch
from consol import ConsoLogger

class TestConsoLogger(unittest.TestCase):
    def test_estimate_required_battery(self):
        logger = ConsoLogger(battery_voltage=3.7, safety_margin=1.2, target_days=1)
        avg_power = 100
        # Expected: (100mW * 24h * 1 day / 3.7V) * 1.2 safety_margin = 778.378... mAh
<<<<<<< HEAD
        self.assertAlmostEqual(
            logger.estimate_required_battery(avg_power), 778.378, places=3
        )
=======
        self.assertAlmostEqual(logger.estimate_required_battery(avg_power), 778.378, places=3)
>>>>>>> 4254174d6031d65239b91694ba749050d87bcf21

    def test_estimate_autonomy(self):
        logger = ConsoLogger()
        logger.avg_current_kalman = 100
        battery_capacity_mah = 4000
        expected_autonomy_days = (battery_capacity_mah / logger.avg_current_kalman) / 24
<<<<<<< HEAD
        self.assertAlmostEqual(
            logger.estimate_autonomy(battery_capacity_mah), expected_autonomy_days
        )
=======
        self.assertAlmostEqual(logger.estimate_autonomy(battery_capacity_mah), expected_autonomy_days)
>>>>>>> 4254174d6031d65239b91694ba749050d87bcf21

    def test_check_thresholds(self):
        logger = ConsoLogger(voltage_min=4.0, voltage_max=6.0, current_max=500)
        logger.voltages_kalman = [3.5]
        logger.currents_kalman = [550]
        alerts = logger.check_thresholds()
        # Expect one voltage alert and one current alert
        self.assertEqual(len(alerts), 2)

<<<<<<< HEAD
    @patch("serial.Serial")
    def test_run_without_data(self, mock_serial):
        # Mock the serial port to avoid hardware errors
        mock_serial.return_value.readline.return_value = b""  # Simulate no data
        logger = ConsoLogger(duration=1)  # Use a short duration for the test
        logger.run()
        # After running with no data, averages should not be computed
        self.assertFalse(hasattr(logger, "avg_power_raw"))
=======
    @patch('serial.Serial')
    def test_run_without_data(self, mock_serial):
        # Mock the serial port to avoid hardware errors
        mock_serial.return_value.readline.return_value = b'' # Simulate no data
        logger = ConsoLogger(duration=1) # Use a short duration for the test
        logger.run()
        # After running with no data, averages should not be computed
        self.assertFalse(hasattr(logger, 'avg_power_raw'))
>>>>>>> 4254174d6031d65239b91694ba749050d87bcf21

    def test_kalman_filter_initialization(self):
        logger = ConsoLogger()
        self.assertIsNotNone(logger.kf_voltage)
        self.assertIsNotNone(logger.kf_current)
        self.assertIsNotNone(logger.kf_power)
