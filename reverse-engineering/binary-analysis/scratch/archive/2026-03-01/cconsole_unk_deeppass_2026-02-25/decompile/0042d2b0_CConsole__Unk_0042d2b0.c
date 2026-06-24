/* address: 0x0042d2b0 */
/* name: CConsole__Unk_0042d2b0 */
/* signature: int CConsole__Unk_0042d2b0(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CConsole__Unk_0042d2b0(void)

{
  undefined1 *in_ECX;
  undefined1 in_stack_00000004;
  undefined4 in_stack_00000008;
  undefined4 in_stack_0000000c;
  undefined2 in_stack_00000010;
  undefined4 in_stack_00000014;
  undefined2 in_stack_00000018;
  undefined2 in_stack_0000001c;
  undefined2 in_stack_00000020;

  *(undefined4 *)(in_ECX + 4) = in_stack_00000008;
  *in_ECX = in_stack_00000004;
  *(undefined4 *)(in_ECX + 0xc) = in_stack_0000000c;
  *(undefined4 *)(in_ECX + 8) = 0;
  *(undefined2 *)(in_ECX + 0x10) = in_stack_00000010;
  *(undefined4 *)(in_ECX + 0x14) = 0;
  *(undefined2 *)(in_ECX + 0x12) = in_stack_0000001c;
  *(undefined4 *)(in_ECX + 0x18) = in_stack_00000014;
  *(undefined2 *)(in_ECX + 0x1c) = in_stack_00000018;
  *(undefined2 *)(in_ECX + 0x1e) = in_stack_00000020;
  return (int)in_ECX;
}
