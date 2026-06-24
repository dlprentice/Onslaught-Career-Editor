/* address: 0x00465640 */
/* name: CFrontEnd__Unk_00465640 */
/* signature: int CFrontEnd__Unk_00465640(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFrontEnd__Unk_00465640(void)

{
  int iVar1;
  int *in_ECX;
  undefined4 in_stack_00000004;
  int in_stack_00000008;
  int in_stack_0000000c;
  undefined4 in_stack_00000010;
  undefined4 in_stack_00000014;
  undefined4 in_stack_00000018;
  undefined4 in_stack_0000001c;

  if ((in_stack_00000008 == 0) && (DAT_006630cc == 0)) {
    iVar1 = 0;
  }
  else {
    iVar1 = 1;
  }
  in_ECX[3] = iVar1;
  CController__Unk_0042d7d0(1);
  iVar1 = (**(code **)(*in_ECX + 0x2c))
                    (in_stack_00000004,-(uint)(in_stack_0000000c != 0) & g_LanguageIndex,
                     in_stack_00000010,in_stack_00000014,in_stack_00000018,in_stack_0000001c);
  CController__Unk_0042d7d0(0);
  return iVar1;
}
