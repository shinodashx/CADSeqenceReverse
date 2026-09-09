"""Measure a scan against exported CAD surfaces; never fit or modify geometry."""
from pathlib import Path
import argparse
import csv
import json
import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy
from inspect_cloud import empty_output, read_cloud, sha256


def triangle_distances(points, mesh_path):
    if not Path(mesh_path).is_file() or Path(mesh_path).suffix.lower() != ".stl":
        raise ValueError("--mesh must be an existing CAD-exported STL.")
    reader = vtk.vtkSTLReader()
    reader.SetFileName(str(mesh_path))
    reader.Update()
    mesh = reader.GetOutput()
    if mesh.GetNumberOfCells() == 0 or not np.isfinite(vtk_to_numpy(mesh.GetPoints().GetData())).all():
        raise ValueError("STL has no triangles or has nonfinite coordinates.")
    locator = vtk.vtkStaticCellLocator()
    locator.SetDataSet(mesh)
    locator.BuildLocator()
    distances = np.empty(len(points))
    for i, point in enumerate(points):
        closest = [0., 0., 0.]
        cell, sub, squared = vtk.mutable(0), vtk.mutable(0), vtk.mutable(0.)
        locator.FindClosestPoint(point, closest, cell, sub, squared)
        distances[i] = float(squared)**.5
    if not np.isfinite(distances).all():
        raise ValueError("Nonfinite distances; inspect the exported mesh.")
    return distances, mesh.GetNumberOfCells()


def step_distances(points, step_path):
    import cadquery as cq
    imported = cq.importers.importStep(str(step_path))
    bodies = cq.Compound.makeCompound(imported.vals())
    if not bodies.isValid() or not bodies.Faces():
        raise ValueError("STEP is invalid or has no faces.")
    # Important: Solid distance can be zero for points inside the solid.
    surface = cq.Compound.makeCompound(bodies.Faces())
    return [cq.Vertex.makeVertex(*map(float, point)).distance(surface) for point in points]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--points", type=Path, required=True)
    parser.add_argument("--source-indices", type=Path)
    parser.add_argument("--mesh", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--threshold", type=float, required=True, help="In the unchanged coordinate units.")
    parser.add_argument("--require-within-fraction", type=float)
    parser.add_argument("--step", type=Path)
    parser.add_argument("--exact-worst", type=int, default=0)
    args = parser.parse_args()
    if not np.isfinite(args.threshold) or args.threshold <= 0:
        parser.error("--threshold must be finite and positive.")
    if args.require_within_fraction is not None and not 0 <= args.require_within_fraction <= 1:
        parser.error("--require-within-fraction must be in [0,1].")
    if args.exact_worst < 0 or bool(args.step) != (args.exact_worst > 0):
        parser.error("Provide --step and positive --exact-worst together, or neither.")
    try:
        points, info = read_cloud(args.points)
        source = np.arange(len(points), dtype=np.int64)
        if args.source_indices:
            source = np.load(args.source_indices, allow_pickle=False)
            if source.shape != (len(points),) or source.dtype.kind not in "iu" or np.any(source < 0) or len(np.unique(source)) != len(source):
                raise ValueError("Source indices must be unique nonnegative integers matching the point rows.")
        out = empty_output(args.out)
        distances, triangles = triangle_distances(points, args.mesh)
        worst = np.argsort(-distances, kind="stable")
        fraction = float(np.mean(distances <= args.threshold))
        result = {"points": info, "mesh": str(args.mesh.resolve()), "mesh_sha256": sha256(args.mesh),
                  "source_indices_sha256": sha256(args.source_indices) if args.source_indices else None,
                  "index_definition": "zero-based source row" if args.source_indices else "zero-based input row",
                  "distance_definition": "one-way unsigned point to closest exported triangle face; all input points",
                  "coordinate_units": "unchanged input units; not inferred", "triangles": triangles,
                  "count": len(points), "mean": float(distances.mean()),
                  "rms": float(np.sqrt(np.mean(distances**2))), "median": float(np.median(distances)),
                  "p95": float(np.quantile(distances, .95)), "maximum": float(distances.max()),
                  "threshold": args.threshold, "within_count": int(np.sum(distances <= args.threshold)),
                  "within_fraction": fraction, "worst_source_indices": source[worst[:20]].tolist(),
                  "required_fraction": args.require_within_fraction,
                  "criterion_passed": None if args.require_within_fraction is None else fraction >= args.require_within_fraction,
                  "limitations": "Not bidirectional, not a full CAD/mesh-integrity/assembly/strength acceptance test."}
        if args.step:
            selected = worst[:args.exact_worst]
            exact = step_distances(points[selected], args.step)
            result["step_face_crosscheck"] = {"step": str(args.step.resolve()), "sha256": sha256(args.step),
                "selection": "largest triangle residuals, not independent or full-cloud unless count equals input count",
                "count": len(selected), "source_indices": source[selected].tolist(),
                "surface_distances": exact, "triangle_distances": distances[selected].tolist()}
        with (out / "point_errors.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(["source_index", "x", "y", "z", "triangle_surface_distance"])
            writer.writerows((int(source[i]), *map(float, p), float(distances[i])) for i, p in enumerate(points))
        (out / "verification.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    except (ValueError, OSError) as ex:
        parser.error(str(ex))
    print(f"N={len(points)} RMS={result['rms']:.9g} P95={result['p95']:.9g} MAX={result['maximum']:.9g} within={fraction:.3%}")
    print("Surface criterion:", result["criterion_passed"] if result["criterion_passed"] is not None else "not specified")
    return 1 if result["criterion_passed"] is False else 0


if __name__ == "__main__":
    raise SystemExit(main())
