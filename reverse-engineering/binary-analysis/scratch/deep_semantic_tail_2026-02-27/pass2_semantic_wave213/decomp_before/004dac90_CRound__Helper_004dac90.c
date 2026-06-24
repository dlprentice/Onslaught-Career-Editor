/* address: 0x004dac90 */
/* name: CRound__Helper_004dac90 */
/* signature: void __thiscall CRound__Helper_004dac90(void * this, void * param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CRound__Helper_004dac90(void *this,void *param_1,void *param_2)

{
  int *this_00;
  float fVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  void *to_read;
  uint uVar4;
  int iVar5;
  undefined4 *puVar6;
  int unaff_EDI;
  undefined4 *puVar7;
  float10 fVar8;
  float local_48;
  float local_44;
  float local_40;
  float local_3c;
  float local_38;
  undefined4 local_34;
  undefined4 local_30 [4];
  undefined4 local_20;
  float local_18;
  undefined4 local_10;
  float local_c;

  if (*(int *)(*(int *)((int)this + 0xf0) + 0x48) == 1) {
    this_00 = (int *)((int)this + 0xe8);
    if ((*(int *)((int)this + 0xe8) == 0) && (*(int *)((int)this + 0xec) != 0)) {
      local_48 = -2.0;
      puVar6 = (undefined4 *)((int)this + 0x3c);
      puVar7 = local_30;
      for (iVar5 = 0xc; local_44 = local_18, uVar3 = local_20, uVar2 = local_30[2], iVar5 != 0;
          iVar5 = iVar5 + -1) {
        *puVar7 = *puVar6;
        puVar6 = puVar6 + 1;
        puVar7 = puVar7 + 1;
      }
      local_20 = local_30[1];
      local_30[1] = uVar3;
      local_30[2] = local_10;
      local_10 = uVar2;
      local_18 = local_c;
      to_read = CSPtrSet__First(&DAT_008550d0);
      while (to_read != (void *)0x0) {
        uVar4 = *(uint *)((int)to_read + 0x34) & 8;
        if (((uVar4 != 0) && (*(int *)((int)this + 0x130) != 0)) || (uVar4 == 0)) {
          Vec3__SetXYZ();
          fVar1 = SQRT(local_40 * local_40 + local_38 * local_38 + local_3c * local_3c);
          if (fVar1 != _DAT_005d856c) {
            fVar1 = _DAT_005d8568 / fVar1;
            local_40 = fVar1 * local_40;
            local_3c = fVar1 * local_3c;
            local_38 = local_38 * fVar1;
          }
          iVar5 = *(int *)((int)this + 0xf0);
          if (*(int *)(iVar5 + 0x54) == 0) {
            if (((local_48 < local_3c) &&
                (fVar8 = (float10)fcos((float10)*(float *)(iVar5 + 0x40)), fVar8 < (float10)local_3c
                )) && (iVar5 = CBattleEngine__IsWeaponModeCompatibleWithMountState
                                         (*(void **)((int)this + 0xec),
                                          *(int *)((int)to_read + 0x138),unaff_EDI), iVar5 != 0)) {
              if ((to_read != (void *)0x0) &&
                 ((*(int *)(*(int *)((int)this + 0xf0) + 0x48) != 0 ||
                  (*(float *)(*(int *)((int)this + 0xf0) + 0x1c) < _DAT_005d856c)))) {
                CRound__RemoveActiveReaderById(this);
                CGenericActiveReader__SetReader(this_00,to_read);
                if ((*(byte *)((int)to_read + 0x34) & 8) != 0) {
                  CSPtrSet__AddToHead(&DAT_008551a0,this);
                }
              }
              local_48 = local_3c;
            }
          }
          else if (((local_48 < local_3c) &&
                   (fVar8 = (float10)fcos((float10)*(float *)(iVar5 + 0x40)),
                   (float10)local_3c < fVar8)) &&
                  (iVar5 = CBattleEngine__IsWeaponModeCompatibleWithMountState
                                     (*(void **)((int)this + 0xec),*(int *)((int)to_read + 0x138),
                                      unaff_EDI), iVar5 != 0)) {
            if ((to_read != (void *)0x0) &&
               ((*(int *)(*(int *)((int)this + 0xf0) + 0x48) != 0 ||
                (*(float *)(*(int *)((int)this + 0xf0) + 0x1c) < _DAT_005d856c)))) {
              CRound__RemoveActiveReaderById(this);
              CGenericActiveReader__SetReader(this_00,to_read);
              if ((*(byte *)((int)to_read + 0x34) & 8) != 0) {
                CSPtrSet__AddToHead(&DAT_008551a0,this);
              }
            }
            local_48 = local_3c;
          }
        }
        to_read = CSPtrSet__Next(&DAT_008550d0);
      }
    }
    iVar5 = *this_00;
    if (iVar5 == 0) {
      local_40 = -1.0;
      local_3c = -1.0;
      local_38 = -1.0;
      *(undefined4 *)((int)this + 0x108) = 0xbf800000;
      *(undefined4 *)((int)this + 0x10c) = 0xbf800000;
      *(undefined4 *)((int)this + 0x110) = 0xbf800000;
    }
    else {
      *(undefined4 *)((int)this + 0x108) = *(undefined4 *)(iVar5 + 0x1c);
      *(undefined4 *)((int)this + 0x10c) = *(undefined4 *)(iVar5 + 0x20);
      *(undefined4 *)((int)this + 0x110) = *(undefined4 *)(iVar5 + 0x24);
      local_34 = *(undefined4 *)(iVar5 + 0x28);
    }
    *(undefined4 *)((int)this + 0x114) = local_34;
    uVar4 = Random__NextLCGAbs(DAT_008a9d9c);
    uVar4 = uVar4 & 0x8000ffff;
    if ((int)uVar4 < 0) {
      uVar4 = (uVar4 - 1 | 0xffff0000) + 1;
    }
    local_44 = (float)(int)uVar4 * _DAT_005d8d50 + DAT_00672fd0 + _DAT_005d858c;
    CEventManager__AddEvent_AtTime(&EVENT_MANAGER,0xfa3,this,&local_44,0,(void *)0x0,param_1);
  }
  return;
}
