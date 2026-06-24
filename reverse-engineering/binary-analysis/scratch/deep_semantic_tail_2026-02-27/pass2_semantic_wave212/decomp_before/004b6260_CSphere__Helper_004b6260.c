/* address: 0x004b6260 */
/* name: CSphere__Helper_004b6260 */
/* signature: int CSphere__Helper_004b6260(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CSphere__Helper_004b6260(void)

{
  int in_EAX;
  int iVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  int in_stack_00000004;
  undefined4 *in_stack_00000008;
  int in_stack_0000000c;
  int in_stack_00000014;
  char in_stack_0000001c;
  undefined4 local_54 [12];
  undefined4 uStack_24;
  int iStack_20;
  undefined4 uStack_14;

  while( true ) {
    if (in_stack_0000000c == 0) {
      return in_EAX;
    }
    iVar1 = *(int *)(in_stack_0000000c + 0x15c);
    if (0 < iVar1) {
      if ((in_stack_00000014 == 0) || (*(int *)(in_stack_00000014 + 0xc) == 0)) {
        uStack_24 = **(undefined4 **)(in_stack_0000000c + 0x160);
        puVar2 = in_stack_00000008;
        puVar3 = local_54;
        for (iVar1 = 0xc; iVar1 != 0; iVar1 = iVar1 + -1) {
          *puVar3 = *puVar2;
          puVar2 = puVar2 + 1;
          puVar3 = puVar3 + 1;
        }
        iVar1 = CMeshPart__RenderAnimatedRecursive();
      }
      else {
        uStack_14 = 1;
        uStack_24 = 0x4b629b;
        iStack_20 = in_stack_0000000c;
        CMeshPart__RefreshCachedPoseIfStale();
        puVar2 = in_stack_00000008;
        puVar3 = local_54 + 1;
        iStack_20 = in_stack_0000000c;
        for (iVar1 = 0xc; iVar1 != 0; iVar1 = iVar1 + -1) {
          *puVar3 = *puVar2;
          puVar2 = puVar2 + 1;
          puVar3 = puVar3 + 1;
        }
        local_54[0] = *(undefined4 *)(in_stack_00000004 + 0xc);
        iVar1 = CSphere__Helper_004b5e80();
      }
    }
    in_EAX = CONCAT31((int3)((uint)iVar1 >> 8),in_stack_0000001c);
    if (in_stack_0000001c == '\0') break;
    in_stack_0000000c = *(int *)(in_stack_0000000c + 8);
  }
  return in_EAX;
}
