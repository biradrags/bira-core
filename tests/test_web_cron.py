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
