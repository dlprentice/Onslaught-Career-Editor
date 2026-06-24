/* address: 0x00591ef0 */
/* name: CDXTexture__Unk_00591ef0 */
/* signature: int __stdcall CDXTexture__Unk_00591ef0(void * param_1) */


int CDXTexture__Unk_00591ef0(void *param_1)

{
  undefined1 uVar1;
  byte bVar2;
  byte bVar3;
  undefined4 *puVar4;
  undefined4 *puVar5;
  int iVar6;
  int iVar7;
  undefined4 unaff_EBX;
  undefined1 *puVar8;
  byte *pbVar9;

  puVar4 = *(undefined4 **)((int)param_1 + 0x18);
  iVar7 = puVar4[1];
  puVar8 = (undefined1 *)*puVar4;
  if (iVar7 == 0) {
    iVar7 = (*(code *)puVar4[3])(param_1);
    if (iVar7 == 0) {
      return 0;
    }
    puVar8 = (undefined1 *)*puVar4;
    iVar7 = puVar4[1];
  }
  uVar1 = *puVar8;
  iVar7 = iVar7 + -1;
  puVar8 = puVar8 + 1;
  if (iVar7 == 0) {
    iVar7 = (*(code *)puVar4[3])(param_1);
    if (iVar7 == 0) {
      return 0;
    }
    puVar8 = (undefined1 *)*puVar4;
    iVar7 = puVar4[1];
  }
  iVar7 = iVar7 + -1;
  pbVar9 = puVar8 + 1;
  if (CONCAT11(uVar1,*puVar8) != 4) {
    puVar5 = *(undefined4 **)param_1;
    puVar5[5] = 0xb;
    (*(code *)*puVar5)(param_1);
  }
  if (iVar7 == 0) {
    iVar7 = (*(code *)puVar4[3])(param_1);
    if (iVar7 == 0) {
      return 0;
    }
    pbVar9 = (byte *)*puVar4;
    iVar7 = puVar4[1];
  }
  bVar2 = *pbVar9;
  iVar7 = iVar7 + -1;
  pbVar9 = pbVar9 + 1;
  if (iVar7 == 0) {
    iVar7 = (*(code *)puVar4[3])(param_1);
    if (iVar7 == 0) {
      return 0;
    }
    pbVar9 = (byte *)*puVar4;
    iVar7 = puVar4[1];
  }
  bVar3 = *pbVar9;
  iVar6 = *(int *)param_1;
  *(undefined4 *)(iVar6 + 0x14) = 0x52;
  *(uint *)(iVar6 + 0x18) = (uint)bVar2 * 0x100 + (uint)bVar3;
  (**(code **)(iVar6 + 4))(param_1,1);
  *puVar4 = pbVar9 + 1;
  puVar4[1] = iVar7 + -1;
  *(undefined4 *)((int)param_1 + 0x118) = unaff_EBX;
  return 1;
}
