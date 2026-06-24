/* address: 0x0049bd50 */
/* name: CMCMech__Helper_0049bd50 */
/* signature: void CMCMech__Helper_0049bd50(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CMCMech__Helper_0049bd50(void)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  undefined4 in_stack_0000002c;
  undefined4 in_stack_00000030;
  undefined4 in_stack_00000034;
  undefined4 in_stack_00000038;
  int in_stack_00000044;
  undefined4 auStack_74 [12];
  undefined4 uStack_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined1 *puStack_30;
  undefined1 *puStack_2c;
  undefined1 *puStack_24;
  undefined1 *puStack_20;

  puStack_20 = &stack0x0000004c;
  puStack_24 = &stack0x00000048;
  puStack_2c = &stack0x00000014;
  puStack_30 = &stack0x00000004;
  uStack_34 = 0x49bd81;
  CMCMech__UpdateBone();
  iVar2 = 0;
  if (0 < *(int *)(in_stack_00000044 + 0x90)) {
    do {
      uStack_34 = in_stack_00000038;
      uStack_38 = in_stack_00000034;
      uStack_3c = in_stack_00000030;
      uStack_40 = in_stack_0000002c;
      uStack_44 = *(undefined4 *)(*(int *)(in_stack_00000044 + 0x94) + iVar2 * 4);
      puVar3 = (undefined4 *)&stack0xfffffff8;
      puVar4 = auStack_74;
      for (iVar1 = 0xc; iVar1 != 0; iVar1 = iVar1 + -1) {
        *puVar4 = *puVar3;
        puVar3 = puVar3 + 1;
        puVar4 = puVar4 + 1;
      }
      CMCMech__Helper_0049bd50();
      iVar2 = iVar2 + 1;
    } while (iVar2 < *(int *)(in_stack_00000044 + 0x90));
  }
  return;
}
