/* address: 0x00404790 */
/* name: CAtmospheric__Unk_00404790 */
/* signature: void __fastcall CAtmospheric__Unk_00404790(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CAtmospheric__Unk_00404790(int param_1)

{
  float fVar1;
  float fVar2;
  double dVar3;
  int iVar4;
  int unaff_ESI;
  double dVar5;

  iVar4 = *(int *)(param_1 + 0x14);
  *(undefined4 *)(param_1 + 0xc) = *(undefined4 *)(param_1 + 8);
  if ((iVar4 != 0) && (iVar4 != -1)) {
    fVar1 = *(float *)(param_1 + 0x18) + *(float *)(param_1 + 8);
    fVar2 = (float)_DAT_005d87e0;
    *(float *)(param_1 + 8) = fVar1;
    if (fVar2 <= fVar1) {
      if (((iVar4 < 1) || (10 < iVar4)) && (*(int *)(param_1 + 0x1c) != 1)) {
        iVar4 = (**(code **)(**(int **)(param_1 + 0x20) + 0xec))();
        if ((iVar4 != 0) && (_DAT_005d8568 <= *(float *)(param_1 + 8))) {
          dVar5 = CAtmospheric__Helper_004f3c80
                            (*(void **)(param_1 + 0x20),3,param_1 + 0x10,unaff_ESI);
          *(float *)(param_1 + 0x18) = (float)dVar5;
          dVar3 = _DAT_005d87d8;
          *(undefined4 *)(param_1 + 8) = 0;
          *(undefined4 *)(param_1 + 0x14) = 3;
          if (dVar5 <= dVar3) {
            *(undefined4 *)(param_1 + 0x18) = 0x3f800000;
          }
        }
      }
      else {
        *(float *)(param_1 + 8) = fVar1 - (float)_DAT_005d87e0;
      }
      if (_DAT_005d8568 <= *(float *)(param_1 + 8)) {
        *(undefined4 *)(param_1 + 8) = 0x3f800000;
      }
    }
  }
  return;
}
