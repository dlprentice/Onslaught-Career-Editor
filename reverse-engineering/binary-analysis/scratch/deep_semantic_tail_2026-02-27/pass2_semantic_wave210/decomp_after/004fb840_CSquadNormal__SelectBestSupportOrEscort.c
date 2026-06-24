/* address: 0x004fb840 */
/* name: CSquadNormal__SelectBestSupportOrEscort */
/* signature: void __thiscall CSquadNormal__SelectBestSupportOrEscort(void * this, void * param_1, int param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CSquadNormal__SelectBestSupportOrEscort(void *this,void *param_1,int param_2)

{
  undefined4 *puVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  bool bVar5;
  int iVar6;
  void *pvVar7;
  undefined3 extraout_var;
  uint uVar8;
  uint unaff_EDI;
  double dVar9;
  float fStack_54;
  float local_4c;
  int *piStack_48;
  int iStack_44;
  undefined4 uStack_40;
  float fStack_3c;
  undefined4 *local_38;
  int local_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  float fStack_24;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  float fStack_14;
  undefined4 uStack_10;
  undefined4 uStack_c;
  undefined4 uStack_8;
  float fStack_4;

  local_34 = (int)this + 0x17c;
  iVar6 = LinkedPtrCursor__MoveFirstAndGet(&local_38);
  while (iVar6 != 0) {
    iVar6 = CUnit__IsTargetTimeoutBeforeProfileLimit(iVar6);
    if (iVar6 != 0) {
      return;
    }
    iVar6 = LinkedPtrCursor__MoveNextAndGet(&local_38);
  }
  if (param_1 != (void *)0x0) {
    *(undefined4 *)((int)this + 0x140) = 0;
    CGenericActiveReader__SetReader((void *)((int)this + 0x144),(void *)0x0);
    fVar2 = *(float *)((int)param_1 + 0x1c) - *(float *)((int)this + 0x1c);
    fVar3 = *(float *)((int)param_1 + 0x20) - *(float *)((int)this + 0x20);
    fVar4 = *(float *)((int)param_1 + 0x24) - *(float *)((int)this + 0x24);
    local_4c = -1.0;
    fVar2 = SQRT(fVar4 * fVar4 + fVar3 * fVar3 + fVar2 * fVar2);
    local_34 = (int)this + 0x18c;
    pvVar7 = (void *)LinkedPtrCursor__MoveFirstAndGet(&local_38);
    fVar3 = fStack_3c;
    while (pvVar7 != (void *)0x0) {
      bVar5 = false;
      fStack_3c = fVar3;
      iVar6 = (**(code **)(*(int *)this + 0x10c))();
      if ((((iVar6 != 0) && ((*(byte *)(*(int *)((int)pvVar7 + 0x3d0) + 0x14) & 2) != 0)) ||
          ((iVar6 = HeightDelta__Below025_D0((int)this), iVar6 != 0 &&
           ((*(byte *)(*(int *)((int)pvVar7 + 0x3d0) + 0x14) & 1) != 0)))) ||
         (((iVar6 = (**(code **)(*(int *)this + 0x10c))(), iVar6 == 0 &&
           (iVar6 = HeightDelta__Below025_D0((int)this), iVar6 == 0)) &&
          ((*(byte *)(*(int *)((int)pvVar7 + 0x3d0) + 0x14) & 4) != 0)))) {
        bVar5 = true;
      }
      iVar6 = CSquadNormal__IsTargetMaskCompatible(pvVar7,(int)param_1,unaff_EDI);
      if ((iVar6 != 0) && (bVar5)) {
        iVar6 = *(int *)((int)pvVar7 + 0x3d0);
        if ((fVar2 <= *(float *)(iVar6 + 0x2c)) || (*(float *)(iVar6 + 0x30) <= fVar2)) {
          fStack_54 = fVar2 - *(float *)(iVar6 + 0x30);
        }
        else {
          fStack_54 = 1e+06;
        }
        iVar6 = CUnit__CanProvideSupportNow((int)pvVar7);
        if (iVar6 != 0) {
          iStack_44 = (int)this + 0x18c;
          iVar6 = LinkedPtrCursor__MoveFirstAndGet(&piStack_48);
          while (iVar6 != 0) {
            bVar5 = CUnit__IsInBlockedSupportState(iVar6);
            if (CONCAT31(extraout_var,bVar5) != 0) goto LAB_004fb9fd;
            piStack_48 = (int *)piStack_48[1];
            if (piStack_48 == (int *)0x0) {
              iVar6 = 0;
            }
            else {
              iVar6 = *piStack_48;
            }
          }
          fStack_54 = fStack_54 + _DAT_005db290;
        }
LAB_004fb9fd:
        if (local_4c < fStack_54) {
          CGenericActiveReader__SetReader((void *)((int)this + 0x144),pvVar7);
          local_4c = fStack_54;
        }
      }
      local_38 = (undefined4 *)local_38[1];
      fVar3 = fStack_3c;
      if (local_38 == (undefined4 *)0x0) {
        pvVar7 = (void *)0x0;
      }
      else {
        pvVar7 = (void *)*local_38;
      }
    }
    puVar1 = *(undefined4 **)((int)this + 0x17c);
    if (puVar1 == (undefined4 *)0x0) {
      pvVar7 = (void *)0x0;
    }
    else {
      pvVar7 = (void *)*puVar1;
    }
    while (pvVar7 != (void *)0x0) {
      uVar8 = CSquadNormal__HasActiveMaskMatchWithTarget(pvVar7,(int)param_1,unaff_EDI);
      if (uVar8 != 0) {
        dVar9 = CStaticShadows__Helper_0047eb80(0x6fadc8,(void *)((int)param_1 + 0x1c));
        if ((double)DAT_006fbdfc < dVar9) {
          dVar9 = (double)DAT_006fbdfc;
        }
        dVar9 = dVar9 - (double)*(float *)((int)param_1 + 0x24);
        if (((double)*(float *)(*(int *)((int)pvVar7 + 0xa0) + 0x6c) < dVar9) &&
           (dVar9 < (double)*(float *)(*(int *)((int)pvVar7 + 0xa0) + 0x70))) {
          fStack_54 = 0.0;
          if (((*(uint *)((int)param_1 + 0x34) & 0x80000) != 0) &&
             (uVar8 = CUnit__HasMaskBitsA8(pvVar7,0x80000,unaff_EDI), uVar8 != 0)) {
            fStack_54 = 2e+06;
          }
          piStack_48 = (int *)0x0;
          iStack_44 = 0;
          uStack_40 = 0;
          dVar9 = CUnit__ComputeMinBallisticTravelDistance(pvVar7,(void *)0x0,0.0,0.0,fVar3);
          if (dVar9 <= (double)fVar2) {
            uStack_20 = 0;
            uStack_1c = 0;
            uStack_18 = 0;
            dVar9 = CUnit__ComputeMaxBallisticTravelDistance(pvVar7,(void *)0x0,0.0,0.0,fStack_14);
            if ((double)fVar2 <= dVar9) {
              fStack_54 = fStack_54 + _DAT_005db290;
            }
            else {
              uStack_10 = 0;
              uStack_c = 0;
              uStack_8 = 0;
              dVar9 = CUnit__ComputeMaxBallisticTravelDistance(pvVar7,(void *)0x0,0.0,0.0,fStack_4);
              fStack_54 = (fVar2 - (float)dVar9) + fStack_54;
            }
          }
          else {
            uStack_30 = 0;
            uStack_2c = 0;
            uStack_28 = 0;
            dVar9 = CUnit__ComputeMinBallisticTravelDistance(pvVar7,(void *)0x0,0.0,0.0,fStack_24);
            fStack_54 = ((float)dVar9 - fVar2) + fStack_54;
          }
          iVar6 = CUnit__IsEligibleByDistanceBucketOrRange((int)pvVar7);
          if (iVar6 != 0) {
            fStack_54 = fStack_54 + _DAT_005db290;
          }
          if (local_4c < fStack_54) {
            *(void **)((int)this + 0x140) = pvVar7;
            CGenericActiveReader__SetReader((void *)((int)this + 0x144),(void *)0x0);
            local_4c = fStack_54;
          }
        }
      }
      puVar1 = (undefined4 *)puVar1[1];
      if (puVar1 == (undefined4 *)0x0) {
        pvVar7 = (void *)0x0;
      }
      else {
        pvVar7 = (void *)*puVar1;
      }
    }
  }
  return;
}
