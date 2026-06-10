"""taxi_zones.zip (shapefile, EPSG:2263) → GeoJSON (WGS84) for Leaflet,
plus geometry rows for dim_zone.
"""
import json
import zipfile

import shapefile  # pyshp
from pyproj import Transformer

from .config import DATA_DIR, ZONES_GEOJSON, ZONES_ZIP

_transformer = Transformer.from_crs("EPSG:2263", "EPSG:4326", always_xy=True)


def _reproject(coords):
    """Recursively reproject nested coordinate arrays to [lon, lat]."""
    if coords and isinstance(coords[0], (int, float)):
        lon, lat = _transformer.transform(coords[0], coords[1])
        return [round(lon, 6), round(lat, 6)]
    return [_reproject(c) for c in coords]


def build_geojson() -> dict:
    """Extract shapefile, reproject, return FeatureCollection keyed by LocationID."""
    extract_dir = DATA_DIR / "taxi_zones_shp"
    with zipfile.ZipFile(ZONES_ZIP) as zf:
        zf.extractall(extract_dir)

    # The zip's internal layout varies (flat vs. nested in a subfolder), so
    # locate the .shp wherever it landed rather than assuming a fixed path.
    shp_files = list(extract_dir.rglob("*.shp"))
    if not shp_files:
        raise FileNotFoundError(f"No .shp found under {extract_dir}")
    sf = shapefile.Reader(str(shp_files[0].with_suffix("")))
    features = []
    for sr in sf.shapeRecords():
        rec = sr.record.as_dict()
        geom = sr.shape.__geo_interface__
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "location_id": rec["LocationID"],
                    "zone": rec["zone"],
                    "borough": rec["borough"],
                },
                "geometry": {
                    "type": geom["type"],
                    "coordinates": _reproject([list(c) for c in geom["coordinates"]]
                                              if geom["type"] == "Polygon"
                                              else [[list(c) for c in ring] for ring in geom["coordinates"]]),
                },
            }
        )

    collection = {"type": "FeatureCollection", "features": features}
    ZONES_GEOJSON.write_text(json.dumps(collection))
    print(f"zones: wrote {len(features)} features → {ZONES_GEOJSON}")
    return collection
