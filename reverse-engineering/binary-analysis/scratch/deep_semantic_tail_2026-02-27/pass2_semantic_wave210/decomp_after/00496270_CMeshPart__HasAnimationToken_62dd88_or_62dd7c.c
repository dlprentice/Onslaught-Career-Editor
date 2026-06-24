/* address: 0x00496270 */
/* name: CMeshPart__HasAnimationToken_62dd88_or_62dd7c */
/* signature: bool CMeshPart__HasAnimationToken_62dd88_or_62dd7c(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

bool CMeshPart__HasAnimationToken_62dd88_or_62dd7c(void)

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
