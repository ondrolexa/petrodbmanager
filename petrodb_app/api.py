import os

import validators
from httpx import AsyncClient

BASE_URL = os.getenv("PETRODB_API", default="")

if not validators.url(BASE_URL):
    if BASE_URL:
        raise ValueError(
            f"{BASE_URL} is not valid url. Check your PETRODB_API environment variable."
        )
    else:
        raise ValueError(
            "PETRODB_API environment variable must be set to your PetroDB instance url."
        )


class APIError(Exception):
    pass


class APIClient:
    def __init__(self) -> None:
        self._client = AsyncClient(base_url=BASE_URL)
        self._token: str | None = None

    @property
    def _headers(self) -> dict[str, str]:
        if self._token:
            return {"Authorization": f"Bearer {self._token}"}
        return {}

    async def login(self, username: str, password: str) -> str:
        r = await self._client.post(
            "/token",
            data={"grant_type": "password", "username": username, "password": password},
        )
        if r.is_error:
            raise APIError(r.json().get("detail", str(r.status_code)))
        data = r.json()
        self._token = data["access_token"]
        return self._token

    # ── Projects ──────────────────────────────────────────────────

    async def get_projects(self) -> list[dict]:
        r = await self._client.get("/api/projects/", headers=self._headers)
        if r.is_error:
            raise APIError(r.json().get("detail", str(r.status_code)))
        return r.json()

    async def get_project(self, project_id: int) -> dict:
        r = await self._client.get(f"/api/project/{project_id}", headers=self._headers)
        if r.is_error:
            raise APIError(r.json().get("detail", str(r.status_code)))
        return r.json()

    # ── Samples ───────────────────────────────────────────────────

    async def get_samples(self, project_id: int) -> list[dict]:
        r = await self._client.get(f"/api/samples/{project_id}", headers=self._headers)
        if r.is_error:
            raise APIError(r.json().get("detail", str(r.status_code)))
        return r.json()

    async def get_sample(self, project_id: int, sample_id: int) -> dict:
        r = await self._client.get(
            f"/api/sample/{project_id}/{sample_id}", headers=self._headers
        )
        if r.is_error:
            raise APIError(r.json().get("detail", str(r.status_code)))
        return r.json()

    async def create_sample(
        self, project_id: int, name: str, description: str | None = None
    ) -> dict:
        payload: dict[str, str | None] = {"name": name, "description": description}
        r = await self._client.post(
            f"/api/sample/{project_id}", json=payload, headers=self._headers
        )
        if r.is_error:
            raise APIError(r.json().get("detail", str(r.status_code)))
        return r.json()

    async def update_sample(
        self,
        project_id: int,
        sample_id: int,
        name: str,
        description: str | None = None,
    ) -> dict:
        payload: dict[str, str | None] = {"name": name, "description": description}
        r = await self._client.put(
            f"/api/sample/{project_id}/{sample_id}",
            json=payload,
            headers=self._headers,
        )
        if r.is_error:
            raise APIError(r.json().get("detail", str(r.status_code)))
        return r.json()

    async def delete_sample(self, project_id: int, sample_id: int) -> None:
        r = await self._client.delete(
            f"/api/sample/{project_id}/{sample_id}", headers=self._headers
        )
        if r.is_error:
            raise APIError(r.json().get("detail", str(r.status_code)))

    # ── Spots ─────────────────────────────────────────────────────

    async def get_spots(self, project_id: int, sample_id: int) -> list[dict]:
        r = await self._client.get(
            f"/api/spots/{project_id}/{sample_id}", headers=self._headers
        )
        if r.is_error:
            raise APIError(r.json().get("detail", str(r.status_code)))
        return r.json()

    async def get_spot(self, project_id: int, sample_id: int, spot_id: int) -> dict:
        r = await self._client.get(
            f"/api/spot/{project_id}/{sample_id}/{spot_id}", headers=self._headers
        )
        if r.is_error:
            raise APIError(r.json().get("detail", str(r.status_code)))
        return r.json()

    async def create_spot(
        self,
        project_id: int,
        sample_id: int,
        label: str,
        mineral: str | None = None,
        values: dict | None = None,
    ) -> dict:
        payload: dict = {"label": label, "values": values or {}}
        if mineral is not None:
            payload["mineral"] = mineral
        r = await self._client.post(
            f"/api/spot/{project_id}/{sample_id}", json=payload, headers=self._headers
        )
        if r.is_error:
            raise APIError(r.json().get("detail", str(r.status_code)))
        return r.json()

    async def update_spot(
        self,
        project_id: int,
        sample_id: int,
        spot_id: int,
        label: str,
        mineral: str | None = None,
        values: dict | None = None,
    ) -> dict:
        payload: dict = {"label": label, "values": values or {}}
        if mineral is not None:
            payload["mineral"] = mineral
        r = await self._client.put(
            f"/api/spot/{project_id}/{sample_id}/{spot_id}",
            json=payload,
            headers=self._headers,
        )
        if r.is_error:
            raise APIError(r.json().get("detail", str(r.status_code)))
        return r.json()

    async def delete_spot(self, project_id: int, sample_id: int, spot_id: int) -> None:
        r = await self._client.delete(
            f"/api/spot/{project_id}/{sample_id}/{spot_id}",
            headers=self._headers,
        )
        if r.is_error:
            raise APIError(r.json().get("detail", str(r.status_code)))

    # ── Areas ─────────────────────────────────────────────────────

    async def get_areas(self, project_id: int, sample_id: int) -> list[dict]:
        r = await self._client.get(
            f"/api/areas/{project_id}/{sample_id}", headers=self._headers
        )
        if r.is_error:
            raise APIError(r.json().get("detail", str(r.status_code)))
        return r.json()

    async def get_area(self, project_id: int, sample_id: int, area_id: int) -> dict:
        r = await self._client.get(
            f"/api/area/{project_id}/{sample_id}/{area_id}", headers=self._headers
        )
        if r.is_error:
            raise APIError(r.json().get("detail", str(r.status_code)))
        return r.json()

    async def create_area(
        self,
        project_id: int,
        sample_id: int,
        label: str,
        values: dict | None = None,
    ) -> dict:
        payload: dict = {"label": label, "values": values or {}}
        r = await self._client.post(
            f"/api/area/{project_id}/{sample_id}", json=payload, headers=self._headers
        )
        if r.is_error:
            raise APIError(r.json().get("detail", str(r.status_code)))
        return r.json()

    async def update_area(
        self,
        project_id: int,
        sample_id: int,
        area_id: int,
        label: str,
        values: dict | None = None,
    ) -> dict:
        payload: dict = {"label": label, "values": values or {}}
        r = await self._client.put(
            f"/api/area/{project_id}/{sample_id}/{area_id}",
            json=payload,
            headers=self._headers,
        )
        if r.is_error:
            raise APIError(r.json().get("detail", str(r.status_code)))
        return r.json()

    async def delete_area(self, project_id: int, sample_id: int, area_id: int) -> None:
        r = await self._client.delete(
            f"/api/area/{project_id}/{sample_id}/{area_id}",
            headers=self._headers,
        )
        if r.is_error:
            raise APIError(r.json().get("detail", str(r.status_code)))

    # ── Profiles ──────────────────────────────────────────────────

    async def get_profiles(self, project_id: int, sample_id: int) -> list[dict]:
        r = await self._client.get(
            f"/api/profiles/{project_id}/{sample_id}", headers=self._headers
        )
        if r.is_error:
            raise APIError(r.json().get("detail", str(r.status_code)))
        return r.json()

    async def get_profile(
        self, project_id: int, sample_id: int, profile_id: int
    ) -> dict:
        r = await self._client.get(
            f"/api/profile/{project_id}/{sample_id}/{profile_id}",
            headers=self._headers,
        )
        if r.is_error:
            raise APIError(r.json().get("detail", str(r.status_code)))
        return r.json()

    async def create_profile(
        self,
        project_id: int,
        sample_id: int,
        label: str,
        mineral: str | None = None,
    ) -> dict:
        payload: dict = {"label": label}
        if mineral is not None:
            payload["mineral"] = mineral
        r = await self._client.post(
            f"/api/profile/{project_id}/{sample_id}",
            json=payload,
            headers=self._headers,
        )
        if r.is_error:
            raise APIError(r.json().get("detail", str(r.status_code)))
        return r.json()

    async def update_profile(
        self,
        project_id: int,
        sample_id: int,
        profile_id: int,
        label: str,
        mineral: str | None = None,
    ) -> dict:
        payload: dict = {"label": label}
        if mineral is not None:
            payload["mineral"] = mineral
        r = await self._client.put(
            f"/api/profile/{project_id}/{sample_id}/{profile_id}",
            json=payload,
            headers=self._headers,
        )
        if r.is_error:
            raise APIError(r.json().get("detail", str(r.status_code)))
        return r.json()

    async def delete_profile(
        self, project_id: int, sample_id: int, profile_id: int
    ) -> None:
        r = await self._client.delete(
            f"/api/profile/{project_id}/{sample_id}/{profile_id}",
            headers=self._headers,
        )
        if r.is_error:
            raise APIError(r.json().get("detail", str(r.status_code)))

    # ── Profile Spots ─────────────────────────────────────────────

    async def get_profile_spots(
        self, project_id: int, sample_id: int, profile_id: int
    ) -> list[dict]:
        r = await self._client.get(
            f"/api/profilespots/{project_id}/{sample_id}/{profile_id}",
            headers=self._headers,
        )
        if r.is_error:
            raise APIError(r.json().get("detail", str(r.status_code)))
        return r.json()

    async def get_profile_spot(
        self, project_id: int, sample_id: int, profile_id: int, spot_id: int
    ) -> dict:
        r = await self._client.get(
            f"/api/profilespot/{project_id}/{sample_id}/{profile_id}/{spot_id}",
            headers=self._headers,
        )
        if r.is_error:
            raise APIError(r.json().get("detail", str(r.status_code)))
        return r.json()

    async def create_profile_spot(
        self,
        project_id: int,
        sample_id: int,
        profile_id: int,
        index: int,
        values: dict | None = None,
    ) -> dict:
        payload: dict = {"index": index, "values": values or {}}
        r = await self._client.post(
            f"/api/profilespot/{project_id}/{sample_id}/{profile_id}",
            json=payload,
            headers=self._headers,
        )
        if r.is_error:
            raise APIError(r.json().get("detail", str(r.status_code)))
        return r.json()

    async def update_profile_spot(
        self,
        project_id: int,
        sample_id: int,
        profile_id: int,
        spot_id: int,
        index: int,
        values: dict | None = None,
    ) -> dict:
        payload: dict = {"index": index, "values": values or {}}
        r = await self._client.put(
            f"/api/profilespot/{project_id}/{sample_id}/{profile_id}/{spot_id}",
            json=payload,
            headers=self._headers,
        )
        if r.is_error:
            raise APIError(r.json().get("detail", str(r.status_code)))
        return r.json()

    async def delete_profile_spot(
        self, project_id: int, sample_id: int, profile_id: int, spot_id: int
    ) -> None:
        r = await self._client.delete(
            f"/api/profilespot/{project_id}/{sample_id}/{profile_id}/{spot_id}",
            headers=self._headers,
        )
        if r.is_error:
            raise APIError(r.json().get("detail", str(r.status_code)))
