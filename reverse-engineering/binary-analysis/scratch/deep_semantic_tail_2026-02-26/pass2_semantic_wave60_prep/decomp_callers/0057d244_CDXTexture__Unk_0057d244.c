/* address: 0x0057d244 */
/* name: CDXTexture__Unk_0057d244 */
/* signature: int CDXTexture__Unk_0057d244(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXTexture__Unk_0057d244(void)

{
  uint *puVar1;
  uint *puVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint *puVar6;
  uint *in_stack_00000004;
  uint in_stack_00000008;
  uint *in_stack_0000000c;
  uint in_stack_00000010;
  int in_stack_00000014;
  int in_stack_00000018;
  int local_10;

  uVar5 = in_stack_00000010 * in_stack_00000014 + in_stack_00000008;
  if (in_stack_00000008 < uVar5) {
    in_stack_00000010 = in_stack_00000008 + (int)in_stack_0000000c * 4;
    do {
      in_stack_0000000c = in_stack_00000004;
      if (in_stack_00000008 < in_stack_00000010) {
        local_10 = ((in_stack_00000010 - in_stack_00000008) - 1 >> 3) + 1;
        puVar6 = (uint *)(in_stack_00000008 + 4);
        do {
          puVar2 = (uint *)((int)puVar6 + in_stack_00000014);
          uVar3 = *puVar6;
          uVar4 = *(uint *)(in_stack_00000014 + -4 + (int)puVar6);
          puVar1 = puVar6 + -1;
          puVar6 = puVar6 + 2;
          local_10 = local_10 + -1;
          *in_stack_0000000c =
               ((*puVar1 & 0xff00ff) + (uVar4 & 0xff00ff) + (*puVar2 & 0xff00ff) + 0x20002 +
                (uVar3 & 0xff00ff) & 0x3fc03fc |
               (*puVar1 & 0xff00) + (uVar4 & 0xff00) + (*puVar2 & 0xff00) + 0x200 + (uVar3 & 0xff00)
               & 0x3fc00) >> 2;
          in_stack_0000000c = in_stack_0000000c + 1;
        } while (local_10 != 0);
      }
      in_stack_00000004 = (uint *)((int)in_stack_00000004 + in_stack_00000018);
      in_stack_00000010 = in_stack_00000010 + in_stack_00000014 * 2;
      in_stack_00000008 = in_stack_00000008 + in_stack_00000014 * 2;
    } while (in_stack_00000008 < uVar5);
  }
  return 0;
}
