import time
from datetime import datetime
from aiohttp import (
    web,
    ClientSession,
    TCPConnector,
)
from decouple import config
from functools import wraps


ACTION = config('MNI_ACTION')
ACCESS_FILE_LOCATION = config('ACCESS_FILE_LOCATION')
access = []


def lprint(*args):
    saida = " - ".join(
        [str(datetime.now())] +
        [str(item) for item in args]
    )
    print(saida)


def accessible(func):
    @wraps(func)
    async def wrapped(request):
        start = time.time()
        token = request.headers['access-token']
        action = request.headers['soapaction']
        if token not in access:
            lprint(
                action,
                token,
                'Not Authorized'
            )
            return web.Response(
                body='Not Authorized',
                status=403
            )
        lprint(action, token)
        try:
            result = await func(request)
        except Exception as error:
            lprint(action, token, str(error))
            return web.Response(
                body=str(error),
                status=500
            )
        else:
            lprint(
                action,
                token,
                time.time()-start,
                result.status
            )
            return result
    return wrapped


@accessible
async def tjrj(request):
    headers = dict(request.headers)
    headers.pop('access-token')

    async with ClientSession(connector=TCPConnector(ssl=False)) as session:
        result = await session.post(
            ACTION,
            data=await request.content.read(),
            headers=request.headers
        )
        retorno = await result.read()

    return web.Response(
        body=retorno,
        status=result.status
    )


if __name__ == '__main__':
    with open(ACCESS_FILE_LOCATION, 'r') as file:
        access = file.readlines()

    app = web.Application()
    app.add_routes([
        web.post('/', tjrj)
    ])
    web.run_app(app)
