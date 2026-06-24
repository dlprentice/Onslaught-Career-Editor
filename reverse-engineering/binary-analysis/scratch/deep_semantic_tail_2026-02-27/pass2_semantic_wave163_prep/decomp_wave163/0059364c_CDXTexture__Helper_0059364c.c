/* address: 0x0059364c */
/* name: CDXTexture__Helper_0059364c */
/* signature: int CDXTexture__Helper_0059364c(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXTexture__Helper_0059364c(void)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  int in_stack_00000004;
  uint *in_stack_00000008;
  uint *in_stack_0000000c;
  uint *in_stack_00000010;
  uint *in_stack_00000014;
  uint *in_stack_00000018;
  uint *in_stack_0000001c;
  uint *in_stack_00000020;
  uint *in_stack_00000024;

  if ((((in_stack_00000004 == 0) || (in_stack_00000008 == (uint *)0x0)) ||
      (in_stack_0000000c == (uint *)0x0)) ||
     (((in_stack_00000010 == (uint *)0x0 || (in_stack_00000014 == (uint *)0x0)) ||
      (in_stack_00000018 == (uint *)0x0)))) {
    iVar3 = 0;
  }
  else {
    *in_stack_0000000c = *in_stack_00000008;
    *in_stack_00000010 = in_stack_00000008[1];
    *in_stack_00000014 = (uint)(byte)in_stack_00000008[6];
    *in_stack_00000018 = (uint)*(byte *)((int)in_stack_00000008 + 0x19);
    if (in_stack_00000020 != (uint *)0x0) {
      *in_stack_00000020 = (uint)*(byte *)((int)in_stack_00000008 + 0x1a);
    }
    if (in_stack_00000024 != (uint *)0x0) {
      *in_stack_00000024 = (uint)*(byte *)((int)in_stack_00000008 + 0x1b);
    }
    if (in_stack_0000001c != (uint *)0x0) {
      *in_stack_0000001c = (uint)(byte)in_stack_00000008[7];
    }
    uVar1 = *in_stack_00000018;
    if (uVar1 == 3) {
      uVar2 = 1;
    }
    else {
      uVar2 = (int)(char)uVar1 & 2U | 1;
    }
    if ((uVar1 & 4) != 0) {
      uVar2 = uVar2 + 1;
    }
    if ((uint)(0x7fffffff / (ulonglong)(uint)((int)(*in_stack_00000014 * uVar2 + 7) >> 3)) <
        *in_stack_0000000c) {
      CDXTexture__Helper_00592d63(in_stack_00000004,0x5eea60);
    }
    iVar3 = 1;
  }
  return iVar3;
}
