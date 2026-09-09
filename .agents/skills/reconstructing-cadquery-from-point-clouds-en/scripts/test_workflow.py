"""Self-contained input/measurement regressions; synthetic CAD is a test, not a reconstructor."""
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import unittest
import numpy as np
from plyfile import PlyData, PlyElement
from inspect_cloud import read_cloud, sha256
from verify_surface import step_distances, triangle_distances

HERE = Path(__file__).resolve().parent


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.points = np.array([[0, 0, 0], [1.25, 0, 0], [0, 2.5, 0], [0, 0, -3.75], [0, 0, 0]])

    def run_script(self, name, *args, code=0):
        result = subprocess.run([sys.executable, str(HERE / name), *map(str, args)],
                                cwd=self.root, capture_output=True, text=True,
                                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.assertEqual(result.returncode, code, result.stdout+result.stderr)
        return result

    def write_ply(self, path, text, order="<"):
        # Deliberately non-XYZ property order, plus color and faces to ignore.
        vertices = np.empty(len(self.points), dtype=[("z", "f8"), ("red", "u1"), ("x", "f8"), ("y", "f8")])
        for i, name in enumerate("xyz"):
            vertices[name] = self.points[:, i]
        vertices["red"] = 128
        faces = np.array([([0, 1, 2],)], dtype=[("vertex_indices", "i4", (3,))])
        PlyData([PlyElement.describe(vertices, "vertex"), PlyElement.describe(faces, "face")],
                text=text, byte_order=order).write(str(path))

    def test_all_input_encodings_preserve_points_and_faces_are_ignored(self):
        np.save(self.root / "cloud.npy", self.points)
        np.savetxt(self.root / "cloud.xyz", self.points, fmt="%.17e")
        np.savetxt(self.root / "cloud.csv", self.points, delimiter=",")
        (self.root / "cloud.txt").write_text(repr(self.points.tolist()))
        (self.root / "cloud.json").write_text(json.dumps(self.points.tolist()))
        for name, text, order in [("ascii.ply", True, "<"), ("little.ply", False, "<"), ("big.ply", False, ">")]:
            self.write_ply(self.root / name, text, order)
        for path in self.root.iterdir():
            with self.subTest(format=path.name):
                before = sha256(path)
                points, info = read_cloud(path)
                np.testing.assert_array_equal(points, self.points)
                self.assertEqual(sha256(path), before)
                self.assertEqual(info["excluded_count"], 0)
                if path.suffix == ".ply":
                    self.assertEqual(info["ignored_elements"], {"face": 1})
                    self.assertEqual(info["ignored_vertex_properties"], ["red"])

    def test_extra_columns_require_explicit_selection(self):
        path = self.root / "cloud.npy"
        np.save(path, np.column_stack([np.ones(len(self.points)), self.points]))
        with self.assertRaises(ValueError):
            read_cloud(path)
        np.testing.assert_array_equal(read_cloud(path, [1, 2, 3])[0], self.points)
        for columns in [[1, 1, 2], [-1, 1, 2], [1, 2, 4]]:
            with self.assertRaises(ValueError):
                read_cloud(path, columns)

    def test_bad_arrays_and_nonfinite_values_are_rejected(self):
        for data in [np.empty((0, 3)), np.zeros((3, 5)), np.zeros((3, 3), dtype=complex),
                     np.array([[1, 2, None]], dtype=object), np.array([[1, 2, np.nan]]),
                     np.array([[1, 2, np.inf]]), np.array([["1", "2", "3"]])]:
            with self.subTest(dtype=str(data.dtype), shape=data.shape):
                path = self.root / "bad.npy"
                np.save(path, data)
                with self.assertRaises(ValueError):
                    read_cloud(path)

    def test_bad_text_cannot_execute_or_silently_truncate(self):
        for text in ["", "[[1,2,3], ...]", "[[1,2,3]", "[[1,2,3], [4,5]]", "1 2 nan",
                     "1,,2,3", "1,2,3,", "[100 tokens truncated]",
                     "__import__('pathlib').Path('owned').touch()"]:
            path = self.root / "bad.txt"
            path.write_text(text)
            with self.subTest(text=text), self.assertRaises((ValueError, SyntaxError)):
                read_cloud(path)
        self.assertFalse((self.root / "owned").exists())

    def test_missing_ply_coordinates_are_rejected(self):
        path = self.root / "bad.ply"
        vertices = np.zeros(3, dtype=[("x", "f8"), ("y", "f8")])
        PlyData([PlyElement.describe(vertices, "vertex")], text=True).write(str(path))
        with self.assertRaises(ValueError):
            read_cloud(path)

    def test_reader_cli_report_indices_plot_and_overwrite_protection(self):
        path = self.root / "cloud.npy"
        np.save(path, self.points)
        out = self.root / "analysis"
        self.run_script("inspect_cloud.py", path, "--out", out, "--unit", "mm", "--unit-status", "assumed")
        report = json.loads((out / "input_report.json").read_text())
        self.assertEqual(report["duplicate_count"], 1)
        self.assertEqual(report["unit_status"], "assumed")
        np.testing.assert_array_equal(np.load(out / "points.npy"), self.points)
        np.testing.assert_array_equal(np.load(out / "source_indices.npy"), np.arange(5))
        self.assertGreater((out / "projections.png").stat().st_size, 1000)
        before = sha256(out / "points.npy")
        self.run_script("inspect_cloud.py", path, "--out", out, code=2)
        self.assertEqual(sha256(out / "points.npy"), before)
        self.run_script("inspect_cloud.py", path, "--out", self.root / "invalid-units", "--unit", "mm", code=2)

    def test_cad_surface_distances_and_failed_acceptance(self):
        import cadquery as cq
        # Explicit feature sequence, independent of scan inputs.
        blank = cq.Workplane("XY").placeSketch(cq.Sketch().rect(10, 10)).extrude(10)
        rounded = blank.edges("|Z").fillet(.5)
        model = rounded.faces(">Z").edges().chamfer(.2)
        self.assertTrue(model.val().isValid())
        self.assertEqual(model.solids().size(), 1)
        step, stl = self.root / "part.step", self.root / "part.stl"
        cq.exporters.export(model, str(step))
        cq.exporters.export(model, str(stl), tolerance=.002, angularTolerance=.05)
        points = np.array([[0, 0, 5], [0, 0, 10], [0, 0, 10.25], [6, 0, 5]], dtype=float)
        expected = [5, 0, .25, 1]  # Interior point must NOT get a zero surface distance.
        np.testing.assert_allclose(triangle_distances(points, stl)[0], expected, atol=1e-6)
        np.testing.assert_allclose(step_distances(points, step), expected, atol=1e-7)
        np.save(self.root / "points.npy", points)
        np.save(self.root / "indices.npy", np.array([20, 1, 4, 99]))
        base = ["--points", self.root / "points.npy", "--source-indices", self.root / "indices.npy",
                "--mesh", stl, "--step", step, "--exact-worst", 4, "--require-within-fraction", 1]
        self.run_script("verify_surface.py", *base, "--out", self.root / "fail", "--threshold", .1, code=1)
        failed = json.loads((self.root / "fail/verification.json").read_text())
        self.assertFalse(failed["criterion_passed"])
        self.assertEqual(failed["within_count"], 1)
        self.assertEqual(failed["worst_source_indices"][0], 20)
        self.assertEqual(failed["step_face_crosscheck"]["count"], 4)
        self.run_script("verify_surface.py", *base, "--out", self.root / "pass", "--threshold", 5.1)
        self.assertTrue(json.loads((self.root / "pass/verification.json").read_text())["criterion_passed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
