/* address: 0x004b0c40 */
/* name: CMeshPart__FindNearestVertexIndex */
/* signature: int __thiscall CMeshPart__FindNearestVertexIndex(void * this, int param_1, float param_2, float param_3, float param_4) */


int __thiscall
CMeshPart__FindNearestVertexIndex(void *this,int param_1,float param_2,float param_3,float param_4)

{
  float fVar1;
  float *pfVar2;
  int iVar3;
  int iVar4;
  float local_4;

  if ((*(undefined4 **)((int)this + 0x84) != (undefined4 *)0x0) &&
     (pfVar2 = (float *)**(undefined4 **)((int)this + 0x84), pfVar2 != (float *)0x0)) {
    iVar4 = 0;
    iVar3 = 0;
    local_4 = 99999.0;
    if (0 < *(int *)((int)this + 0xac)) {
      do {
        fVar1 = SQRT((*pfVar2 - (float)param_1) * (*pfVar2 - (float)param_1) +
                     (pfVar2[1] - param_2) * (pfVar2[1] - param_2) +
                     (pfVar2[2] - param_3) * (pfVar2[2] - param_3));
        if (fVar1 < local_4) {
          iVar4 = iVar3;
          local_4 = fVar1;
        }
        iVar3 = iVar3 + 1;
        pfVar2 = pfVar2 + 4;
      } while (iVar3 < *(int *)((int)this + 0xac));
    }
    return iVar4;
  }
  return 0;
}
