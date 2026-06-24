/* address: 0x00592420 */
/* name: CTexture__Helper_00592420 */
/* signature: int __stdcall CTexture__Helper_00592420(void * param_1) */


int CTexture__Helper_00592420(void *param_1)

{
  byte bVar1;
  undefined4 *puVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  void *unaff_EBX;
  uint uVar6;
  byte *pbVar7;

  puVar2 = *(undefined4 **)((int)param_1 + 0x18);
  iVar5 = puVar2[1];
  pbVar7 = (byte *)*puVar2;
  while( true ) {
    if (iVar5 == 0) {
      iVar5 = (*(code *)puVar2[3])(param_1);
      if (iVar5 == 0) {
        return 0;
      }
      pbVar7 = (byte *)*puVar2;
      iVar5 = puVar2[1];
    }
    bVar1 = *pbVar7;
    while( true ) {
      pbVar7 = pbVar7 + 1;
      iVar5 = iVar5 + -1;
      if (bVar1 == 0xff) break;
      *(int *)(*(int *)((int)param_1 + 0x1bc) + 0x18) =
           *(int *)(*(int *)((int)param_1 + 0x1bc) + 0x18) + 1;
      *puVar2 = pbVar7;
      puVar2[1] = iVar5;
      if (iVar5 == 0) {
        iVar5 = (*(code *)puVar2[3])(param_1);
        if (iVar5 == 0) {
          return 0;
        }
        pbVar7 = (byte *)*puVar2;
        iVar5 = puVar2[1];
      }
      bVar1 = *pbVar7;
    }
    do {
      if (iVar5 == 0) {
        iVar5 = (*(code *)puVar2[3])(param_1);
        if (iVar5 == 0) {
          return 0;
        }
        pbVar7 = (byte *)*puVar2;
        iVar5 = puVar2[1];
      }
      uVar6 = (uint)*pbVar7;
      iVar5 = iVar5 + -1;
      pbVar7 = pbVar7 + 1;
    } while (uVar6 == 0xff);
    if (uVar6 != 0) break;
    *(int *)(*(int *)((int)param_1 + 0x1bc) + 0x18) =
         *(int *)(*(int *)((int)param_1 + 0x1bc) + 0x18) + 2;
    *puVar2 = pbVar7;
    puVar2[1] = iVar5;
  }
  iVar3 = *(int *)(*(int *)((int)param_1 + 0x1bc) + 0x18);
  if (iVar3 != 0) {
    iVar4 = *(int *)param_1;
    *(undefined4 *)(iVar4 + 0x14) = 0x74;
    *(int *)(iVar4 + 0x18) = iVar3;
    *(uint *)(iVar4 + 0x1c) = uVar6;
    (**(code **)(iVar4 + 4))(param_1,0xffffffff);
    *(undefined4 *)(*(int *)((int)unaff_EBX + 0x1bc) + 0x18) = 0;
    param_1 = unaff_EBX;
  }
  *puVar2 = pbVar7;
  puVar2[1] = iVar5;
  *(uint *)((int)param_1 + 0x1a4) = uVar6;
  return 1;
}
