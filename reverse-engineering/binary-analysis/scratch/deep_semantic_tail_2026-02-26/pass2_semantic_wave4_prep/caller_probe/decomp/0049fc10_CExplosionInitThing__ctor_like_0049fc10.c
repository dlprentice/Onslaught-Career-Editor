/* address: 0x0049fc10 */
/* name: CExplosionInitThing__ctor_like_0049fc10 */
/* signature: void __fastcall CExplosionInitThing__ctor_like_0049fc10(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CExplosionInitThing__ctor_like_0049fc10(void *param_1)

{
  int iVar1;
  int iVar2;
  int *piVar3;
  float fVar4;
  float fVar5;
  int *piVar6;
  int iVar7;
  undefined **ppuStack_3d8;
  undefined4 uStack_3d4;
  undefined4 uStack_3d0;
  undefined4 uStack_3cc;
  undefined4 uStack_3c8;
  undefined4 uStack_338;
  int iStack_1c;
  undefined4 uStack_18;
  void *pvStack_14;
  undefined4 uStack_10;
  undefined4 uStack_c;
  undefined4 uStack_8;
  undefined4 uStack_4;

  if ((*(byte *)((int)param_1 + 0x2c) & 4) != 0) {
    fVar4 = *(float *)((int)param_1 + 0x264) + _DAT_005d8bbc;
    *(float *)((int)param_1 + 0x264) = fVar4;
    fVar5 = fVar4 + *(float *)((int)param_1 + 0x260);
    *(float *)((int)param_1 + 0x260) = fVar5;
    if (-*(float *)((int)param_1 + 0x268) <= fVar5) {
      fVar4 = fVar4 * _DAT_005d8bf0;
      *(float *)((int)param_1 + 0x260) = -*(float *)((int)param_1 + 0x268);
      *(float *)((int)param_1 + 0x264) = fVar4;
    }
    (**(code **)(*(int *)param_1 + 0x17c))();
  }
  iVar1 = *(int *)((int)param_1 + 0x70);
  if (((iVar1 != 0) && (*(int *)(iVar1 + 0xd0) != 0)) &&
     (piVar6 = (int *)CWorldPhysicsManager__CreatePickup
                                (*(undefined4 *)(*(int *)((int)param_1 + 0x164) + 0xf0)),
     piVar6 != (int *)0x0)) {
    CInfluenceMap__Init();
    ppuStack_3d8 = &PTR_VFuncSlot_00_0040e1b0_005d8c80;
    uStack_3d4 = *(undefined4 *)(iVar1 + 0xd4);
    uStack_10 = 0;
    uStack_3d0 = *(undefined4 *)(iVar1 + 0xd8);
    uStack_c = 0;
    uStack_4 = 0;
    uStack_3cc = *(undefined4 *)(iVar1 + 0xdc);
    uStack_8 = 0;
    uStack_3c8 = *(undefined4 *)(iVar1 + 0xe0);
    uStack_338 = *(undefined4 *)((int)param_1 + 0x138);
    iVar2 = *(int *)(*(int *)((int)param_1 + 0x164) + 0xf0);
    piVar3 = (int *)*DAT_008553f8;
    iVar7 = 0;
    DAT_008553f8[2] = (int)piVar3;
    if (piVar3 == (int *)0x0) {
      iStack_1c = 0;
    }
    else {
      iStack_1c = *piVar3;
    }
    while (iStack_1c != 0) {
      if (iVar7 == iVar2) goto LAB_0049fd72;
      iVar7 = iVar7 + 1;
      piVar3 = *(int **)(DAT_008553f8[2] + 4);
      DAT_008553f8[2] = (int)piVar3;
      if (piVar3 == (int *)0x0) {
        iStack_1c = 0;
      }
      else {
        iStack_1c = *piVar3;
      }
    }
    iStack_1c = 0;
LAB_0049fd72:
    uStack_18 = 0;
    pvStack_14 = param_1;
    (**(code **)(*piVar6 + 0x24))(&ppuStack_3d8);
    *(undefined4 *)(iVar1 + 0xd0) = 0;
  }
  CCannon__Helper_0047c970(param_1);
  return;
}
