/* address: 0x0040acc0 */
/* name: CBattleEngine__Helper_0040acc0 */
/* signature: int __thiscall CBattleEngine__Helper_0040acc0(void * this, void * param_1, void * param_2, int param_3, int param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __thiscall
CBattleEngine__Helper_0040acc0(void *this,void *param_1,void *param_2,int param_3,int param_4)

{
  void *this_00;
  int iVar1;
  uint uVar2;
  int *piVar3;
  void *unaff_EDI;
  double dVar4;
  int in_stack_fffffe6c;
  float local_130;
  int local_12c;
  undefined1 *puStack_124;
  undefined1 local_120 [48];
  undefined4 uStack_f0;
  undefined4 uStack_ec;
  undefined4 uStack_e8;
  undefined4 uStack_e4;
  undefined4 uStack_e0;
  undefined4 uStack_dc;
  undefined4 uStack_d8;
  undefined4 uStack_d4;
  int aiStack_d0 [8];
  undefined **appuStack_b0 [5];
  undefined4 uStack_9c;
  undefined4 uStack_98;
  undefined4 uStack_94;
  undefined4 uStack_90;
  undefined4 uStack_8c;
  undefined4 uStack_88;
  undefined4 uStack_84;
  undefined4 uStack_80;
  undefined1 auStack_3c [48];
  void *pvStack_c;
  undefined1 *puStack_8;
  undefined4 uStack_4;

  uStack_4 = 0xffffffff;
  puStack_8 = &LAB_005d124b;
  pvStack_c = ExceptionList;
  local_12c = 0;
  ExceptionList = &pvStack_c;
  if (*(int *)((int)this + 0x574) != 0) {
    ExceptionList = &pvStack_c;
    if (param_3 != 0) {
      ExceptionList = &pvStack_c;
      CGenericActiveReader__SetReader((void *)((int)this + 0x4c8),(void *)0x0);
      CGenericActiveReader__SetReader((void *)((int)this + 0x4cc),(void *)0x0);
    }
    CBattleEngine__Unk_004062d0
              (local_120,*(void **)((int)this + 0x4e8),*(float *)((int)this + 0x4f4),0.0,
               (float)unaff_EDI);
    this_00 = (void *)(**(code **)(*(int *)this + 0x1d4))();
    dVar4 = CEngine__Unk_00509c80
                      (this_00,*(int *)((int)this + 0x1c),*(int *)((int)this + 0x20),
                       *(float *)((int)this + 0x24),*(float *)((int)this + 0x28));
    local_130 = (float)dVar4;
    if (dVar4 <= (double)_DAT_005d856c) {
      local_130 = 1000.0;
    }
    CPlayer__Unk_004d2a70(*(void **)((int)this + 0x574),(int)&uStack_f0,unaff_EDI);
    CPlayer__Unk_004d2ae0(*(void **)((int)this + 0x574),(int)auStack_3c,unaff_EDI);
    Vec3__SetXYZ();
    Vec3__SetXYZ();
    Vec3__SetXYZ();
    Mat34__SetRows();
    Vec3__SetXYZ();
    Vec3__SetXYZ();
    CGeneralVolume__ctor_like_0040b100(appuStack_b0);
    uStack_9c = uStack_f0;
    uStack_98 = uStack_ec;
    uStack_94 = uStack_e8;
    uStack_90 = uStack_e4;
    uStack_8c = uStack_e0;
    uStack_88 = uStack_dc;
    uStack_84 = uStack_d8;
    uStack_80 = uStack_d4;
    appuStack_b0[0] = &PTR_VFuncSlot_00_00426340_005d8bfc;
    uStack_4 = 0;
    aiStack_d0[0] = 0;
    aiStack_d0[1] = 0xffffffff;
    aiStack_d0[2] = 0;
    aiStack_d0[3] = 0xbf800000;
    piVar3 = (int *)((int)this + 0x4d0);
    if (param_3 == 0) {
      piVar3 = aiStack_d0;
    }
    puStack_124 = &stack0xfffffe6c;
    CGeneralVolume__ctor_like_004098e0(&stack0xfffffe6c,appuStack_b0,in_stack_fffffe6c);
    iVar1 = CWorld__Unk_0050b030();
    if (((iVar1 == 3) && (iVar1 = *piVar3, (*(byte *)(iVar1 + 0x34) & 0x10) != 0)) &&
       (((*(uint *)(iVar1 + 0x34) & 0x100) == 0 ||
        (dVar4 = CUnit__Unk_004f99f0(iVar1), (double)_DAT_005d856c < dVar4)))) {
      if ((float)piVar3[3] < local_130) {
        local_12c = *piVar3;
      }
      if (param_3 != 0) {
        CGenericActiveReader__SetReader((void *)((int)this + 0x4cc),(void *)*piVar3);
      }
    }
  }
  uStack_4 = 0xffffffff;
  if (param_1 != (void *)0x0) {
    uVar2 = Random__NextLCGAbs(DAT_008a9d9c);
    uVar2 = uVar2 & 0x8000ffff;
    if ((int)uVar2 < 0) {
      uVar2 = (uVar2 - 1 | 0xffff0000) + 1;
    }
    puStack_124 = (undefined1 *)((float)(int)uVar2 * _DAT_005d8808 + DAT_00672fd0 + _DAT_005d85c0);
    CEventManager__AddEvent_AtTime
              (&EVENT_MANAGER,0x1772,this,(float *)&puStack_124,0,(void *)0x0,param_1);
  }
  ExceptionList = pvStack_c;
  return local_12c;
}
