/* address: 0x004fa8d0 */
/* name: CUnit__Unk_004fa8d0 */
/* signature: void __fastcall CUnit__Unk_004fa8d0(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CUnit__Unk_004fa8d0(void *param_1)

{
  float fVar1;
  float fVar2;
  int *piVar3;
  float fVar4;
  undefined4 uVar5;
  bool bVar6;
  int iVar7;
  undefined3 extraout_var;
  void *pvVar8;
  int iVar9;
  void *unaff_ESI;
  undefined4 *puVar10;
  void *unaff_EDI;
  undefined4 *puVar11;
  float10 fVar12;
  float10 fVar13;
  float10 fVar14;
  char *pcVar15;
  void *pvVar16;
  int iStack_a8;
  float fStack_a4;
  int iStack_a0;
  undefined4 uStack_90;
  undefined4 uStack_8c;
  undefined4 uStack_88;
  undefined4 uStack_84;
  float fStack_80;
  float fStack_7c;
  float fStack_74;
  float afStack_70 [4];
  undefined4 auStack_60 [12];
  undefined4 auStack_30 [12];

  if ((*(int **)((int)param_1 + 0x208) == (int *)0x0) ||
     ((*(int *)((int)param_1 + 0x214) == 0 && ((*(byte *)((int)param_1 + 0x2c) & 4) == 0)))) {
    (**(code **)(*(int *)param_1 + 0x100))();
  }
  else {
    (**(code **)(**(int **)((int)param_1 + 0x208) + 0xc))();
  }
  *(undefined4 *)((int)param_1 + 0x248) = 0;
  CUnit__Unk_004fa800(param_1);
  CUnit__IntegrateVelocityAndResolveGroundCollision(param_1);
  iVar7 = (**(code **)(*(int *)param_1 + 0x130))();
  if (iVar7 != 0) {
    if (((*(float *)((int)param_1 + 0x120) != *(float *)((int)param_1 + 0x114)) ||
        (*(float *)((int)param_1 + 0x124) != *(float *)((int)param_1 + 0x118))) ||
       (*(float *)((int)param_1 + 0x128) != *(float *)((int)param_1 + 0x11c))) {
      (**(code **)(*(int *)param_1 + 0x134))
                ((int)param_1 + 0x114,(int)param_1 + 0x120,(int)param_1 + 300,(int)param_1 + 0x3c);
    }
  }
  if ((*(byte *)((int)param_1 + 0x2c) & 4) == 0) {
    fVar1 = *(float *)((int)param_1 + 0x108) + *(float *)((int)param_1 + 0x100);
    *(float *)((int)param_1 + 0x100) = fVar1;
    if (*(float *)((int)param_1 + 0x104) < fVar1) {
      *(undefined4 *)((int)param_1 + 0x100) = *(undefined4 *)((int)param_1 + 0x104);
    }
  }
  else if (*(int *)(*(int *)((int)param_1 + 0x164) + 0x124) != 0) {
    fVar12 = (float10)(**(code **)(*(int *)param_1 + 0x60))();
    iStack_a0 = (int)(longlong)ROUND(fVar12);
    if (0 < iStack_a0) {
      do {
        (**(code **)(*(int *)param_1 + 0x17c))();
        iStack_a0 = iStack_a0 + -1;
      } while (iStack_a0 != 0);
    }
  }
  fVar1 = *(float *)((int)param_1 + 0x170) + _DAT_005d85c0;
  if (*(float *)((int)param_1 + 0x174) <= fVar1) {
    fVar1 = *(float *)((int)param_1 + 0x170) - _DAT_005d85c0;
    if (fVar1 <= *(float *)((int)param_1 + 0x174)) {
      *(undefined4 *)((int)param_1 + 0x170) = *(undefined4 *)((int)param_1 + 0x174);
    }
    else {
      *(float *)((int)param_1 + 0x170) = fVar1;
    }
  }
  else {
    *(float *)((int)param_1 + 0x170) = fVar1;
  }
  piVar3 = *(int **)((int)param_1 + 0x1c4);
  iStack_a8 = 1;
  if (piVar3 == (int *)0x0) {
    iVar7 = 0;
  }
  else {
    iVar7 = *piVar3;
  }
  while (iVar7 != 0) {
    if (*(int *)(iVar7 + 4) != 0) {
      (**(code **)(*(int *)param_1 + 0x160))(0x15,iStack_a8,&uStack_90,auStack_60);
      if (*(void **)(iVar7 + 4) != (void *)0x0) {
        CUnit__Helper_004097a0(*(void **)(iVar7 + 4),&uStack_90,unaff_EDI);
      }
      iVar7 = *(int *)(iVar7 + 4);
      if (iVar7 != 0) {
        puVar10 = auStack_60;
        puVar11 = (undefined4 *)(iVar7 + 0x10);
        for (iVar9 = 0xc; iVar9 != 0; iVar9 = iVar9 + -1) {
          *puVar11 = *puVar10;
          puVar10 = puVar10 + 1;
          puVar11 = puVar11 + 1;
        }
        *(undefined4 *)(iVar7 + 0xa0) = 1;
      }
    }
    piVar3 = (int *)piVar3[1];
    iStack_a8 = iStack_a8 + 1;
    if (piVar3 == (int *)0x0) {
      iVar7 = 0;
    }
    else {
      iVar7 = *piVar3;
    }
  }
  if (((*(int *)((int)param_1 + 0x168) == 1) && (*(int *)(*(int *)((int)param_1 + 0x1ac) + 4) != 0))
     && (*(void **)((int)param_1 + 0x140) != (void *)0x0)) {
    OID__Helper_0044a850(*(void **)((int)param_1 + 0x140),(int)afStack_70,unaff_EDI);
    OID__Helper_0044a930(*(void **)((int)param_1 + 0x140),(int)auStack_30,unaff_EDI);
    pvVar8 = *(void **)(*(int *)((int)param_1 + 0x1ac) + 4);
    if (pvVar8 != (void *)0x0) {
      CUnit__Helper_004097a0(pvVar8,afStack_70,unaff_EDI);
    }
    iVar7 = *(int *)(*(int *)((int)param_1 + 0x1ac) + 4);
    if (iVar7 != 0) {
      puVar10 = auStack_30;
      puVar11 = (undefined4 *)(iVar7 + 0x10);
      for (iVar9 = 0xc; iVar9 != 0; iVar9 = iVar9 + -1) {
        *puVar11 = *puVar10;
        puVar10 = puVar10 + 1;
        puVar11 = puVar11 + 1;
      }
      *(undefined4 *)(iVar7 + 0xa0) = 1;
    }
  }
  if ((*(int *)(*(int *)((int)param_1 + 0x164) + 0x10c) != 0) &&
     (iVar7 = (**(code **)(*(int *)param_1 + 0x10c))(), iVar7 != 0)) {
    piVar3 = *(int **)((int)param_1 + 0x1b4);
    iStack_a8 = 1;
    if (piVar3 == (int *)0x0) {
      iVar7 = 0;
    }
    else {
      iVar7 = *piVar3;
    }
    while (iVar7 != 0) {
      if ((*(int *)(iVar7 + 4) != 0) ||
         (CParticleManager__CreateEffect
                    (*(undefined4 *)(*(int *)((int)param_1 + 0x164) + 0x18),iVar7,DAT_00854d80,
                     DAT_00854d84,DAT_00854d88,DAT_00854d8c,0,0), *(int *)(iVar7 + 4) != 0)) {
        (**(code **)(*(int *)param_1 + 0x160))(0x16,iStack_a8,&uStack_90,auStack_60);
        puVar10 = *(undefined4 **)(iVar7 + 4);
        if (puVar10 != (undefined4 *)0x0) {
          if (puVar10[0x12] == 0x461c4000) {
            puVar10[0x20] = uStack_90;
            puVar10[0x21] = uStack_8c;
            puVar10[0x22] = uStack_88;
            puVar10[0x23] = uStack_84;
            puVar10[0x10] = uStack_90;
            puVar10[0x11] = uStack_8c;
            puVar10[0x12] = uStack_88;
            puVar10[0x13] = uStack_84;
          }
          else {
            puVar10[0x10] = *puVar10;
            puVar10[0x11] = puVar10[1];
            puVar10[0x12] = puVar10[2];
            puVar10[0x13] = puVar10[3];
          }
          CMeshRenderer__Helper_00403650(puVar10,&uStack_90,unaff_EDI);
        }
        iVar7 = *(int *)(iVar7 + 4);
        if (iVar7 != 0) {
          puVar10 = auStack_60;
          puVar11 = (undefined4 *)(iVar7 + 0x10);
          for (iVar9 = 0xc; iVar9 != 0; iVar9 = iVar9 + -1) {
            *puVar11 = *puVar10;
            puVar10 = puVar10 + 1;
            puVar11 = puVar11 + 1;
          }
          *(undefined4 *)(iVar7 + 0xa0) = 1;
        }
      }
      piVar3 = (int *)piVar3[1];
      iStack_a8 = iStack_a8 + 1;
      if (piVar3 == (int *)0x0) {
        iVar7 = 0;
      }
      else {
        iVar7 = *piVar3;
      }
    }
  }
  if ((((*(byte *)((int)param_1 + 0x2c) & 4) == 0) &&
      (_DAT_005d856c <= *(float *)((int)param_1 + 0xf8))) && (*(int *)((int)param_1 + 0x1f0) != 0))
  {
    piVar3 = *(int **)((int)param_1 + 0x18c);
    if (piVar3 == (int *)0x0) {
      iVar7 = 0;
    }
    else {
      iVar7 = *piVar3;
    }
    while (iVar7 != 0) {
      CSpawnerThng__DoSpawn();
      piVar3 = (int *)piVar3[1];
      if (piVar3 == (int *)0x0) {
        iVar7 = 0;
      }
      else {
        iVar7 = *piVar3;
      }
    }
  }
  *(undefined4 *)((int)param_1 + 0xe4) = *(undefined4 *)((int)param_1 + 0xe0);
  *(undefined4 *)((int)param_1 + 0xf0) = *(undefined4 *)((int)param_1 + 0xe8);
  fVar12 = (float10)(**(code **)(*(int *)param_1 + 0x60))();
  fVar1 = (float)fVar12;
  if (((*(int *)((int)param_1 + 0x13c) == 0) || ((*(byte *)((int)param_1 + 0x2c) & 4) != 0)) ||
     (iVar7 = (**(code **)(*(int *)param_1 + 0x1b4))(), iVar7 == 0)) goto LAB_004fb053;
  fVar12 = (float10)*(float *)((int)param_1 + 0xe0);
  piVar3 = *(int **)(*(int *)((int)param_1 + 0x13c) + 0xc);
  if (piVar3 == (int *)0x0) {
    if (DAT_00672fd0 <= *(float *)((int)param_1 + 0x20c)) goto LAB_004fadfa;
    fVar12 = (float10)_DAT_005d856c;
  }
  else {
    (**(code **)(*piVar3 + 0x168))(afStack_70);
    fStack_80 = *(float *)((int)param_1 + 0x4c) * *(float *)((int)param_1 + 0x1f8) +
                *(float *)((int)param_1 + 0x50) * *(float *)((int)param_1 + 0x1fc) +
                *(float *)((int)param_1 + 0x54) * *(float *)((int)param_1 + 0x200) +
                *(float *)((int)param_1 + 0x20);
    fpatan((float10)fStack_74 -
           ((float10)*(float *)((int)param_1 + 0x1f8) * (float10)*(float *)((int)param_1 + 0x3c) +
            (float10)*(float *)((int)param_1 + 0x40) * (float10)*(float *)((int)param_1 + 0x1fc) +
            (float10)*(float *)((int)param_1 + 0x44) * (float10)*(float *)((int)param_1 + 0x200) +
           (float10)*(float *)((int)param_1 + 0x1c)),(float10)afStack_70[0] - (float10)fStack_80);
    fVar12 = (float10)(**(code **)(*(int *)param_1 + 0x170))();
    fVar12 = (float10)fStack_a4 - fVar12;
    *(float *)((int)param_1 + 0x20c) = DAT_00672fd0 + _DAT_005d85cc;
LAB_004fadfa:
    if (fVar12 <= (float10)_DAT_005d85e8) {
      if (fVar12 < (float10)_DAT_005d85dc) {
        fVar12 = fVar12 + (float10)_DAT_005d85e0;
      }
    }
    else {
      fVar12 = fVar12 - (float10)_DAT_005d85e0;
    }
  }
  iVar7 = *(int *)((int)param_1 + 0x164);
  fVar2 = fVar1 * *(float *)(iVar7 + 0xdc);
  if (fVar12 <= (float10)fVar2) {
    if (fVar12 < (float10)-fVar2) {
      fVar12 = (float10)-fVar2;
    }
  }
  else {
    fVar12 = (float10)fVar2;
  }
  fVar13 = (float10)fVar1 * (float10)*(float *)(iVar7 + 0xbc);
  fVar4 = *(float *)((int)param_1 + 0xe0);
  fVar2 = (float)fVar13;
  if ((_DAT_005d85c8 <= fVar4) || (fVar12 <= (float10)_DAT_005d85e4)) {
    fVar14 = fVar12;
    if ((_DAT_005d85e4 < fVar4) && (fVar12 < (float10)_DAT_005d85c8)) {
      fVar14 = fVar12 + (float10)_DAT_005d85e0;
    }
  }
  else {
    fVar14 = fVar12 - (float10)_DAT_005d85e0;
  }
  if (ABS((float10)fVar4 - fVar14) <= fVar13) {
LAB_004faf9f:
    *(float *)((int)param_1 + 0xe0) = (float)fVar12;
  }
  else {
    if (fVar12 <= (float10)*(float *)((int)param_1 + 0xe0)) {
      if ((float10)*(float *)((int)param_1 + 0xe0) - fVar12 <= (float10)_DAT_005d85e8)
      goto LAB_004faf55;
      fVar2 = fVar2 + *(float *)((int)param_1 + 0xe0);
    }
    else if ((float10)_DAT_005d85e8 < fVar12 - (float10)*(float *)((int)param_1 + 0xe0)) {
LAB_004faf55:
      fVar2 = *(float *)((int)param_1 + 0xe0) - fVar2;
    }
    else {
      fVar2 = fVar2 + *(float *)((int)param_1 + 0xe0);
    }
    *(float *)((int)param_1 + 0xe0) = fVar2;
    if (_DAT_005d85e8 < *(float *)((int)param_1 + 0xe0)) {
      fVar12 = (float10)*(float *)((int)param_1 + 0xe0) - (float10)_DAT_005d85e0;
      goto LAB_004faf9f;
    }
    if ((float10)*(float *)((int)param_1 + 0xe0) < (float10)_DAT_005d85dc) {
      fVar12 = (float10)*(float *)((int)param_1 + 0xe0) + (float10)_DAT_005d85e0;
      goto LAB_004faf9f;
    }
  }
  if (*(float *)((int)param_1 + 0xe0) <= *(float *)(iVar7 + 0xdc)) {
    if (*(float *)((int)param_1 + 0xe0) < -*(float *)(iVar7 + 0xdc)) {
      *(float *)((int)param_1 + 0xe0) = -*(float *)(iVar7 + 0xdc);
    }
  }
  else {
    *(undefined4 *)((int)param_1 + 0xe0) = *(undefined4 *)(iVar7 + 0xdc);
  }
  if (*(int *)((int)param_1 + 0x224) != 0) {
    fVar1 = fVar1 * *(float *)(iVar7 + 0xbc);
    if (ABS(*(float *)((int)param_1 + 0xe8) - *(float *)((int)param_1 + 0xec)) <= fVar1) {
      *(undefined4 *)((int)param_1 + 0xe8) = *(undefined4 *)((int)param_1 + 0xec);
    }
    else if (*(float *)((int)param_1 + 0xec) <= *(float *)((int)param_1 + 0xe8)) {
      *(float *)((int)param_1 + 0xe8) = *(float *)((int)param_1 + 0xe8) - fVar1;
    }
    else {
      *(float *)((int)param_1 + 0xe8) = fVar1 + *(float *)((int)param_1 + 0xe8);
    }
  }
LAB_004fb053:
  iVar7 = *(int *)((int)param_1 + 0x244);
  if (iVar7 == 1) {
    iVar7 = *(int *)((int)param_1 + 0x208);
    if ((iVar7 != 0) &&
       (fVar1 = *(float *)((int)param_1 + 0x1c) - *(float *)(iVar7 + 8),
       fVar2 = *(float *)((int)param_1 + 0x20) - *(float *)(iVar7 + 0xc),
       uVar5 = *(undefined4 *)(iVar7 + 0x14), SQRT(fVar1 * fVar1 + fVar2 * fVar2) < _DAT_005d85bc))
    {
      *(undefined4 *)((int)param_1 + 0x244) = 2;
      fStack_7c = *(float *)((int)param_1 + 0x50) * _DAT_005db520;
      (**(code **)(*(int *)param_1 + 0xf4))
                (*(float *)((int)param_1 + 0x40) * _DAT_005db520 + *(float *)((int)param_1 + 0x1c),
                 fStack_7c + *(float *)((int)param_1 + 0x20),*(undefined4 *)((int)param_1 + 0x24),
                 uVar5,0);
    }
  }
  else if (iVar7 == 2) {
    (**(code **)(*(int *)param_1 + 0x1d0))();
  }
  else if (((iVar7 == 4) && (iVar7 = (**(code **)(*(int *)param_1 + 0x144))(), iVar7 == 0)) &&
          (*(int *)((int)param_1 + 0x244) == 4)) {
    iVar7 = *(int *)param_1;
    *(undefined4 *)((int)param_1 + 0x244) = 5;
    pvVar16 = (void *)0x1;
    pcVar15 = s_undeploying_006239d8;
    pvVar8 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))
                               (s_undeploying_006239d8,1,0);
    iVar9 = FindAnimationIndex(pvVar8,(int)pcVar15,pvVar16);
    (**(code **)(iVar7 + 0xf0))(iVar9);
  }
  if (*(int *)(*(int *)((int)param_1 + 0x164) + 0x38) != 0) {
    piVar3 = *(int **)((int)param_1 + 0x18c);
    if (piVar3 == (int *)0x0) {
      iVar7 = 0;
    }
    else {
      iVar7 = *piVar3;
    }
    while (iVar7 != 0) {
      bVar6 = CUnit__Helper_004e4420(iVar7);
      if (CONCAT31(extraout_var,bVar6) != 0) {
        if (*(int *)((int)param_1 + 0x230) == 0) {
          CMonitor__Helper_004e1940
                    (&DAT_00896988,*(void **)(*(int *)((int)param_1 + 0x164) + 0x38),param_1);
        }
        *(undefined4 *)((int)param_1 + 0x230) = 1;
        CUnit__Helper_004f39b0(param_1,(int)unaff_EDI,unaff_ESI);
        return;
      }
      piVar3 = (int *)piVar3[1];
      if (piVar3 == (int *)0x0) {
        iVar7 = 0;
      }
      else {
        iVar7 = *piVar3;
      }
    }
    if (*(int *)((int)param_1 + 0x230) != 0) {
      pvVar8 = (void *)CSoundManager__GetOrCreateSample
                                 (&DAT_00896988,
                                  (char *)(*(int *)(*(int *)((int)param_1 + 0x164) + 0x38) + 0x40),0
                                  ,'\0');
      CSoundManager__KillSample(&DAT_00896988,(int)param_1,pvVar8,(int)unaff_EDI);
    }
    *(undefined4 *)((int)param_1 + 0x230) = 0;
  }
  CUnit__Helper_004f39b0(param_1,(int)unaff_EDI,unaff_ESI);
  return;
}
