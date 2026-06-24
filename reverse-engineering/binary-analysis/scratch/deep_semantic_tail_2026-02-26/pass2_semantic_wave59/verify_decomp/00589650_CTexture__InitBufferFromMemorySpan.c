/* address: 0x00589650 */
/* name: CTexture__InitBufferFromMemorySpan */
/* signature: int CTexture__InitBufferFromMemorySpan(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CTexture__InitBufferFromMemorySpan(void)

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
