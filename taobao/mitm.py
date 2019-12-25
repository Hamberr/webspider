from mitmproxy import ctx

def response(flow):

	if 'um.js' in flow.request.url or '118.js' or '115.js' in flow.request.url:
		flow.response.text = flow.response.text + 'Object.defineProperties(navigator,{webdriver:{get:() => false}}); '
