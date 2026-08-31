import aiohttp
from aiohttp import web

from bira_core.web import attach_cron_site


async def test_attach_cron_site_lifecycle(unused_tcp_port_factory) -> None:
    port = unused_tcp_port_factory()
    app = web.Application()
    cron_app = web.Application()

    async def ping(_: web.Request) -> web.Response:
        return web.json_response({"ok": True})

    cron_app.router.add_get("/ping", ping)
    attach_cron_site(app, cron_app, port=port)

    for hook in app.on_startup:
        await hook(app)

    client = aiohttp.ClientSession()
    try:
        async with client.get(f"http://127.0.0.1:{port}/ping") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data == {"ok": True}
    finally:
        await client.close()

    for hook in app.on_cleanup:
        await hook(app)

    client2 = aiohttp.ClientSession()
    try:
        async with client2.get(
            f"http://127.0.0.1:{port}/ping",
            timeout=aiohttp.ClientTimeout(total=0.5),
        ) as resp:
            assert resp.status != 200
    except (aiohttp.ClientError, TimeoutError):
        pass
    finally:
        await client2.close()
