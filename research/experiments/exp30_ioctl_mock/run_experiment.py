#!/usr/bin/env python3
import socket, threading, json, hashlib, struct, os, sys, subprocess, datetime, time
HERE=os.path.dirname(os.path.abspath(__file__))
SOCK=os.path.join(HERE,"pupmock.sock")
NAMES={0xC0184401:"DECRYPT_HDR",0xC0184402:"VERIFY_SEG_ADD",0xC0184403:"VERIFY_SEG",
       0xC0184404:"DECRYPT_SEG",0xC0284405:"DECRYPT_SEG_BLK"}
def decode(cmd,a):
    if cmd==0xC0184401: return {"len":struct.unpack_from("<Q",a,8)[0],
        "type":struct.unpack_from("<i",a,16)[0]}
    if cmd in (0xC0184402,0xC0184403,0xC0184404):
        return {"idx":struct.unpack_from("<H",a,0)[0],
                "len":struct.unpack_from("<Q",a,16)[0]}
    if cmd==0xC0284405:
        return {"entry":struct.unpack_from("<H",a,0)[0],
                "block":struct.unpack_from("<H",a,2)[0],
                "block_len":struct.unpack_from("<Q",a,16)[0]}
    return {}
def handle(cmd,args,payload):
    if cmd==0xC0184401:
        ln=decode(cmd,args)["len"]; out=bytearray(ln)
        out[0:7]=b"MOCKHDR"
        if len(payload)>=16: out[0:16]=payload[0:16]
        struct.pack_into("<Q",out,16,503310848)
        struct.pack_into("<H",out,24,3)
        def seg(f,o,c,u): return struct.pack("<Ixxxxqqq",f,o,c,u)
        out[32:64]=seg(0x0,ln,0x10000,0x10000)
        out[64:96]=seg(0xF0001000,0,64,64)
        out[96:128]=seg(0xE0002000,0,64,64)
        want=decode(cmd,args).get("len")
        if want is not None and len(out)>want: out=out[:want]
        return 0,bytes(out)
    if cmd in (0xC0184402,0xC0184403): return 0,b""
    return 0,payload
logs=[]
def server():
    if os.path.exists(SOCK): os.unlink(SOCK)
    s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM); s.bind(SOCK); s.listen(1)
    c,_=s.accept()
    while True:
        h=b""
        while len(h)<20:
            b=c.recv(20-len(h))
            if not b: return
            h+=b
        magic,cmd,alen,plen,_=struct.unpack("<IIIII",h); assert magic==0x504D434B
        args=payload=b""
        while len(args)<alen: args+=c.recv(alen-len(args))
        while len(payload)<plen: payload+=c.recv(plen-len(payload))
        rv,outb=handle(cmd,args,payload)
        print(f"[SRV] recibido cmd={hex(cmd)} alen={alen} plen={plen}",flush=True)
        e={"seq":len(logs)+1,"cmd":hex(cmd),"name":NAMES.get(cmd,"?"),
           "fields":decode(cmd,args),"payload_len":plen,
           "sha16":hashlib.sha256(payload).hexdigest()[:16],
           "head_hex":payload[:32].hex(),"response":"MOCK","rv":rv,"out_len":len(outb)}
        logs.append(e); print("[MOCK]",json.dumps(e),flush=True)
def main():
    pup=os.path.expanduser("~/fl_pup/out/PS4SYS_13.52.rebuilt.PUP")
    t=threading.Thread(target=server,daemon=True); t.start(); time.sleep(0.3)
    mnt=os.path.join(HERE,"host","mnt_usb0"); os.makedirs(mnt,exist_ok=True)
    link=os.path.join(mnt,"PS4UPDATE.PUP")
    if os.path.lexists(link): os.unlink(link)
    os.symlink(pup,link)
    binp=os.path.join(HERE,"host","pup_decrypt_mock")
    try:
        env=dict(os.environ, PUP_MOCK_SOCK=SOCK)
        r=subprocess.run([binp],cwd=HERE,capture_output=True,text=True,timeout=120,env=env)
        rc,out,err=r.returncode,r.stdout,r.stderr
    except subprocess.TimeoutExpired as e:
        rc,out,err=-9,(e.stdout or "").decode(errors="replace"),(e.stderr or "").decode(errors="replace")
    open(os.path.join(HERE,"payload_stdout.log"),"w").write(out or "")
    open(os.path.join(HERE,"payload_stderr.log"),"w").write(err or "")
    json.dump(logs,open(os.path.join(HERE,"driver_seen.jsonl"),"w"),indent=1)
    summary={"experiment":"exp30_ioctl_mock",
             "date":datetime.datetime.now(datetime.timezone.utc).isoformat(),
             "input_pup":pup,"payload_exit":rc,"ioctls_captured":len(logs),
             "by_name":{},"status":"UNKNOWN"}
    for e in logs: summary["by_name"][e["name"]]=summary["by_name"].get(e["name"],0)+1
    if any(e["name"]=="DECRYPT_HDR" for e in logs): summary["status"]="PASS"
    json.dump(summary,open(os.path.join(HERE,"result_summary.json"),"w"),indent=2)
    print(json.dumps(summary,indent=2)); print("[STDERR payload]"); print((err or "")[-1500:])
if __name__=="__main__": main()
