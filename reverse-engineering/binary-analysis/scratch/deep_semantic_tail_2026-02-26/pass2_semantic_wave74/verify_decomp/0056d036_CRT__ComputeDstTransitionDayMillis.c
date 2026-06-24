/* address: 0x0056d036 */
/* name: CRT__ComputeDstTransitionDayMillis */
/* signature: int CRT__ComputeDstTransitionDayMillis(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CRT__ComputeDstTransitionDayMillis(void)

{
  int iVar1;
  int iVar2;
  int in_stack_00000004;
  int in_stack_00000008;
  uint in_stack_0000000c;
  int in_stack_00000010;
  int in_stack_00000014;
  int in_stack_00000018;
  int in_stack_0000001c;
  int in_stack_00000020;
  int in_stack_00000024;
  int in_stack_00000028;
  int in_stack_0000002c;

  if (in_stack_00000008 == 1) {
    if ((in_stack_0000000c & 3) == 0) {
      iVar1 = (&DAT_00656a38)[in_stack_00000010];
    }
    else {
      iVar1 = *(int *)(&DAT_00656a6c + in_stack_00000010 * 4);
    }
    iVar2 = (int)(in_stack_0000000c * 0x16d + -0x63db +
                 iVar1 + 1 + ((int)(in_stack_0000000c - 1) >> 2)) % 7;
    if (in_stack_00000018 < iVar2) {
      iVar1 = iVar1 + 1 + (in_stack_00000014 * 7 - iVar2) + in_stack_00000018;
    }
    else {
      iVar1 = iVar1 + -6 + (in_stack_00000014 * 7 - iVar2) + in_stack_00000018;
    }
    if (in_stack_00000014 == 5) {
      if ((in_stack_0000000c & 3) == 0) {
        iVar2 = *(int *)(&DAT_00656a3c + in_stack_00000010 * 4);
      }
      else {
        iVar2 = *(int *)(&DAT_00656a70 + in_stack_00000010 * 4);
      }
      if (iVar2 < iVar1) {
        iVar1 = iVar1 + -7;
      }
    }
  }
  else {
    if ((in_stack_0000000c & 3) == 0) {
      iVar1 = (&DAT_00656a38)[in_stack_00000010];
    }
    else {
      iVar1 = *(int *)(&DAT_00656a6c + in_stack_00000010 * 4);
    }
    iVar1 = iVar1 + in_stack_0000001c;
  }
  if (in_stack_00000004 == 1) {
    DAT_00656a20 = in_stack_0000000c;
    DAT_00656a28 = ((in_stack_00000020 * 0x3c + in_stack_00000024) * 0x3c + in_stack_00000028) *
                   1000 + in_stack_0000002c;
    iVar2 = DAT_00656a28;
    DAT_00656a24 = iVar1;
  }
  else {
    DAT_00656a38 = ((in_stack_00000020 * 0x3c + in_stack_00000024) * 0x3c + _DAT_00656990 +
                   in_stack_00000028) * 1000 + in_stack_0000002c;
    if (DAT_00656a38 < 0) {
      DAT_00656a38 = DAT_00656a38 + 86400000;
      DAT_00656a34 = iVar1 + -1;
    }
    else {
      DAT_00656a34 = iVar1;
      if (86399999 < DAT_00656a38) {
        DAT_00656a38 = DAT_00656a38 + -86400000;
        DAT_00656a34 = iVar1 + 1;
      }
    }
    DAT_00656a30 = in_stack_0000000c;
    iVar2 = DAT_00656a38;
  }
  return iVar2;
}
