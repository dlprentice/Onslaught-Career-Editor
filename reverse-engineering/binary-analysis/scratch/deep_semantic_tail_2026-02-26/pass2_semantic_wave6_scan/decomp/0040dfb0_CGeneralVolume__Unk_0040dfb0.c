/* address: 0x0040dfb0 */
/* name: CGeneralVolume__Unk_0040dfb0 */
/* signature: void __fastcall CGeneralVolume__Unk_0040dfb0(void * param_1) */


void __fastcall CGeneralVolume__Unk_0040dfb0(void *param_1)

{
  byte bVar1;
  byte *pbVar2;
  int *piVar3;
  byte *pbVar4;
  int iVar5;
  int *piVar6;
  int iVar7;
  byte *pbVar8;
  bool bVar9;
  undefined **local_3d8;
  undefined4 uStack_3d4;
  undefined4 uStack_3d0;
  undefined4 uStack_3cc;
  undefined4 uStack_3c8;
  undefined4 local_338;
  int local_1c;
  uint local_18;
  void *local_14;
  undefined4 local_10;
  undefined4 local_c;
  undefined4 local_8;
  undefined4 local_4;

  pbVar2 = *(byte **)(*(int *)((int)param_1 + 0x4b0) + 0x68);
  if (pbVar2 != (byte *)0x0) {
    iVar7 = 0;
    piVar6 = (int *)*DAT_008553f8;
    DAT_008553f8[2] = (int)piVar6;
    if (piVar6 == (int *)0x0) {
      iVar5 = 0;
    }
    else {
      iVar5 = *piVar6;
    }
    while (iVar5 != 0) {
      pbVar8 = *(byte **)(iVar5 + 0x30);
      pbVar4 = pbVar2;
      do {
        bVar1 = *pbVar4;
        bVar9 = bVar1 < *pbVar8;
        if (bVar1 != *pbVar8) {
LAB_0040e011:
          iVar5 = (1 - (uint)bVar9) - (uint)(bVar9 != 0);
          goto LAB_0040e016;
        }
        if (bVar1 == 0) break;
        bVar1 = pbVar4[1];
        bVar9 = bVar1 < pbVar8[1];
        if (bVar1 != pbVar8[1]) goto LAB_0040e011;
        pbVar4 = pbVar4 + 2;
        pbVar8 = pbVar8 + 2;
      } while (bVar1 != 0);
      iVar5 = 0;
LAB_0040e016:
      if (iVar5 == 0) goto LAB_0040e03f;
      iVar7 = iVar7 + 1;
      piVar6 = *(int **)(DAT_008553f8[2] + 4);
      DAT_008553f8[2] = (int)piVar6;
      if (piVar6 == (int *)0x0) {
        iVar5 = 0;
      }
      else {
        iVar5 = *piVar6;
      }
    }
  }
  iVar7 = -1;
LAB_0040e03f:
  piVar6 = (int *)CWorldPhysicsManager__CreatePickup(iVar7);
  CInfluenceMap__Init();
  local_3d8 = &PTR_VFuncSlot_00_0040e1b0_005d8c80;
  local_18 = 0;
  local_c = 0;
  local_4 = 0;
  local_8 = 0;
  pbVar2 = *(byte **)(*(int *)((int)param_1 + 0x4b0) + 0x68);
  if (pbVar2 != (byte *)0x0) {
    piVar3 = (int *)*DAT_008553f8;
    DAT_008553f8[2] = (int)piVar3;
    if (piVar3 == (int *)0x0) {
      local_1c = 0;
    }
    else {
      local_1c = *piVar3;
    }
    while (local_1c != 0) {
      pbVar8 = *(byte **)(local_1c + 0x30);
      pbVar4 = pbVar2;
      do {
        bVar1 = *pbVar4;
        bVar9 = bVar1 < *pbVar8;
        if (bVar1 != *pbVar8) {
LAB_0040e0e7:
          iVar7 = (1 - (uint)bVar9) - (uint)(bVar9 != 0);
          goto LAB_0040e0ec;
        }
        if (bVar1 == 0) break;
        bVar1 = pbVar4[1];
        bVar9 = bVar1 < pbVar8[1];
        if (bVar1 != pbVar8[1]) goto LAB_0040e0e7;
        pbVar4 = pbVar4 + 2;
        pbVar8 = pbVar8 + 2;
      } while (bVar1 != 0);
      iVar7 = 0;
LAB_0040e0ec:
      if (iVar7 == 0) goto LAB_0040e111;
      piVar3 = *(int **)(DAT_008553f8[2] + 4);
      DAT_008553f8[2] = (int)piVar3;
      if (piVar3 == (int *)0x0) {
        local_1c = 0;
      }
      else {
        local_1c = *piVar3;
      }
    }
  }
  local_1c = 0;
LAB_0040e111:
  local_338 = *(undefined4 *)((int)param_1 + 0x138);
  local_10 = 1;
  local_14 = param_1;
  iVar7 = (**(code **)(*(int *)param_1 + 0x10c))();
  if (iVar7 == 0) {
    iVar7 = HeightDelta__Below025_D0((int)param_1);
    local_18 = -(uint)(iVar7 != 0) & 2;
  }
  else {
    local_18 = 1;
  }
  if (piVar6 != (int *)0x0) {
    uStack_3d4 = *(undefined4 *)((int)param_1 + 0x1c);
    uStack_3d0 = *(undefined4 *)((int)param_1 + 0x20);
    uStack_3cc = *(undefined4 *)((int)param_1 + 0x24);
    uStack_3c8 = *(undefined4 *)((int)param_1 + 0x28);
    (**(code **)(*piVar6 + 0x24))(&local_3d8);
  }
  return;
}
