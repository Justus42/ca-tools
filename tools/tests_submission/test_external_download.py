#!/usr/bin/env python3
"""external_array downloads: a zip member fetched by ranges (only the directory, the member's header and its
data) and a whole-file fetch from a server without ranges both give the member byte for byte, also when one
run reads several members of the same archive (the sparse copy gets each member's bytes as it is asked for)."""
import http.server, os, sys, tempfile, threading, zipfile, random
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import external_array as ea


def server(root, ranges):
    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k): super().__init__(*a, directory=root, **k)
        def log_message(self, *a): pass
        def do_GET(self):
            p = os.path.join(root, self.path.lstrip("/")); data = open(p, "rb").read(); rg = self.headers.get("Range")
            if ranges and rg:
                a, b = rg.split("=")[1].split("-"); a = int(a); b = int(b) if b else len(data) - 1
                self.send_response(206); self.send_header("Content-Range", "bytes %d-%d/%d" % (a, b, len(data)))
                self.send_header("Content-Length", str(b - a + 1)); self.end_headers(); self.wfile.write(data[a:b + 1])
            else:
                self.send_response(200); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
    class S(http.server.ThreadingHTTPServer):
        def handle_error(self, request, client_address):
            if not isinstance(sys.exc_info()[1], (ConnectionResetError, BrokenPipeError)):
                super().handle_error(request, client_address)
    s = S(("127.0.0.1", 0), H); threading.Thread(target=s.serve_forever, daemon=True).start()
    return s


def main():
    fails = 0
    with tempfile.TemporaryDirectory() as d:
        rng = random.Random(7); members = {}
        with zipfile.ZipFile(os.path.join(d, "a.zip"), "w", zipfile.ZIP_STORED) as z:
            for i in range(5):
                txt = "\n".join(" ".join(str(rng.randrange(3)) for _ in range(40)) for _ in range(6000)) + "\n"
                members["arrays/CA_%d.txt" % i] = txt.encode(); z.writestr("arrays/CA_%d.txt" % i, txt)
        for ranges in (True, False):
            s = server(d, ranges); url = "http://127.0.0.1:%d/a.zip" % s.server_address[1]
            path = os.path.join(d, "got_%d.zip" % ranges)
            sparse = ea.fetch_member_sparse(url, "arrays/CA_3.txt", path)
            if not sparse: ea.fetch_whole(url, path)
            with zipfile.ZipFile(path) as z: got = z.read("arrays/CA_3.txt")
            ok = got == members["arrays/CA_3.txt"] and sparse == ranges
            print("server %s ranges (%s): member byte for byte: %s" % ("with" if ranges else "without", "member by ranges" if ranges else "whole file", "PASS" if ok else "FAIL"))
            fails += not ok
            ea._ZIP_CACHE.clear(); ea._ZIP_SPARSE.clear()
            ea.check_location = lambda loc, local_root=None: tuple(loc.split("::", 1))
            order = ["arrays/CA_3.txt", "arrays/CA_0.txt", "arrays/CA_4.txt", "arrays/CA_3.txt", "arrays/CA_1.txt"]
            ok = True
            for j, m in enumerate(order):
                wd = os.path.join(d, "w%d_%d" % (ranges, j)); os.makedirs(wd)
                with open(ea.download(url + "::" + m, wd), "rb") as f:
                    ok = ok and f.read() == members[m]
            print("server %s ranges: five members of one zip in one run (the copy reused), each byte for byte: %s"
                  % ("with" if ranges else "without", "PASS" if ok else "FAIL"))
            fails += not ok; s.shutdown()
            ea._ZIP_CACHE.clear(); ea._ZIP_SPARSE.clear()
        ok = os.path.getsize(os.path.join(d, "a.zip")) > 2 * (1 << 20)
        print("the archive is larger than the 1 MiB tail the range fetch reads first: %s" % ("PASS" if ok else "FAIL"))
        fails += not ok
    print("ALL TESTS PASSED" if not fails else "%d TEST(S) FAILED" % fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
