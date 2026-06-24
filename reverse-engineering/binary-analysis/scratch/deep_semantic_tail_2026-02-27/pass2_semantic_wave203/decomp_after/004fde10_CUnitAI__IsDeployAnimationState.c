/* address: 0x004fde10 */
/* name: CUnitAI__IsDeployAnimationState */
/* signature: int __fastcall CUnitAI__IsDeployAnimationState(int param_1) */


int __fastcall CUnitAI__IsDeployAnimationState(int param_1)

{
  int iVar1;

  iVar1 = *(int *)(param_1 + 0x244);
  if (((iVar1 != 4) && (iVar1 != 3)) && (iVar1 != 5)) {
    return 0;
  }
  return 1;
}
