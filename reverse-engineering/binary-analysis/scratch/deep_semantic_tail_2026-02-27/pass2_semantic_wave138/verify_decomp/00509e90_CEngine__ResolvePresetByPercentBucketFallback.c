/* address: 0x00509e90 */
/* name: CEngine__ResolvePresetByPercentBucketFallback */
/* signature: int __fastcall CEngine__ResolvePresetByPercentBucketFallback(int param_1) */


int __fastcall CEngine__ResolvePresetByPercentBucketFallback(int param_1)

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
  do {
    if (iVar3 == 0) {
LAB_00509f08:
      do {
        local_8 = local_8 + -1;
        iVar5 = iVar5 + -4;
        if (local_8 < 0) {
          return 0;
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
        while (iVar3 != 0) {
          if (iVar4 == iVar1) {
            if (iVar3 != 0) {
              return iVar3;
            }
            break;
          }
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
    }
    if (iVar4 == iVar1) {
      if (iVar3 != 0) {
        return iVar3;
      }
      goto LAB_00509f08;
    }
    iVar4 = iVar4 + 1;
    piVar2 = *(int **)(DAT_008553ec[2] + 4);
    DAT_008553ec[2] = (int)piVar2;
    if (piVar2 == (int *)0x0) {
      iVar3 = 0;
    }
    else {
      iVar3 = *piVar2;
    }
  } while( true );
}
