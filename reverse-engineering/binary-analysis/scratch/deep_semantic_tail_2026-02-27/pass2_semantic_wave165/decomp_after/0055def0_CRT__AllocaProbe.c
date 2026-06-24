/* address: 0x0055def0 */
/* name: CRT__AllocaProbe */
/* signature: void CRT__AllocaProbe(void) */


/* WARNING: Unable to track spacebase fully for stack */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CRT__AllocaProbe(void)

{
  uint in_EAX;
  undefined1 *puVar1;
  undefined4 unaff_retaddr;

  puVar1 = &stack0x00000004;
  for (; 0xfff < in_EAX; in_EAX = in_EAX - 0x1000) {
    puVar1 = puVar1 + -0x1000;
  }
  *(undefined4 *)(puVar1 + (-4 - in_EAX)) = unaff_retaddr;
  return;
}
