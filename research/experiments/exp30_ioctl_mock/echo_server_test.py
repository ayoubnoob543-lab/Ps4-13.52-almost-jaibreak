import socket,os,struct
P=os.path.abspath("test.sock")
if os.path.exists(P): os.unlink(P)
s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM); s.bind(P); s.listen(1)
print("[echo] listo en",P,flush=True)
c,_=s.accept(); print("[echo] cliente conectado",flush=True)
while True:
    h=c.recv(20)
    if len(h)<20: print("[echo] cerrado"); break
    m,cmd,al,pl,x=struct.unpack("<IIIII",h)
    a=b""
    while len(a)<al: a+=c.recv(al-len(a))
    p=b""
    while len(p)<pl: p+=c.recv(pl-len(p))
    print(f"[echo] cmd={hex(cmd)} pl={pl}",flush=True)
    c.sendall(struct.pack("<II",0,pl)+p)
