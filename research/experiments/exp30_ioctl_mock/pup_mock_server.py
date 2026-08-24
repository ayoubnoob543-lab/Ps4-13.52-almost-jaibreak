#!/usr/bin/env python3
"""Mock standalone de /dev/pup_update0 (PS4 13.52) — registra ioctls,
responde datos MOCK marcados. NO descifra ni contiene claves."""
import os,socket,struct,json,hashlib,sys
HERE=os.path.dirname(os.path.abspath(__file__))
SOCK=os.path.join(HERE,"pupmock.sock")
LOGJ=os.path.join(HERE,"ioctl_log_server.jsonl")
NAMES={0xC0184401:"DECRYPT_HDR",0xC0184402:"VERIFY_SEG_ADD",0xC0184403:"VERIFY_SEG",
       0xC0184404:"DECRYPT_SEG",0xC0284405:"DECRYPT_SEG_BLK"}
def _decode(cmd,a):
    if cmd==0xC0184401: return {"len":struct.unpack_from("<Q",a,8)[0],
        "type":struct.unpack_from("<i",a,16)[0]}
    if cmd in (0xC0184402,0xC0184403,0xC0184404):
        return {"idx":struct.unpack_from("<H",a,0)[0],
                "len":struct.unpack_from("<Q",a,16)[0]}
    if cmd==0xC0284405: return {"block_len":struct.unpack_from("<Q",a,16)[0]}
    return {}
def handle(cmd,args,payload):
    if cmd==0xC0184401:
        ln=_decode(cmd,args)["len"]; out=bytearray(ln)
        out[0:7]=b"MOCKHDR"
        if len(payload)>=16: out[0:16]=payload[0:16]
        struct.pack_into("<Q",out,16,503310848)
        struct.pack_into("<H",out,24,3)
        def seg(f,o,c,u): return struct.pack("<Ixxxxqqq",f,o,c,u)
        out[32:64]=seg(0x0,ln,0x10000,0x10000)
        out[64:96]=seg(0xF0001000,0,64,64)
        out[96:128]=seg(0xE0002000,0,64,64)
        want=ln
        if len(out)>want: out=out[:want]
        return 0,bytes(out)
    return 0,payload
def main():
    logs=[]
    if os.path.exists(SOCK): os.unlink(SOCK)
    s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM); s.bind(SOCK); s.listen(1)
    print("[mock] listo",SOCK,flush=True)
    c,_=s.accept(); print("[mock] payload conectado",flush=True)
    seq=0
    while True:
        h=b""
        while len(h)<20:
            b=c.recv(20-len(h))
            if not b: print("[mock] fin"); return
            h+=b
        magic,cmd,alen,plen,_=struct.unpack("<IIIII",h); assert magic==0x504D434B
        args=payload=b""
        while len(args)<alen: args+=c.recv(alen-len(args))
        while len(payload)<plen: payload+=c.recv(plen-len(payload))
        try:
            rv,outb=handle(cmd,args,payload)
        except Exception as ex:
            print("[mock] EXCEPCIÓN en frame:",ex,flush=True)
            rv,outb=-1,b""
        seq+=1
        rec={"seq":seq,"cmd":hex(cmd),"name":NAMES.get(cmd,"?"),
             "args_hex":args.hex(),"fields":_decode(cmd,args),"payload_len":plen,
             "sha16":hashlib.sha256(payload).hexdigest()[:16],
             "args_hex":args.hex(),"head_hex":payload[:32].hex(),"response":"MOCK","rv":rv,"out_len":len(outb)}
        logs.append(rec)
        print("[MOCK]",json.dumps(rec),flush=True)
        open(LOGJ,"w").write("\n".join(json.dumps(x) for x in logs))
        blob=struct.pack("<II",rv&0xFFFFFFFF,len(outb))+outb
        try:
            n=c.sendall(blob)
            print(f"[mock] respuesta enviada {len(blob)}B",flush=True)
        except Exception as ex:
            print(f"[mock] ERROR sendall: {ex}",flush=True)
if __name__=="__main__": main()
