/* address: 0x0044c810 */
/* name: CSquadNormal__FindNearestFreeCellSpiral */
/* signature: void __thiscall CSquadNormal__FindNearestFreeCellSpiral(void * this, int param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CSquadNormal__FindNearestFreeCellSpiral(void *this,int param_1,void *param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int *piVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int local_20;
  int local_8;

  local_8 = (int)(longlong)ROUND(*(float *)param_1);
  iVar2 = local_8 + (local_8 >> 0x1f & 7U);
  local_8 = (int)(longlong)ROUND(*(float *)(param_1 + 4));
  iVar2 = iVar2 >> 3;
  iVar3 = (int)(local_8 + (local_8 >> 0x1f & 7U)) >> 3;
  if ((((iVar2 < 0) || (iVar3 < 0)) || (0x3f < iVar2)) || (0x3f < iVar3)) {
    return;
  }
  iVar9 = iVar3 - iVar2;
  iVar5 = iVar2 << 6;
  iVar8 = iVar2 - iVar3;
  local_20 = 0;
  do {
    for (iVar7 = iVar9 + iVar2; iVar7 <= iVar3; iVar7 = iVar7 + 1) {
      if (((-1 < iVar7) && (iVar7 < 0x40)) && (iVar1 = iVar8 + iVar3, iVar2 <= iVar1)) {
        piVar6 = (int *)((int)this + (iVar5 + iVar7) * 4 + 8);
        iVar4 = iVar2;
        do {
          if (((-1 < iVar4) && (iVar4 < 0x40)) && (*piVar6 == 0)) {
            if (local_20 < 1) {
              return;
            }
            *(float *)param_1 = (float)iVar4 * _DAT_005d8c44;
            *(float *)(param_1 + 4) = (float)iVar7 * _DAT_005d8c44;
            return;
          }
          iVar4 = iVar4 + 1;
          piVar6 = piVar6 + 0x40;
        } while (iVar4 <= iVar1);
      }
    }
    iVar5 = iVar5 + -0x40;
    local_20 = local_20 + 1;
    iVar2 = iVar2 + -1;
    iVar3 = iVar3 + 1;
    if (0x3f < local_20) {
      return;
    }
  } while( true );
}
