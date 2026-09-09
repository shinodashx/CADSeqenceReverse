"""Numerical-only NPY/PLY/XYZ inspection; no images or CAD geometry generated."""
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


def inspect(points, info, out, unit="unknown", unit_status="unknown"):
    from scipy.spatial import cKDTree

    unique = np.unique(points, axis=0)
    if len(unique) < 3:
        raise ValueError("At least three distinct points are needed for initial inspection.")
    if (unit == "unknown") != (unit_status == "unknown"):
        raise ValueError("Supply both a unit and confirmed/assumed status, or leave both unknown.")
    out = empty_output(out)
    center = points.mean(axis=0)
    eigenvalues, axes = np.linalg.eigh(np.cov((points-center).T))
    eigenvalues, axes = eigenvalues[::-1], axes[:, ::-1]
    if np.linalg.det(axes) < 0:
        axes[:, -1] *= -1
    # Unique points only for spacing; output/validation retain every original row.
    nearest = cKDTree(unique).query(unique, k=2)[0][:, 1]
    modes = {}
    for axis, name in enumerate("XYZ"):
        values, counts = np.unique(points[:, axis], return_counts=True)
        order = np.argsort(counts, kind="stable")[-8:][::-1]
        modes[name] = [{"coordinate": float(values[i]), "count": int(counts[i])} for i in order]
    info.update(unit=unit, unit_status=unit_status, unit_conversion="none", unique_count=len(unique),
                duplicate_count=len(points)-len(unique), bounds=[points.min(0).tolist(), points.max(0).tolist()],
                spans=np.ptp(points, axis=0).tolist(), centroid=center.tolist(),
                pca_eigenvalues=eigenvalues.tolist(), pca_candidate_axes_columns=axes.tolist(),
                pca_warning="Candidates only; not a verified CAD frame, no transform applied.",
                nearest_unique_spacing={"median": float(np.median(nearest)), "p95": float(np.quantile(nearest, .95))},
                exact_coordinate_modes=modes, analysis_mode="numerical-only")
    np.save(out / "points.npy", points, allow_pickle=False)
    np.save(out / "source_indices.npy", np.arange(len(points), dtype=np.int64), allow_pickle=False)
    (out / "input_report.json").write_text(json.dumps(info, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    return info


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--xyz-columns", type=int, nargs=3)
    parser.add_argument("--unit", choices=["unknown", "mm", "cm", "m", "inch"], default="unknown")
    parser.add_argument("--unit-status", choices=["unknown", "confirmed", "assumed"], default="unknown")
    args = parser.parse_args()
    try:
        points, info = read_cloud(args.input, args.xyz_columns)
        result = inspect(points, info, args.out, args.unit, args.unit_status)
    except (ValueError, SyntaxError, OSError) as ex:
        parser.error(str(ex))
    print(f"Read {result['count']} points; {result['duplicate_count']} duplicates preserved. No geometry generated.")
    print(args.out / "input_report.json")


if __name__ == "__main__":
    main()
