/* address: 0x004250f0 */
/* name: CUnitAI__DecayDeployTrackingTransformToNeutral */
/* signature: void __fastcall CUnitAI__DecayDeployTrackingTransformToNeutral(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CUnitAI__DecayDeployTrackingTransformToNeutral(int param_1)

{
  float fVar1;
  float fVar2;
  float fVar3;
  int iVar4;
  int iVar5;
  undefined4 *puVar6;
  undefined4 *puVar7;
  float10 fVar8;
  undefined4 local_30 [12];

  iVar5 = *(int *)(param_1 + 0x110);
  if ((iVar5 != 0) && ((*(byte *)(iVar5 + 0x2c) & 4) == 0)) {
    fVar8 = (float10)fcos((float10)*(float *)(param_1 + 0xa0));
    puVar6 = (undefined4 *)(param_1 + 0xb0);
    puVar7 = (undefined4 *)(param_1 + 0x2c);
    for (iVar4 = 0xc; iVar4 != 0; iVar4 = iVar4 + -1) {
      *puVar7 = *puVar6;
      puVar6 = puVar6 + 1;
      puVar7 = puVar7 + 1;
    }
    fVar1 = *(float *)(iVar5 + 0x278);
    fVar2 = *(float *)(iVar5 + 0x278);
    fVar3 = *(float *)(iVar5 + 0x280) * _DAT_005d95c0;
    if (_DAT_005d95b4 <= *(float *)(param_1 + 0xa4)) {
      if (*(float *)(param_1 + 0xa4) <= _DAT_005d8574) {
        *(undefined4 *)(param_1 + 0xa4) = 0;
      }
      else {
        *(float *)(param_1 + 0xa4) = *(float *)(param_1 + 0xa4) - _DAT_005d8574;
      }
    }
    else {
      *(float *)(param_1 + 0xa4) = *(float *)(param_1 + 0xa4) + _DAT_005d8574;
    }
    if (_DAT_005d95b4 <= *(float *)(param_1 + 0xa8)) {
      if (*(float *)(param_1 + 0xa8) <= _DAT_005d8574) {
        *(undefined4 *)(param_1 + 0xa8) = 0;
      }
      else {
        *(float *)(param_1 + 0xa8) = *(float *)(param_1 + 0xa8) - _DAT_005d8574;
      }
    }
    else {
      *(float *)(param_1 + 0xa8) = *(float *)(param_1 + 0xa8) + _DAT_005d8574;
    }
    fVar8 = (fVar8 * (float10)*(float *)(param_1 + 0x9c) - (float10)fVar1) +
            (float10)*(float *)(param_1 + 0xa8);
    fVar3 = fVar3 + *(float *)(param_1 + 0xa4);
    fcos((float10)-fVar2);
    fsin((float10)-fVar2);
    fcos(fVar8);
    fsin(fVar8);
    fcos((float10)fVar3);
    fsin((float10)fVar3);
    Vec3__SetXYZ();
    Vec3__SetXYZ();
    Vec3__SetXYZ();
    Mat34__SetRows();
    puVar6 = local_30;
    puVar7 = (undefined4 *)(param_1 + 0x2c);
    for (iVar5 = 0xc; iVar5 != 0; iVar5 = iVar5 + -1) {
      *puVar7 = *puVar6;
      puVar6 = puVar6 + 1;
      puVar7 = puVar7 + 1;
    }
  }
  return;
}
