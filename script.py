import json
from shapely.geometry import shape, box, mapping
from shapely.ops import unary_union

def generate_tiles_for_boundaries(boundaries_geojson, tile_size):
    """
    Generate a grid of tiles within the boundaries of each neighborhood.
    :param boundaries_geojson: GeoJSON containing neighborhood boundaries.
    :param tile_size: The size of each tile in degrees.
    :return: GeoJSON FeatureCollection of tiles clipped to neighborhood boundaries.
    """
    features = []

    for feature in boundaries_geojson["features"]:
        neighborhood_name = feature["properties"].get("sec_neigh", "Unknown")
        neighborhood_geom = shape(feature["geometry"])

        # Get bounding box of the neighborhood
        min_lng, min_lat, max_lng, max_lat = neighborhood_geom.bounds

        # Generate tiles within the bounding box
        lng = min_lng
        tile_id_x = 0

        while lng < max_lng:
            lat = min_lat
            tile_id_y = 0
            while lat < max_lat:
                # Create a tile (rectangle) as a Shapely Polygon
                tile = box(lng, lat, lng + tile_size, lat + tile_size)

                # Clip the tile to the neighborhood boundary
                clipped_tile = tile.intersection(neighborhood_geom)

                if not clipped_tile.is_empty:
                    # Add tile to the feature collection
                    features.append({
                        "type": "Feature",
                        "properties": {
                            "neighborhood": neighborhood_name,
                            "tileId": f"{tile_id_x}-{tile_id_y}",
                            "visited": False
                        },
                        "geometry": mapping(clipped_tile)
                    })

                lat += tile_size
                tile_id_y += 1
            lng += tile_size
            tile_id_x += 1
            print(tile_size)

    return {
        "type": "FeatureCollection",
        "features": features
    }

# Load the Boundaries GeoJSON
with open("littleItaly.geojson") as f:
    boundaries_geojson = json.load(f)

# Define tile size in degrees (e.g., ~100m x 100m tiles)
tile_size = .01  # Adjust tile size as needed

# Generate the tiles
tiles_geojson = generate_tiles_for_boundaries(boundaries_geojson, tile_size)

# Save the tiles to a new GeoJSON file
with open("logbook2.geojson", "w") as f:
    json.dump(tiles_geojson, f, indent=2)

print("Tile grid saved to 'tiles.geojson'")
