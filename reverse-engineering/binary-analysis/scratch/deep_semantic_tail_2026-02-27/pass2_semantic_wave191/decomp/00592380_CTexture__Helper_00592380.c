/* address: 0x00592380 */
/* name: CTexture__Helper_00592380 */
/* signature: int __stdcall CTexture__Helper_00592380(void * param_1) */


int CTexture__Helper_00592380(void *param_1)

{
  byte bVar1;
  byte bVar2;
  undefined4 *puVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  int unaff_EBX;
  byte *pbVar7;

  puVar3 = *(undefined4 **)((int)param_1 + 0x18);
  iVar6 = puVar3[1];
  pbVar7 = (byte *)*puVar3;
  if (iVar6 == 0) {
    iVar6 = (*(code *)puVar3[3])(param_1);
    if (iVar6 == 0) {
      return 0;
    }
    pbVar7 = (byte *)*puVar3;
    iVar6 = puVar3[1];
  }
  bVar1 = *pbVar7;
  iVar6 = iVar6 + -1;
  pbVar7 = pbVar7 + 1;
  if (iVar6 == 0) {
    iVar6 = (*(code *)puVar3[3])(param_1);
    if (iVar6 == 0) {
      return 0;
    }
    pbVar7 = (byte *)*puVar3;
    iVar6 = puVar3[1];
  }
  bVar2 = *pbVar7;
  iVar4 = *(int *)param_1;
  uVar5 = *(undefined4 *)((int)param_1 + 0x1a4);
  *(undefined4 *)(iVar4 + 0x14) = 0x5b;
  *(undefined4 *)(iVar4 + 0x18) = uVar5;
  *(uint *)(iVar4 + 0x1c) = (uint)bVar1 * 0x100 + -2 + (uint)bVar2;
  (**(code **)(iVar4 + 4))(param_1,1);
  *puVar3 = pbVar7 + 1;
  puVar3[1] = iVar6 + -1;
  if (0 < unaff_EBX) {
    (**(code **)(*(int *)((int)param_1 + 0x18) + 0x10))(param_1,unaff_EBX);
  }
  return 1;
}
