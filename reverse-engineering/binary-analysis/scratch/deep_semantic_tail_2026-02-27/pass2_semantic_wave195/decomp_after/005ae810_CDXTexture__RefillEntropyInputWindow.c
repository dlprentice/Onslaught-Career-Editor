/* address: 0x005ae810 */
/* name: CDXTexture__RefillEntropyInputWindow */
/* signature: int CDXTexture__RefillEntropyInputWindow(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXTexture__RefillEntropyInputWindow(void)

{
  int iVar1;
  int *piVar2;
  int *unaff_EBP;
  int iVar3;
  int iVar4;
  uint uVar5;
  int in_stack_00000004;
  int *in_stack_00000018;
  int in_stack_0000001c;

  iVar1 = *(int *)(in_stack_00000004 + 0x1c8);
  if (*(int *)(in_stack_00000004 + 0x13c) <= *(int *)(iVar1 + 0x5c)) {
    iVar3 = 0;
    if (0 < *(int *)(in_stack_00000004 + 0x24)) {
      iVar4 = iVar1 + 0xc;
      do {
        (**(code **)(iVar4 + 0x28))();
        iVar3 = iVar3 + 1;
        iVar4 = iVar4 + 4;
      } while (iVar3 < *(int *)(in_stack_00000004 + 0x24));
    }
    *(undefined4 *)(iVar1 + 0x5c) = 0;
  }
  uVar5 = *(int *)(in_stack_00000004 + 0x13c) - *(int *)(iVar1 + 0x5c);
  if (*(uint *)(iVar1 + 0x60) < uVar5) {
    uVar5 = *(uint *)(iVar1 + 0x60);
  }
  if ((uint)(in_stack_0000001c - *in_stack_00000018) < uVar5) {
    uVar5 = in_stack_0000001c - *in_stack_00000018;
  }
  (**(code **)(*(int *)(in_stack_00000004 + 0x1cc) + 4))();
  iVar3 = *(int *)(iVar1 + 0x60);
  iVar4 = *(int *)(iVar1 + 0x5c);
  *in_stack_00000018 = *in_stack_00000018 + uVar5;
  piVar2 = *(int **)(in_stack_00000004 + 0x13c);
  iVar4 = iVar4 + uVar5;
  *(uint *)(iVar1 + 0x60) = iVar3 - uVar5;
  *(int *)(iVar1 + 0x5c) = iVar4;
  if ((int)piVar2 <= iVar4) {
    *unaff_EBP = *unaff_EBP + 1;
    piVar2 = unaff_EBP;
  }
  return (int)piVar2;
}
