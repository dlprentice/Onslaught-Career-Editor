/* address: 0x0046baf0 */
/* name: CFEPWingmen__UpdateSpinnerTransformAndPulse */
/* signature: void __fastcall CFEPWingmen__UpdateSpinnerTransformAndPulse(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CFEPWingmen__UpdateSpinnerTransformAndPulse(int param_1)

{
  float fVar1;
  int iVar2;
  float10 fVar3;
  float10 fVar4;
  undefined4 local_4;

  fVar3 = (float10)fcos((float10)(DAT_00672fd0 * _DAT_005d8c68));
  fVar4 = (float10)fsin((float10)(DAT_00672fd0 * _DAT_005d8c68));
  *(float *)(param_1 + 0x14) = (float)fVar3;
  *(float *)(param_1 + 0x18) = (float)-fVar4;
  *(undefined4 *)(param_1 + 0x1c) = 0;
  *(undefined4 *)(param_1 + 0x20) = local_4;
  *(float *)(param_1 + 0x24) = (float)fVar4;
  *(float *)(param_1 + 0x28) = (float)fVar3;
  *(undefined4 *)(param_1 + 0x2c) = 0;
  *(undefined4 *)(param_1 + 0x30) = local_4;
  *(undefined4 *)(param_1 + 0x34) = 0;
  *(undefined4 *)(param_1 + 0x38) = 0;
  *(undefined4 *)(param_1 + 0x3c) = 0x3f800000;
  *(undefined4 *)(param_1 + 0x40) = local_4;
  fVar1 = *(float *)(param_1 + 0x48) * _DAT_005d8bb8;
  if (*(int *)(param_1 + 0x50) == 0) {
    fVar1 = *(float *)(param_1 + 0x4c) - fVar1;
    *(float *)(param_1 + 0x4c) = fVar1;
    if (fVar1 < _DAT_005d856c) {
      *(undefined4 *)(param_1 + 0x4c) = 0;
      iVar2 = *(int *)(param_1 + 0x54) + -1;
      *(int *)(param_1 + 0x54) = iVar2;
      if (iVar2 == 0) {
        *(undefined4 *)(param_1 + 0x54) = 200;
        *(undefined4 *)(param_1 + 0x50) = 1;
      }
    }
  }
  else {
    fVar1 = fVar1 + *(float *)(param_1 + 0x4c);
    *(float *)(param_1 + 0x4c) = fVar1;
    if (_DAT_005d8568 < fVar1) {
      *(undefined4 *)(param_1 + 0x4c) = 0x3f800000;
      iVar2 = *(int *)(param_1 + 0x54) + -1;
      *(int *)(param_1 + 0x54) = iVar2;
      if (iVar2 == 0) {
        *(undefined4 *)(param_1 + 0x54) = 200;
        *(undefined4 *)(param_1 + 0x50) = 0;
        return;
      }
    }
  }
  return;
}
