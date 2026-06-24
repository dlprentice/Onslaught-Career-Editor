/* address: 0x004aa7e0 */
/* name: CMesh__FindEntryValueByTypeId */
/* signature: double __thiscall CMesh__FindEntryValueByTypeId(void * this, int param_1, int param_2, void * param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __thiscall CMesh__FindEntryValueByTypeId(void *this,int param_1,int param_2,void *param_3)

{
  float fVar1;
  int iVar2;
  int iVar3;

  fVar1 = _DAT_005d856c;
  iVar3 = *(int *)((int)this + 0x18);
  iVar2 = 0;
  if (0 < *(int *)((int)this + 0x14)) {
    do {
      if (*(int *)(iVar3 + 0x10) == param_1) {
        *(int *)param_2 = iVar2;
        return (double)*(float *)(iVar3 + 0x20);
      }
      iVar3 = iVar3 + 0x24;
      iVar2 = iVar2 + 1;
    } while (iVar2 < *(int *)((int)this + 0x14));
  }
  *(undefined4 *)param_2 = 0xffffffff;
  return (double)fVar1;
}
