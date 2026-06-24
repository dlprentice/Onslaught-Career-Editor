/* address: 0x0057d0ee */
/* name: CWaypointManager__Helper_0057d0ee */
/* signature: int CWaypointManager__Helper_0057d0ee(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CWaypointManager__Helper_0057d0ee(void)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint *puVar6;
  uint *in_stack_00000004;
  uint in_stack_00000008;
  int in_stack_0000000c;
  uint in_stack_00000010;
  int in_stack_00000014;
  int in_stack_00000018;
  int local_14;
  uint *local_8;

  uVar5 = in_stack_00000010 * in_stack_00000014 + in_stack_00000008;
  if (in_stack_00000008 < uVar5) {
    in_stack_00000010 = in_stack_00000008 + in_stack_0000000c * 4;
    do {
      local_8 = in_stack_00000004;
      if (in_stack_00000008 < in_stack_00000010) {
        puVar6 = (uint *)(in_stack_00000008 + 4);
        local_14 = ((in_stack_00000010 - in_stack_00000008) - 1 >> 3) + 1;
        do {
          uVar1 = *(uint *)((int)puVar6 + in_stack_00000014);
          uVar2 = *(uint *)(in_stack_00000014 + -4 + (int)puVar6);
          uVar3 = *puVar6;
          uVar4 = puVar6[-1];
          *local_8 = ((uVar4 >> 2 & 0xffc03fc0) + (uVar2 >> 2 & 0xffc03fc0) +
                      (uVar1 >> 2 & 0xffc03fc0) + -0x7fff80 + (uVar3 >> 2 & 0xffc03fc0) ^
                     (uVar4 & 0xff00ff) + (uVar2 & 0xff00ff) + (uVar1 & 0xff00ff) + 0x20002 +
                     (uVar3 & 0xff00ff) >> 2) & 0xff00ff ^
                     (uint)(&DAT_00800080 +
                           (uVar3 >> 2 & 0x3fc03fc0) +
                           (uVar4 >> 2 & 0x3fc03fc0) + (uVar2 >> 2 & 0x3fc03fc0) +
                           (uVar1 >> 2 & 0x3fc03fc0));
          puVar6 = puVar6 + 2;
          local_14 = local_14 + -1;
          local_8 = local_8 + 1;
        } while (local_14 != 0);
      }
      in_stack_00000004 = (uint *)((int)in_stack_00000004 + in_stack_00000018);
      in_stack_00000010 = in_stack_00000010 + in_stack_00000014 * 2;
      in_stack_00000008 = in_stack_00000008 + in_stack_00000014 * 2;
    } while (in_stack_00000008 < uVar5);
  }
  return 0;
}
