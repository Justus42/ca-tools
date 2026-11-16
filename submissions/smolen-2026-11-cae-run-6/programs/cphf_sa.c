/* cphf_sa.c - simulated annealing for a covering perfect hash family CPHF(n; k, q, t) (ca-tools engine, own code).
 * A CPHF(n; k, q, t) is an n x k array of vectors of GF(q)^t such that every t columns are linearly independent in
 * some row (Sherwood, Martirosyan and Colbourn 2006). It expands to a CA(n(q^t - 1) + 1; t, k, q).
 * Fields: q prime, or q = 4, 8, 9 (tables). Cost = number of t-sets of columns independent in no row.
 * Move: replace one cell by a random nonzero vector; exact incremental update over the C(k-1, t-1) t-sets through
 * that column. Metropolis with geometric cooling and reheats.
 * usage: cphf_sa n k q t seed max_seconds [T0] [alpha] OUT [INIT]
 * OUT gets the family (one row per line, k vectors written as t field digits each) when the cost reaches 0. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <stdint.h>
static int q, t, k, n;
static int ADD[16][16], MUL[16][16], INV[16], NEG[16];
static void field(void) {
    int p = 0;
    if (q == 4 || q == 8) { int m = q == 4 ? 2 : 3, poly = q == 4 ? 0x7 : 0xB;
        for (int a = 0; a < q; a++) for (int b = 0; b < q; b++) { ADD[a][b] = a ^ b;
            int r = 0, x = a, y = b; while (y) { if (y & 1) r ^= x; y >>= 1; x <<= 1; if (x & q) x ^= poly; } MUL[a][b] = r; }
        (void)m;
    } else if (q == 9) { /* a = a0 + 3 a1 with i^2 = -1 over GF(3) */
        for (int a = 0; a < 9; a++) for (int b = 0; b < 9; b++) { int a0 = a % 3, a1 = a / 3, b0 = b % 3, b1 = b / 3;
            ADD[a][b] = (a0 + b0) % 3 + 3 * ((a1 + b1) % 3);
            int r0 = ((a0 * b0 - a1 * b1) % 3 + 3) % 3, r1 = (a0 * b1 + a1 * b0) % 3; MUL[a][b] = r0 + 3 * r1; }
    } else { p = q; for (int i = 2; i * i <= q; i++) if (q % i == 0) { fprintf(stderr, "q must be prime or 4, 8, 9\n"); exit(2); }
        for (int a = 0; a < q; a++) for (int b = 0; b < q; b++) { ADD[a][b] = (a + b) % q; MUL[a][b] = a * b % q; } }
    (void)p;
    for (int a = 0; a < q; a++) { for (int b = 0; b < q; b++) { if (MUL[a][b] == 1) INV[a] = b; if (ADD[a][b] == 0) NEG[a] = b; } }
}
static int Q_T, SH = 0;   /* SH: Sherwood form, first coordinate 1 */                 /* q^t */
static unsigned char *DIG;      /* digits of each vector index */
static int *A;                  /* n x k vector indices */
static int indep(int r, const int *cols) {   /* are the t vectors of row r in these columns independent? */
    int M[8][8];
    for (int i = 0; i < t; i++) { const unsigned char *d = DIG + (size_t)A[r * k + cols[i]] * t; for (int j = 0; j < t; j++) M[i][j] = d[j]; }
    for (int c = 0; c < t; c++) {
        int p = -1; for (int i = c; i < t; i++) if (M[i][c]) { p = i; break; }
        if (p < 0) return 0;
        if (p != c) for (int j = 0; j < t; j++) { int x = M[p][j]; M[p][j] = M[c][j]; M[c][j] = x; }
        int iv = INV[M[c][c]];
        for (int i = c + 1; i < t; i++) if (M[i][c]) { int f = MUL[M[i][c]][iv];
            for (int j = c; j < t; j++) M[i][j] = ADD[M[i][j]][NEG[MUL[f][M[c][j]]]]; }
    }
    return 1;
}
/* t-set index by the combinatorial number system */
static int64_t BIN[512][8];
static int64_t rank_set(const int *c) { int64_t x = 0; for (int i = 0; i < t; i++) x += BIN[c[i]][i + 1]; return x; }
static unsigned char *CNT; static int64_t NS, cost;
static uint64_t rs = 88172645463325252ULL;
static inline uint64_t rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static double ur(void) { return (rnd() >> 11) * (1.0 / 9007199254740992.0); }
/* enumerate (t-1)-subsets of columns other than c, sorted, insert c */
static int delta_cell(int r, int c, int newv, int apply) {
    int old = A[r * k + c]; int64_t d = 0; int s[8], full[8];
    for (int i = 0; i < t - 1; i++) s[i] = i;
    for (;;) {
        /* map s (over 0..k-2) to columns skipping c, then insert c */
        int m = 0, placed = 0;
        for (int i = 0; i < t - 1; i++) { int col = s[i] >= c ? s[i] + 1 : s[i];
            if (!placed && c < col) { full[m++] = c; placed = 1; } full[m++] = col; }
        if (!placed) full[m++] = c;
        int64_t id = rank_set(full);
        A[r * k + c] = old; int a = indep(r, full);
        A[r * k + c] = newv; int b = indep(r, full);
        A[r * k + c] = old;
        if (a != b) {
            int cnt = CNT[id], nc = cnt + b - a;
            if (cnt == 0 && nc > 0) d--; else if (cnt > 0 && nc == 0) d++;
            if (apply) CNT[id] = (unsigned char)nc;
        }
        int i = t - 2; while (i >= 0 && s[i] == k - 2 - (t - 2 - i)) i--;
        if (i < 0) break; s[i]++; for (int j = i + 1; j < t - 1; j++) s[j] = s[j - 1] + 1;
    }
    if (apply) A[r * k + c] = newv;
    return (int)d;
}
int main(int argc, char **argv) {
    if (argc < 8) { fprintf(stderr, "usage: cphf_sa n k q t seed max_seconds [T0] [alpha] OUT [INIT]\n"); return 2; }
    n = atoi(argv[1]); k = atoi(argv[2]); q = atoi(argv[3]); t = atoi(argv[4]);
    unsigned seed = atoi(argv[5]); double maxs = atof(argv[6]);
    double T0 = argc > 9 ? atof(argv[7]) : 0.6, alpha = argc > 9 ? atof(argv[8]) : 0.99999;
    const char *out = argc > 9 ? argv[9] : argv[7]; const char *init = argc > 10 ? argv[10] : NULL;
    if (t > 8 || k > 511) { fprintf(stderr, "t <= 8, k <= 511\n"); return 2; }
    if (getenv("SHERWOOD")) SH = 1;
    field(); Q_T = 1; for (int i = 0; i < t; i++) Q_T *= q;
    DIG = malloc((size_t)Q_T * t);
    for (int v = 0; v < Q_T; v++) { int x = v; for (int j = 0; j < t; j++) { DIG[(size_t)v * t + j] = x % q; x /= q; } }
    for (int i = 0; i < 512; i++) { BIN[i][0] = 1; for (int j = 1; j < 8; j++) BIN[i][j] = i ? BIN[i - 1][j - 1] + BIN[i - 1][j] : 0; }
    NS = BIN[k][t]; CNT = calloc(NS, 1); A = malloc(sizeof(int) * n * k);
    rs ^= (uint64_t)seed * 0x9E3779B97F4A7C15ULL; for (int i = 0; i < 20; i++) rnd();
    if (init) { FILE *f = fopen(init, "r"); for (int i = 0; i < n * k; i++) { int v = 0, p = 1; for (int j = 0; j < t; j++) { int d; if (fscanf(f, "%1d", &d) != 1) d = 0; v += d * p; p *= q; } A[i] = v ? v : 1; } fclose(f); }
    else for (int i = 0; i < n * k; i++) A[i] = SH ? 1 + q * (int)(rnd() % (Q_T / q)) : 1 + (int)(rnd() % (Q_T - 1));
    /* initial counts */
    { int c[8]; for (int i = 0; i < t; i++) c[i] = i; cost = 0;
      for (;;) { int64_t id = rank_set(c); int cnt = 0; for (int r = 0; r < n; r++) cnt += indep(r, c); CNT[id] = cnt; if (!cnt) cost++;
        int i = t - 1; while (i >= 0 && c[i] == k - t + i) i--; if (i < 0) break; c[i]++; for (int j = i + 1; j < t; j++) c[j] = c[j - 1] + 1; } }
    fprintf(stderr, "CPHF(%d; %d, %d, %d): %lld t-sets, initial uncovered %lld\n", n, k, q, t, (long long)NS, (long long)cost);
    /* projective representatives: first nonzero digit 1 (scalar multiples behave identically) */
    int *PR = malloc(sizeof(int) * Q_T), NPR = 0;
    for (int v = 1; v < Q_T; v++) { const unsigned char *d = DIG + (size_t)v * t; int j = 0; while (!d[j]) j++; if (d[j] == 1 && (!SH || j == 0)) PR[NPR++] = v; }
    double prep = getenv("PREPAIR") ? atof(getenv("PREPAIR")) : 0.5; int cand = getenv("CAND") ? atoi(getenv("CAND")) : 64;
    if (cand > NPR) cand = NPR;
    int *BA = malloc(sizeof(int) * n * k); memcpy(BA, A, sizeof(int) * n * k);
    clock_t t0 = clock(); double T = T0; int64_t best = cost, it = 0, since = 0;
    while (cost > 0) {
        if ((it & 63) == 0 && (double)(clock() - t0) / CLOCKS_PER_SEC > maxs) break;
        int r, c, nv, d;
        if (ur() < prep) {   /* repair: an uncovered t-set, a random row and one of its columns, best of `cand` vectors */
            int64_t id; do id = (int64_t)(rnd() % (uint64_t)NS); while (CNT[id]);
            int cols[8]; int64_t x = id; for (int i = t; i >= 1; i--) { int cc = i - 1; while (BIN[cc + 1][i] <= x) cc++; cols[i - 1] = cc; x -= BIN[cc][i]; }
            r = rnd() % n; c = cols[rnd() % t];
            int bd = 1 << 30, bv = -1, ties = 0;
            for (int j = 0; j < cand; j++) { int v = cand == NPR ? PR[j] : PR[rnd() % NPR]; if (v == A[r * k + c]) continue;
                int dd = delta_cell(r, c, v, 0);
                if (dd < bd) { bd = dd; bv = v; ties = 1; } else if (dd == bd && rnd() % (++ties) == 0) bv = v; }
            if (bv < 0) continue; nv = bv; d = bd;
        } else { r = rnd() % n; c = rnd() % k; nv = PR[rnd() % NPR]; if (nv == A[r * k + c]) continue; d = delta_cell(r, c, nv, 0); }
        if (d <= 0 || ur() < exp(-d / T)) { delta_cell(r, c, nv, 1); cost += d; }
        it++; T *= alpha; if (T < 0.05) T = T0;
        if (cost < best) { best = cost; since = 0; memcpy(BA, A, sizeof(int) * n * k); }
    }
    if (cost > 0 && getenv("BEST")) { memcpy(A, BA, sizeof(int) * n * k); cost = best; }
    fprintf(stderr, "end cost %lld best %lld iterations %lld time %.1f s\n", (long long)cost, (long long)best, (long long)it, (double)(clock() - t0) / CLOCKS_PER_SEC);
    if (cost == 0 || getenv("BEST")) { FILE *f = fopen(out, "w");
        fprintf(f, "# CPHF(%d; %d, %d, %d) cphf_sa seed %u\n", n, k, q, t, seed);
        for (int r = 0; r < n; r++) { for (int c = 0; c < k; c++) { const unsigned char *d = DIG + (size_t)A[r * k + c] * t; if (c) fputc(' ', f); for (int j = 0; j < t; j++) fputc('0' + d[j], f); } fputc('\n', f); }
        fclose(f); if (cost == 0) { printf("FOUND\n"); return 0; } }
    printf("NOT FOUND %lld\n", (long long)cost); return 1;
}
