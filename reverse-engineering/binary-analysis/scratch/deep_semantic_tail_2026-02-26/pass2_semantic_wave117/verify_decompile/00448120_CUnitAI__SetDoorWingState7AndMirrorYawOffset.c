/* address: 0x00448120 */
/* name: CUnitAI__SetDoorWingState7AndMirrorYawOffset */
/* signature: void __fastcall CUnitAI__SetDoorWingState7AndMirrorYawOffset(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CUnitAI__SetDoorWingState7AndMirrorYawOffset(int param_1)

{
  float fVar1;

  fVar1 = _DAT_005d8568 - *(float *)(param_1 + 0x2a4);
  *(undefined4 *)(param_1 + 0x27c) = 7;
  *(float *)(param_1 + 0x2a4) = fVar1;
  return;
}
