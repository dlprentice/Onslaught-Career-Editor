/* address: 0x00402fa0 */
/* name: CUnit__UpdateMotionAndTrailEffects */
/* signature: void __fastcall CUnit__UpdateMotionAndTrailEffects(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CUnit__UpdateMotionAndTrailEffects(void *param_1)

{
  int *piVar1;
  float *pfVar2;
  float fVar3;
  int iVar4;
  void *this;
  int iVar5;
  int iVar6;
  undefined4 *puVar7;
  void *unaff_EDI;
  undefined4 *puVar8;
  float10 fVar9;
  int iStack_84;
  float local_80;
  float local_7c;
  float local_78;
  float fStack_74;
  undefined1 auStack_70 [16];
  undefined4 auStack_60 [12];
  undefined1 auStack_30 [48];

  if ((*(byte *)((int)param_1 + 0x2c) & 4) != 0) {
    local_80 = *(float *)(*(int *)((int)param_1 + 0x164) + 0xb8) * _DAT_005d8608;
    *(float *)((int)param_1 + 300) = local_80;
    *(float *)((int)param_1 + 0x130) = local_80;
    *(float *)((int)param_1 + 0x134) = local_80;
    local_7c = local_80;
    local_78 = local_80;
  }
  *(float *)((int)param_1 + 0x7c) =
       *(float *)((int)param_1 + 0x14c) + *(float *)((int)param_1 + 0x7c);
  *(float *)((int)param_1 + 0x80) =
       *(float *)((int)param_1 + 0x150) + *(float *)((int)param_1 + 0x80);
  *(float *)((int)param_1 + 0x84) =
       *(float *)((int)param_1 + 0x154) + *(float *)((int)param_1 + 0x84);
  fVar9 = (float10)(**(code **)(*(int *)param_1 + 0xb4))();
  *(float *)((int)param_1 + 0x84) = (float)(fVar9 + (float10)*(float *)((int)param_1 + 0x84));
  fVar3 = DAT_006fbdfc;
  if ((*(int *)(*(int *)((int)param_1 + 0x164) + 0x124) == 0) ||
     (fVar9 = (float10)(**(code **)(*(int *)param_1 + 0x40))(),
     fVar9 * (float10)_DAT_005d8604 + (float10)*(float *)((int)param_1 + 0x24) <= (float10)fVar3)) {
    fVar9 = (float10)(**(code **)(*(int *)param_1 + 0x124))();
    *(float *)((int)param_1 + 0x7c) = (float)(fVar9 * (float10)*(float *)((int)param_1 + 0x7c));
    *(float *)((int)param_1 + 0x80) = (float)(fVar9 * (float10)*(float *)((int)param_1 + 0x80));
    *(float *)((int)param_1 + 0x84) = (float)(fVar9 * (float10)*(float *)((int)param_1 + 0x84));
  }
  else {
    *(float *)((int)param_1 + 0x7c) = *(float *)((int)param_1 + 0x7c) * _DAT_005d8600;
    *(float *)((int)param_1 + 0x80) = *(float *)((int)param_1 + 0x80) * _DAT_005d8600;
    *(float *)((int)param_1 + 0x84) = *(float *)((int)param_1 + 0x84) * _DAT_005d8600;
    if ((*(byte *)((int)param_1 + 0x2c) & 4) != 0) {
      (**(code **)(*(int *)param_1 + 0x180))();
    }
  }
  fVar3 = SQRT(*(float *)((int)param_1 + 0x84) * *(float *)((int)param_1 + 0x84) +
               *(float *)((int)param_1 + 0x80) * *(float *)((int)param_1 + 0x80) +
               *(float *)((int)param_1 + 0x7c) * *(float *)((int)param_1 + 0x7c));
  if (_DAT_005d856c < fVar3) {
    fVar9 = (float10)(**(code **)(*(int *)param_1 + 0x1bc))();
    if (fVar9 * (float10)_DAT_005d8584 < (float10)fVar3) {
      fVar9 = (fVar9 * (float10)_DAT_005d8584) / (float10)fVar3;
      *(float *)((int)param_1 + 0x7c) = (float)(fVar9 * (float10)*(float *)((int)param_1 + 0x7c));
      *(float *)((int)param_1 + 0x80) = (float)(fVar9 * (float10)*(float *)((int)param_1 + 0x80));
      *(float *)((int)param_1 + 0x84) = (float)(fVar9 * (float10)*(float *)((int)param_1 + 0x84));
    }
  }
  CUnit__UpdateMotionAttachmentsAndEffects(param_1);
  fVar3 = *(float *)((int)param_1 + 0x170) + _DAT_005d85c0;
  if (*(float *)((int)param_1 + 0x174) <= fVar3) {
    fVar3 = *(float *)((int)param_1 + 0x170) - _DAT_005d85c0;
    if (fVar3 <= *(float *)((int)param_1 + 0x174)) {
      *(undefined4 *)((int)param_1 + 0x170) = *(undefined4 *)((int)param_1 + 0x174);
    }
    else {
      *(float *)((int)param_1 + 0x170) = fVar3;
    }
  }
  else {
    *(float *)((int)param_1 + 0x170) = fVar3;
  }
  fVar9 = (float10)(**(code **)(*(int *)param_1 + 0x16c))();
  iStack_84 = 1;
  *(float *)((int)param_1 + 0x170) =
       (float)(((float10)_DAT_005d8568 - fVar9 * (float10)_DAT_005d85fc) *
              (float10)*(float *)((int)param_1 + 0x170));
  piVar1 = *(int **)((int)param_1 + 0x25c);
  *(int **)((int)param_1 + 0x264) = piVar1;
  if (piVar1 == (int *)0x0) {
    iVar6 = 0;
  }
  else {
    iVar6 = *piVar1;
  }
  while (iVar6 != 0) {
    if ((_DAT_005d856c < *(float *)((int)param_1 + 0x170)) && (*(int *)(iVar6 + 4) == 0)) {
      CParticleManager__CreateEffect
                (*(undefined4 *)(*(int *)((int)param_1 + 0x164) + 8),iVar6,DAT_006600e0,DAT_006600e4
                 ,DAT_006600e8,DAT_006600ec,0,0);
    }
    (**(code **)(*(int *)param_1 + 0x160))(0x18,iStack_84,&local_80,auStack_60);
    puVar7 = *(undefined4 **)(iVar6 + 4);
    if (puVar7 != (undefined4 *)0x0) {
      if (puVar7[0x12] == 0x461c4000) {
        puVar7[0x20] = local_80;
        puVar7[0x21] = local_7c;
        puVar7[0x22] = local_78;
        puVar7[0x23] = fStack_74;
        puVar7[0x10] = local_80;
        puVar7[0x11] = local_7c;
        puVar7[0x12] = local_78;
        puVar7[0x13] = fStack_74;
      }
      else {
        puVar7[0x10] = *puVar7;
        puVar7[0x11] = puVar7[1];
        puVar7[0x12] = puVar7[2];
        puVar7[0x13] = puVar7[3];
      }
      CMeshRenderer__Helper_00403650(puVar7,&local_80,unaff_EDI);
    }
    iVar4 = *(int *)(iVar6 + 4);
    if (iVar4 != 0) {
      puVar7 = (undefined4 *)((int)param_1 + 0x3c);
      puVar8 = (undefined4 *)(iVar4 + 0x10);
      for (iVar5 = 0xc; iVar5 != 0; iVar5 = iVar5 + -1) {
        *puVar8 = *puVar7;
        puVar7 = puVar7 + 1;
        puVar8 = puVar8 + 1;
      }
      *(undefined4 *)(iVar4 + 0xa0) = 1;
    }
    if ((*(int *)(iVar6 + 4) != 0) && (iVar6 = *(int *)(*(int *)(iVar6 + 4) + 0xa8), iVar6 != 0)) {
      *(undefined4 *)(iVar6 + 0x74) = *(undefined4 *)((int)param_1 + 0x170);
    }
    iStack_84 = iStack_84 + 1;
    piVar1 = *(int **)(*(int *)((int)param_1 + 0x264) + 4);
    *(int **)((int)param_1 + 0x264) = piVar1;
    if (piVar1 == (int *)0x0) {
      iVar6 = 0;
    }
    else {
      iVar6 = *piVar1;
    }
  }
  puVar7 = *(undefined4 **)((int)param_1 + 0x26c);
  iVar6 = 1;
  *(undefined4 **)((int)param_1 + 0x274) = puVar7;
  if (puVar7 == (undefined4 *)0x0) {
    this = (void *)0x0;
  }
  else {
    this = (void *)*puVar7;
  }
  while (this != (void *)0x0) {
    iVar4 = (**(code **)(*(int *)param_1 + 0x1d4))();
    if (iVar4 == 0) {
      CUnit__Helper_004cb0b0(this,0,(int)unaff_EDI);
    }
    else {
      if (*(int *)((int)this + 4) == 0) {
        CParticleManager__CreateEffect
                  (*(undefined4 *)(*(int *)((int)param_1 + 0x164) + 0x14),this,DAT_006600e0,
                   DAT_006600e4,DAT_006600e8,DAT_006600ec,0,0);
      }
      (**(code **)(*(int *)param_1 + 0x160))(0x17,iVar6,&local_80,auStack_60);
      pfVar2 = *(float **)((int)this + 4);
      if (pfVar2 != (float *)0x0) {
        if (pfVar2[0x12] == 10000.0) {
          pfVar2[0x20] = local_80;
          pfVar2[0x21] = local_7c;
          pfVar2[0x22] = local_78;
          pfVar2[0x23] = fStack_74;
          pfVar2[0x10] = local_80;
          pfVar2[0x11] = local_7c;
          pfVar2[0x12] = local_78;
          pfVar2[0x13] = fStack_74;
          *pfVar2 = local_80;
          pfVar2[1] = local_7c;
          pfVar2[2] = local_78;
          pfVar2[3] = fStack_74;
          if (pfVar2[0x2b] != -1.0) {
            pfVar2[0x2b] = DAT_00672fd0;
          }
        }
        else {
          pfVar2[0x10] = *pfVar2;
          pfVar2[0x11] = pfVar2[1];
          pfVar2[0x12] = pfVar2[2];
          pfVar2[0x13] = pfVar2[3];
          CMeshRenderer__Helper_00403650(pfVar2,&local_80,unaff_EDI);
        }
      }
      iVar4 = *(int *)((int)this + 4);
      if (iVar4 != 0) {
        puVar7 = auStack_60;
        puVar8 = (undefined4 *)(iVar4 + 0x10);
        for (iVar5 = 0xc; iVar5 != 0; iVar5 = iVar5 + -1) {
          *puVar8 = *puVar7;
          puVar7 = puVar7 + 1;
          puVar8 = puVar8 + 1;
        }
        *(undefined4 *)(iVar4 + 0xa0) = 1;
      }
    }
    iVar6 = iVar6 + 1;
    puVar7 = *(undefined4 **)(*(int *)((int)param_1 + 0x274) + 4);
    *(undefined4 **)((int)param_1 + 0x274) = puVar7;
    if (puVar7 == (undefined4 *)0x0) {
      this = (void *)0x0;
    }
    else {
      this = (void *)*puVar7;
    }
  }
  if (*(float *)((int)param_1 + 0xf8) < _DAT_005d856c) {
    if ((*(float *)((int)param_1 + 0xf8) < -*(float *)(*(int *)((int)param_1 + 0x164) + 0xc0)) &&
       (*(int *)(*(int *)((int)param_1 + 0x164) + 0x11c) == 0)) {
      CExplosionInitThing__ctor_like_004fd230(param_1);
      (**(code **)(*(int *)param_1 + 0x38))();
    }
    if ((*(int *)((int)param_1 + 600) != 0) && ((*(byte *)((int)param_1 + 0x2c) & 1) == 0)) {
      (**(code **)(*(int *)param_1 + 0x160))
                (0x19,*(int *)((int)param_1 + 600),auStack_70,auStack_30);
      pfVar2 = *(float **)((int)param_1 + 0x254);
      if (pfVar2 != (float *)0x0) {
        if (pfVar2[0x12] == 10000.0) {
          pfVar2[0x20] = local_80;
          pfVar2[0x21] = local_7c;
          pfVar2[0x22] = local_78;
          pfVar2[0x23] = fStack_74;
          pfVar2[0x10] = local_80;
          pfVar2[0x11] = local_7c;
          pfVar2[0x12] = local_78;
          pfVar2[0x13] = fStack_74;
          *pfVar2 = local_80;
          pfVar2[1] = local_7c;
          pfVar2[2] = local_78;
          fVar3 = pfVar2[0x2b];
          pfVar2[3] = fStack_74;
        }
        else {
          pfVar2[0x10] = *pfVar2;
          pfVar2[0x11] = pfVar2[1];
          pfVar2[0x12] = pfVar2[2];
          pfVar2[0x13] = pfVar2[3];
          *pfVar2 = local_80;
          pfVar2[1] = local_7c;
          pfVar2[2] = local_78;
          fVar3 = pfVar2[0x2b];
          pfVar2[3] = fStack_74;
        }
        if (fVar3 != -1.0) {
          pfVar2[0x2b] = DAT_00672fd0;
        }
      }
    }
  }
  return;
}
