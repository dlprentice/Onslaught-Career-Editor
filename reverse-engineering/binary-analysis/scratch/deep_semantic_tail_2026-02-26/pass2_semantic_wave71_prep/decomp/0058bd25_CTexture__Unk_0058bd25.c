/* address: 0x0058bd25 */
/* name: CTexture__Unk_0058bd25 */
/* signature: int CTexture__Unk_0058bd25(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CTexture__Unk_0058bd25(void)

{
  int extraout_EAX;
  int iVar1;
  void *in_ECX;
  void *unaff_ESI;
  void *in_stack_0000000c;
  undefined4 in_stack_00000010;

  CFastVB__Helper_00426fd0(0x70);
  if (extraout_EAX == 0) {
    iVar1 = 0;
  }
  else {
    iVar1 = CTexture__Helper_00589405(extraout_EAX);
  }
  *(int *)((int)in_ECX + 0x50) = iVar1;
  if (iVar1 == 0) {
    iVar1 = -0x7ff8fff2;
  }
  else {
    iVar1 = CTexture__InitBufferFromMemorySpan();
    if (-1 < iVar1) {
      iVar1 = CTexture__Helper_0058b1a0(in_ECX,in_stack_0000000c,unaff_ESI);
      if (-1 < iVar1) {
        *(undefined4 *)((int)in_ECX + 0x54) = *(undefined4 *)((int)in_ECX + 0x50);
        *(undefined4 *)((int)in_ECX + 0x58) = in_stack_00000010;
        iVar1 = 0;
      }
    }
  }
  return iVar1;
}
