import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_urumqi_sketch_map import haversine_km, main, project


class GenerateUrumqiSketchMapTests(unittest.TestCase):
    def test_haversine_same_point(self) -> None:
        self.assertEqual(haversine_km(43.8256, 87.6168, 43.8256, 87.6168), 0)

    def test_project_stays_in_canvas(self) -> None:
        bounds = {"min_lat": 42.0, "max_lat": 49.0, "min_lon": 81.0, "max_lon": 90.0}
        x, y = project(87.6168, 43.8256, bounds)
        self.assertGreaterEqual(x, 0)
        self.assertLessEqual(x, 1000)
        self.assertGreaterEqual(y, 0)
        self.assertLessEqual(y, 760)

    def test_main_generates_html(self) -> None:
        main()
        output = (
            Path(__file__).resolve().parents[1]
            / "outputs"
            / "Trip_Sketch_Map_Urumqi_Xinjiang.html"
        )
        self.assertTrue(output.exists())
        content = output.read_text(encoding="utf-8")
        self.assertIn("新疆周边手绘互动关系图", content)
        self.assertIn("手绘互动关系图", content)
        self.assertIn("赛里木湖", content)


if __name__ == "__main__":
    unittest.main()
