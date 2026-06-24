/* address: 0x004db090 */
/* name: CEngine__GetPresetScalarByName */
/* signature: double __fastcall CEngine__GetPresetScalarByName(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __fastcall CEngine__GetPresetScalarByName(int param_1)

{
  byte bVar1;
  byte *pbVar2;
  int *piVar3;
  byte *pbVar4;
  int iVar5;
  int iVar6;
  byte *pbVar7;
  bool bVar8;

  pbVar2 = *(byte **)(*(int *)(param_1 + 0xf0) + 8);
  if (pbVar2 != (byte *)0x0) {
    piVar3 = (int *)*DAT_008553f8;
    DAT_008553f8[2] = (int)piVar3;
    if (piVar3 == (int *)0x0) {
      iVar6 = 0;
    }
    else {
      iVar6 = *piVar3;
    }
    while (iVar6 != 0) {
      pbVar7 = *(byte **)(iVar6 + 0x30);
      pbVar4 = pbVar2;
      do {
        bVar1 = *pbVar4;
        bVar8 = bVar1 < *pbVar7;
        if (bVar1 != *pbVar7) {
LAB_004db0e9:
          iVar5 = (1 - (uint)bVar8) - (uint)(bVar8 != 0);
          goto LAB_004db0ee;
        }
        if (bVar1 == 0) break;
        bVar1 = pbVar4[1];
        bVar8 = bVar1 < pbVar7[1];
        if (bVar1 != pbVar7[1]) goto LAB_004db0e9;
        pbVar4 = pbVar4 + 2;
        pbVar7 = pbVar7 + 2;
      } while (bVar1 != 0);
      iVar5 = 0;
LAB_004db0ee:
      if (iVar5 == 0) {
        if (iVar6 != 0) {
          return (double)*(float *)(iVar6 + 0x38);
        }
        break;
      }
      piVar3 = *(int **)(DAT_008553f8[2] + 4);
      DAT_008553f8[2] = (int)piVar3;
      if (piVar3 == (int *)0x0) {
        iVar6 = 0;
      }
      else {
        iVar6 = *piVar3;
      }
    }
  }
  return (double)_DAT_005d856c;
}
