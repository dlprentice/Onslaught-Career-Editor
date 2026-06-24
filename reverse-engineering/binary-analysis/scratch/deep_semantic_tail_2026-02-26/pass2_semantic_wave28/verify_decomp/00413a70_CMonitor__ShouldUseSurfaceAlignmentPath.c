/* address: 0x00413a70 */
/* name: CMonitor__ShouldUseSurfaceAlignmentPath */
/* signature: int __fastcall CMonitor__ShouldUseSurfaceAlignmentPath(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __fastcall CMonitor__ShouldUseSurfaceAlignmentPath(int param_1)

{
  int *piVar1;
  int iVar2;
  float *pfVar3;
  float unaff_EDI;
  double dVar4;
  double dVar5;
  float fStack_24;
  float fStack_20;
  float fStack_1c;
  undefined1 auStack_10 [16];

  iVar2 = (**(code **)(**(int **)(param_1 + 0x20) + 0x10c))();
  if (iVar2 != 0) {
    iVar2 = HeightDelta__Below015_D4(*(int *)(param_1 + 0x20));
    if (iVar2 == 0) {
      fStack_24 = DAT_006fbdfc;
      dVar4 = CStaticShadows__Helper_0047eb80(0x6fadc8,(void *)(*(int *)(param_1 + 0x20) + 0x1c));
      if (dVar4 - (double)fStack_24 <= (double)_DAT_005d8cb4) {
        piVar1 = *(int **)(param_1 + 0x20);
        pfVar3 = (float *)(**(code **)(*piVar1 + 0x6c))(auStack_10);
        fStack_1c = pfVar3[2] + (float)piVar1[9];
        fStack_20 = pfVar3[1] + (float)piVar1[8];
        fStack_24 = (float)piVar1[7] + *pfVar3;
        dVar4 = CStaticShadows__Helper_0047eb80(0x6fadc8,&fStack_24);
        if ((double)_DAT_005d8cb4 < dVar4 - (double)unaff_EDI) {
          return 1;
        }
      }
      else {
        piVar1 = *(int **)(param_1 + 0x20);
        pfVar3 = (float *)(**(code **)(*piVar1 + 0x6c))(auStack_10);
        fStack_1c = pfVar3[2] + (float)piVar1[9];
        fStack_20 = pfVar3[1] + (float)piVar1[8];
        fStack_24 = (float)piVar1[7] + *pfVar3;
        dVar4 = CStaticShadows__Helper_0047eb80(0x6fadc8,(void *)(*(int *)(param_1 + 0x20) + 0x1c));
        dVar5 = CStaticShadows__Helper_0047eb80(0x6fadc8,&fStack_24);
        if ((double)(float)dVar4 < dVar5) {
          return 1;
        }
      }
    }
  }
  return 0;
}
