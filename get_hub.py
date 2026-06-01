import os
import socket
import ssl
import urllib.request
import json
import time

def monitor():
    header = []
    header.append('@Time') # must be alphabetically first, due to how Flask jsonify works!

    hub_ip = socket.gethostbyname('hubitat.local')
    url = f'https://{hub_ip}/apps/api/129/devices/all?access_token=6dfc126c-428a-4984-9db9-bb483eb01cf3'

    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url)

    fd = os.path.expanduser('~/.logs/monitoring')
    if not os.path.exists(fd): os.makedirs(fd)

    t_last = '75'

    # Wait until the next 5-minute boundary (MM:00 where MM % 5 == 0)
    now_t = time.localtime()
    secs_past = (now_t.tm_min % 5) * 60 + now_t.tm_sec
    if secs_past != 0:
        time.sleep(300 - secs_past)

    now = time.strftime('%Y-%m-%d_%H-%M-%S')
    fn = os.path.join(fd, now + '.csv')
    efn = os.path.join(fd, now + '.err')
#    fn = 'test.csv'
#    efn = 'test.err'

    retries = 0
    with open(fn, 'w') as f:
        while True:
            try:
                with urllib.request.urlopen(req, context=ssl_ctx) as response:
                    record = []
                    page = response.read()
                    t_read = time.strftime('%m/%d/%Y %H:%M:%S')
                    #print(f"response = {page}")
                    data = json.loads(page.decode('utf-8'))
                    #print(json.dumps(data[0], indent=4))
                    for item in data:
                        if 'label' in item and 'attributes' in item:
                            label = item['label']
                            attr = item['attributes']
                            if 'temperature' in attr:
                                if not label in header:
                                    header.append(label)
                                    #print(f"header = {header}")
                                else:
                                    if len(record) == 0:
                                        record.append(t_read)
                                    temp = attr['temperature']
                                    t = float(temp)
                                    if t < 0 or t > 200:
                                        with open(efn, 'a') as ef:
                                            print(f"ERROR at {t_read}: {json.dumps(item, indent=4)}", file=ef)
                                        temp = t_last
                                    record.append(temp)
                                    t_last = temp
                    if len(record) == 0:
                        print(*header, file=f, sep=",", end="\n", flush=True)
                    else:
                        print(*record, file=f, sep=",", end="\n", flush=True)
                        #print(*record, sep=",", end="\n", flush=True)
                    retries = 0

            except Exception as e:
                retries += 1
                with open(efn, 'a') as ef:
                    print(f"{time.strftime('%m/%d/%Y %H:%M:%S')} RETRY {retries}: {e}", file=ef, flush=True)
                if retries < 100:
                    time.sleep(3)
                    continue

            time.sleep(300)
            retries = 0

            #os.system(f"cat {fn}")

if __name__ == '__main__':
    monitor()
