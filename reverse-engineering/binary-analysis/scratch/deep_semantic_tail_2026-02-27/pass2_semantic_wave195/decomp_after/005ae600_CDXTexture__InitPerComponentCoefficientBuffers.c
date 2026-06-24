/* address: 0x005ae600 */
/* name: CDXTexture__InitPerComponentCoefficientBuffers */
/* signature: void __stdcall CDXTexture__InitPerComponentCoefficientBuffers(int param_1) */


void CDXTexture__InitPerComponentCoefficientBuffers(int param_1)

{
  int iVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  int iVar5;
  int iVar6;

  puVar2 = (undefined4 *)(*(code *)**(undefined4 **)(param_1 + 4))(param_1,1,0x54);
  iVar5 = *(int *)(param_1 + 0x24);
  iVar1 = *(int *)(param_1 + 0xdc);
  iVar6 = 0;
  *(undefined4 **)(param_1 + 0x1c4) = puVar2;
  *puVar2 = &LAB_005ae1f0;
  if (0 < iVar5) {
    puVar4 = (undefined4 *)(iVar1 + 0x50);
    puVar2 = puVar2 + 0xb;
    do {
      puVar3 = (undefined4 *)(*(code *)**(undefined4 **)(param_1 + 4))(param_1,1,0x100);
      *puVar4 = puVar3;
      for (iVar5 = 0x40; iVar5 != 0; iVar5 = iVar5 + -1) {
        *puVar3 = 0;
        puVar3 = puVar3 + 1;
      }
      iVar5 = *(int *)(param_1 + 0x24);
      *puVar2 = 0xffffffff;
      iVar6 = iVar6 + 1;
      puVar4 = puVar4 + 0x15;
      puVar2 = puVar2 + 1;
    } while (iVar6 < iVar5);
  }
  return;
}
