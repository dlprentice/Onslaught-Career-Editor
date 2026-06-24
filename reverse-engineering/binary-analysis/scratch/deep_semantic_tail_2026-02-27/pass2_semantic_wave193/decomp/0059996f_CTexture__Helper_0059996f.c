/* address: 0x0059996f */
/* name: CTexture__Helper_0059996f */
/* signature: int CTexture__Helper_0059996f(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CTexture__Helper_0059996f(void)

{
  undefined4 *in_ECX;
  int unaff_ESI;
  undefined4 in_stack_00000004;
  undefined4 in_stack_00000008;
  undefined4 in_stack_0000000c;
  undefined4 in_stack_00000010;
  undefined4 in_stack_00000014;

  CTexture__NodePayloadBaseCtor(in_ECX,(void *)0x12,unaff_ESI);
  in_ECX[4] = in_stack_00000004;
  in_ECX[5] = in_stack_00000008;
  in_ECX[6] = in_stack_0000000c;
  in_ECX[7] = in_stack_00000010;
  in_ECX[10] = in_stack_00000014;
  *in_ECX = &PTR_CTexture__NodeType12_ScalarDeletingDtor_005ef384;
  in_ECX[8] = 0xf0000;
  in_ECX[9] = 0xe40000;
  return (int)in_ECX;
}
