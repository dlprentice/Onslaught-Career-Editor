/* address: 0x00579601 */
/* name: Math__BuildMatrixFromQuaternion */
/* signature: void __stdcall Math__BuildMatrixFromQuaternion(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void Math__BuildMatrixFromQuaternion(void *param_1)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  undefined4 local_14;
  undefined4 local_10;
  undefined4 local_c;
  undefined4 local_8;

  CTexture__Helper_005780e3();
  fVar4 = _DAT_005e6a34;
  fVar1 = local_14 * _DAT_005e9338;
  fVar3 = local_10 * _DAT_005e9338;
  fVar2 = local_c * _DAT_005e9338;
  *(float *)param_1 = local_14 * fVar1 + _DAT_005e6a34;
  *(float *)((int)param_1 + 4) = fVar3 * local_14;
  *(float *)((int)param_1 + 8) = fVar2 * local_14;
  *(undefined4 *)((int)param_1 + 0xc) = 0;
  *(float *)((int)param_1 + 0x10) = local_10 * fVar1;
  *(float *)((int)param_1 + 0x14) = local_10 * fVar3 + fVar4;
  *(float *)((int)param_1 + 0x18) = fVar2 * local_10;
  *(undefined4 *)((int)param_1 + 0x1c) = 0;
  *(float *)((int)param_1 + 0x20) = local_c * fVar1;
  *(float *)((int)param_1 + 0x24) = local_c * fVar3;
  *(float *)((int)param_1 + 0x28) = local_c * fVar2 + fVar4;
  *(undefined4 *)((int)param_1 + 0x2c) = 0;
  *(float *)((int)param_1 + 0x30) = local_8 * fVar1;
  *(float *)((int)param_1 + 0x34) = local_8 * fVar3;
  *(float *)((int)param_1 + 0x38) = local_8 * fVar2;
  *(undefined4 *)((int)param_1 + 0x3c) = 0x3f800000;
  return;
}
