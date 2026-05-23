# PetroDB TUI

Textual-based client for the PetroDB REST API. Provides a terminal interface for managing petrological project data — samples, spots, areas, profiles, and profile spots.

## Requirements

- Python 3.14+
- A running PetroDB REST API

## Installation

```bash
git clone <repo>
cd aitest
uv sync
```

## Usage

```bash
uv run petrodb-manager
```

Note: The PETRODB_API environment variable must be set to your PetroDB instance url.

### Navigation

| Key | Action |
|-----|--------|
| `Enter` | Open selected item / confirm |
| `Esc` | Back / Cancel |
| `Ctrl+Q` | Quit |

### Screens

| Screen | Description |
|--------|-------------|
| **Login** | Authenticate with username/password via OAuth2 |
| **Projects** | List and select projects |
| **Samples** | CRUD samples within a project; Open to see components |
| **Sample Detail** | View/edit/delete sample; navigate to Spots, Areas, Profiles |
| **Spots** | CRUD analytical spots (label, mineral, values dict) |
| **Areas** | CRUD analytical areas (label, values dict) |
| **Profiles** | CRUD profiles (label, mineral); Open to see profile spots |
| **Profile Spots** | CRUD profile spots (index, values dict) |

## API Endpoints Used

- `POST /token` — authentication
- `GET /api/projects/` — list projects
- `GET/POST /api/samples/{project_id}` — list/create samples
- `GET/PUT/DELETE /api/sample/{project_id}/{sample_id}` — get/update/delete sample
- `GET/POST /api/spots/{project_id}/{sample_id}` — list/create spots
- `GET/PUT/DELETE /api/spot/{project_id}/{sample_id}/{spot_id}` — get/update/delete spot
- `GET/POST /api/areas/{project_id}/{sample_id}` — list/create areas
- `GET/PUT/DELETE /api/area/{project_id}/{sample_id}/{area_id}` — get/update/delete area
- `GET/POST /api/profiles/{project_id}/{sample_id}` — list/create profiles
- `GET/PUT/DELETE /api/profile/{project_id}/{sample_id}/{profile_id}` — get/update/delete profile
- `GET/POST /api/profilespots/{project_id}/{sample_id}/{profile_id}` — list/create profile spots
- `GET/PUT/DELETE /api/profilespot/{project_id}/{sample_id}/{profile_id}/{spot_id}` — get/update/delete profile spot

## Project Structure

```
petrodb_tui/
  __init__.py
  __main__.py     # Entry point
  api.py          # Async HTTP client (httpx)
  app.py          # Textual App definition
  screens.py      # All screen classes
```

## Development

```bash
uv run ruff check .
uv run ruff format .
```
