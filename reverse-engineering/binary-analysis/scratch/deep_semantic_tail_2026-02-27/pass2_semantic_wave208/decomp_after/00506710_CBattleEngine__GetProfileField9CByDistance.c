/* address: 0x00506710 */
/* name: CBattleEngine__GetProfileField9CByDistance */
/* signature: double __fastcall CBattleEngine__GetProfileField9CByDistance(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __fastcall CBattleEngine__GetProfileField9CByDistance(int param_1)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int local_8;

  local_8 = (int)(longlong)ROUND(*(float *)(param_1 + 0x60));
  iVar4 = 0;
  local_8 = local_8 / 100;
  iVar5 = local_8 * 4 + 0xc;
  iVar1 = *(int *)(iVar5 + *(int *)(param_1 + 0xa4));
  piVar2 = (int *)*DAT_008553ec;
  DAT_008553ec[2] = (int)piVar2;
  if (piVar2 == (int *)0x0) {
    iVar3 = 0;
  }
  else {
    iVar3 = *piVar2;
  }
  while (iVar3 != 0) {
    if (iVar4 == iVar1) goto joined_r0x00506786;
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
LAB_00506788:
  do {
    do {
      local_8 = local_8 + -1;
      iVar5 = iVar5 + -4;
      if (local_8 < 0) {
        return (double)_DAT_005d856c;
      }
      iVar4 = 0;
      iVar1 = *(int *)(iVar5 + *(int *)(param_1 + 0xa4));
      piVar2 = (int *)*DAT_008553ec;
      DAT_008553ec[2] = (int)piVar2;
      if (piVar2 == (int *)0x0) {
        iVar3 = 0;
      }
      else {
        iVar3 = *piVar2;
      }
    } while (iVar3 == 0);
    do {
      if (iVar4 == iVar1) goto joined_r0x00506786;
      iVar4 = iVar4 + 1;
      piVar2 = *(int **)(DAT_008553ec[2] + 4);
      DAT_008553ec[2] = (int)piVar2;
      if (piVar2 == (int *)0x0) {
        iVar3 = 0;
      }
      else {
        iVar3 = *piVar2;
      }
    } while (iVar3 != 0);
  } while( true );
joined_r0x00506786:
  if (iVar3 != 0) {
    return (double)*(float *)(iVar3 + 0x9c);
  }
  goto LAB_00506788;
}
