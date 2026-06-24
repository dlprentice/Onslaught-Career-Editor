/* address: 0x0047c970 */
/* name: CCannon__UpdateLinkedEffectsByHeightClearance */
/* signature: void __fastcall CCannon__UpdateLinkedEffectsByHeightClearance(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CCannon__UpdateLinkedEffectsByHeightClearance(void *param_1)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  void *this;
  int iVar4;
  int *piVar5;
  undefined4 *puVar6;
  void *unaff_EDI;
  undefined4 *puVar7;
  float10 fVar8;
  float10 fVar9;
  float10 fVar10;
  float fStack_68;
  int iStack_64;
  float fStack_5c;
  undefined8 uStack_58;
  float fStack_50;
  undefined4 uStack_4c;
  longlong lStack_48;
  float fStack_40;
  float fStack_3c;
  float fStack_38;
  undefined4 uStack_34;
  undefined4 auStack_30 [12];

  fVar8 = (float10)(**(code **)(*(int *)param_1 + 0x60))();
  lStack_48 = (longlong)ROUND(fVar8);
  iVar4 = (int)lStack_48;
  fStack_5c = 0.0;
  iVar2 = (**(code **)(*(int *)param_1 + 0xb8))();
  if (iVar2 != 0) {
    fVar9 = (float10)(**(code **)(*(int *)param_1 + 0xb4))();
    fStack_5c = (float)fVar9;
  }
  fStack_40 = 0.0;
  fStack_3c = 0.0;
  fStack_38 = 0.0;
  fVar9 = (float10)(**(code **)(*(int *)param_1 + 0x124))();
  fStack_68 = (float)fVar9;
  iVar2 = (**(code **)(*(int *)param_1 + 0x10c))();
  if ((((iVar2 != 0) || (iVar2 = HeightDelta__Below025_D0((int)param_1), iVar2 != 0)) ||
      (iVar2 = (**(code **)(*(int *)param_1 + 0xb8))(), iVar2 == 0)) &&
     (iVar2 = (**(code **)(*(int *)param_1 + 0x130))(), iVar2 != 0)) {
    fVar9 = (float10)(**(code **)(*(int *)param_1 + 0x120))();
    fStack_68 = (float)fVar9;
    fStack_40 = *(float *)((int)param_1 + 0x14c) * _DAT_005d8c40;
    fStack_3c = *(float *)((int)param_1 + 0x150) * _DAT_005d8c40;
    uStack_58 = CONCAT44(fStack_3c,fStack_40);
    fStack_50 = *(float *)((int)param_1 + 0x154) * _DAT_005d8c40;
    uStack_34 = uStack_4c;
    fStack_38 = fStack_50;
  }
  if (((*(byte *)((int)param_1 + 0x2c) & 4) == 0) &&
     (*(int *)(*(int *)((int)param_1 + 0x164) + 0x100) == 1)) {
    uStack_58._0_4_ = (float)(longlong)ROUND(*(float *)((int)param_1 + 0x1c));
    uVar3 = (uint)(float)uStack_58;
    uStack_58._0_4_ = (float)(longlong)ROUND(*(float *)((int)param_1 + 0x20));
    uVar1 = (uint)(float)uStack_58;
    uStack_58._4_4_ =
         (undefined4)((ulonglong)(longlong)ROUND(*(float *)((int)param_1 + 0x20)) >> 0x20);
    uStack_58._0_4_ = DAT_006fbdf4;
    uVar3 = CWorld__GetHeightSamplePacked16(0x6fadc8,uVar3,uVar1);
    uStack_58 = CONCAT44(uStack_58._4_4_,
                         *(float *)((int)param_1 + 0x24) -
                         (float)(int)(short)uVar3 * (float)uStack_58);
    fVar9 = (float10)(**(code **)(*(int *)param_1 + 0xc0))();
    if (((float10)(float)uStack_58 - fVar9 <=
         -(float10)*(float *)(*(int *)((int)param_1 + 0x164) + 0x18c)) ||
       (-(float10)*(float *)(*(int *)((int)param_1 + 0x164) + 0x188) <=
        (float10)(float)uStack_58 - fVar9)) {
      if (*(int *)((int)param_1 + 0x1e4) != 0) {
        puVar6 = *(undefined4 **)((int)param_1 + 0x1d4);
        if (puVar6 == (undefined4 *)0x0) {
          this = (void *)0x0;
        }
        else {
          this = (void *)*puVar6;
        }
        while (this != (void *)0x0) {
          CUnit__FinalizeLinkedUnitStateAndClear(this,0,(int)unaff_EDI);
          puVar6 = (undefined4 *)puVar6[1];
          if (puVar6 == (undefined4 *)0x0) {
            this = (void *)0x0;
          }
          else {
            this = (void *)*puVar6;
          }
        }
        *(undefined4 *)((int)param_1 + 0x1e4) = 0;
      }
    }
    else {
      fStack_68 = fStack_68 * _DAT_005dbd88;
      *(undefined4 *)((int)param_1 + 0x1e4) = 1;
      piVar5 = *(int **)((int)param_1 + 0x1d4);
      iStack_64 = 1;
      if (piVar5 == (int *)0x0) {
        iVar2 = 0;
      }
      else {
        iVar2 = *piVar5;
      }
      if (iVar2 != 0) {
        do {
          if (*(int *)(iVar2 + 4) == 0) {
            CParticleManager__CreateEffect
                      (*(undefined4 *)(*(int *)((int)param_1 + 0x164) + 0xc),iVar2,DAT_0067a2f0,
                       DAT_0067a2f4,DAT_0067a2f8,DAT_0067a2fc,0,0);
          }
          (**(code **)(*(int *)param_1 + 0x160))(0x1a,iStack_64,&uStack_58,auStack_30);
          puVar6 = *(undefined4 **)(iVar2 + 4);
          if (puVar6 != (undefined4 *)0x0) {
            if (puVar6[0x12] == 0x461c4000) {
              puVar6[0x20] = (float)uStack_58;
              puVar6[0x21] = uStack_58._4_4_;
              puVar6[0x22] = fStack_50;
              puVar6[0x23] = uStack_4c;
              puVar6[0x10] = (float)uStack_58;
              puVar6[0x11] = uStack_58._4_4_;
              puVar6[0x12] = fStack_50;
              puVar6[0x13] = uStack_4c;
            }
            else {
              puVar6[0x10] = *puVar6;
              puVar6[0x11] = puVar6[1];
              puVar6[0x12] = puVar6[2];
              puVar6[0x13] = puVar6[3];
            }
            CMeshRenderer__Helper_00403650(puVar6,&uStack_58,unaff_EDI);
          }
          iVar4 = *(int *)(iVar2 + 4);
          if (iVar4 != 0) {
            puVar6 = auStack_30;
            puVar7 = (undefined4 *)(iVar4 + 0x10);
            for (iVar2 = 0xc; iVar2 != 0; iVar2 = iVar2 + -1) {
              *puVar7 = *puVar6;
              puVar6 = puVar6 + 1;
              puVar7 = puVar7 + 1;
            }
            *(undefined4 *)(iVar4 + 0xa0) = 1;
          }
          piVar5 = (int *)piVar5[1];
          iStack_64 = iStack_64 + 1;
          if (piVar5 == (int *)0x0) {
            iVar2 = 0;
          }
          else {
            iVar2 = *piVar5;
          }
        } while (iVar2 != 0);
        iVar4 = (int)lStack_48;
      }
    }
  }
  if (0 < iVar4) {
    do {
      iVar4 = iVar4 + -1;
      *(float *)((int)param_1 + 0x7c) = fStack_40 + *(float *)((int)param_1 + 0x7c);
      *(float *)((int)param_1 + 0x80) = fStack_3c + *(float *)((int)param_1 + 0x80);
      *(float *)((int)param_1 + 0x84) = fStack_38 + fStack_5c + *(float *)((int)param_1 + 0x84);
      *(float *)((int)param_1 + 0x7c) = fStack_68 * *(float *)((int)param_1 + 0x7c);
      *(float *)((int)param_1 + 0x80) = fStack_68 * *(float *)((int)param_1 + 0x80);
      *(float *)((int)param_1 + 0x84) = fStack_68 * *(float *)((int)param_1 + 0x84);
    } while (iVar4 != 0);
  }
  fStack_40 = *(float *)((int)param_1 + 0x7c);
  fStack_3c = *(float *)((int)param_1 + 0x80);
  fStack_38 = *(float *)((int)param_1 + 0x84);
  uStack_34 = *(undefined4 *)((int)param_1 + 0x88);
  fVar9 = (float10)(**(code **)(*(int *)param_1 + 0x1bc))();
  fVar10 = SQRT((float10)fStack_40 * (float10)fStack_40 + (float10)fStack_3c * (float10)fStack_3c);
  if (fVar9 * (float10)_DAT_005d8584 < fVar10) {
    fVar10 = (fVar9 * (float10)_DAT_005d8584) / fVar10;
    fStack_3c = (float)(fVar10 * (float10)fStack_3c);
    *(float *)((int)param_1 + 0x7c) = (float)(fVar10 * (float10)fStack_40);
    *(float *)((int)param_1 + 0x80) = fStack_3c;
  }
  CUnit__UpdateMotionAttachmentsAndEffects(param_1);
  if ((*(int *)(*(int *)((int)param_1 + 0x164) + 0x10c) != 0) || (*(int *)((int)param_1 + 600) != 0)
     ) {
    *(undefined4 *)((int)param_1 + 0x254) = *(undefined4 *)((int)param_1 + 0x250);
    if ((*(byte *)((int)param_1 + 0x2c) & 4) != 0) {
      *(float *)((int)param_1 + 0x250) =
           *(float *)((int)param_1 + 0x25c) + *(float *)((int)param_1 + 0x250);
      *(float *)((int)param_1 + 0x25c) =
           *(float *)((int)param_1 + 0x25c) - (float)fVar8 * _DAT_005d8cb0;
      return;
    }
    iVar4 = CUnitAI__IsDeployAnimationState((int)param_1);
    if ((iVar4 != 0) && (*(float *)((int)param_1 + 0x25c) < _DAT_005d85c0)) {
      *(undefined4 *)((int)param_1 + 0x25c) = 0;
      return;
    }
    fVar8 = (float10)(float)fVar8 * (float10)_DAT_005d85c0 +
            (float10)*(float *)((int)param_1 + 0x25c);
    *(float *)((int)param_1 + 0x25c) = (float)fVar8;
    fVar9 = (float10)fsin(fVar8);
    *(float *)((int)param_1 + 0x250) = (float)(fVar9 * (float10)_DAT_005d8578);
    if ((float10)_DAT_005d85e0 < fVar8) {
      *(float *)((int)param_1 + 0x25c) = (float)(fVar8 - (float10)_DAT_005d85e0);
      return;
    }
  }
  return;
}
