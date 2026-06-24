/* address: 0x00446400 */
/* name: CUnitAI__EnterDoorWingOpenTrackingState */
/* signature: void __fastcall CUnitAI__EnterDoorWingOpenTrackingState(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CUnitAI__EnterDoorWingOpenTrackingState(int param_1)

{
  uint uVar1;

  if (*(int *)(param_1 + 0x68) == 0) {
    *(undefined4 *)(param_1 + 0x68) = 1;
    uVar1 = Random__NextLCGAbs(DAT_008a9d9c);
    uVar1 = uVar1 & 0x8000ffff;
    if ((int)uVar1 < 0) {
      uVar1 = (uVar1 - 1 | 0xffff0000) + 1;
    }
    *(float *)(param_1 + 0x70) = (float)(int)uVar1 * _DAT_005db1e0 + _DAT_005d85d4;
    CUnitAI__PlayOpenAnimationIfState1Or3(*(void **)(param_1 + 8));
  }
  if (*(int *)(param_1 + 0xc) != 0) {
    CUnitAI__Helper_004fcec0();
  }
  return;
}
