import logging

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from bira_core.web.cron import cron_protocol, fly_src_gate


async def _make_client() -> TestClient:
    async def job(request: web.Request) -> web.Response:
        return web.json_response({"done": True})

    cron_app = web.Application(
        middlewares=[fly_src_gate(frozenset({"bira-cron"})), cron_protocol()]
    )
    cron_app.router.add_post("/{job}", job)
    app = web.Application()
    app.add_subapp("/cron", cron_app)
    client = TestClient(TestServer(app))
    await client.start_server()
    return client


async def test_blocks_without_fly_src() -> None:
    client = await _make_client()
    resp = await client.post("/cron/ping")
    assert resp.status in (401, 403)
    await client.close()


async def test_passes_with_allowed_src() -> None:
    client = await _make_client()
    resp = await client.post(
        "/cron/ping", headers={"fly-src": "instance=i;app=bira-cron;org=personal"}
    )
    assert resp.status == 200
    await client.close()


async def test_job_name_from_path_without_prefix(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO, logger="bira_core.web.cron")

    async def job(request: web.Request) -> web.Response:
        return web.json_response({})

    app = web.Application(middlewares=[cron_protocol()])
    app.router.add_post("/cron/foo", job)
    client = TestClient(TestServer(app))
    await client.start_server()

    resp = await client.post("/cron/foo")

    assert (await resp.json())["job"] == "foo"
    done = [r for r in caplog.records if r.getMessage() == "cron job done"]
    assert done[0].job == "foo"
    await client.close()
