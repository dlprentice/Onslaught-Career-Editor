/* address: 0x004e8930 */
/* name: CSquadNormal__Unk_004e8930 */
/* signature: void __fastcall CSquadNormal__Unk_004e8930(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CSquadNormal__Unk_004e8930(void *param_1)

{
  float fVar1;
  undefined4 *puVar2;
  int *piVar3;
  float fVar4;
  uint uVar5;
  int iVar6;
  int *piVar7;
  void *pvVar8;
  void *extraout_EAX;
  void *extraout_EAX_00;
  uint uVar9;
  int iVar10;
  uint uVar11;
  int *piVar12;
  void *unaff_EDI;
  int iVar13;
  bool bVar14;
  float10 fVar15;
  float fStack_70;
  float fStack_6c;
  undefined4 uStack_60;
  undefined4 uStack_5c;
  undefined4 uStack_58;
  undefined4 uStack_54;
  undefined1 auStack_50 [32];
  undefined1 auStack_30 [32];
  undefined1 auStack_10 [16];

  CSquadNormal__Unk_004e83b0(param_1,(void *)0x0,(float)unaff_EDI);
  if ((*(float *)((int)param_1 + 0x104) != _DAT_005d856c) && (*(int *)((int)param_1 + 0xbc) != 2)) {
    uVar5 = *(uint *)((int)param_1 + 0xb4);
    iVar10 = 0;
    uVar11 = (int)uVar5 / 2;
    if ((int)uVar11 < 6) {
      uVar11 = 6;
    }
    if ((int)uVar5 < (int)uVar11) {
      uVar11 = uVar5;
    }
    uVar5 = uVar11 & 0x80000001;
    bVar14 = uVar5 == 0;
    if ((int)uVar5 < 0) {
      bVar14 = (uVar5 - 1 | 0xfffffffe) == 0xffffffff;
    }
    fVar1 = _DAT_005d856c;
    if (bVar14) {
      fVar1 = *(float *)((int)param_1 + 0x104);
    }
    piVar12 = *(int **)((int)param_1 + 0xa4);
    if (piVar12 == (int *)0x0) {
      iVar13 = 0;
    }
    else {
      iVar13 = *piVar12;
    }
    while (iVar13 != 0) {
      iVar6 = iVar10 / (int)uVar11;
      uVar5 = iVar10 - iVar6 * uVar11;
      uVar9 = uVar5 & 0x80000001;
      if ((int)uVar9 < 0) {
        uVar9 = (uVar9 - 1 | 0xfffffffe) + 1;
      }
      if (uVar9 == 1) {
        fVar4 = (float)(int)(-1 - uVar5) * *(float *)((int)param_1 + 0x104);
      }
      else {
        fVar4 = (float)(int)uVar5 * *(float *)((int)param_1 + 0x104);
      }
      iVar10 = iVar10 + 1;
      *(float *)(iVar13 + 4) = fVar4 + fVar1;
      *(float *)(iVar13 + 8) = (float)iVar6 * *(float *)((int)param_1 + 0x104) * _DAT_005d95c0;
      piVar12 = (int *)piVar12[1];
      if (piVar12 == (int *)0x0) {
        iVar13 = 0;
      }
      else {
        iVar13 = *piVar12;
      }
    }
    *(undefined4 *)((int)param_1 + 0xbc) = 2;
  }
  iVar10 = CSquadNormal__Unk_004e84e0((int)param_1);
  while (iVar10 == 0) {
    iVar10 = CSquadNormal__Unk_004e84e0((int)param_1);
  }
  puVar2 = *(undefined4 **)((int)param_1 + 0xa4);
  if (puVar2 == (undefined4 *)0x0) {
    piVar12 = (int *)0x0;
  }
  else {
    piVar12 = (int *)*puVar2;
  }
  do {
    if (piVar12 == (int *)0x0) {
      return;
    }
    iVar10 = *piVar12;
    if (iVar10 != 0) {
      piVar3 = *(int **)((int)param_1 + 0xc4);
      piVar7 = (int *)0x0;
      if (piVar3 != (int *)0x0) {
        if ((piVar3[0xd] & 0x20000000U) == 0) {
          if ((piVar3[0xd] & 0x10U) != 0) {
            piVar7 = piVar3;
          }
        }
        else {
          piVar7 = (int *)(**(code **)(*piVar3 + 300))
                                    (*(undefined4 *)(iVar10 + 0x1c),*(undefined4 *)(iVar10 + 0x20),
                                     *(undefined4 *)(iVar10 + 0x24),*(undefined4 *)(iVar10 + 0x28));
        }
      }
      if (*piVar12 == 0) {
LAB_004e8b73:
        if (*(int *)((int)param_1 + 0x110) == 0) {
          if (*piVar12 != 0) {
            if (piVar7 != (int *)0x0) {
              CUnitAI__Helper_004fcec0();
            }
            if (*(void **)(*piVar12 + 0x13c) != (void *)0x0) {
              CSquadNormal__Helper_004ffdd0
                        (*(void **)(*piVar12 + 0x13c),(int)piVar7,(void *)0x0,(int)unaff_EDI);
            }
          }
          goto LAB_004e8caa;
        }
      }
      else {
        iVar10 = piVar12[4];
        pvVar8 = (void *)Vec3__SetXYZ();
        CSquadNormal__Helper_0040d2c0((void *)(piVar12[4] + 0x3c),auStack_30,pvVar8,unaff_EDI);
        Vec3__Add((void *)(iVar10 + 0x1c),auStack_50,extraout_EAX,unaff_EDI);
        CMeshCollisionVolume__Helper_0040d120
                  ((void *)(*piVar12 + 0x1c),&fStack_70,auStack_50,unaff_EDI);
        (**(code **)(*(int *)piVar12[4] + 0x138))();
        fVar1 = fStack_6c * fStack_6c;
        fVar4 = fStack_70 * fStack_70;
        fVar15 = (float10)(**(code **)(*(int *)piVar12[4] + 0x138))();
        if (SQRT((float10)(fVar4 + fVar1)) <= fVar15 * (float10)_DAT_005df260) goto LAB_004e8b73;
      }
      if ((*piVar12 == 0) || (iVar10 = CSquadNormal__Helper_004fd570(*piVar12), iVar10 == 0)) {
        if ((*piVar12 != 0) && (pvVar8 = *(void **)(*piVar12 + 0x13c), pvVar8 != (void *)0x0)) {
          piVar7 = (int *)0x0;
LAB_004e8c36:
          CSquadNormal__Helper_004ffdd0(pvVar8,(int)piVar7,(void *)0x0,(int)unaff_EDI);
        }
      }
      else if (*piVar12 != 0) {
        if (piVar7 != (int *)0x0) {
          CUnitAI__Helper_004fcec0();
        }
        pvVar8 = *(void **)(*piVar12 + 0x13c);
        if (pvVar8 != (void *)0x0) goto LAB_004e8c36;
      }
      if (*piVar12 != 0) {
        iVar10 = piVar12[4];
        pvVar8 = (void *)Vec3__SetXYZ();
        CSquadNormal__Helper_0040d2c0((void *)(piVar12[4] + 0x3c),auStack_10,pvVar8,unaff_EDI);
        Vec3__Add((void *)(iVar10 + 0x1c),&uStack_60,extraout_EAX_00,unaff_EDI);
        (**(code **)(*(int *)*piVar12 + 0xf4))(uStack_60,uStack_5c,uStack_58,uStack_54,0);
      }
    }
LAB_004e8caa:
    puVar2 = (undefined4 *)puVar2[1];
    if (puVar2 == (undefined4 *)0x0) {
      piVar12 = (int *)0x0;
    }
    else {
      piVar12 = (int *)*puVar2;
    }
  } while( true );
}
