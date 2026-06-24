/* address: 0x004ffe00 */
/* name: CWaypoint__RandomizeOffsetVectors */
/* signature: void __fastcall CWaypoint__RandomizeOffsetVectors(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CWaypoint__RandomizeOffsetVectors(int param_1)

{
  uint uVar1;

  uVar1 = Random__NextLCGAbs(DAT_008a9d9c);
  uVar1 = uVar1 & 0x8000ffff;
  if ((int)uVar1 < 0) {
    uVar1 = (uVar1 - 1 | 0xffff0000) + 1;
  }
  *(float *)(param_1 + 0x48) = (float)(int)uVar1 * _DAT_005dfb7c + _DAT_005d9088;
  uVar1 = Random__NextLCGAbs(DAT_008a9d9c);
  uVar1 = uVar1 & 0x8000ffff;
  if ((int)uVar1 < 0) {
    uVar1 = (uVar1 - 1 | 0xffff0000) + 1;
  }
  *(float *)(param_1 + 0x54) = (float)(int)uVar1 * _DAT_005dfb7c + _DAT_005d9088;
  uVar1 = Random__NextLCGAbs(DAT_008a9d9c);
  uVar1 = uVar1 & 0x8000ffff;
  if ((int)uVar1 < 0) {
    uVar1 = (uVar1 - 1 | 0xffff0000) + 1;
  }
  if (_DAT_005d85ec < (float)(int)uVar1 * _DAT_005d8d54) {
    *(float *)(param_1 + 0x48) = -*(float *)(param_1 + 0x48);
  }
  uVar1 = Random__NextLCGAbs(DAT_008a9d9c);
  uVar1 = uVar1 & 0x8000ffff;
  if ((int)uVar1 < 0) {
    uVar1 = (uVar1 - 1 | 0xffff0000) + 1;
  }
  if (_DAT_005d85ec < (float)(int)uVar1 * _DAT_005d8d54) {
    *(float *)(param_1 + 0x54) = -*(float *)(param_1 + 0x54);
  }
  *(float *)(param_1 + 0x50) = -*(float *)(param_1 + 0x48);
  *(float *)(param_1 + 0x5c) = -*(float *)(param_1 + 0x54);
  *(undefined4 *)(param_1 + 0x4c) = *(undefined4 *)(param_1 + 0x48);
  *(undefined4 *)(param_1 + 0x58) = *(undefined4 *)(param_1 + 0x54);
  return;
}
