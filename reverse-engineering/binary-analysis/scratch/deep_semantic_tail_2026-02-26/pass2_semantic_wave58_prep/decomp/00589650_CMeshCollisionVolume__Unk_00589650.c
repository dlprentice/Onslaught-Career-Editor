/* address: 0x00589650 */
/* name: CMeshCollisionVolume__Unk_00589650 */
/* signature: int CMeshCollisionVolume__Unk_00589650(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CMeshCollisionVolume__Unk_00589650(void)

{
  int iVar1;
  int in_ECX;
  int in_stack_00000004;
  int in_stack_00000008;

  if ((in_stack_00000008 == 0) || (in_stack_00000004 != 0)) {
    *(int *)(in_ECX + 100) = in_stack_00000004;
    *(int *)(in_ECX + 0x68) = in_stack_00000008;
    iVar1 = CMeshCollisionVolume__Helper_0058c396();
    if (-1 < iVar1) {
      iVar1 = 0;
    }
  }
  else {
    iVar1 = -0x7789f794;
  }
  return iVar1;
}
