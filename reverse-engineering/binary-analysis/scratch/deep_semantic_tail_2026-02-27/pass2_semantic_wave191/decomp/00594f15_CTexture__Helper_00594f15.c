/* address: 0x00594f15 */
/* name: CTexture__Helper_00594f15 */
/* signature: int CTexture__Helper_00594f15(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CTexture__Helper_00594f15(void)

{
  byte bVar1;
  uint in_EAX;
  uint extraout_EAX;
  int in_stack_00000004;
  uint *in_stack_00000008;
  uint in_stack_0000000c;
  uint in_stack_00000010;
  char in_stack_00000014;
  byte in_stack_00000018;
  undefined1 in_stack_0000001c;
  undefined1 in_stack_00000020;
  undefined1 in_stack_00000024;

  if ((in_stack_00000004 != 0) && (in_stack_00000008 != (uint *)0x0)) {
    *(undefined1 *)((int)in_stack_00000008 + 0x1a) = in_stack_00000020;
    in_stack_00000008[1] = in_stack_00000010;
    *(undefined1 *)((int)in_stack_00000008 + 0x1b) = in_stack_00000024;
    *in_stack_00000008 = in_stack_0000000c;
    *(char *)(in_stack_00000008 + 6) = in_stack_00000014;
    *(byte *)((int)in_stack_00000008 + 0x19) = in_stack_00000018;
    *(undefined1 *)(in_stack_00000008 + 7) = in_stack_0000001c;
    if ((in_stack_00000018 == 3) || ((in_stack_00000018 & 2) == 0)) {
      *(undefined1 *)((int)in_stack_00000008 + 0x1d) = 1;
    }
    else {
      *(undefined1 *)((int)in_stack_00000008 + 0x1d) = 3;
    }
    if ((in_stack_00000018 & 4) != 0) {
      *(char *)((int)in_stack_00000008 + 0x1d) = *(char *)((int)in_stack_00000008 + 0x1d) + '\x01';
    }
    bVar1 = *(char *)((int)in_stack_00000008 + 0x1d) * in_stack_00000014;
    *(byte *)((int)in_stack_00000008 + 0x1e) = bVar1;
    in_EAX = (uint)(0x7fffffff / (ulonglong)(uint)((int)(bVar1 + 7) >> 3));
    if (in_EAX < in_stack_0000000c) {
      CDXTexture__ReportDecodeWarning(in_stack_00000004,0x5eeaec);
      in_stack_00000008[3] = 0;
      in_EAX = extraout_EAX;
    }
    else {
      in_stack_00000008[3] = bVar1 * in_stack_0000000c + 7 >> 3;
    }
  }
  return in_EAX;
}
