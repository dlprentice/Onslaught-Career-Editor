/* address: 0x005602d2 */
/* name: CDXTexture__Unk_005602d2 */
/* signature: int CDXTexture__Unk_005602d2(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXTexture__Unk_005602d2(void)

{
  int iVar1;
  int *in_stack_00000004;
  int in_stack_00000008;
  undefined4 in_stack_0000000c;
  int in_stack_00000010;
  int *in_stack_00000014;
  int in_stack_00000018;

  if (*in_stack_00000014 != 0x19930520) {
    CDXTexture__Unk_00560c5b();
  }
  if ((*(byte *)(in_stack_00000004 + 1) & 0x66) == 0) {
    if (in_stack_00000014[3] != 0) {
      if (((*in_stack_00000004 == -0x1f928c9d) && (0x19930520 < (uint)in_stack_00000004[5])) &&
         (*(code **)(in_stack_00000004[7] + 8) != (code *)0x0)) {
        iVar1 = (**(code **)(in_stack_00000004[7] + 8))
                          (in_stack_00000004,in_stack_00000008,in_stack_0000000c,in_stack_00000010);
        return iVar1;
      }
      CDXTexture__Unk_0056036d();
    }
  }
  else if ((in_stack_00000014[1] != 0) && (in_stack_00000018 == 0)) {
    CDXTexture__Unk_00560627(in_stack_00000008,in_stack_00000010,(int)in_stack_00000014,-1);
  }
  return 1;
}
