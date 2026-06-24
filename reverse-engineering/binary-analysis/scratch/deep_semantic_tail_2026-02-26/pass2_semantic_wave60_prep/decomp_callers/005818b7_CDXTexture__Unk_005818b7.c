/* address: 0x005818b7 */
/* name: CDXTexture__Unk_005818b7 */
/* signature: void __fastcall CDXTexture__Unk_005818b7(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CDXTexture__Unk_005818b7(int param_1)

{
  undefined4 uVar1;

  uVar1 = _DAT_005e9f04;
  if ((*(int *)(param_1 + 4) != 0x32545844) && (*(int *)(param_1 + 4) != 0x33545844)) {
    uVar1 = _DAT_005e9f08;
  }
  *(undefined4 *)(param_1 + 0x1074) = uVar1;
  *(float *)(param_1 + 0x1078) = 1.0 / *(float *)(param_1 + 0x1074);
  *(float *)(param_1 + 0x24) =
       (float)(int)ROUND(*(float *)(param_1 + 0x24) * _DAT_005e9f00 + _DAT_005e72d4) * _DAT_005e9efc
  ;
  *(float *)(param_1 + 0x28) =
       (float)(int)ROUND(*(float *)(param_1 + 0x28) * _DAT_005e9ef8 + _DAT_005e72d4) * _DAT_005e9ef4
  ;
  *(float *)(param_1 + 0x2c) =
       (float)(int)ROUND(*(float *)(param_1 + 0x2c) * _DAT_005e9f00 + _DAT_005e72d4) * _DAT_005e9efc
  ;
  *(float *)(param_1 + 0x30) =
       (float)(int)ROUND(*(float *)(param_1 + 0x1074) * *(float *)(param_1 + 0x30) + _DAT_005e72d4)
       * *(float *)(param_1 + 0x1078);
  return;
}
