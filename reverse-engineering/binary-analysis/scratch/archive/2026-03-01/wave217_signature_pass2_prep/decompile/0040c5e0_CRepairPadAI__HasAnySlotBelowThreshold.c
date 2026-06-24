/* address: 0x0040c5e0 */
/* name: CRepairPadAI__HasAnySlotBelowThreshold */
/* signature: int __fastcall CRepairPadAI__HasAnySlotBelowThreshold(int param_1) */


int __fastcall CRepairPadAI__HasAnySlotBelowThreshold(int param_1)

{
  float *pfVar1;
  int iVar2;

  iVar2 = 0;
  pfVar1 = (float *)(param_1 + 0x52c);
  while ((pfVar1[0xc] != 0.0 ||
         (*(float *)(*(int *)(param_1 + 0x4b0) + (-0x4a4 - param_1) + (int)pfVar1) <= *pfVar1))) {
    iVar2 = iVar2 + 1;
    pfVar1 = pfVar1 + 1;
    if (5 < iVar2) {
      return 0;
    }
  }
  return 1;
}
