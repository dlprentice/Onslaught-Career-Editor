/* address: 0x004f3d10 */
/* name: CCollisionSeekingRound__Helper_004f3d10 */
/* signature: int __fastcall CCollisionSeekingRound__Helper_004f3d10(int param_1) */


int __fastcall CCollisionSeekingRound__Helper_004f3d10(int param_1)

{
  int iVar1;

  if (*(int **)(param_1 + 0x38) != (int *)0x0) {
                    /* WARNING: Could not recover jumptable at 0x004f3d19. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    iVar1 = (**(code **)(**(int **)(param_1 + 0x38) + 0x10))();
    return iVar1;
  }
  return 0;
}
