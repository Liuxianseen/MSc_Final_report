from sanic import Sanic
from sanic import response

app = Sanic('myserver')

@app.route('/1.jpg')
async def get1(request):
    return await response.file(
    './1.jpg')

@app.route('/2.jpg')
async def get1(request):
    return await response.file(
    './2.jpg')

@app.route('/3.jpg')
async def get1(request):
    return await response.file(
    './3.jpg')

@app.route('/4.jpg')
async def get1(request):
    return await response.file(
    './4.jpg')

if __name__ == '__main__':
    app.run(host='146.169.142.90', port=8888)
