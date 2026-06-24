/* address: 0x0059be70 */
/* name: CDXTexture__Helper_0059be70 */
/* signature: int CDXTexture__Helper_0059be70(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXTexture__Helper_0059be70(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 *puVar3;
  int *in_stack_00000004;
  int in_stack_00000008;
  undefined4 in_stack_0000000c;
  undefined4 in_stack_00000010;
  undefined4 in_stack_00000014;
  undefined4 in_stack_00000018;

  iVar1 = in_stack_00000004[1];
  if (in_stack_00000008 != 1) {
    puVar3 = (undefined4 *)*in_stack_00000004;
    puVar3[5] = 0xe;
    puVar3[6] = in_stack_00000008;
    (*(code *)*puVar3)();
  }
  puVar3 = (undefined4 *)
           CDXTexture__AllocFromBank_SplitBlock(in_stack_00000004,in_stack_00000008,0x248);
  puVar3[1] = in_stack_00000014;
  puVar3[3] = in_stack_00000018;
  uVar2 = *(undefined4 *)(iVar1 + 0x48);
  *(undefined4 **)(iVar1 + 0x48) = puVar3;
  puVar3[2] = in_stack_00000010;
  *puVar3 = 0;
  puVar3[8] = in_stack_0000000c;
  puVar3[10] = 0;
  puVar3[0xb] = uVar2;
  return (int)puVar3;
}
