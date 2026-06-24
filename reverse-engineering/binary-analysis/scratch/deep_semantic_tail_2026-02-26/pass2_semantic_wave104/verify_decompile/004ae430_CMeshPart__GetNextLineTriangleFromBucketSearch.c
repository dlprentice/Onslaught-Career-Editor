/* address: 0x004ae430 */
/* name: CMeshPart__GetNextLineTriangleFromBucketSearch */
/* signature: int __thiscall CMeshPart__GetNextLineTriangleFromBucketSearch(void * this, int param_1, void * param_2, int param_3) */


int __thiscall
CMeshPart__GetNextLineTriangleFromBucketSearch(void *this,int param_1,void *param_2,int param_3)

{
  short *psVar1;

  if (*(int *)((int)this + 0x100) != 0) {
    psVar1 = (short *)CPolyBucket__GetNextLineTriangle(param_2);
    if (psVar1 != (short *)0x0) {
      *(int *)param_1 = **(int **)(*(int *)((int)this + 0x100) + 0x98) + *psVar1 * 6;
      *(int *)(param_1 + 4) = **(int **)(*(int *)((int)this + 0x100) + 0x98) + psVar1[1] * 6;
      *(int *)(param_1 + 8) = **(int **)(*(int *)((int)this + 0x100) + 0x98) + psVar1[2] * 6;
      return 1;
    }
  }
  return 0;
}
