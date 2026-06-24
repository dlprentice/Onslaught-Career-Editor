/* address: 0x005ae190 */
/* name: CDXTexture__InitBlockCoefficientHistory */
/* signature: void __stdcall CDXTexture__InitBlockCoefficientHistory(int param_1) */


void CDXTexture__InitBlockCoefficientHistory(int param_1)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  int iVar3;

  puVar1 = (undefined4 *)(*(code *)**(undefined4 **)(param_1 + 4))(param_1,1,0x40);
  puVar2 = *(undefined4 **)(param_1 + 4);
  *puVar1 = &LAB_005adf50;
  *(undefined4 **)(param_1 + 0x1c0) = puVar1;
  puVar1[0xb] = 0;
  puVar1[0xc] = 0;
  puVar1[0xd] = 0;
  puVar1[0xe] = 0;
  puVar2 = (undefined4 *)(*(code *)*puVar2)(param_1,1,*(int *)(param_1 + 0x24) << 8);
  *(undefined4 **)(param_1 + 0xa4) = puVar2;
  if (0 < (int)*(uint *)(param_1 + 0x24)) {
    for (iVar3 = (*(uint *)(param_1 + 0x24) & 0xffffff) << 6; iVar3 != 0; iVar3 = iVar3 + -1) {
      *puVar2 = 0xffffffff;
      puVar2 = puVar2 + 1;
    }
  }
  return;
}
