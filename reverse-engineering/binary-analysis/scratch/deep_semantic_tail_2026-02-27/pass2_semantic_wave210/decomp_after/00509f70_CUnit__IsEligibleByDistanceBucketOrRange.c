/* address: 0x00509f70 */
/* name: CUnit__IsEligibleByDistanceBucketOrRange */
/* signature: int __fastcall CUnit__IsEligibleByDistanceBucketOrRange(int param_1) */


int __fastcall CUnit__IsEligibleByDistanceBucketOrRange(int param_1)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int local_8;

  if (*(int *)(param_1 + 0xa0) != 0) {
    if (DAT_00672fd0 <= *(float *)(param_1 + 100)) {
      return 0;
    }
    return 1;
  }
  local_8 = (int)(longlong)ROUND(*(float *)(param_1 + 0x60));
  iVar4 = 0;
  local_8 = local_8 / 100;
  iVar1 = *(int *)(*(int *)(param_1 + 0xa4) + 0xc + local_8 * 4);
  iVar5 = local_8 * 4 + 0xc;
  piVar2 = (int *)*DAT_008553ec;
  DAT_008553ec[2] = (int)piVar2;
  if (piVar2 == (int *)0x0) {
    iVar3 = 0;
  }
  else {
    iVar3 = *piVar2;
  }
  while (iVar3 != 0) {
    if (iVar4 == iVar1) goto joined_r0x0050a012;
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
LAB_0050a014:
  do {
    local_8 = local_8 + -1;
    iVar5 = iVar5 + -4;
    if (local_8 < 0) {
      return 0;
    }
    iVar4 = 0;
    iVar1 = *(int *)(*(int *)(param_1 + 0xa4) + iVar5);
    piVar2 = (int *)*DAT_008553ec;
    DAT_008553ec[2] = (int)piVar2;
    if (piVar2 == (int *)0x0) {
      iVar3 = 0;
    }
    else {
      iVar3 = *piVar2;
    }
    while (iVar3 != 0) {
      if (iVar4 == iVar1) goto joined_r0x0050a012;
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
  } while( true );
joined_r0x0050a012:
  if (iVar3 != 0) {
    return 1;
  }
  goto LAB_0050a014;
}
