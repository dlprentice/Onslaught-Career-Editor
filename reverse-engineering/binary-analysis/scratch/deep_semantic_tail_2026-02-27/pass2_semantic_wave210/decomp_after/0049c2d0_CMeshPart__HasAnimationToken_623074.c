/* address: 0x0049c2d0 */
/* name: CMeshPart__HasAnimationToken_623074 */
/* signature: bool CMeshPart__HasAnimationToken_623074(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

bool CMeshPart__HasAnimationToken_623074(void)

{
  int iVar1;
  void *unaff_retaddr;
  void *in_stack_00000004;

  iVar1 = FindAnimationIndex(in_stack_00000004,0x623074,unaff_retaddr);
  return iVar1 != -1;
}
