// clq.c: QI graph on a list of columns (strings), randomized greedy + swap local search for a large clique.
// usage: clq POOL seed iters [out]
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
int n,N; uint32_t (*M)[3]; uint64_t *adj; int W;
static inline int qi(int i,int j){ for(int a=0;a<3;a++)for(int b=0;b<3;b++) if(!(M[i][a]&M[j][b])) return 0; return 1; }
static inline int A(int i,int j){ return adj[(size_t)i*W+(j>>6)]>>(j&63)&1; }
uint64_t s=88172645463325252ULL; static inline uint64_t rnd(){ s^=s<<13; s^=s>>7; s^=s<<17; return s; }
int main(int argc,char**argv){ FILE*f=fopen(argv[1],"r"); char line[256]; int cap=1<<17; M=malloc(cap*12); char **str=malloc(cap*sizeof(char*)); n=0;
  while(fgets(line,sizeof line,f)){ int L=strcspn(line,"\n"); if(!L)continue; N=L; if(n==cap){cap*=2;M=realloc(M,cap*12);str=realloc(str,cap*sizeof(char*));} M[n][0]=M[n][1]=M[n][2]=0; for(int r=0;r<L;r++) M[n][line[r]-'0']|=1u<<r; line[L]=0; str[n]=strdup(line); n++; }
  s^=atoll(argv[2])*0x9E3779B97F4A7C15ULL; long iters=atol(argv[3]);
  W=(n+63)/64; adj=calloc((size_t)n*W,8); long ne=0;
  for(int i=0;i<n;i++) for(int j=i+1;j<n;j++) if(qi(i,j)){ adj[(size_t)i*W+(j>>6)]|=1ULL<<(j&63); adj[(size_t)j*W+(i>>6)]|=1ULL<<(i&63); ne++; }
  fprintf(stderr,"n %d edges %ld density %.4f\n",n,ne,2.0*ne/((double)n*(n-1)));
  // local search: clique C; cand = common neighbours; when empty, try 1-swaps (vertices adjacent to all but one), plateau walk with tabu
  int *C=malloc(n*sizeof(int)),nc=0,*inC=calloc(n,sizeof(int)),*miss=calloc(n,sizeof(int)),*tabu=calloc(n,sizeof(int)); int best=0; int *bestC=malloc(n*sizeof(int));
  // miss[v] = number of clique members not adjacent to v
  #define ADD(v) do{ inC[v]=1; C[nc++]=v; for(int u=0;u<n;u++) if(u!=v && !A(v,u)) miss[u]++; }while(0)
  #define DEL(idx) do{ int v=C[idx]; C[idx]=C[--nc]; inC[v]=0; for(int u=0;u<n;u++) if(u!=v && !A(v,u)) miss[u]--; }while(0)
  int *lst=malloc(n*sizeof(int));
  for(long it=1;it<=iters;it++){
    int m=0; for(int u=0;u<n;u++) if(!inC[u]&&miss[u]==0) lst[m++]=u;
    if(m){ int v=lst[rnd()%m]; ADD(v); if(nc>best){best=nc;memcpy(bestC,C,nc*sizeof(int)); fprintf(stderr,"it %ld clique %d\n",it,best);} continue; }
    m=0; for(int u=0;u<n;u++) if(!inC[u]&&miss[u]==1&&tabu[u]<it) lst[m++]=u;
    if(m && (rnd()%100)<98){ int v=lst[rnd()%m]; int k; for(k=0;k<nc;k++) if(!A(v,C[k])) break; int w=C[k]; DEL(k); ADD(v); tabu[w]=it+1+rnd()%10; continue; }
    if(nc){ int k=rnd()%nc; int w=C[k]; DEL(k); tabu[w]=it+1+rnd()%10; }
  }
  fprintf(stderr,"best %d\n",best);
  if(argc>4){ FILE*o=fopen(argv[4],"w"); for(int i=0;i<best;i++) fprintf(o,"%s\n",str[bestC[i]]); fclose(o); }
  return 0; }
