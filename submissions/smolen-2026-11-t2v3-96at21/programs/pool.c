// pool.c: all columns (normalized up to relabel) QI with every column of ARRAY. usage: pool ARRAY > pool.txt
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAXN 32
#define MAXK 512
int N,K; int A[MAXN][MAXK]; int c[MAXN]; long cnt=0,nodes=0;
unsigned short cov[MAXN+1][MAXK];
void dfs(int r,int nsym){
  if(r==N){ if(nsym<3)return; cnt++; for(int i=0;i<N;i++)putchar('0'+c[i]); putchar('\n'); return; }
  nodes++;
  int rem=N-r-1;
  for(int s=0;s<=nsym&&s<3;s++){ c[r]=s; int ok=1;
    for(int j=0;j<K;j++){ unsigned short m=cov[r][j]|(1<<(s*3+A[r][j])); cov[r+1][j]=m; if(9-__builtin_popcount(m)>rem){ok=0;break;} }
    if(ok) dfs(r+1,s==nsym?nsym+1:nsym); }
}
int main(int argc,char**argv){ FILE*f=fopen(argv[1],"r"); char line[8192]; N=0;
  while(fgets(line,sizeof line,f)){ int k=0; for(char*p=line;*p;p++) if(*p>='0'&&*p<='2') A[N][k++]=*p-'0'; if(k){K=k;N++;} }
  memset(cov,0,sizeof cov); dfs(0,0); fprintf(stderr,"N %d K %d pool %ld nodes %ld\n",N,K,cnt,nodes); return 0; }
