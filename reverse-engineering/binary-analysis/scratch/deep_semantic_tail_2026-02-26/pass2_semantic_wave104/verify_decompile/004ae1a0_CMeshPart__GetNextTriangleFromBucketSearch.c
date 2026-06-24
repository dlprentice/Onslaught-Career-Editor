/* address: 0x004ae1a0 */
/* name: CMeshPart__GetNextTriangleFromBucketSearch */
/* signature: int __thiscall CMeshPart__GetNextTriangleFromBucketSearch(void * this, int param_1, void * param_2) */


int __thiscall CMeshPart__GetNextTriangleFromBucketSearch(void *this,int param_1,void *param_2)

{
  short *psVar1;

  if (*(int *)((int)this + 0x100) != 0) {
    psVar1 = (short *)CPolyBucket__GetNextTriangle();
    if (psVar1 != (short *)0x0) {
      *(int *)param_1 = **(int **)(*(int *)((int)this + 0x100) + 0x98) + *psVar1 * 6;
      *(int *)(param_1 + 4) = **(int **)(*(int *)((int)this + 0x100) + 0x98) + psVar1[1] * 6;
      *(int *)(param_1 + 8) = **(int **)(*(int *)((int)this + 0x100) + 0x98) + psVar1[2] * 6;
      return 1;
    }
  }
  return 0;
}
