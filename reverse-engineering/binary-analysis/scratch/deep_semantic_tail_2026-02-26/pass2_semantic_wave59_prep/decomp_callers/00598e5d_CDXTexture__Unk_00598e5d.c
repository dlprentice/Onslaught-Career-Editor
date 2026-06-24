/* address: 0x00598e5d */
/* name: CDXTexture__Unk_00598e5d */
/* signature: int __thiscall CDXTexture__Unk_00598e5d(void * this, void * param_1, int param_2) */


int __thiscall CDXTexture__Unk_00598e5d(void *this,void *param_1,int param_2)

{
  int iVar1;
  bool bVar2;
  undefined3 extraout_var;
  uint uVar3;
  int iVar4;
  int extraout_EDX;
  int unaff_EBX;
  int *piVar5;
  int *piVar6;

  bVar2 = CMeshCollisionVolume__Unk_00598749(this,(int)param_1,unaff_EBX);
  if (CONCAT31(extraout_var,bVar2) != 0) {
    iVar1 = *(int *)(extraout_EDX + 0x10);
    if (iVar1 == *(int *)((int)param_1 + 0x10)) {
      iVar4 = 4;
      bVar2 = true;
      piVar5 = (int *)(extraout_EDX + 0x10);
      piVar6 = (int *)((int)param_1 + 0x10);
      do {
        if (iVar4 == 0) break;
        iVar4 = iVar4 + -1;
        bVar2 = *piVar5 == *piVar6;
        piVar5 = piVar5 + 1;
        piVar6 = piVar6 + 1;
      } while (bVar2);
      if ((bVar2) ||
         ((iVar1 == 4 &&
          (uVar3 = CTexture__Helper_0059877f
                             (*(void **)(extraout_EDX + 0x18),*(int *)((int)param_1 + 0x18)),
          uVar3 != 0)))) {
        return 1;
      }
    }
  }
  return 0;
}
