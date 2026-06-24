/* address: 0x00496270 */
/* name: CUnitAI__Unk_00496270 */
/* signature: bool CUnitAI__Unk_00496270(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

bool CUnitAI__Unk_00496270(void)

{
  int iVar1;
  void *unaff_ESI;
  void *in_stack_00000004;

  iVar1 = FindAnimationIndex(in_stack_00000004,0x62dd88,unaff_ESI);
  if (iVar1 != -1) {
    return true;
  }
  iVar1 = FindAnimationIndex(in_stack_00000004,0x62dd7c,unaff_ESI);
  return iVar1 != -1;
}
