import os
import urllib.request
import json
import time

def monitor():
    header = []
    header.append('time')

    url = 'http://192.168.0.108/apps/api/129/devices/all?access_token=6dfc126c-428a-4984-9db9-bb483eb01cf3'

    req =  urllib.request.Request(url)

    fd = '/var/log/monitoring'
    if not os.path.exists(fd): os.mkdir(fd)
    now = time.strftime('%Y-%m-%d_%H-%M-%S')
    fn = os.path.join(fd, now + '.csv')
    efn = os.path.join(fd, now + '.err')
#    fn = 'test.csv'
#    efn = 'test.err'

    t_last = '75'

    with open(fn, 'w') as f, open(efn, 'w') as ef:
        while True:
            with urllib.request.urlopen(req) as response:
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
                                    print(f"ERROR at {t_read}: {json.dumps(item, indent=4)}", file=ef)
                                    temp = t_last
                                record.append(temp)
                                t_last = temp
                if len(record) == 0:
                    print(*header, file=f, sep=",", end="\n", flush=True)
                else:
                    print(*record, file=f, sep=",", end="\n", flush=True)

            time.sleep(300)
            #os.system(f"cat {fn}")

if __name__ == '__main__':
    monitor()
