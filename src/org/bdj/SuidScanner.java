package org.bdj;

import org.bdj.api.API;

public class SuidScanner {

    private static final int O_RDONLY = 0x0000;
    private static final int O_WRONLY = 0x0001;
    private static final int O_CREAT  = 0x0200;
    private static final int O_TRUNC  = 0x0400;
    private static final int S_ISUID  = 0x0800;
    private static final int S_ISGID  = 0x0400;
    private static final int DT_DIR = 4;
    private static final int DT_REG = 8;
    private static final int DENTS_BUF_SIZE = 4096;
    private static final int DIRENT_HEADER_SIZE = 8;
    private static final int DIRENT_RECLEN_OFFSET = 4;
    private static final int DIRENT_TYPE_OFFSET = 6;
    private static final int DIRENT_NAMELEN_OFFSET = 7;
    private static final int STAT_BUF_SIZE = 256;
    private static final int STAT_MODE_OFFSET = 0x08;
    private static final int STAT_UID_OFFSET = 0x0C;
    private static final int STAT_GID_OFFSET = 0x10;
    private static final int PATH_MAX = 1024;
    // Target-specific FreeBSD/Orbis layout. These offsets require validation
    // against the exact target ABI before deployment.
    private static final String STAT_LAYOUT = "Orbis/FreeBSD target layout (unverified)";

    private API api;
    private long openAddr, closeAddr, getdentsAddr, statAddr, writeAddr;
    private StringBuffer results;
    private int suidCount;

    public SuidScanner() {
        results = new StringBuffer();
        suidCount = 0;
        try {
            api = API.getInstance();
            openAddr = api.dlsym(API.LIBC_MODULE_HANDLE, "open");
            closeAddr = api.dlsym(API.LIBC_MODULE_HANDLE, "close");
            getdentsAddr = api.dlsym(API.LIBC_MODULE_HANDLE, "getdents");
            statAddr = api.dlsym(API.LIBC_MODULE_HANDLE, "stat");
            writeAddr = api.dlsym(API.LIBC_MODULE_HANDLE, "write");
            Status.println("open=" + Long.toHexString(openAddr) +
                " stat=" + Long.toHexString(statAddr) +
                " getdents=" + Long.toHexString(getdentsAddr));
            validateStatLayout();
        } catch (Exception e) {
            Status.printStackTrace("SuidScanner init: ", e);
        }
    }

    private void validateStatLayout() {
        if (STAT_MODE_OFFSET + 2 > STAT_BUF_SIZE ||
            STAT_UID_OFFSET + 4 > STAT_BUF_SIZE ||
            STAT_GID_OFFSET + 4 > STAT_BUF_SIZE) {
            throw new IllegalStateException("invalid stat layout: " + STAT_LAYOUT);
        }
    }

    private boolean hasRequiredSymbols() {
        return api != null && openAddr != 0 && closeAddr != 0 &&
            getdentsAddr != 0 && statAddr != 0 && writeAddr != 0;
    }

    private long allocatePath(String path) {
        if (path == null || path.length() + 1 > PATH_MAX) {
            Status.println("[WARN] path exceeds PATH_MAX: " + path);
            return 0;
        }
        long pathBuf = api.malloc(PATH_MAX);
        if (pathBuf != 0) api.strcpy(pathBuf, path);
        return pathBuf;
    }

    public void scan() {
        String[] dirs = {"/", "/bin", "/sbin", "/usr/bin", "/usr/sbin",
            "/usr/local/bin", "/system", "/system/common/lib",
            "/system/sys", "/system/vsh", "/system_ex", "/system_ex/app",
            "/mini-syscore", "/mini-syscore/bin", "/sandboxDir",
            "/app0", "/data", "/mnt/usb0", "/mnt/usb1"};
        Status.println("=== SUID Scanner PS4 13.52 ===");
        if (!hasRequiredSymbols()) {
            Status.println("[ERROR] required libc symbols are unavailable; scan aborted");
            return;
        }
        for (int i = 0; i < dirs.length; i++) {
            scanDir(dirs[i], 0);
        }
        Status.println("=== Done: " + suidCount + " SUID/SGID found ===");
        saveToUsb();
    }

    private void scanDir(String path, int depth) {
        if (depth > 3 || !hasRequiredSymbols()) return;
        long pathBuf = allocatePath(path);
        if (pathBuf == 0) return;
        long fd = api.call(openAddr, pathBuf, O_RDONLY);
        if (fd < 0) { api.free(pathBuf); return; }
        Status.println("[DIR] " + path);
        long dentsBuf = api.malloc(DENTS_BUF_SIZE);
        if (dentsBuf == 0) {
            long closeRet = api.call(closeAddr, fd);
            if (closeRet < 0) Status.println("[WARN] close failed for " + path + ": " + closeRet);
            api.free(pathBuf);
            return;
        }
        long nread;
        while (true) {
            nread = api.call(getdentsAddr, fd, dentsBuf, DENTS_BUF_SIZE);
            if (nread < 0) {
                Status.println("[WARN] getdents failed for " + path + ": " + nread);
                break;
            }
            if (nread == 0) break;
            if (nread > DENTS_BUF_SIZE) {
                Status.println("[WARN] getdents returned oversized length: " + nread);
                break;
            }
            long pos = 0;
            while (pos < nread) {
                if (nread - pos < DIRENT_HEADER_SIZE) {
                    Status.println("[WARN] truncated dirent header in " + path);
                    break;
                }
                int reclen = api.read16(dentsBuf + pos + DIRENT_RECLEN_OFFSET) & 0xFFFF;
                if (reclen < DIRENT_HEADER_SIZE || reclen > nread - pos) {
                    Status.println("[WARN] invalid dirent reclen=" + reclen + " in " + path);
                    break;
                }
                int dtype = api.read8(dentsBuf + pos + DIRENT_TYPE_OFFSET) & 0xFF;
                int namlen = api.read8(dentsBuf + pos + DIRENT_NAMELEN_OFFSET) & 0xFF;
                int nameCapacity = reclen - DIRENT_HEADER_SIZE;
                if (namlen > nameCapacity) {
                    Status.println("[WARN] invalid dirent namlen=" + namlen + " in " + path);
                    break;
                }
                String name = api.readString(dentsBuf + pos + DIRENT_HEADER_SIZE, namlen);
                if (!name.equals(".") && !name.equals("..")) {
                    String full = path.equals("/") ? "/" + name : path + "/" + name;
                    checkSuid(full);
                    if (dtype == DT_DIR && depth < 3) scanDir(full, depth + 1);
                }
                pos += reclen;
            }
        }
        long closeRet = api.call(closeAddr, fd);
        if (closeRet < 0) Status.println("[WARN] close failed for " + path + ": " + closeRet);
        api.free(dentsBuf);
        api.free(pathBuf);
    }

    private void checkSuid(String filePath) {
        long pathBuf = allocatePath(filePath);
        if (pathBuf == 0) return;
        long statBuf = api.calloc(1, STAT_BUF_SIZE);
        if (statBuf == 0) { api.free(pathBuf); return; }
        long ret = api.call(statAddr, pathBuf, statBuf);
        if (ret == 0) {
            int mode = api.read16(statBuf + STAT_MODE_OFFSET) & 0xFFFF;
            int uid = api.read32(statBuf + STAT_UID_OFFSET);
            int gid = api.read32(statBuf + STAT_GID_OFFSET);
            boolean suid = (mode & S_ISUID) != 0;
            boolean sgid = (mode & S_ISGID) != 0;
            if (suid || sgid) {
                String flags = (suid ? "SUID " : "") + (sgid ? "SGID " : "");
                String line = "[FOUND] " + flags + "mode=0" +
                    Integer.toOctalString(mode) + " uid=" + uid +
                    " gid=" + gid + " " + filePath;
                Status.println(line);
                results.append(line + "\n");
                suidCount++;
            }
        } else {
            Status.println("[WARN] stat failed for " + filePath + ": " + ret);
        }
        api.free(statBuf);
        api.free(pathBuf);
    }

    private void saveToUsb() {
        if (results.length() == 0 || writeAddr == 0) return;
        String[] usbs = {"/mnt/usb0/suid_scan.txt", "/mnt/usb1/suid_scan.txt"};
        for (int i = 0; i < usbs.length; i++) {
            long p = api.malloc(PATH_MAX);
            if (p == 0) continue;
            api.strcpy(p, usbs[i]);
            long fd = api.call(openAddr, p, O_WRONLY | O_CREAT | O_TRUNC, 0x1A4);
            if (fd >= 0) {
                String data = "PS4 13.52 SUID Scan\nFound: " + suidCount + "\n\n" + results.toString();
                long buf = api.malloc(data.length() + 1);
                if (buf != 0) {
                    api.strcpy(buf, data);
                    long written = api.call(writeAddr, fd, buf, (long) data.length());
                    if (written != data.length()) {
                        Status.println("[WARN] write incomplete for " + usbs[i] + ": " + written);
                    }
                    api.free(buf);
                }
                long closeRet = api.call(closeAddr, fd);
                if (closeRet < 0) Status.println("[WARN] close failed for " + usbs[i] + ": " + closeRet);
                Status.println("Saved to " + usbs[i]);
                api.free(p);
                return;
            }
            api.free(p);
        }
        Status.println("USB save failed - results on screen only");
    }
}
