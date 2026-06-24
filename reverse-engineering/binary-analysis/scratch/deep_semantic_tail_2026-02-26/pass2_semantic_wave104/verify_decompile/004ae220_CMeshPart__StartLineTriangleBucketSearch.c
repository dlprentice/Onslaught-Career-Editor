/* address: 0x004ae220 */
/* name: CMeshPart__StartLineTriangleBucketSearch */
/* signature: int __thiscall CMeshPart__StartLineTriangleBucketSearch(void * this, int param_1, int param_2, int param_3, void * param_4) */


int __thiscall
CMeshPart__StartLineTriangleBucketSearch
          (void *this,int param_1,int param_2,int param_3,void *param_4)

{
  short *psVar1;

  if (*(int *)((int)this + 0x100) == 0) {
    return 0;
  }
  psVar1 = (short *)CPolyBucket__StartLineSearch(param_1,param_2);
  if (psVar1 == (short *)0x0) {
    return 0;
  }
  *(int *)param_3 = **(int **)(*(int *)((int)this + 0x100) + 0x98) + *psVar1 * 6;
  *(int *)(param_3 + 4) = **(int **)(*(int *)((int)this + 0x100) + 0x98) + psVar1[1] * 6;
  *(int *)(param_3 + 8) = **(int **)(*(int *)((int)this + 0x100) + 0x98) + psVar1[2] * 6;
  return 1;
}
