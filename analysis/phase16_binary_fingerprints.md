# Fase 16 — Fingerprints estáticos del blob
Los fingerprints se calculan sobre bytes relativos al inicio del blob. Las instrucciones están normalizadas sólo para eliminar direcciones literales de destinos; no se asignan símbolos.
## `0x00510`
- **bytes[0:32]**: `48 c7 c0 15 02 00 00 49 89 ca 0f 05 72 01 c3 48 8d 0d 1a e4 ff ff ff e1 90 90 90 90 90 90 90 90`
- **SHA-256 ventana 32 bytes**: `d42d62fe1dd1091551e739df39c0d5eac7e496cfd127fea4c166e5de6a026556`
- **desensamblado**:
```text
     510:	48 c7 c0 15 02 00 00 	mov    rax,0x215
     517:	49 89 ca             	mov    r10,rcx
     51a:	0f 05                	syscall
     51c:	72 01                	jb     0x51f
     51e:	c3                   	ret
     51f:	48 8d 0d 1a e4 ff ff 	lea    rcx,[rip+0xffffffffffffe41a]        # 0xffffffffffffe940
     526:	ff e1                	jmp    rcx
     528:	90                   	nop
     529:	90                   	nop
     52a:	90                   	nop
     52b:	90                   	nop
     52c:	90                   	nop
     52d:	90                   	nop
     52e:	90                   	nop
     52f:	90                   	nop
     530:	48 c7 c0 16 02 00 00 	mov    rax,0x216
     537:	49 89 ca             	mov    r10,rcx
     53a:	0f 05                	syscall
```
- **instrucciones normalizadas**:
```text
mov    rax,TARGET
mov    r10,rcx
syscall
jb     TARGET
ret
lea    rcx,[rip+TARGET]        # TARGET
jmp    rcx
nop
nop
nop
nop
nop
nop
nop
nop
mov    rax,TARGET
mov    r10,rcx
syscall
```
- **referencias textuales en el desensamblado completo (muestra, 53)**:
  - `b806:	48 8d bd f0 fa ff ff 	lea    rdi,[rbp-0x510]`
  - `b81e:	8b 85 f0 fa ff ff    	mov    eax,DWORD PTR [rbp-0x510]`
  - `b82d:	89 85 f0 fa ff ff    	mov    DWORD PTR [rbp-0x510],eax`
  - `b833:	48 8d bd f0 fa ff ff 	lea    rdi,[rbp-0x510]`
  - `b867:	48 81 ec 10 05 00 00 	sub    rsp,0x510`
  - `b8bd:	48 81 c4 10 05 00 00 	add    rsp,0x510`
  - `e837:	48 8d 05 22 10 05 00 	lea    rax,[rip+0x51022]        # 0x5f860`
  - `ecde:	c5 f8 29 b5 f0 fa ff 	vmovaps XMMWORD PTR [rbp-0x510],xmm6`
  - `16c69:	e8 a2 98 fe ff       	call   0x510`
  - `36c4b:	ff ae 74 fd ff ae    	jmp    FWORD PTR [rsi-0x5100028c]`
  - `36c53:	ff ae 74 fd ff ae    	jmp    FWORD PTR [rsi-0x5100028c]`
  - `36c5b:	ff ae 74 fd ff ae    	jmp    FWORD PTR [rsi-0x5100028c]`
  - `36c63:	ff ae 74 fd ff ae    	jmp    FWORD PTR [rsi-0x5100028c]`
  - `37de7:	ff ae b8 fe ff ae    	jmp    FWORD PTR [rsi-0x51000148]`
  - `37df3:	ff ae b8 fe ff ae    	jmp    FWORD PTR [rsi-0x51000148]`
  - `37dff:	ff ae b8 fe ff ae    	jmp    FWORD PTR [rsi-0x51000148]`
  - `37e0b:	ff ae b8 fe ff ae    	jmp    FWORD PTR [rsi-0x51000148]`
  - `37e17:	ff ae b8 fe ff ae    	jmp    FWORD PTR [rsi-0x51000148]`
  - `37e23:	ff ae b8 fe ff ae    	jmp    FWORD PTR [rsi-0x51000148]`
  - `37e2f:	ff ae b8 fe ff ae    	jmp    FWORD PTR [rsi-0x51000148]`

## `0x00530`
- **bytes[0:32]**: `48 c7 c0 16 02 00 00 49 89 ca 0f 05 72 01 c3 48 8d 0d fa e3 ff ff ff e1 90 90 90 90 90 90 90 90`
- **SHA-256 ventana 32 bytes**: `e3d59d26004700de46799757c869cd61d48d16354be40c4392ef3846a79d8fca`
- **desensamblado**:
```text
     530:	48 c7 c0 16 02 00 00 	mov    rax,0x216
     537:	49 89 ca             	mov    r10,rcx
     53a:	0f 05                	syscall
     53c:	72 01                	jb     0x53f
     53e:	c3                   	ret
     53f:	48 8d 0d fa e3 ff ff 	lea    rcx,[rip+0xffffffffffffe3fa]        # 0xffffffffffffe940
     546:	ff e1                	jmp    rcx
     548:	90                   	nop
     549:	90                   	nop
     54a:	90                   	nop
     54b:	90                   	nop
     54c:	90                   	nop
     54d:	90                   	nop
     54e:	90                   	nop
     54f:	90                   	nop
     550:	48 c7 c0 17 02 00 00 	mov    rax,0x217
     557:	49 89 ca             	mov    r10,rcx
     55a:	0f 05                	syscall
```
- **instrucciones normalizadas**:
```text
mov    rax,TARGET
mov    r10,rcx
syscall
jb     TARGET
ret
lea    rcx,[rip+TARGET]        # TARGET
jmp    rcx
nop
nop
nop
nop
nop
nop
nop
nop
mov    rax,TARGET
mov    r10,rcx
syscall
```
- **referencias textuales en el desensamblado completo (muestra, 27)**:
  - `b9d6:	48 8d bd d0 fa ff ff 	lea    rdi,[rbp-0x530]`
  - `ba05:	8b 85 d0 fa ff ff    	mov    eax,DWORD PTR [rbp-0x530]`
  - `ba13:	89 8d d0 fa ff ff    	mov    DWORD PTR [rbp-0x530],ecx`
  - `ba3c:	48 8d bd d0 fa ff ff 	lea    rdi,[rbp-0x530]`
  - `ba8a:	89 85 d0 fa ff ff    	mov    DWORD PTR [rbp-0x530],eax`
  - `bab0:	48 8d b5 d0 fa ff ff 	lea    rsi,[rbp-0x530]`
  - `c75a:	48 8b 05 e7 30 05 00 	mov    rax,QWORD PTR [rip+0x530e7]        # 0x5f848`
  - `c76d:	48 8d 05 d4 30 05 00 	lea    rax,[rip+0x530d4]        # 0x5f848`
  - `c776:	48 8b 05 c3 30 05 00 	mov    rax,QWORD PTR [rip+0x530c3]        # 0x5f840`
  - `c789:	48 8d 05 b0 30 05 00 	lea    rax,[rip+0x530b0]        # 0x5f840`
  - `ecce:	c5 f8 29 a5 d0 fa ff 	vmovaps XMMWORD PTR [rbp-0x530],xmm4`
  - `16ca9:	e8 82 98 fe ff       	call   0x530`
  - `2259b:	4c 8d bd d0 fa ff ff 	lea    r15,[rbp-0x530]`
  - `27254:	48 8d 9d d0 fa ff ff 	lea    rbx,[rbp-0x530]`
  - `272ea:	48 8d bd d0 fa ff ff 	lea    rdi,[rbp-0x530]`
  - `27331:	48 8d b5 d0 fa ff ff 	lea    rsi,[rbp-0x530]`
  - `27344:	c6 85 d0 fa ff ff 00 	mov    BYTE PTR [rbp-0x530],0x0`
  - `27391:	48 8d 8d d0 fa ff ff 	lea    rcx,[rbp-0x530]`
  - `3712c:	69 2d 73 63 00 53 79 	imul   ebp,DWORD PTR [rip+0x53006373],0x6f437379        # 0x5303d4a9`
  - `41a7f:	00 b0 3d fc ff ac    	add    BYTE PTR [rax-0x530003c3],dh`

## `0x01bb0`
- **bytes[0:32]**: `55 48 89 e5 48 8b 05 15 4c 05 00 48 85 c0 74 05 48 89 e9 eb 02 31 c9 48 8d 15 32 b0 08 00 48 83`
- **SHA-256 ventana 32 bytes**: `d89d1da5ddf26e33e1288c4cb454c4cc98b60b3dc1433ff7656332e00b6fc9ab`
- **desensamblado**:
```text
    1bb0:	55                   	push   rbp
    1bb1:	48 89 e5             	mov    rbp,rsp
    1bb4:	48 8b 05 15 4c 05 00 	mov    rax,QWORD PTR [rip+0x54c15]        # 0x567d0
    1bbb:	48 85 c0             	test   rax,rax
    1bbe:	74 05                	je     0x1bc5
    1bc0:	48 89 e9             	mov    rcx,rbp
    1bc3:	eb 02                	jmp    0x1bc7
    1bc5:	31 c9                	xor    ecx,ecx
    1bc7:	48 8d 15 32 b0 08 00 	lea    rdx,[rip+0x8b032]        # 0x8cc00
    1bce:	48 83 3a 00          	cmp    QWORD PTR [rdx],0x0
    1bd2:	74 3c                	je     0x1c10
    1bd4:	48 8d 70 ff          	lea    rsi,[rax-0x1]
    1bd8:	48 39 ce             	cmp    rsi,rcx
    1bdb:	73 0c                	jae    0x1be9
    1bdd:	48 03 05 f4 4b 05 00 	add    rax,QWORD PTR [rip+0x54bf4]        # 0x567d8
    1be4:	48 39 c1             	cmp    rcx,rax
    1be7:	76 27                	jbe    0x1c10
    1be9:	64 48 8b 0c 25 10 00 	mov    rcx,QWORD PTR fs:0x10
```
- **instrucciones normalizadas**:
```text
push   rbp
mov    rbp,rsp
mov    rax,QWORD PTR [rip+TARGET]        # TARGET
test   rax,rax
je     TARGET
mov    rcx,rbp
jmp    TARGET
xor    ecx,ecx
lea    rdx,[rip+TARGET]        # TARGET
cmp    QWORD PTR [rdx],TARGET
je     TARGET
lea    rsi,[rax-TARGET]
cmp    rsi,rcx
jae    TARGET
add    rax,QWORD PTR [rip+TARGET]        # TARGET
cmp    rcx,rax
jbe    TARGET
mov    rcx,QWORD PTR fs:TARGET
```
- **referencias textuales en el desensamblado completo (muestra, 80)**:
  - `25db:	e8 d0 f5 ff ff       	call   0x1bb0`
  - `263a:	e8 71 f5 ff ff       	call   0x1bb0`
  - `26bb:	e8 f0 f4 ff ff       	call   0x1bb0`
  - `271a:	e8 91 f4 ff ff       	call   0x1bb0`
  - `2875:	e8 36 f3 ff ff       	call   0x1bb0`
  - `2e68:	e8 43 ed ff ff       	call   0x1bb0`
  - `6116:	e8 95 ba ff ff       	call   0x1bb0`
  - `6281:	e8 2a b9 ff ff       	call   0x1bb0`
  - `6679:	e8 32 b5 ff ff       	call   0x1bb0`
  - `6d14:	e8 97 ae ff ff       	call   0x1bb0`
  - `6f6b:	e8 40 ac ff ff       	call   0x1bb0`
  - `6fcc:	e8 df ab ff ff       	call   0x1bb0`
  - `728c:	e8 1f a9 ff ff       	call   0x1bb0`
  - `72dd:	e8 ce a8 ff ff       	call   0x1bb0`
  - `73f8:	e8 b3 a7 ff ff       	call   0x1bb0`
  - `744c:	e8 5f a7 ff ff       	call   0x1bb0`
  - `7572:	e8 39 a6 ff ff       	call   0x1bb0`
  - `75c1:	e8 ea a5 ff ff       	call   0x1bb0`
  - `7652:	e8 59 a5 ff ff       	call   0x1bb0`
  - `76cb:	e8 e0 a4 ff ff       	call   0x1bb0`

## `0x13b20`
- **bytes[0:32]**: `55 48 89 e5 41 56 53 48 83 ec 30 4c 8d 35 2e bd 04 00 48 8d 5d d8 49 8b 06 48 89 45 e8 89 f8 48`
- **SHA-256 ventana 32 bytes**: `181db34b4f320579ab438c775b63e01df84c1581a6235cfc9f487b2d3a5ef683`
- **desensamblado**:
```text
   13b20:	55                   	push   rbp
   13b21:	48 89 e5             	mov    rbp,rsp
   13b24:	41 56                	push   r14
   13b26:	53                   	push   rbx
   13b27:	48 83 ec 30          	sub    rsp,0x30
   13b2b:	4c 8d 35 2e bd 04 00 	lea    r14,[rip+0x4bd2e]        # 0x5f860
   13b32:	48 8d 5d d8          	lea    rbx,[rbp-0x28]
   13b36:	49 8b 06             	mov    rax,QWORD PTR [r14]
   13b39:	48 89 45 e8          	mov    QWORD PTR [rbp-0x18],rax
   13b3d:	89 f8                	mov    eax,edi
   13b3f:	48 69 c0 83 de 1b 43 	imul   rax,rax,0x431bde83
   13b46:	48 c1 e8 32          	shr    rax,0x32
   13b4a:	69 c8 40 42 0f 00    	imul   ecx,eax,0xf4240
   13b50:	29 cf                	sub    edi,ecx
   13b52:	69 cf e8 03 00 00    	imul   ecx,edi,0x3e8
   13b58:	48 8d 7d c8          	lea    rdi,[rbp-0x38]
   13b5c:	48 89 4d d0          	mov    QWORD PTR [rbp-0x30],rcx
   13b60:	48 89 45 c8          	mov    QWORD PTR [rbp-0x38],rax
```
- **instrucciones normalizadas**:
```text
push   rbp
mov    rbp,rsp
push   r14
push   rbx
sub    rsp,TARGET
lea    r14,[rip+TARGET]        # TARGET
lea    rbx,[rbp-TARGET]
mov    rax,QWORD PTR [r14]
mov    QWORD PTR [rbp-TARGET],rax
mov    eax,edi
imul   rax,rax,TARGET
shr    rax,TARGET
imul   ecx,eax,TARGET
sub    edi,ecx
imul   ecx,edi,TARGET
lea    rdi,[rbp-TARGET]
mov    QWORD PTR [rbp-TARGET],rcx
mov    QWORD PTR [rbp-TARGET],rax
```
- **referencias textuales en el desensamblado completo (muestra, 2)**:
  - `27225:	e8 f6 c8 fe ff       	call   0x13b20`
  - `2749a:	e8 81 c6 fe ff       	call   0x13b20`

## `0x114d0`
- **bytes[0:32]**: `e9 db 03 ff ff 90 90 90 90 90 90 90 90 90 90 90 e9 eb 03 ff ff 90 90 90 90 90 90 90 90 90 90 90`
- **SHA-256 ventana 32 bytes**: `a4e644661210ae3be8a185faf919f9e5a1a1908bdce8e89df3cbd56cac470a56`
- **desensamblado**:
```text
   114d0:	e9 db 03 ff ff       	jmp    0x18b0
   114d5:	90                   	nop
   114d6:	90                   	nop
   114d7:	90                   	nop
   114d8:	90                   	nop
   114d9:	90                   	nop
   114da:	90                   	nop
   114db:	90                   	nop
   114dc:	90                   	nop
   114dd:	90                   	nop
   114de:	90                   	nop
   114df:	90                   	nop
   114e0:	e9 eb 03 ff ff       	jmp    0x18d0
   114e5:	90                   	nop
   114e6:	90                   	nop
   114e7:	90                   	nop
   114e8:	90                   	nop
   114e9:	90                   	nop
```
- **instrucciones normalizadas**:
```text
jmp    TARGET
nop
nop
nop
nop
nop
nop
nop
nop
nop
nop
nop
jmp    TARGET
nop
nop
nop
nop
nop
```
- **referencias textuales en el desensamblado completo (muestra, 1)**:
  - `154f4:	e8 d7 bf ff ff       	call   0x114d0`

## `0x114e0`
- **bytes[0:32]**: `e9 eb 03 ff ff 90 90 90 90 90 90 90 90 90 90 90 e9 fb 03 ff ff 90 90 90 90 90 90 90 90 90 90 90`
- **SHA-256 ventana 32 bytes**: `e03d69b8a52132adc33b8807848daea60e47fe837fdc4664044fa4ea300696b6`
- **desensamblado**:
```text
   114e0:	e9 eb 03 ff ff       	jmp    0x18d0
   114e5:	90                   	nop
   114e6:	90                   	nop
   114e7:	90                   	nop
   114e8:	90                   	nop
   114e9:	90                   	nop
   114ea:	90                   	nop
   114eb:	90                   	nop
   114ec:	90                   	nop
   114ed:	90                   	nop
   114ee:	90                   	nop
   114ef:	90                   	nop
   114f0:	e9 fb 03 ff ff       	jmp    0x18f0
   114f5:	90                   	nop
   114f6:	90                   	nop
   114f7:	90                   	nop
   114f8:	90                   	nop
   114f9:	90                   	nop
```
- **instrucciones normalizadas**:
```text
jmp    TARGET
nop
nop
nop
nop
nop
nop
nop
nop
nop
nop
nop
jmp    TARGET
nop
nop
nop
nop
nop
```
- **referencias textuales en el desensamblado completo (muestra, 16)**:
  - `7f1e:	e8 bd 95 00 00       	call   0x114e0`
  - `c65c:	e8 7f 4e 00 00       	call   0x114e0`
  - `c685:	e8 56 4e 00 00       	call   0x114e0`
  - `f01f:	e8 bc 24 00 00       	call   0x114e0`
  - `154c4:	e8 17 c0 ff ff       	call   0x114e0`
  - `16354:	e8 87 b1 ff ff       	call   0x114e0`
  - `16af4:	e8 e7 a9 ff ff       	call   0x114e0`
  - `16d62:	e8 79 a7 ff ff       	call   0x114e0`
  - `172fa:	e8 e1 a1 ff ff       	call   0x114e0`
  - `17427:	e8 b4 a0 ff ff       	call   0x114e0`
  - `17612:	e8 c9 9e ff ff       	call   0x114e0`
  - `18b2c:	e8 af 89 ff ff       	call   0x114e0`
  - `18eee:	e8 ed 85 ff ff       	call   0x114e0`
  - `25f9f:	e8 3c b5 fe ff       	call   0x114e0`
  - `25fec:	e8 ef b4 fe ff       	call   0x114e0`
  - `324f9:	e8 e2 ef fd ff       	call   0x114e0`

## `0x114f0`
- **bytes[0:32]**: `e9 fb 03 ff ff 90 90 90 90 90 90 90 90 90 90 90 e9 0b 04 ff ff 90 90 90 90 90 90 90 90 90 90 90`
- **SHA-256 ventana 32 bytes**: `cf8687dc3aa4016a2a77d29b0f7dc9519e62b58460ae56c449a4bfb089b215fe`
- **desensamblado**:
```text
   114f0:	e9 fb 03 ff ff       	jmp    0x18f0
   114f5:	90                   	nop
   114f6:	90                   	nop
   114f7:	90                   	nop
   114f8:	90                   	nop
   114f9:	90                   	nop
   114fa:	90                   	nop
   114fb:	90                   	nop
   114fc:	90                   	nop
   114fd:	90                   	nop
   114fe:	90                   	nop
   114ff:	90                   	nop
   11500:	e9 0b 04 ff ff       	jmp    0x1910
   11505:	90                   	nop
   11506:	90                   	nop
   11507:	90                   	nop
   11508:	90                   	nop
   11509:	90                   	nop
```
- **instrucciones normalizadas**:
```text
jmp    TARGET
nop
nop
nop
nop
nop
nop
nop
nop
nop
nop
nop
jmp    TARGET
nop
nop
nop
nop
nop
```
- **referencias textuales en el desensamblado completo (muestra, 2)**:
  - `15464:	e8 87 c0 ff ff       	call   0x114f0`
  - `1facc:	e8 1f 1a ff ff       	call   0x114f0`

## `0x11500`
- **bytes[0:32]**: `e9 0b 04 ff ff 90 90 90 90 90 90 90 90 90 90 90 e9 cb c8 ff ff 90 90 90 90 90 90 90 90 90 90 90`
- **SHA-256 ventana 32 bytes**: `71ccfe83410e7f315d9aca5ca2779fb30ff3178d87b64ce5d244966e25279cc9`
- **desensamblado**:
```text
   11500:	e9 0b 04 ff ff       	jmp    0x1910
   11505:	90                   	nop
   11506:	90                   	nop
   11507:	90                   	nop
   11508:	90                   	nop
   11509:	90                   	nop
   1150a:	90                   	nop
   1150b:	90                   	nop
   1150c:	90                   	nop
   1150d:	90                   	nop
   1150e:	90                   	nop
   1150f:	90                   	nop
   11510:	e9 cb c8 ff ff       	jmp    0xdde0
   11515:	90                   	nop
   11516:	90                   	nop
   11517:	90                   	nop
   11518:	90                   	nop
   11519:	90                   	nop
```
- **instrucciones normalizadas**:
```text
jmp    TARGET
nop
nop
nop
nop
nop
nop
nop
nop
nop
nop
nop
jmp    TARGET
nop
nop
nop
nop
nop
```
- **referencias textuales en el desensamblado completo (muestra, 2)**:
  - `15494:	e8 67 c0 ff ff       	call   0x11500`
  - `2b2a5:	81 7d c0 00 00 50 11 	cmp    DWORD PTR [rbp-0x40],0x11500000`

## `0x11520`
- **bytes[0:32]**: `e9 0b 04 ff ff 90 90 90 90 90 90 90 90 90 90 90 55 48 89 e5 4d 85 c0 74 36 41 83 38 03 75 30 83`
- **SHA-256 ventana 32 bytes**: `6e0885bf061c74bcffcfafca9e779e1284c922354396f5cd75360365d9ab2667`
- **desensamblado**:
```text
   11520:	e9 0b 04 ff ff       	jmp    0x1930
   11525:	90                   	nop
   11526:	90                   	nop
   11527:	90                   	nop
   11528:	90                   	nop
   11529:	90                   	nop
   1152a:	90                   	nop
   1152b:	90                   	nop
   1152c:	90                   	nop
   1152d:	90                   	nop
   1152e:	90                   	nop
   1152f:	90                   	nop
   11530:	55                   	push   rbp
   11531:	48 89 e5             	mov    rbp,rsp
   11534:	4d 85 c0             	test   r8,r8
   11537:	74 36                	je     0x1156f
   11539:	41 83 38 03          	cmp    DWORD PTR [r8],0x3
   1153d:	75 30                	jne    0x1156f
```
- **instrucciones normalizadas**:
```text
jmp    TARGET
nop
nop
nop
nop
nop
nop
nop
nop
nop
nop
nop
push   rbp
mov    rbp,rsp
test   r8,r8
je     TARGET
cmp    DWORD PTR [r8],TARGET
jne    TARGET
```
- **referencias textuales en el desensamblado completo (muestra, 1)**:
  - `15524:	e8 f7 bf ff ff       	call   0x11520`

## `0x14870`
- **bytes[0:32]**: `55 48 89 e5 e8 67 87 ff ff 48 85 c0 78 02 5d c3 e8 2b d3 fe ff 8b 00 8d 88 00 00 02 80 85 c0 0f`
- **SHA-256 ventana 32 bytes**: `4a60abaf93bc3d3a21dd8e9c6256e5d257755620afbd75bba3fbcc7831f9f5da`
- **desensamblado**:
```text
   14870:	55                   	push   rbp
   14871:	48 89 e5             	mov    rbp,rsp
   14874:	e8 67 87 ff ff       	call   0xcfe0
   14879:	48 85 c0             	test   rax,rax
   1487c:	78 02                	js     0x14880
   1487e:	5d                   	pop    rbp
   1487f:	c3                   	ret
   14880:	e8 2b d3 fe ff       	call   0x1bb0
   14885:	8b 00                	mov    eax,DWORD PTR [rax]
   14887:	8d 88 00 00 02 80    	lea    ecx,[rax-0x7ffe0000]
   1488d:	85 c0                	test   eax,eax
   1488f:	0f 44 c8             	cmove  ecx,eax
   14892:	48 63 c1             	movsxd rax,ecx
   14895:	5d                   	pop    rbp
   14896:	c3                   	ret
   14897:	90                   	nop
   14898:	90                   	nop
   14899:	90                   	nop
```
- **instrucciones normalizadas**:
```text
push   rbp
mov    rbp,rsp
call   TARGET
test   rax,rax
js     TARGET
pop    rbp
ret
call   TARGET
mov    eax,DWORD PTR [rax]
lea    ecx,[rax-TARGET]
test   eax,eax
cmove  ecx,eax
movsxd rax,ecx
pop    rbp
ret
nop
nop
nop
```
- **referencias textuales en el desensamblado completo (muestra, 0)**:

## `0x148a0`
- **bytes[0:32]**: `55 48 89 e5 e8 a7 8c ff ff 48 85 c0 78 02 5d c3 e8 fb d2 fe ff 8b 00 8d 88 00 00 02 80 85 c0 0f`
- **SHA-256 ventana 32 bytes**: `f485b21446d1b45b956fa8fa40ee71e09ccea8d02390af0008a100c00ea8347d`
- **desensamblado**:
```text
   148a0:	55                   	push   rbp
   148a1:	48 89 e5             	mov    rbp,rsp
   148a4:	e8 a7 8c ff ff       	call   0xd550
   148a9:	48 85 c0             	test   rax,rax
   148ac:	78 02                	js     0x148b0
   148ae:	5d                   	pop    rbp
   148af:	c3                   	ret
   148b0:	e8 fb d2 fe ff       	call   0x1bb0
   148b5:	8b 00                	mov    eax,DWORD PTR [rax]
   148b7:	8d 88 00 00 02 80    	lea    ecx,[rax-0x7ffe0000]
   148bd:	85 c0                	test   eax,eax
   148bf:	0f 44 c8             	cmove  ecx,eax
   148c2:	48 63 c1             	movsxd rax,ecx
   148c5:	5d                   	pop    rbp
   148c6:	c3                   	ret
   148c7:	90                   	nop
   148c8:	90                   	nop
   148c9:	90                   	nop
```
- **instrucciones normalizadas**:
```text
push   rbp
mov    rbp,rsp
call   TARGET
test   rax,rax
js     TARGET
pop    rbp
ret
call   TARGET
mov    eax,DWORD PTR [rax]
lea    ecx,[rax-TARGET]
test   eax,eax
cmove  ecx,eax
movsxd rax,ecx
pop    rbp
ret
nop
nop
nop
```
- **referencias textuales en el desensamblado completo (muestra, 0)**:

## `0x148d0`
- **bytes[0:32]**: `55 48 89 e5 31 c0 e8 b5 83 ff ff 85 c0 78 02 5d c3 e8 ca d2 fe ff 8b 08 8d 81 00 00 02 80 85 c9`
- **SHA-256 ventana 32 bytes**: `85f8578173696b79cdb252f331b1fded015f1d2a2e3272e4ecaf497a1483910f`
- **desensamblado**:
```text
   148d0:	55                   	push   rbp
   148d1:	48 89 e5             	mov    rbp,rsp
   148d4:	31 c0                	xor    eax,eax
   148d6:	e8 b5 83 ff ff       	call   0xcc90
   148db:	85 c0                	test   eax,eax
   148dd:	78 02                	js     0x148e1
   148df:	5d                   	pop    rbp
   148e0:	c3                   	ret
   148e1:	e8 ca d2 fe ff       	call   0x1bb0
   148e6:	8b 08                	mov    ecx,DWORD PTR [rax]
   148e8:	8d 81 00 00 02 80    	lea    eax,[rcx-0x7ffe0000]
   148ee:	85 c9                	test   ecx,ecx
   148f0:	0f 44 c1             	cmove  eax,ecx
   148f3:	5d                   	pop    rbp
   148f4:	c3                   	ret
   148f5:	90                   	nop
   148f6:	90                   	nop
   148f7:	90                   	nop
```
- **instrucciones normalizadas**:
```text
push   rbp
mov    rbp,rsp
xor    eax,eax
call   TARGET
test   eax,eax
js     TARGET
pop    rbp
ret
call   TARGET
mov    ecx,DWORD PTR [rax]
lea    eax,[rcx-TARGET]
test   ecx,ecx
cmove  eax,ecx
pop    rbp
ret
nop
nop
nop
```
- **referencias textuales en el desensamblado completo (muestra, 2)**:
  - `346bd:	e8 0e 02 fe ff       	call   0x148d0`
  - `347ba:	e8 11 01 fe ff       	call   0x148d0`

## `0x14900`
- **bytes[0:32]**: `55 48 89 e5 e8 07 80 ff ff 85 c0 78 02 5d c3 e8 9c d2 fe ff 8b 08 8d 81 00 00 02 80 85 c9 0f 44`
- **SHA-256 ventana 32 bytes**: `829ad6bc4c5f32f8f6082457ee303ffa79668d3f9dccefbdb8a4504b27d711e5`
- **desensamblado**:
```text
   14900:	55                   	push   rbp
   14901:	48 89 e5             	mov    rbp,rsp
   14904:	e8 07 80 ff ff       	call   0xc910
   14909:	85 c0                	test   eax,eax
   1490b:	78 02                	js     0x1490f
   1490d:	5d                   	pop    rbp
   1490e:	c3                   	ret
   1490f:	e8 9c d2 fe ff       	call   0x1bb0
   14914:	8b 08                	mov    ecx,DWORD PTR [rax]
   14916:	8d 81 00 00 02 80    	lea    eax,[rcx-0x7ffe0000]
   1491c:	85 c9                	test   ecx,ecx
   1491e:	0f 44 c1             	cmove  eax,ecx
   14921:	5d                   	pop    rbp
   14922:	c3                   	ret
   14923:	90                   	nop
   14924:	90                   	nop
   14925:	90                   	nop
   14926:	90                   	nop
```
- **instrucciones normalizadas**:
```text
push   rbp
mov    rbp,rsp
call   TARGET
test   eax,eax
js     TARGET
pop    rbp
ret
call   TARGET
mov    ecx,DWORD PTR [rax]
lea    eax,[rcx-TARGET]
test   ecx,ecx
cmove  eax,ecx
pop    rbp
ret
nop
nop
nop
nop
```
- **referencias textuales en el desensamblado completo (muestra, 4)**:
  - `34727:	e8 d4 01 fe ff       	call   0x14900`
  - `3474b:	e8 b0 01 fe ff       	call   0x14900`
  - `3481d:	e9 de 00 fe ff       	jmp    0x14900`
  - `34836:	e8 c5 00 fe ff       	call   0x14900`

## `0x15310`
- **bytes[0:32]**: `55 48 89 e5 e8 37 9a fe ff 85 c0 78 02 5d c3 e8 8c c8 fe ff 8b 08 8d 81 00 00 02 80 85 c9 0f 44`
- **SHA-256 ventana 32 bytes**: `7ef07915e10eff083e839c02a4f8d5761b0163cd53b18e7bb8c567707e27fd0e`
- **desensamblado**:
```text
   15310:	55                   	push   rbp
   15311:	48 89 e5             	mov    rbp,rsp
   15314:	e8 37 9a fe ff       	call   0xffffffffffffed50
   15319:	85 c0                	test   eax,eax
   1531b:	78 02                	js     0x1531f
   1531d:	5d                   	pop    rbp
   1531e:	c3                   	ret
   1531f:	e8 8c c8 fe ff       	call   0x1bb0
   15324:	8b 08                	mov    ecx,DWORD PTR [rax]
   15326:	8d 81 00 00 02 80    	lea    eax,[rcx-0x7ffe0000]
   1532c:	85 c9                	test   ecx,ecx
   1532e:	0f 44 c1             	cmove  eax,ecx
   15331:	5d                   	pop    rbp
   15332:	c3                   	ret
   15333:	90                   	nop
   15334:	90                   	nop
   15335:	90                   	nop
   15336:	90                   	nop
```
- **instrucciones normalizadas**:
```text
push   rbp
mov    rbp,rsp
call   TARGET
test   eax,eax
js     TARGET
pop    rbp
ret
call   TARGET
mov    ecx,DWORD PTR [rax]
lea    eax,[rcx-TARGET]
test   ecx,ecx
cmove  eax,ecx
pop    rbp
ret
nop
nop
nop
nop
```
- **referencias textuales en el desensamblado completo (muestra, 0)**:

## `0x15460`
- **bytes[0:32]**: `55 48 89 e5 e8 87 c0 ff ff 48 85 c0 78 02 5d c3 e8 3b c7 fe ff 8b 00 8d 88 00 00 02 80 85 c0 0f`
- **SHA-256 ventana 32 bytes**: `216415fda8b5b29aa7bb27aaae0736f02df23ca5526271f1fbb37c95a3b370ce`
- **desensamblado**:
```text
   15460:	55                   	push   rbp
   15461:	48 89 e5             	mov    rbp,rsp
   15464:	e8 87 c0 ff ff       	call   0x114f0
   15469:	48 85 c0             	test   rax,rax
   1546c:	78 02                	js     0x15470
   1546e:	5d                   	pop    rbp
   1546f:	c3                   	ret
   15470:	e8 3b c7 fe ff       	call   0x1bb0
   15475:	8b 00                	mov    eax,DWORD PTR [rax]
   15477:	8d 88 00 00 02 80    	lea    ecx,[rax-0x7ffe0000]
   1547d:	85 c0                	test   eax,eax
   1547f:	0f 44 c8             	cmove  ecx,eax
   15482:	48 63 c1             	movsxd rax,ecx
   15485:	5d                   	pop    rbp
   15486:	c3                   	ret
   15487:	90                   	nop
   15488:	90                   	nop
   15489:	90                   	nop
```
- **instrucciones normalizadas**:
```text
push   rbp
mov    rbp,rsp
call   TARGET
test   rax,rax
js     TARGET
pop    rbp
ret
call   TARGET
mov    eax,DWORD PTR [rax]
lea    ecx,[rax-TARGET]
test   eax,eax
cmove  ecx,eax
movsxd rax,ecx
pop    rbp
ret
nop
nop
nop
```
- **referencias textuales en el desensamblado completo (muestra, 2)**:
  - `346ec:	e8 6f 0d fe ff       	call   0x15460`
  - `347e9:	e8 72 0c fe ff       	call   0x15460`

## `0x15490`
- **bytes[0:32]**: `55 48 89 e5 e8 67 c0 ff ff 48 85 c0 78 02 5d c3 e8 0b c7 fe ff 8b 00 8d 88 00 00 02 80 85 c0 0f`
- **SHA-256 ventana 32 bytes**: `e15d159dde793d1d43947ecc766141b6d5c71addd84daf0465371fdb6dc98d49`
- **desensamblado**:
```text
   15490:	55                   	push   rbp
   15491:	48 89 e5             	mov    rbp,rsp
   15494:	e8 67 c0 ff ff       	call   0x11500
   15499:	48 85 c0             	test   rax,rax
   1549c:	78 02                	js     0x154a0
   1549e:	5d                   	pop    rbp
   1549f:	c3                   	ret
   154a0:	e8 0b c7 fe ff       	call   0x1bb0
   154a5:	8b 00                	mov    eax,DWORD PTR [rax]
   154a7:	8d 88 00 00 02 80    	lea    ecx,[rax-0x7ffe0000]
   154ad:	85 c0                	test   eax,eax
   154af:	0f 44 c8             	cmove  ecx,eax
   154b2:	48 63 c1             	movsxd rax,ecx
   154b5:	5d                   	pop    rbp
   154b6:	c3                   	ret
   154b7:	90                   	nop
   154b8:	90                   	nop
   154b9:	90                   	nop
```
- **instrucciones normalizadas**:
```text
push   rbp
mov    rbp,rsp
call   TARGET
test   rax,rax
js     TARGET
pop    rbp
ret
call   TARGET
mov    eax,DWORD PTR [rax]
lea    ecx,[rax-TARGET]
test   eax,eax
cmove  ecx,eax
movsxd rax,ecx
pop    rbp
ret
nop
nop
nop
```
- **referencias textuales en el desensamblado completo (muestra, 1)**:
  - `34710:	e8 7b 0d fe ff       	call   0x15490`

## `0x154f0`
- **bytes[0:32]**: `55 48 89 e5 e8 d7 bf ff ff 48 85 c0 78 02 5d c3 e8 ab c6 fe ff 8b 00 8d 88 00 00 02 80 85 c0 0f`
- **SHA-256 ventana 32 bytes**: `6bf0dc62bd2f8b0414d146dc851370202c3c32b0a21cb9d00a3ef8471d60168a`
- **desensamblado**:
```text
   154f0:	55                   	push   rbp
   154f1:	48 89 e5             	mov    rbp,rsp
   154f4:	e8 d7 bf ff ff       	call   0x114d0
   154f9:	48 85 c0             	test   rax,rax
   154fc:	78 02                	js     0x15500
   154fe:	5d                   	pop    rbp
   154ff:	c3                   	ret
   15500:	e8 ab c6 fe ff       	call   0x1bb0
   15505:	8b 00                	mov    eax,DWORD PTR [rax]
   15507:	8d 88 00 00 02 80    	lea    ecx,[rax-0x7ffe0000]
   1550d:	85 c0                	test   eax,eax
   1550f:	0f 44 c8             	cmove  ecx,eax
   15512:	48 63 c1             	movsxd rax,ecx
   15515:	5d                   	pop    rbp
   15516:	c3                   	ret
   15517:	90                   	nop
   15518:	90                   	nop
   15519:	90                   	nop
```
- **instrucciones normalizadas**:
```text
push   rbp
mov    rbp,rsp
call   TARGET
test   rax,rax
js     TARGET
pop    rbp
ret
call   TARGET
mov    eax,DWORD PTR [rax]
lea    ecx,[rax-TARGET]
test   eax,eax
cmove  ecx,eax
movsxd rax,ecx
pop    rbp
ret
nop
nop
nop
```
- **referencias textuales en el desensamblado completo (muestra, 0)**:

## `0x19320`
- **bytes[0:32]**: `55 48 89 e5 41 57 41 56 41 54 53 49 89 f4 89 fb 48 8d 3d b1 66 04 00 48 8d 35 72 00 00 00 41 89`
- **SHA-256 ventana 32 bytes**: `6fff622cca6581f3342a54f80e0b81f4b16962c15b3f06df9bfc5f02bff29c72`
- **desensamblado**:
```text
   19320:	55                   	push   rbp
   19321:	48 89 e5             	mov    rbp,rsp
   19324:	41 57                	push   r15
   19326:	41 56                	push   r14
   19328:	41 54                	push   r12
   1932a:	53                   	push   rbx
   1932b:	49 89 f4             	mov    r12,rsi
   1932e:	89 fb                	mov    ebx,edi
   19330:	48 8d 3d b1 66 04 00 	lea    rdi,[rip+0x466b1]        # 0x5f9e8
   19337:	48 8d 35 72 00 00 00 	lea    rsi,[rip+0x72]        # 0x193b0
   1933e:	41 89 cf             	mov    r15d,ecx
   19341:	49 89 d6             	mov    r14,rdx
   19344:	e8 97 f1 fe ff       	call   0x84e0
   19349:	b8 09 00 02 80       	mov    eax,0x80020009
   1934e:	83 fb 01             	cmp    ebx,0x1
   19351:	77 50                	ja     0x193a3
   19353:	89 d8                	mov    eax,ebx
   19355:	48 8d 15 a4 66 04 00 	lea    rdx,[rip+0x466a4]        # 0x5fa00
```
- **instrucciones normalizadas**:
```text
push   rbp
mov    rbp,rsp
push   r15
push   r14
push   r12
push   rbx
mov    r12,rsi
mov    ebx,edi
lea    rdi,[rip+TARGET]        # TARGET
lea    rsi,[rip+TARGET]        # TARGET
mov    r15d,ecx
mov    r14,rdx
call   TARGET
mov    eax,TARGET
cmp    ebx,TARGET
ja     TARGET
mov    eax,ebx
lea    rdx,[rip+TARGET]        # TARGET
```
- **referencias textuales en el desensamblado completo (muestra, 0)**:

## `0x045f0`
- **bytes[0:32]**: `55 48 89 e5 41 57 41 56 41 54 53 48 89 d3 49 89 f6 49 89 ff 41 bc 16 00 00 00 48 85 d2 74 29 48`
- **SHA-256 ventana 32 bytes**: `d3892bb67c5f33153a7c8eac52bff0bf6d8f5dbe1dea7d6c957802d5f44c180d`
- **desensamblado**:
```text
    45f0:	55                   	push   rbp
    45f1:	48 89 e5             	mov    rbp,rsp
    45f4:	41 57                	push   r15
    45f6:	41 56                	push   r14
    45f8:	41 54                	push   r12
    45fa:	53                   	push   rbx
    45fb:	48 89 d3             	mov    rbx,rdx
    45fe:	49 89 f6             	mov    r14,rsi
    4601:	49 89 ff             	mov    r15,rdi
    4604:	41 bc 16 00 00 00    	mov    r12d,0x16
    460a:	48 85 d2             	test   rdx,rdx
    460d:	74 29                	je     0x4638
    460f:	48 83 3b 00          	cmp    QWORD PTR [rbx],0x0
    4613:	78 23                	js     0x4638
    4615:	48 81 7b 08 ff c9 9a 	cmp    QWORD PTR [rbx+0x8],0x3b9ac9ff
    461c:	3b
    461d:	77 19                	ja     0x4638
    461f:	4c 89 ff             	mov    rdi,r15
```
- **instrucciones normalizadas**:
```text
push   rbp
mov    rbp,rsp
push   r15
push   r14
push   r12
push   rbx
mov    rbx,rdx
mov    r14,rsi
mov    r15,rdi
mov    r12d,TARGET
test   rdx,rdx
je     TARGET
cmp    QWORD PTR [rbx],TARGET
js     TARGET
cmp    QWORD PTR [rbx+TARGET],TARGET
3b
ja     TARGET
mov    rdi,r15
```
- **referencias textuales en el desensamblado completo (muestra, 0)**:

## `0x0c970`
- **bytes[0:32]**: `55 48 89 e5 48 89 fa bf 07 83 ff a0 be 01 00 02 80 31 c9 45 31 c0 45 31 c9 e8 12 a8 01 00 5d c3`
- **SHA-256 ventana 32 bytes**: `2543a526570541989a87871831582121f133b803315155a0f86abb4bb6b36ba1`
- **desensamblado**:
```text
    c970:	55                   	push   rbp
    c971:	48 89 e5             	mov    rbp,rsp
    c974:	48 89 fa             	mov    rdx,rdi
    c977:	bf 07 83 ff a0       	mov    edi,0xa0ff8307
    c97c:	be 01 00 02 80       	mov    esi,0x80020001
    c981:	31 c9                	xor    ecx,ecx
    c983:	45 31 c0             	xor    r8d,r8d
    c986:	45 31 c9             	xor    r9d,r9d
    c989:	e8 12 a8 01 00       	call   0x271a0
    c98e:	5d                   	pop    rbp
    c98f:	c3                   	ret
    c990:	55                   	push   rbp
    c991:	48 89 e5             	mov    rbp,rsp
    c994:	41 57                	push   r15
    c996:	41 56                	push   r14
    c998:	41 55                	push   r13
    c99a:	41 54                	push   r12
    c99c:	53                   	push   rbx
```
- **instrucciones normalizadas**:
```text
push   rbp
mov    rbp,rsp
mov    rdx,rdi
mov    edi,TARGET
mov    esi,TARGET
xor    ecx,ecx
xor    r8d,r8d
xor    r9d,r9d
call   TARGET
pop    rbp
ret
push   rbp
mov    rbp,rsp
push   r15
push   r14
push   r13
push   r12
push   rbx
```
- **referencias textuales en el desensamblado completo (muestra, 1)**:
  - `c95a:	e8 11 00 00 00       	call   0xc970`

## `0x0c990`
- **bytes[0:32]**: `55 48 89 e5 41 57 41 56 41 55 41 54 53 50 41 89 fc 64 4c 8b 2c 25 10 00 00 00 4c 89 ef 41 89 d6`
- **SHA-256 ventana 32 bytes**: `c337d2376dd0cd76dcb8988d4ee8a7133f83910fa3f87b53ad6cc7567581af74`
- **desensamblado**:
```text
    c990:	55                   	push   rbp
    c991:	48 89 e5             	mov    rbp,rsp
    c994:	41 57                	push   r15
    c996:	41 56                	push   r14
    c998:	41 55                	push   r13
    c99a:	41 54                	push   r12
    c99c:	53                   	push   rbx
    c99d:	50                   	push   rax
    c99e:	41 89 fc             	mov    r12d,edi
    c9a1:	64 4c 8b 2c 25 10 00 	mov    r13,QWORD PTR fs:0x10
    c9a8:	00 00
    c9aa:	4c 89 ef             	mov    rdi,r13
    c9ad:	41 89 d6             	mov    r14d,edx
    c9b0:	49 89 f7             	mov    r15,rsi
    c9b3:	e8 18 6f ff ff       	call   0x38d0
    c9b8:	44 89 e7             	mov    edi,r12d
    c9bb:	4c 89 fe             	mov    rsi,r15
    c9be:	44 89 f2             	mov    edx,r14d
```
- **instrucciones normalizadas**:
```text
push   rbp
mov    rbp,rsp
push   r15
push   r14
push   r13
push   r12
push   rbx
push   rax
mov    r12d,edi
mov    r13,QWORD PTR fs:TARGET
00 00
mov    rdi,r13
mov    r14d,edx
mov    r15,rsi
call   TARGET
mov    edi,r12d
mov    rsi,r15
mov    edx,r14d
```
- **referencias textuales en el desensamblado completo (muestra, 0)**:
