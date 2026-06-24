/* address: 0x005061f0 */
/* name: CEngine__Unk_005061f0 */
/* signature: bool __thiscall CEngine__Unk_005061f0(void * this, int param_1, int param_2) */


bool __thiscall CEngine__Unk_005061f0(void *this,int param_1,int param_2)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int local_8;

  if (*(int *)(param_1 + 0x214) == 0) {
    return false;
  }
  iVar5 = *(int *)(param_1 + 0x164);
  if (((iVar5 == 0) || (*(int *)(iVar5 + 300) == 0)) && (*(int *)(param_1 + 0x228) != 0)) {
    return false;
  }
  if (*(int *)(param_1 + 0x22c) != 0) {
    return false;
  }
  if ((iVar5 != 0) && (*(int *)(iVar5 + 0x114) == 0)) {
    return false;
  }
  local_8 = (int)(longlong)ROUND(*(float *)((int)this + 0x60));
  iVar4 = 0;
  local_8 = local_8 / 100;
  iVar5 = local_8 * 4 + 0xc;
  iVar1 = *(int *)(iVar5 + *(int *)((int)this + 0xa4));
  piVar2 = (int *)*DAT_008553ec;
  DAT_008553ec[2] = (int)piVar2;
  if (piVar2 == (int *)0x0) {
    iVar3 = 0;
  }
  else {
    iVar3 = *piVar2;
  }
  while( true ) {
    if (iVar3 == 0) goto LAB_005062d0;
    if (iVar4 == iVar1) break;
    iVar4 = iVar4 + 1;
    piVar2 = *(int **)(DAT_008553ec[2] + 4);
    DAT_008553ec[2] = (int)piVar2;
    if (piVar2 == (int *)0x0) {
      iVar3 = 0;
    }
    else {
      iVar3 = *piVar2;
    }
  }
joined_r0x005062ce:
  if (iVar3 == 0) {
LAB_005062d0:
    while( true ) {
      local_8 = local_8 + -1;
      iVar5 = iVar5 + -4;
      if (local_8 < 0) break;
      iVar4 = 0;
      iVar1 = *(int *)(iVar5 + *(int *)((int)this + 0xa4));
      piVar2 = (int *)*DAT_008553ec;
      DAT_008553ec[2] = (int)piVar2;
      if (piVar2 == (int *)0x0) {
        iVar3 = 0;
      }
      else {
        iVar3 = *piVar2;
      }
      while (iVar3 != 0) {
        if (iVar4 == iVar1) goto joined_r0x005062ce;
        iVar4 = iVar4 + 1;
        piVar2 = *(int **)(DAT_008553ec[2] + 4);
        DAT_008553ec[2] = (int)piVar2;
        if (piVar2 == (int *)0x0) {
          iVar3 = 0;
        }
        else {
          iVar3 = *piVar2;
        }
      }
    }
    iVar3 = 0;
  }
  return (*(uint *)(iVar3 + 0xa4) & *(uint *)(param_1 + 0x34)) != 0;
}
