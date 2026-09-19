import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('experiment', ROOT / 'scripts/experiment.py')
experiment = importlib.util.module_from_spec(spec)
spec.loader.exec_module(experiment)


class ExperimentTests(unittest.TestCase):
    def test_known_constant_samples(self):
        results = experiment.compute({1: [10, 10], 2: [5, 5]})
        self.assertEqual(results[1]['speedup'], 2)
        self.assertEqual(results[1]['efficiency'], 1)
        self.assertEqual(results[1]['low'], 5)
        self.assertEqual(results[1]['high'], 5)

    def test_reject_nonfinite_and_duplicate(self):
        parent = ROOT / '.work/tests'
        parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as folder:
            path = Path(folder) / 'bad.csv'
            for rows in ['1,1,nan\n', '1,1,0\n', '1,1,2\n1,1,3\n']:
                path.write_text('workers,run,seconds\n' + rows)
                with self.assertRaises(ValueError):
                    experiment.read_data(path)


if __name__ == '__main__':
    unittest.main()
