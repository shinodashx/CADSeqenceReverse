"""Render NPY/PLY/XYZ for visual-only analysis; no feature measurements or fitting."""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import numpy as np


def sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_cloud(path, columns=None):
    path = Path(path)
    if not path.is_file():
        raise ValueError(f"Not a file: {path}")
    if path.stat().st_size > 512 * 1024**2:
        raise ValueError("Input exceeds 512 MiB; use a documented large-cloud workflow.")
    info = {"file": str(path.resolve()), "sha256": sha256(path)}
    suffix = path.suffix.lower()
    if suffix == ".npy":
        data = np.load(path, allow_pickle=False, mmap_mode="r")
        info["format"] = "npy"
    elif suffix == ".ply":
        if columns is not None:
            raise ValueError("PLY uses named x/y/z fields, not --xyz-columns.")
        from plyfile import PlyData
        ply = PlyData.read(str(path))
        if "vertex" not in ply:
            raise ValueError("PLY has no vertex element.")
        vertex = ply["vertex"].data
        if not all(n in vertex.dtype.names for n in ("x", "y", "z")):
            raise ValueError("PLY requires x, y, z vertex properties.")
        data = np.column_stack([vertex[n] for n in ("x", "y", "z")])
        info.update(format="ply", encoding="ascii" if ply.text else f"binary-{ply.byte_order}",
                    ignored_vertex_properties=[n for n in vertex.dtype.names if n not in ("x", "y", "z")],
                    ignored_elements={e.name: e.count for e in ply.elements if e.name != "vertex"})
    elif suffix in (".xyz", ".txt", ".csv", ".json"):
        if path.stat().st_size > 32 * 1024**2:
            raise ValueError("Text input exceeds 32 MiB; supply NPY or PLY instead.")
        text = path.read_text(encoding="utf-8-sig").strip()
        if not text or "..." in text or "…" in text or "truncated" in text.lower():
            raise ValueError("Empty or visibly truncated input; provide the complete coordinates.")
        if text.startswith(("[", "(")):
            data = np.asarray(ast.literal_eval(text))
            info["format"] = "coordinate-literal"
        else:
            rows = []
            for number, line in enumerate(text.splitlines(), 1):
                line = line.split("#", 1)[0].strip()
                if line:
                    try:
                        tokens = line.split(",") if "," in line else line.split()
                        rows.append([float(v) for v in tokens])
                    except ValueError as ex:
                        raise ValueError(f"Invalid numeric row at text line {number}.") from ex
            data = np.asarray(rows)
            info["format"] = "xyz-rows"
    else:
        raise ValueError("Supported inputs: .npy, .ply, .xyz, .txt, .csv, .json")
    if data.ndim != 2 or len(data) == 0 or data.dtype.kind not in "fiu":
        raise ValueError("Expected a nonempty 2D real numeric array (no objects, strings, or complex values).")
    info.update(input_shape=list(data.shape), input_dtype=str(data.dtype))
    if columns is None:
        if data.shape[1] != 3:
            raise ValueError("Expected N×3; select XYZ columns explicitly. No automatic transpose.")
        columns = [0, 1, 2]
    if len(columns) != 3 or len(set(columns)) != 3 or min(columns) < 0 or max(columns) >= data.shape[1]:
        raise ValueError("Select three distinct, in-range XYZ column indices.")
    points = np.asarray(data[:, columns], dtype=np.float64)
    invalid = np.flatnonzero(~np.isfinite(points).all(axis=1))
    if len(invalid):
        raise ValueError(f"Nonfinite XYZ in {len(invalid)} rows; first source indices: {invalid[:10].tolist()}. Nothing dropped.")
    info.update(xyz_columns=list(columns), ignored_columns=[i for i in range(data.shape[1]) if i not in columns],
                count=len(points), excluded_count=0, transform="none; coordinates and order preserved")
    return points, info


def empty_output(path):
    path = Path(path)
    if path.exists() and (not path.is_dir() or any(path.iterdir())):
        raise ValueError(f"Output must be new or empty: {path}")
    path.mkdir(parents=True, exist_ok=True)
    return path


def inspect(points, info, out, unit="unknown", unit_status="unknown", cad_stl=None,
            focus=None, view_span=None):
    import vtk
    from vtk.util.numpy_support import numpy_to_vtk

    if (unit == "unknown") != (unit_status == "unknown"):
        raise ValueError("Supply both a unit and confirmed/assumed status, or leave both unknown.")
    if focus is not None and not np.isfinite(focus).all():
        raise ValueError("Camera focus must be finite.")
    if view_span is not None and (not np.isfinite(view_span) or view_span <= 0):
        raise ValueError("View span must be finite and positive.")
    # Bounds are used ONLY to frame the camera and draw coordinate rulers.
    # No cloud-derived dimensions, axes, fits or residuals are reported.
    low, high = points.min(0), points.max(0)
    diagonal = float(np.linalg.norm(high-low))
    if not np.isfinite(diagonal) or diagonal <= 0:
        raise ValueError("Input has no finite, nonzero display extent.")
    center = (low+high)/2 if focus is None else np.asarray(focus, dtype=float)
    span = diagonal * 1.35 if view_span is None else view_span
    vtk_points = vtk.vtkPoints()
    vtk_points.SetData(numpy_to_vtk(np.ascontiguousarray(points), deep=True))
    cloud = vtk.vtkPolyData()
    cloud.SetPoints(vtk_points)
    vertices = vtk.vtkVertexGlyphFilter()
    vertices.SetInputData(cloud)
    vertices.Update()
    datasets = [("cloud", vertices.GetOutput(), (0.12, 0.35, 0.65))]
    if cad_stl is not None:
        cad_stl = Path(cad_stl)
        if not cad_stl.is_file():
            raise ValueError("CAD preview STL does not exist.")
        reader = vtk.vtkSTLReader()
        reader.SetFileName(str(cad_stl))
        reader.Update()
        mesh = reader.GetOutput()
        if mesh.GetNumberOfPolys() == 0:
            raise ValueError("CAD preview STL has no polygon faces.")
        datasets.append(("cad", mesh, (0.76, 0.48, 0.2)))
        info["cad_preview"] = {"file": str(cad_stl.resolve()), "sha256": sha256(cad_stl)}
    out = empty_output(out)
    views = [("plus_x", (1, 0, 0), (0, 0, 1)), ("minus_x", (-1, 0, 0), (0, 0, 1)),
             ("plus_y", (0, 1, 0), (0, 0, 1)), ("minus_y", (0, -1, 0), (0, 0, 1)),
             ("plus_z", (0, 0, 1), (0, 1, 0)), ("minus_z", (0, 0, -1), (0, 1, 0)),
             ("iso", (1, -1, 1), (0, 0, 1))]
    images = {}
    for name, direction, up in views:
        camera = vtk.vtkCamera()
        camera.SetFocalPoint(*center)
        camera.SetPosition(*(center + np.asarray(direction) * diagonal * 3))
        camera.SetViewUp(*up)
        camera.ParallelProjectionOn()
        camera.SetParallelScale(span/2)
        camera.SetClippingRange(diagonal * .001, diagonal * 20)
        window = vtk.vtkRenderWindow()
        window.SetOffScreenRendering(1)
        window.SetSize(700 * len(datasets), 700)
        window.SetMultiSamples(0)
        for index, (label, data, color) in enumerate(datasets):
            renderer = vtk.vtkRenderer()
            renderer.SetViewport(index/len(datasets), 0, (index+1)/len(datasets), 1)
            renderer.SetBackground(1, 1, 1)
            renderer.SetActiveCamera(camera)  # Identical source-locked camera; no CAD auto-fit.
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputData(data)
            mapper.ScalarVisibilityOff()
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor(*color)
            actor.GetProperty().SetPointSize(3)
            renderer.AddActor(actor)
            axes = vtk.vtkCubeAxesActor()
            axes.SetBounds(low[0], high[0], low[1], high[1], low[2], high[2])
            axes.SetCamera(camera)
            axes.SetFlyModeToOuterEdges()
            for axis in range(3):
                axes.GetTitleTextProperty(axis).SetColor(.2, .2, .2)
                axes.GetLabelTextProperty(axis).SetColor(.2, .2, .2)
            if name == "iso":
                # Oblique tick labels overlap; read the rulers in orthographic views.
                axes.XAxisLabelVisibilityOff()
                axes.YAxisLabelVisibilityOff()
                axes.ZAxisLabelVisibilityOff()
            renderer.AddActor(axes)
            title = vtk.vtkTextActor()
            view_label = "iso (+X,-Y,+Z; up Z)" if name == "iso" else name
            title.SetInput(f"{label.upper()} | {view_label} | {unit} ({unit_status})")
            title.SetPosition(15, 665)
            title.GetTextProperty().SetFontSize(18)
            title.GetTextProperty().SetColor(.15, .15, .15)
            renderer.AddViewProp(title)
            window.AddRenderer(renderer)
        try:
            window.Render()
            capture = vtk.vtkWindowToImageFilter()
            capture.SetInput(window)
            capture.ReadFrontBufferOff()
            capture.Update()
            writer = vtk.vtkPNGWriter()
            image = out / f"{name}.png"
            writer.SetFileName(str(image))
            writer.SetInputConnection(capture.GetOutputPort())
            writer.Write()
            images[image.name] = sha256(image)
        finally:
            window.Finalize()
    info.update(unit=unit, unit_status=unit_status, unit_conversion="none", analysis_mode="visual-only",
                rendered_point_count=len(points), sampling="none; every row submitted, occlusion still applies",
                source_indices="unchanged zero-based input row/vertex order",
                camera_policy="source-framed orthographic; identical camera for cloud and CAD",
                display_overrides={"focus": focus, "view_span": view_span},
                images=images, numerical_accuracy="not evaluated")
    (out / "input_report.json").write_text(json.dumps(info, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    return info


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--xyz-columns", type=int, nargs=3)
    parser.add_argument("--unit", choices=["unknown", "mm", "cm", "m", "inch"], default="unknown")
    parser.add_argument("--unit-status", choices=["unknown", "confirmed", "assumed"], default="unknown")
    parser.add_argument("--cad-stl", type=Path, help="Render only a newly reconstructed CAD export alongside points.")
    parser.add_argument("--focus", type=float, nargs=3, help="Display-only world camera focus, chosen visually.")
    parser.add_argument("--view-span", type=float, help="Display-only orthographic vertical span in input units.")
    args = parser.parse_args()
    try:
        points, info = read_cloud(args.input, args.xyz_columns)
        result = inspect(points, info, args.out, args.unit, args.unit_status,
                         args.cad_stl, args.focus, args.view_span)
    except (ValueError, SyntaxError, OSError) as ex:
        parser.error(str(ex))
    print(f"Rendered {result['count']} input rows; no numerical feature analysis or geometry generated.")
    print(args.out / "input_report.json")


if __name__ == "__main__":
    main()
