import os
import socket
import ssl
import urllib.request
import json
import time
import websocket

ACCESS_TOKEN = '6dfc126c-428a-4984-9db9-bb483eb01cf3'
API_PATH     = '/apps/api/129/devices/all'

def monitor():
    hub_ip = socket.gethostbyname('hubitat.local')
    api_url = f'https://{hub_ip}{API_PATH}?access_token={ACCESS_TOKEN}'
    ws_url  = f'wss://{hub_ip}/eventsocket'

    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE

    # Initial poll to discover sensor names and current values
    req = urllib.request.Request(api_url)
    with urllib.request.urlopen(req, context=ssl_ctx) as response:
        data = json.loads(response.read().decode('utf-8'))

    header  = ['@Time']  # must be alphabetically first, due to how Flask jsonify works!
    current = {}
    for item in data:
        if 'label' in item and 'attributes' in item:
            if 'temperature' in item['attributes']:
                label = item['label']
                header.append(label)
                current[label] = item['attributes']['temperature']

    fd = os.path.expanduser('~/.logs/monitoring')
    if not os.path.exists(fd): os.makedirs(fd)
    fn  = os.path.join(fd, time.strftime('%Y_%m') + '.csv')
    efn = os.path.join(fd, time.strftime('%Y_%m') + '.err')

    new_file = not os.path.exists(fn) or os.path.getsize(fn) == 0
    with open(fn, 'a') as f:
        if new_file:
            print(*header, file=f, sep=',', flush=True)

        def on_message(ws, message):
            try:
                event = json.loads(message)
                if event.get('name') != 'temperature' or event.get('source') != 'DEVICE':
                    return
                label = event.get('displayName')
                value = event.get('value')
                if label not in current:
                    return
                t = float(value)
                if t < 0 or t > 200:
                    with open(efn, 'a') as ef:
                        print(f"{time.strftime('%m/%d/%Y %H:%M:%S')} ERROR {label}: {value}", file=ef, flush=True)
                    return
                current[label] = value
                record = [time.strftime('%m/%d/%Y %H:%M:%S')] + [current[h] for h in header[1:]]
                print(*record, file=f, sep=',', end='\n', flush=True)
            except Exception as e:
                with open(efn, 'a') as ef:
                    print(f"{time.strftime('%m/%d/%Y %H:%M:%S')} ERROR: {e}", file=ef, flush=True)

        def on_error(ws, error):
            with open(efn, 'a') as ef:
                print(f"{time.strftime('%m/%d/%Y %H:%M:%S')} WS ERROR: {error}", file=ef, flush=True)

        def on_close(ws, close_status_code, close_msg):
            with open(efn, 'a') as ef:
                print(f"{time.strftime('%m/%d/%Y %H:%M:%S')} WS CLOSED: {close_status_code} {close_msg}", file=ef, flush=True)

        ws_app = websocket.WebSocketApp(ws_url,
                                        on_message=on_message,
                                        on_error=on_error,
                                        on_close=on_close)
        ws_app.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE}, reconnect=5,
                           ping_interval=60, ping_timeout=10)

if __name__ == '__main__':
    monitor()
