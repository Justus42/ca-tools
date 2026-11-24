/* ca_profile.c - one exact pass over every t-set of an array, for post-optimization (ca-tools engine, own code).
 * Companion of ca_verify: same question (is every t-tuple covered in every t-set?), more answers:
 *   missing   number of (t-set, tuple) pairs not covered, and with -m FILE the list (columns then tuple)
 *   uniq      for every row, the number of (t-set, tuple) pairs it covers alone (-u FILE, one number per line)
 *   need      cells that are the FIRST occurrence of some tuple in some t-set (-n FILE, N lines of k 0/1);
 *             every other cell is a wildcard, and all wildcards can be changed at once without losing coverage
 *             (the redundancy test of Izquierdo-Marquez et al. 2018, stage 3)
 * Speed: columns enumerated in order with prefix codes per row, so each t-set costs N steps; OpenMP over the first
 * column. usage: ca_profile FILE t v [-m FILE] [-u FILE] [-n FILE] [-threads n]
 * Prints: rows, columns, missing, sets, time. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#ifdef _OPENMP
#include <omp.h>
#endif
static int N, k, t, v, VT; static uint8_t *A;  /* column-major: A[c*N + r] */
int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: ca_profile FILE t v [-m FILE] [-u FILE] [-n FILE] [-threads n]\n"); return 2; }
    t = atoi(argv[2]); v = atoi(argv[3]); const char *mf = NULL, *uf = NULL, *nf = NULL; int th = 0;
    for (int i = 4; i < argc; i++) { if (!strcmp(argv[i], "-m")) mf = argv[++i]; else if (!strcmp(argv[i], "-u")) uf = argv[++i];
        else if (!strcmp(argv[i], "-n")) nf = argv[++i]; else if (!strcmp(argv[i], "-threads")) th = atoi(argv[++i]); }
#ifdef _OPENMP
    if (th > 0) omp_set_num_threads(th);
#endif
    /* read rows */
    FILE *f = fopen(argv[1], "r"); if (!f) { perror("file"); return 2; }
    size_t cap = 1 << 20, len = 0; uint8_t *buf = malloc(cap); int c, cur = -1, inrow = 0, cols = 0; k = 0; N = 0;
    while ((c = fgetc(f)) != EOF) {
        if (c >= '0' && c <= '9') { cur = (cur < 0 ? 0 : cur * 10) + (c - '0'); continue; }
        if (cur >= 0) { if (len == cap) { cap *= 2; buf = realloc(buf, cap); } buf[len++] = cur; cur = -1; cols++; inrow = 1; }
        if (c == '\n' && inrow) { if (!k) k = cols; else if (cols != k) { fprintf(stderr, "row %d has %d columns\n", N, cols); return 2; } N++; cols = 0; inrow = 0; }
    }
    if (cur >= 0) { buf[len++] = cur; cols++; inrow = 1; } if (inrow) { if (!k) k = cols; N++; } fclose(f);
    A = malloc((size_t)N * k); for (int r = 0; r < N; r++) for (int j = 0; j < k; j++) A[(size_t)j * N + r] = buf[(size_t)r * k + j]; free(buf);
    VT = 1; for (int i = 0; i < t; i++) VT *= v;
    int64_t *uniq = calloc(N, sizeof(int64_t)); uint8_t *need = calloc((size_t)N * k, 1);
    long long missing = 0, nsets = 0; FILE *mo = mf ? fopen(mf, "w") : NULL;
    clock_t t0 = clock();
    #pragma omp parallel reduction(+:missing,nsets)
    {
        int32_t **pre = malloc(sizeof(int32_t *) * t); for (int i = 0; i < t; i++) pre[i] = malloc(sizeof(int32_t) * N);
        int32_t *first = malloc(sizeof(int32_t) * VT), *count = malloc(sizeof(int32_t) * VT);
        int64_t *lu = calloc(N, sizeof(int64_t)); uint8_t *ln = calloc((size_t)N * k, 1);
        int cs[8];
        #pragma omp for schedule(dynamic, 1)
        for (int c0 = 0; c0 <= k - t; c0++) {
            cs[0] = c0; for (int r = 0; r < N; r++) pre[0][r] = A[(size_t)c0 * N + r];
            int lvl = 1; cs[1] = c0;   /* depth-first over the remaining columns */
            while (lvl >= 1) {
                cs[lvl]++;
                if (cs[lvl] > k - t + lvl) { lvl--; continue; }
                const uint8_t *col = A + (size_t)cs[lvl] * N; int32_t *p = pre[lvl], *q = pre[lvl - 1];
                for (int r = 0; r < N; r++) p[r] = q[r] * v + col[r];
                if (lvl < t - 1) { lvl++; cs[lvl] = cs[lvl - 1]; continue; }
                /* full t-set: codes in pre[t-1] */
                nsets++;
                for (int x = 0; x < VT; x++) { first[x] = -1; count[x] = 0; }
                for (int r = 0; r < N; r++) { int x = p[r]; if (first[x] < 0) first[x] = r; count[x]++; }
                for (int x = 0; x < VT; x++) {
                    if (first[x] < 0) { missing++;
                        if (mo) {
                            #pragma omp critical
                            { for (int i = 0; i < t; i++) fprintf(mo, "%d ", cs[i]); int y = x; int dg[8]; for (int i = t - 1; i >= 0; i--) { dg[i] = y % v; y /= v; } for (int i = 0; i < t; i++) fprintf(mo, i ? " %d" : "%d", dg[i]); fputc('\n', mo); }
                        }
                        continue; }
                    int r = first[x]; if (count[x] == 1) lu[r]++;
                    for (int i = 0; i < t; i++) ln[(size_t)r * k + cs[i]] = 1;
                }
            }
        }
        #pragma omp critical
        { for (int r = 0; r < N; r++) uniq[r] += lu[r]; for (size_t i = 0; i < (size_t)N * k; i++) need[i] |= ln[i]; }
        for (int i = 0; i < t; i++) free(pre[i]); free(pre); free(first); free(count); free(lu); free(ln);
    }
    if (mo) fclose(mo);
    if (uf) { FILE *o = fopen(uf, "w"); for (int r = 0; r < N; r++) fprintf(o, "%lld\n", (long long)uniq[r]); fclose(o); }
    if (nf) { FILE *o = fopen(nf, "w"); for (int r = 0; r < N; r++) { for (int j = 0; j < k; j++) fputc(need[(size_t)r * k + j] ? '1' : '0', o); fputc('\n', o); } fclose(o); }
    long long wild = 0; for (size_t i = 0; i < (size_t)N * k; i++) wild += !need[i];
    printf("rows %d columns %d t %d v %d sets %lld missing %lld wildcards %lld cpu %.2f s\n", N, k, t, v, nsets, missing, wild, (double)(clock() - t0) / CLOCKS_PER_SEC);
    return missing ? 1 : 0;
}
