import unittest

from main import main


class TestMain(unittest.TestCase):
    def test_main(self):
        main(None)


if __name__ == "__main__":
    unittest.main()
