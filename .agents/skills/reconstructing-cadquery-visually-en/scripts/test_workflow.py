"""Reader/rendering regressions; fixture coordinates test I/O, not reconstruction analysis."""
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

    def test_reader_cli_images_without_feature_statistics_and_overwrite_protection(self):
        path = self.root / "cloud.npy"
        np.save(path, self.points)
        out = self.root / "analysis"
        self.run_script("inspect_cloud.py", path, "--out", out, "--unit", "mm", "--unit-status", "assumed")
        report = json.loads((out / "input_report.json").read_text())
        self.assertEqual(report["unit_status"], "assumed")
        self.assertEqual(report["analysis_mode"], "visual-only")
        self.assertEqual(report["rendered_point_count"], len(self.points))
        self.assertEqual(report["numerical_accuracy"], "not evaluated")
        self.assertEqual(set(report), {"file", "sha256", "format", "input_shape", "input_dtype",
                         "xyz_columns", "ignored_columns", "count", "excluded_count", "transform",
                         "unit", "unit_status", "unit_conversion", "analysis_mode", "rendered_point_count",
                         "sampling", "source_indices", "camera_policy", "display_overrides", "images",
                         "numerical_accuracy"})
        self.assertEqual(len(report["images"]), 7)
        for name, digest in report["images"].items():
            self.assertGreater((out / name).stat().st_size, 1000)
            self.assertEqual(sha256(out / name), digest)
        self.assertEqual({p.suffix for p in out.iterdir()}, {".png", ".json"})
        before = sha256(out / "iso.png")
        self.run_script("inspect_cloud.py", path, "--out", out, code=2)
        self.assertEqual(sha256(out / "iso.png"), before)
        np.testing.assert_array_equal(read_cloud(path)[0], self.points)
        self.run_script("inspect_cloud.py", path, "--out", self.root / "invalid-units", "--unit", "mm", code=2)
        self.run_script("inspect_cloud.py", path, "--out", self.root / "invalid-span", "--view-span", 0, code=2)

    def test_cad_only_quality_and_source_locked_comparison(self):
        import cadquery as cq
        import vtk
        from vtk.util.numpy_support import vtk_to_numpy
        # Explicit feature sequence, independent of scan inputs.
        blank = cq.Workplane("XY").placeSketch(cq.Sketch().rect(10, 10)).extrude(10)
        rounded = blank.edges("|Z").fillet(.5)
        model = rounded.faces(">Z").edges().chamfer(.2)
        self.assertTrue(model.val().isValid())
        self.assertEqual(model.solids().size(), 1)
        step, stl = self.root / "part.step", self.root / "part.stl"
        cq.exporters.export(model, str(step))
        cq.exporters.export(model, str(stl), tolerance=.002, angularTolerance=.05)
        self.assertTrue(cq.importers.importStep(str(step)).val().isValid())
        self.assertGreater(model.val().Volume(), 0)
        path = self.root / "cloud.npy"
        np.save(path, self.points)
        base = [path, "--focus", 0, 0, 0, "--view-span", 15]
        self.run_script("inspect_cloud.py", *base, "--out", self.root / "source")
        self.run_script("inspect_cloud.py", *base, "--cad-stl", stl, "--out", self.root / "comparison")
        report = json.loads((self.root / "comparison/input_report.json").read_text())
        self.assertEqual(report["cad_preview"]["sha256"], sha256(stl))
        self.assertEqual(report["display_overrides"], {"focus": [0, 0, 0], "view_span": 15})
        # Rendering regression: adding CAD must not rescale or shift the cloud panel.
        for name in report["images"]:
            images = []
            for folder in ["source", "comparison"]:
                reader = vtk.vtkPNGReader()
                reader.SetFileName(str(self.root / folder / name))
                reader.Update()
                image = reader.GetOutput()
                width, height, _ = image.GetDimensions()
                images.append(vtk_to_numpy(image.GetPointData().GetScalars()).reshape(height, width, -1))
            self.assertEqual(images[1].shape[:2], (700, 1400))
            np.testing.assert_array_equal(images[0], images[1][:, :700])


if __name__ == "__main__":
    unittest.main(verbosity=2)
