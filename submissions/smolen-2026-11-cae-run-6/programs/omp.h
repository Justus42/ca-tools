/* single-thread stand-in for omp.h, used only when the compiler has no OpenMP (engine Mac jobs run one thread per worker) */
#ifndef OMP_STUB_H
#define OMP_STUB_H
#include <sys/time.h>
static inline int omp_get_thread_num(void) { return 0; }
static inline int omp_get_max_threads(void) { return 1; }
static inline int omp_get_num_threads(void) { return 1; }
static inline void omp_set_num_threads(int n) { (void)n; }
static inline double omp_get_wtime(void) { struct timeval tv; gettimeofday(&tv, 0); return tv.tv_sec + tv.tv_usec * 1e-6; }
#endif
