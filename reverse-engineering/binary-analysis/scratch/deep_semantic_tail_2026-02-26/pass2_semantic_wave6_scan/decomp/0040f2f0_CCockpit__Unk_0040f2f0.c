/* address: 0x0040f2f0 */
/* name: CCockpit__Unk_0040f2f0 */
/* signature: int __cdecl CCockpit__Unk_0040f2f0(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __cdecl CCockpit__Unk_0040f2f0(int param_1)

{
  byte bVar1;
  int *piVar2;
  byte *pbVar3;
  int iVar4;
  int iVar5;
  byte *pbVar6;
  bool bVar7;

  if ((param_1 < 0) || (DAT_00660250 <= param_1)) {
    param_1 = 0;
  }
  piVar2 = DAT_006602a0;
  if (DAT_006602a0 == (int *)0x0) {
    iVar5 = 0;
  }
  else {
    iVar5 = *DAT_006602a0;
  }
  do {
    if (iVar5 == 0) {
LAB_0040f380:
      iVar5 = 0;
      _DAT_006602a8 = DAT_006602a0;
      if (DAT_006602a0 == (int *)0x0) {
        iVar4 = 0;
      }
      else {
        iVar4 = *DAT_006602a0;
      }
      while( true ) {
        if (iVar4 == 0) {
          return 0;
        }
        if (iVar5 == 0) break;
        _DAT_006602a8 = (int *)_DAT_006602a8[1];
        iVar5 = iVar5 + -1;
        if (_DAT_006602a8 == (int *)0x0) {
          iVar4 = 0;
        }
        else {
          iVar4 = *_DAT_006602a8;
        }
      }
      return iVar4;
    }
    pbVar3 = *(byte **)(iVar5 + 0xa8);
    pbVar6 = (byte *)(&DAT_00660200)[param_1];
    do {
      bVar1 = *pbVar3;
      bVar7 = bVar1 < *pbVar6;
      if (bVar1 != *pbVar6) {
LAB_0040f35d:
        iVar4 = (1 - (uint)bVar7) - (uint)(bVar7 != 0);
        goto LAB_0040f362;
      }
      if (bVar1 == 0) break;
      bVar1 = pbVar3[1];
      bVar7 = bVar1 < pbVar6[1];
      if (bVar1 != pbVar6[1]) goto LAB_0040f35d;
      pbVar3 = pbVar3 + 2;
      pbVar6 = pbVar6 + 2;
    } while (bVar1 != 0);
    iVar4 = 0;
LAB_0040f362:
    if (iVar4 == 0) {
      if (iVar5 != 0) {
        _DAT_006602a8 = piVar2;
        return iVar5;
      }
      goto LAB_0040f380;
    }
    piVar2 = (int *)piVar2[1];
    if (piVar2 == (int *)0x0) {
      iVar5 = 0;
    }
    else {
      iVar5 = *piVar2;
    }
  } while( true );
}
