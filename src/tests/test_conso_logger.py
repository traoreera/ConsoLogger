import unittest
from consol import ConsoLogger


class TestConsoLogger(unittest.TestCase):
    def test_init(self):
        logger = ConsoLogger()
        self.assertIsNotNone(logger)

    def test_estimate_required_battery(self):
        logger = ConsoLogger()
        avg_power = 10
        self.assertEqual(logger.estimate_required_battery(avg_power), 240)

    def test_estimate_autonomy(self):
        logger = ConsoLogger()
        battery_capacity_mah = 1000
        self.assertEqual(logger.estimate_autonomy(battery_capacity_mah), 4)

    def test_check_thresholds(self):
        logger = ConsoLogger()
        logger.voltages_kalman = [5.0, 5.1, 5.2]
        logger.currents_kalman = [100, 110, 120]
        alerts = logger.check_thresholds()
        self.assertEqual(len(alerts), 0)

    def test_predict_next(self):
        logger = ConsoLogger()
        logger.voltages_kalman = [5.0, 5.1, 5.2]
        logger.currents_kalman = [100, 110, 120]
        predictions = logger.predict_next()
        self.assertEqual(len(predictions), 3)


if __name__ == "__main__":
    unittest.main()
