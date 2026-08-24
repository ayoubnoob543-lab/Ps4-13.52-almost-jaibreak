#!/usr/bin/env python3
"""Mock de /dev/pup_update0 — registra ioctls y responde con datos MOCK
claramente marcados. NO descifra nada (no contiene claves ni algoritmo)."""
import os, socket, json, hashlib, struct, datetime, sys

SOCK = os.environ.get("PUP_MOCK_SOCK", "/tmp/pupmock.sock")
LOG  = os.environ.get("PUP_MOCK_LOG", "ioctl_log.jsonl")
MAGIC = 0x504D434B

NAMES = {0xC0184401:"DECRYPT_HDR",0xC0184402:"VERIFY_SEG_ADD",
         0xC0184403:"VERIFY_SEG",0xC0184404:"DECRYPT_SEG",
         0xC0284405:"DECRYPT_SEG_BLK"}

def decode(cmd, args):
    """decodifica campos por estructura conocida (punteros = dirección cliente)"""
    if cmd == 0xC0184401:  # buf, len, type
        return {"buf_ptr":hex(struct.unpack_from("<Q",args,0)[0]),
                "len":struct.unpack_from("<Q",args,8)[0],
                "type":struct.unpack_from("<i",args,16)[0]}
    if cmd in (0xC0184402,0xC0184403,0xC0184404):
        return {"idx":struct.unpack_from("<H",args,0)[0],
                "buf_ptr":hex(struct.unpack_from("<Q",args,8)[0]),
                "len":struct.unpack_from("<Q",args,16)[0]}
    if cmd == 0xC0284405:
        return {"entry_idx":struct.unpack_from("<H",args,0)[0],
                "block_idx":struct.unpack_from("<H",args,2)[0],
                "block_buf":hex(struct.unpack_from("<Q",args,8)[0]),
                "block_len":struct.unpack_from("<Q",args,16)[0],
                "table_buf":hex(struct.unpack_from("<Q",args,24)[0]),
                "table_len":struct.unpack_from("<Q",args,32)[0]}
    return {}

logf = open(LOG,"w")
seq = 0
def log_ioctl(cmd, args, payload, rv, out):
    global seq; seq += 1
    rec = {"seq":seq,"ts":datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "cmd":hex(cmd),"name":NAMES.get(cmd,"?"),
           "args_fields":decode(cmd,args),
           "payload_len":len(payload),
           "payload_sha256":hashlib.sha256(payload).hexdigest()[:16]+"…",
           "payload_head_hex":payload[:32].hex(),
           "response":"MOCK (marcado)"}
    logf.write(json.dumps(rec)+"\n"); logf.flush()
    print(json.dumps(rec))

def main():
    if os.path.exists(SOCK): os.unlink(SOCK)
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); s.bind(SOCK); s.listen(1)
    print(f"[mock] escuchando en {SOCK}", flush=True)
    c,_ = s.accept()
    print("[mock] payload conectado", flush=True)
    while True:
        hdr = c.recv(20)
        if len(hdr) < 20: break
        magic,cmd,alen,plen,_ = struct.unpack("<IIIII",hdr)
        assert magic == MAGIC
        args = b""
        while len(args) < alen: args += c.recv(alen-len(args))
        payload = b""
        while len(payload) < plen: payload += c.recv(plen-len(payload))
        fields = decode(cmd,args)

        # respuestas MOCK marcadas
        if cmd == 0xC0184401:
            ln = fields["len"]
            hdr_len = ln
            out = bytearray(hdr_len)
            out[0:len(b"MOCKHDR")] = b"MOCKHDR"           # marca inequívoca
            if len(payload) >= 16:
                out[0:16] = payload[0:16]                 # preserva cabecera clara real
            # pup_header: file_size@16, segment_count@24 (=3 MOCK)
            struct.pack_into("<Q", out, 16, 503310848)
            struct.pack_into("<H", out, 24, 3)
            # segmentos (32 B cada uno desde 0x20):
            #  s0: normal, apunta a datos reales tras la cabecera (captura cifrada)
            #  s1: watermark 0xF0001000 (rama skip)   s2: firma adicional E0002000
            def seg(flags, off, cs, us):
                return struct.pack("<Ixxxxqqq", flags, off, cs, us)
            out[32:64]   = seg(0x0,        hdr_len, 0x10000, 0x10000)
            out[64:96]   = seg(0xF0001000, 0,       0,       0)
            out[96:128]  = seg(0xE0002000, 0,       0,       0)
            rv, outb = 0, bytes(out)
        elif cmd in (0xC0184402,0xC0184403):
            rv, outb = 0, b""                              # verificación OK mock
        elif cmd == 0xC0184404:
            rv, outb = 0, payload                          # passthrough cifrado
        elif cmd == 0xC0284405:
            rv, outb = 0, payload                          # ídem bloque
        else:
            rv, outb = -1, b""

        log_ioctl(cmd,args,payload,rv,outb)
        c.sendall(struct.pack("<II", rv & 0xFFFFFFFF, len(outb)) + outb)

if __name__ == "__main__": main()
