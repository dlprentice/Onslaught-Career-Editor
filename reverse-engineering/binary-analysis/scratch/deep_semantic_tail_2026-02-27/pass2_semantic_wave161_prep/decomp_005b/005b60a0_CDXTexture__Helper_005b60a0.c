/* address: 0x005b60a0 */
/* name: CDXTexture__Helper_005b60a0 */
/* signature: void __stdcall CDXTexture__Helper_005b60a0(int param_1) */


void CDXTexture__Helper_005b60a0(int param_1)

{
  int iVar1;
  undefined4 *puVar2;
  int *piVar3;
  uint uVar4;
  int iVar5;
  undefined4 *puVar6;
  undefined4 *puVar7;
  int iVar8;
  undefined4 *puVar9;
  int iStack_1c;
  undefined4 *puStack_18;
  int iStack_8;

  iVar1 = *(int *)(param_1 + 0xf4);
  iVar5 = *(int *)(param_1 + 0x15c);
  iStack_8 = (*(code *)**(undefined4 **)(param_1 + 4))
                       (param_1,1,*(int *)(param_1 + 0x3c) * iVar1 * 0x14);
  iStack_1c = 0;
  if (0 < *(int *)(param_1 + 0x3c)) {
    piVar3 = (int *)(*(int *)(param_1 + 0x44) + 8);
    puVar9 = (undefined4 *)(iStack_8 + iVar1 * 4);
    puStack_18 = (undefined4 *)(iVar5 + 8);
    do {
      puVar2 = (undefined4 *)
               (**(code **)(*(int *)(param_1 + 4) + 8))
                         (param_1,1,(piVar3[5] * *(int *)(param_1 + 0xf0) * 8) / *piVar3,iVar1 * 3);
      puVar7 = puVar2;
      puVar6 = puVar9;
      for (uVar4 = (uint)(iVar1 * 0xc) >> 2; uVar4 != 0; uVar4 = uVar4 - 1) {
        *puVar6 = *puVar7;
        puVar7 = puVar7 + 1;
        puVar6 = puVar6 + 1;
      }
      for (iVar5 = 0; iVar5 != 0; iVar5 = iVar5 + -1) {
        *(undefined1 *)puVar6 = *(undefined1 *)puVar7;
        puVar7 = (undefined4 *)((int)puVar7 + 1);
        puVar6 = (undefined4 *)((int)puVar6 + 1);
      }
      if (0 < iVar1) {
        puVar6 = (undefined4 *)(iVar1 * 0x10 + iStack_8);
        puVar7 = puVar2 + iVar1 * 2;
        iVar8 = iStack_8 - (int)puVar2;
        iVar5 = iVar1;
        do {
          *(undefined4 *)(iVar8 + (int)puVar2) = *puVar7;
          *puVar6 = *puVar2;
          puVar7 = puVar7 + 1;
          puVar2 = puVar2 + 1;
          puVar6 = puVar6 + 1;
          iVar5 = iVar5 + -1;
        } while (iVar5 != 0);
      }
      *puStack_18 = puVar9;
      puVar9 = puVar9 + iVar1 * 5;
      iStack_8 = iStack_8 + iVar1 * 0x14;
      puStack_18 = puStack_18 + 1;
      iStack_1c = iStack_1c + 1;
      piVar3 = piVar3 + 0x15;
    } while (iStack_1c < *(int *)(param_1 + 0x3c));
  }
  return;
}
