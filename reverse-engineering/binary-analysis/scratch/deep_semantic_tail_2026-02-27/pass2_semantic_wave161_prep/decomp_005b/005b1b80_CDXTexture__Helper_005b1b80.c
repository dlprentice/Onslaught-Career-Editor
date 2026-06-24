/* address: 0x005b1b80 */
/* name: CDXTexture__Helper_005b1b80 */
/* signature: void __stdcall CDXTexture__Helper_005b1b80(int param_1) */


void CDXTexture__Helper_005b1b80(int param_1)

{
  int iVar1;
  undefined4 *puVar2;
  int iVar3;
  undefined4 uVar4;

  puVar2 = (undefined4 *)(*(code *)**(undefined4 **)(param_1 + 4))(param_1,1,0x30);
  iVar1 = *(int *)(param_1 + 0x13c);
  iVar3 = *(int *)(param_1 + 0x78) * *(int *)(param_1 + 0x70);
  *(undefined4 **)(param_1 + 0x1c8) = puVar2;
  *puVar2 = &LAB_005b1180;
  puVar2[2] = 0;
  puVar2[10] = iVar3;
  if (iVar1 == 2) {
    iVar1 = *(int *)(param_1 + 4);
    puVar2[1] = &LAB_005b11a0;
    puVar2[3] = &LAB_005b1b40;
    uVar4 = (**(code **)(iVar1 + 4))(param_1,1,iVar3);
    puVar2[8] = uVar4;
    CDXTexture__InitColorTransformLuts();
    return;
  }
  puVar2[1] = &LAB_005b1270;
  puVar2[3] = &LAB_005b12b0;
  puVar2[8] = 0;
  CDXTexture__InitColorTransformLuts();
  return;
}
