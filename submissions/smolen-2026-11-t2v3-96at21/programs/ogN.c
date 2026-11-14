// og.c: orbit graph. usage: og GENFILE REPS EDGES_OUT ; prints edge count, degree stats; writes edges "i j"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#ifndef N
#define N 20
#endif
#define MAXG 256
typedef struct { unsigned char p[N], s[3]; } El;
El G[MAXG]; int ng=0;
static int eq(El*a,El*b){return !memcmp(a,b,sizeof(El));}
static El mul(El a,El b){El c;for(int r=0;r<N;r++)c.p[r]=a.p[b.p[r]];for(int x=0;x<3;x++)c.s[x]=a.s[b.s[x]];return c;}
int main(int argc,char**argv){
  FILE*f=fopen(argv[1],"r"); El gens[8]; int ngen=0; int v;
  while(1){ El e; int ok=1; for(int r=0;r<N;r++){ if(fscanf(f,"%d",&v)!=1){ok=0;break;} e.p[r]=v;} if(!ok)break; for(int x=0;x<3;x++){if(fscanf(f,"%d",&v)!=1)return 1;e.s[x]=v;} gens[ngen++]=e; }
  fclose(f);
  El id; for(int r=0;r<N;r++)id.p[r]=r; for(int x=0;x<3;x++)id.s[x]=x; G[ng++]=id;
  for(int i=0;i<ng;i++) for(int j=0;j<ngen;j++){ El c=mul(gens[j],G[i]); int k; for(k=0;k<ng;k++) if(eq(&c,&G[k]))break; if(k==ng) G[ng++]=c; }
  f=fopen(argv[2],"r"); int cap=1<<20,n=0; uint32_t (*M)[3]=malloc(sizeof(uint32_t[3])*cap); int *osz=malloc(sizeof(int)*cap);
  while(fscanf(f,"%u %u %u %d",&M[n][0],&M[n][1],&M[n][2],&osz[n])==4){ n++; if(n==cap){cap*=2;M=realloc(M,sizeof(uint32_t[3])*cap);osz=realloc(osz,sizeof(int)*cap);} }
  fclose(f);
  // images: for each rep j, all ng images (masks by symbol; relabel irrelevant)
  uint32_t (*I)[3]=malloc(sizeof(uint32_t[3])*(size_t)n*ng);
  for(int j=0;j<n;j++) for(int g=0;g<ng;g++){ uint32_t o[3]={0,0,0}; for(int a=0;a<3;a++){ uint32_t m=M[j][a]; while(m){int b=__builtin_ctz(m); m&=m-1; o[a]|=1u<<G[g].p[b];} } memcpy(I[(size_t)j*ng+g],o,12); }
  FILE*out=fopen(argv[3],"w"); long ne=0;
  for(int i=0;i<n;i++){ uint32_t a0=M[i][0],a1=M[i][1],a2=M[i][2];
    for(int j=i+1;j<n;j++){ uint32_t (*J)[3]=&I[(size_t)j*ng]; int ok=1;
      for(int g=0;g<ng;g++){ uint32_t b0=J[g][0],b1=J[g][1],b2=J[g][2];
        if(!(a0&b0)||!(a0&b1)||!(a0&b2)||!(a1&b0)||!(a1&b1)||!(a1&b2)||!(a2&b0)||!(a2&b1)||!(a2&b2)){ok=0;break;} }
      if(ok){ ne++; fprintf(out,"%d %d\n",i,j);} } }
  fclose(out); fprintf(stderr,"reps %d edges %ld\n",n,ne); return 0; }
