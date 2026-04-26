# STS Map JSON Export Schema

## Overview
The stable export payload is produced by API function `generate_map_payload` or `generate_map_json`.

## Top-level payload

```json
{
  "schema_version": "1.0.0",
  "api_version": "1.0.0",
  "rule_version": "0.6.0",
  "map": {
    "act_id": "act1",
    "nodes_by_floor": {
      "0": [
        {
          "floor": 0,
          "x": 0,
          "room_type": "monster",
          "display_type": "monster"
        }
      ]
    },
    "edges": [
      {
        "src": { "floor": 0, "x": 0 },
        "dst": { "floor": 1, "x": 0 }
      }
    ]
  }
}
```

## Field definitions

- `schema_version`: export schema semantic version. Consumers should branch parsing logic by this value.
- `api_version`: public API version of generator package.
- `rule_version`: runtime rule set version used to generate this map.
- `map.act_id`: one of `act1`, `act2`, `act3`, `act4`.
- `map.nodes_by_floor`: object keyed by floor index as string.
- `map.nodes_by_floor.<floor>[]`: room node array.
- `map.nodes_by_floor.<floor>[].floor`: floor index as integer.
- `map.nodes_by_floor.<floor>[].x`: horizontal node position as integer.
- `map.nodes_by_floor.<floor>[].room_type`: resolved room type or null.
- `map.nodes_by_floor.<floor>[].display_type`: display icon room type.
- `map.edges[]`: directional edges from upper layer to next layer.

## Compatibility policy

- Additive fields are allowed in minor schema versions.
- Breaking field rename/removal requires major schema bump.
- Consumers must ignore unknown fields for forward compatibility.
