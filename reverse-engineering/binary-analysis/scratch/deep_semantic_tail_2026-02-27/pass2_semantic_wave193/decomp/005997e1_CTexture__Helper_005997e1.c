/* address: 0x005997e1 */
/* name: CTexture__Helper_005997e1 */
/* signature: int CTexture__Helper_005997e1(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CTexture__Helper_005997e1(void)

{
  undefined4 *in_ECX;
  int iVar1;
  int unaff_EDI;
  undefined4 *puVar2;
  undefined4 *in_stack_00000004;
  undefined4 in_stack_00000008;
  undefined4 in_stack_0000000c;
  undefined4 in_stack_00000010;

  CTexture__NodePayloadBaseCtor(in_ECX,(void *)0x11,unaff_EDI);
  *in_ECX = &PTR_CTexture__NodeType12_Dtor_DeleteOnFlag_005ef374;
  puVar2 = in_ECX + 4;
  for (iVar1 = 8; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar2 = *in_stack_00000004;
    in_stack_00000004 = in_stack_00000004 + 1;
    puVar2 = puVar2 + 1;
  }
  in_ECX[0xc] = in_stack_00000008;
  in_ECX[0xd] = in_stack_0000000c;
  in_ECX[0xe] = in_stack_00000010;
  in_ECX[0xf] = 0;
  in_ECX[0x10] = 0;
  in_ECX[0x15] = 0;
  in_ECX[0x16] = 0;
  in_ECX[0x11] = 0;
  in_ECX[0x12] = 0;
  in_ECX[0x13] = 0;
  in_ECX[0x14] = 0;
  return (int)in_ECX;
}
