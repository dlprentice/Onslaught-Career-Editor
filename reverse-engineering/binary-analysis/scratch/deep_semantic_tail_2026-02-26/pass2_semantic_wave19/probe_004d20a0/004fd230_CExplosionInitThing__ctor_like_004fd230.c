/* address: 0x004fd230 */
/* name: CExplosionInitThing__ctor_like_004fd230 */
/* signature: void __fastcall CExplosionInitThing__ctor_like_004fd230(void * param_1) */


void __fastcall CExplosionInitThing__ctor_like_004fd230(void *param_1)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
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

  if (*(int *)((int)param_1 + 0x164) != 0) {
    piVar2 = (int *)CWorldPhysicsManager__CreatePickup
                              (*(undefined4 *)(*(int *)((int)param_1 + 0x164) + 0xe8));
    CInfluenceMap__Init();
    local_3d8 = &PTR_VFuncSlot_00_0040e1b0_005d8c80;
    local_18 = 0;
    local_4 = 0;
    local_8 = 0;
    iVar3 = *(int *)(*(int *)((int)param_1 + 0x164) + 0xe8);
    piVar1 = (int *)*DAT_008553f8;
    iVar4 = 0;
    DAT_008553f8[2] = (int)piVar1;
    if (piVar1 == (int *)0x0) {
      local_1c = 0;
    }
    else {
      local_1c = *piVar1;
    }
    while (local_1c != 0) {
      if (iVar4 == iVar3) goto LAB_004fd2ea;
      iVar4 = iVar4 + 1;
      piVar1 = *(int **)(DAT_008553f8[2] + 4);
      DAT_008553f8[2] = (int)piVar1;
      if (piVar1 == (int *)0x0) {
        local_1c = 0;
      }
      else {
        local_1c = *piVar1;
      }
    }
    local_1c = 0;
LAB_004fd2ea:
    local_338 = *(undefined4 *)((int)param_1 + 0x138);
    local_10 = 1;
    local_c = 1;
    local_14 = param_1;
    iVar3 = (**(code **)(*(int *)param_1 + 0x10c))();
    if (iVar3 == 0) {
      iVar3 = HeightDelta__Below025_D0((int)param_1);
      local_18 = -(uint)(iVar3 != 0) & 2;
    }
    else {
      local_18 = 1;
    }
    if (piVar2 != (int *)0x0) {
      uStack_3d4 = *(undefined4 *)((int)param_1 + 0x1c);
      uStack_3d0 = *(undefined4 *)((int)param_1 + 0x20);
      uStack_3cc = *(undefined4 *)((int)param_1 + 0x24);
      uStack_3c8 = *(undefined4 *)((int)param_1 + 0x28);
      (**(code **)(*piVar2 + 0x24))(&local_3d8);
    }
  }
  return;
}
