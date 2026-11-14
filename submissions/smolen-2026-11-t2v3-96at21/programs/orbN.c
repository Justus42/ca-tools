// orb63.c: exact census of group-orbit covering arrays CA(N;2,k,3), N<=20 rows.
// Group given by generators: lines "p0 p1 ... p19 s0 s1 s2" (row r -> p[r], symbol x -> s[x]).
// (g c)(p[r]) = s(c[r]).  Stage 1: all self-compatible columns up to S3 relabel and group orbit. Writes reps.
// usage: orb63 GENFILE OUT [minorb]
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#ifndef N
#define N 20
#endif
#define NH (N-10)
#define P3H (NH==10?59049:177147)
#define MAXG 256
typedef struct { unsigned char p[N], s[3]; } El;
El G[MAXG]; int ng=0;
static int eq(El*a,El*b){return !memcmp(a,b,sizeof(El));}
static El mul(El a,El b){El c;for(int r=0;r<N;r++)c.p[r]=a.p[b.p[r]];for(int x=0;x<3;x++)c.s[x]=a.s[b.s[x]];return c;}
// lookup tables: for element g, symbol-independent row permutation of 20-bit mask
static uint32_t T[MAXG][2][2048];
static inline uint32_t pm(int g,uint32_t m){return T[g][0][m&1023]|T[g][1][m>>10];}
int main(int argc,char**argv){
  FILE*f=fopen(argv[1],"r"); El gens[8]; int ngen=0; int v;
  while(1){ El e; int ok=1; for(int r=0;r<N;r++){ if(fscanf(f,"%d",&v)!=1){ok=0;break;} e.p[r]=v;} if(!ok)break; for(int x=0;x<3;x++){fscanf(f,"%d",&v);e.s[x]=v;} gens[ngen++]=e; }
  fclose(f);
  El id; for(int r=0;r<N;r++)id.p[r]=r; for(int x=0;x<3;x++)id.s[x]=x; G[ng++]=id;
  for(int i=0;i<ng;i++) for(int j=0;j<ngen;j++){ El c=mul(gens[j],G[i]); int k; for(k=0;k<ng;k++) if(eq(&c,&G[k]))break; if(k==ng){ if(ng>=MAXG){fprintf(stderr,"group too big\n");return 1;} G[ng++]=c; } }
  fprintf(stderr,"group order %d\n",ng);
  for(int g=0;g<ng;g++) for(int h=0;h<2;h++) for(int m=0;m<(h?(1<<NH):1024);m++){ uint32_t o=0; for(int b=0;b<(h?NH:10);b++) if(m>>b&1) o|=1u<<G[g].p[h*10+b]; T[g][h][m]=o; }
  // inverse pairs: only test one of g, g^-1
  int use[MAXG]; int nu=0; int inv[MAXG];
  for(int g=0;g<ng;g++){ for(int h=0;h<ng;h++){ El c=mul(G[g],G[h]); if(eq(&c,&id)){inv[g]=h;break;} } }
  for(int g=1;g<ng;g++) if(inv[g]>=g) use[nu++]=g;
  // enumerate columns: half tables
  static uint32_t H[2][P3H][3];
  for(int h=0;h<2;h++) for(int w=0;w<(h?P3H:59049);w++){ int x=w; uint32_t m[3]={0,0,0}; for(int b=0;b<(h?NH:10);b++){ m[x%3]|=1u<<(h*10+b); x/=3;} for(int a=0;a<3;a++)H[h][w][a]=m[a]; }
  FILE*out=fopen(argv[2],"w"); long cnt=0,nrep=0; long hist[MAXG+1]; memset(hist,0,sizeof hist);
  int lo_b=argc>3?atoi(argv[3]):0;
  for(int hi=0;hi<P3H;hi++) for(int lo=0;lo<59049;lo++){
    uint32_t m[3]; for(int a=0;a<3;a++) m[a]=H[0][lo][a]|H[1][hi][a];
    if(!m[0]||!m[1]||!m[2]) continue;
    // normalized: row0 has symbol 0; first non-0 row has symbol 1
    if(!(m[0]&1)) continue;
    { uint32_t n0=~m[0]&((1u<<N)-1); int fr=__builtin_ctz(n0); if(!(m[1]>>fr&1)) continue; }
    if(lo_b){ int a=__builtin_popcount(m[0]),b=__builtin_popcount(m[1]),c=__builtin_popcount(m[2]); if(a<lo_b||b<lo_b||c<lo_b) continue; }
    int ok=1, stab=1;
    for(int u=0;u<nu&&ok;u++){ int g=use[u]; uint32_t gm[3]; // (g c) has symbol s(a) on rows p(m[a])
      for(int a=0;a<3;a++) gm[G[g].s[a]]=pm(g,m[a]);
      if((gm[0]==m[0]||gm[0]==m[1]||gm[0]==m[2])&&(gm[1]==m[0]||gm[1]==m[1]||gm[1]==m[2])){ stab+= (inv[g]==g)?1:2; continue; }
      for(int a=0;a<3&&ok;a++) for(int b=0;b<3;b++) if(!(m[a]&gm[b])){ok=0;break;}
    }
    if(!ok) continue; cnt++;
    // canonical under group orbit + relabel: compare normalized masks of g c
    int canon=1; uint64_t key=((uint64_t)m[0]<<20)|m[1];
    for(int g=1;g<ng&&canon;g++){ uint32_t gm[3]; for(int a=0;a<3;a++) gm[G[g].s[a]]=pm(g,m[a]);
      // normalize: symbol of row 0 -> 0; first other -> 1
      int s0=(gm[0]&1)?0:(gm[1]&1)?1:2; uint32_t n0=~gm[s0]&((1u<<N)-1); int fr=__builtin_ctz(n0); int s1=-1; for(int a=0;a<3;a++) if(a!=s0&&(gm[a]>>fr&1)) s1=a;
      uint64_t k2=((uint64_t)gm[s0]<<20)|gm[s1]; if(k2<key) canon=0; }
    if(!canon) continue; nrep++; hist[stab]++;
    fprintf(out,"%u %u %u %d\n",m[0],m[1],m[2],ng/stab);
  }
  fclose(out); fprintf(stderr,"self-compatible normalized columns %ld, orbit reps %ld\n",cnt,nrep);
  for(int s=1;s<=ng;s++) if(hist[s]) fprintf(stderr,"  stabilizer %d (orbit %d): %ld reps\n",s,ng/s,hist[s]);
  return 0;
}
