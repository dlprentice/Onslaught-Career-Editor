/* address: 0x00407a50 */
/* name: CMonitor__UpdateCameraVectorsAndInput */
/* signature: void __fastcall CMonitor__UpdateCameraVectorsAndInput(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CMonitor__UpdateCameraVectorsAndInput(void *param_1)

{
  float *pfVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  int iVar6;
  undefined4 *puVar7;
  float unaff_EDI;
  undefined4 *puVar8;
  float10 fVar9;
  float fStack_60;
  float fStack_5c;
  float fStack_40;
  float fStack_3c;
  float fStack_38;
  undefined4 auStack_30 [4];
  undefined4 uStack_20;
  float fStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;
  undefined4 uStack_10;
  float fStack_c;
  undefined4 uStack_8;
  undefined4 uStack_4;

  pfVar1 = (float *)((int)param_1 + 0x114);
  *(float *)((int)param_1 + 0x590) = *pfVar1;
  *(undefined4 *)((int)param_1 + 0x594) = *(undefined4 *)((int)param_1 + 0x118);
  *(undefined4 *)((int)param_1 + 0x598) = *(undefined4 *)((int)param_1 + 0x11c);
  if ((*(int *)((int)param_1 + 0x260) == 2) &&
     ((iVar6 = (**(code **)(*(int *)param_1 + 0x10c))(), iVar6 != 0 ||
      (iVar6 = HeightDelta__Below015_D4((int)param_1), iVar6 != 0)))) {
    fVar9 = (float10)fcos((float10)*pfVar1);
    fStack_40 = (float)fVar9;
    fVar9 = (float10)fsin((float10)*pfVar1);
    fStack_3c = (float)-fVar9;
    puVar7 = (undefined4 *)Vec3__SetXYZ();
    uStack_20 = *puVar7;
    fStack_1c = (float)puVar7[1];
    uStack_18 = puVar7[2];
    uStack_14 = puVar7[3];
    puVar7 = (undefined4 *)Vec3__SetXYZ();
    fVar5 = fStack_1c;
    fVar4 = fStack_3c;
    uStack_10 = *puVar7;
    fVar2 = (float)puVar7[1];
    uStack_8 = puVar7[2];
    uStack_4 = puVar7[3];
    fStack_c = fVar2;
    iVar6 = (**(code **)(*(int *)param_1 + 0x10c))();
    if ((iVar6 == 0) || (iVar6 = HeightDelta__Below015_D4((int)param_1), iVar6 != 0)) {
      fStack_38 = -1.0;
      fStack_60 = 0.0;
      fStack_5c = 0.0;
    }
    else {
      CMonitor__Helper_0047ec60(0x6fadc8,&fStack_40,(void *)((int)param_1 + 0x1c));
      fStack_60 = fStack_40;
      fStack_5c = fStack_3c;
    }
    fVar3 = fStack_38 * fVar5 - fStack_5c * fVar2;
    fVar2 = fVar2 * fStack_60 - fStack_38 * fVar4;
    fVar4 = fStack_5c * fVar4 - fVar5 * fStack_60;
    fStack_40 = fVar2 * fStack_38 - fVar4 * fStack_5c;
    fStack_3c = fVar4 * fStack_60 - fStack_38 * fVar3;
    fVar2 = fStack_5c * fVar3 - fVar2 * fStack_60;
    fVar4 = SQRT(fStack_3c * fStack_3c + fVar2 * fVar2 + fStack_40 * fStack_40);
    if (fVar4 != _DAT_005d856c) {
      fVar2 = (_DAT_005d8568 / fVar4) * fVar2;
    }
    if (((((DAT_008a9ac4 != 0) || (DAT_008a9ac0 != 3)) ||
         (((*(byte *)((int)param_1 + 0x2c) & 4) != 0 ||
          ((*(int *)((int)param_1 + 0x580) == 0 || (*(int *)((int)param_1 + 0x260) != 2)))))) ||
        (((&DAT_00889304)[(*(int *)(*(int *)((int)param_1 + 0x574) + 0x2c) + -1) * 3] != 0xe &&
         ((&DAT_00889304)[(*(int *)(*(int *)((int)param_1 + 0x574) + 0x2c) + -1) * 3] != 0xd)))) ||
       ((iVar6 = (**(code **)(*(int *)param_1 + 0x10c))(), iVar6 == 0 &&
        (iVar6 = HeightDelta__Below015_D4((int)param_1), iVar6 == 0)))) {
      fVar2 = *(float *)((int)param_1 + 0x118) - -fVar2;
      if (fVar2 <= _DAT_005d85ec) {
        if (fVar2 < _DAT_005d8be4) {
          if (fVar2 < _DAT_005d8be0) {
            fVar2 = *(float *)((int)param_1 + 0x280) - (fVar2 + _DAT_005d8568) * _DAT_005d87c0;
            goto LAB_00407e91;
          }
          if (*(float *)((int)param_1 + 0x280) < _DAT_005d856c) {
            fVar4 = ABS((fVar2 + _DAT_005d85f8) * _DAT_005d8be8);
            goto LAB_00407da1;
          }
        }
      }
      else if (_DAT_005d8bec < fVar2) {
        fVar2 = *(float *)((int)param_1 + 0x280) - (fVar2 - _DAT_005d8bec) * _DAT_005d87c0;
LAB_00407e91:
        *(float *)((int)param_1 + 0x280) = fVar2;
      }
      else if (_DAT_005d856c < *(float *)((int)param_1 + 0x280)) {
        fVar4 = (fVar2 - _DAT_005d85ec) * _DAT_005d8be8;
LAB_00407da1:
        fVar2 = _DAT_005d8568 - fVar4;
        if (_DAT_005d8568 - fVar4 < _DAT_005d856c) goto LAB_00407e83;
        goto LAB_00407e8b;
      }
    }
  }
  else {
    if ((_DAT_005d8bdc < *(float *)((int)param_1 + 0x118)) &&
       ((_DAT_005d856c < *(float *)((int)param_1 + 0x280) &&
        (*(int *)(*(int *)((int)param_1 + 0x57c) + 0x2c) == 0)))) {
      fVar2 = _DAT_005d8568 - (*(float *)((int)param_1 + 0x118) - _DAT_005d8bdc) * _DAT_005d8bd8;
      if (fVar2 < _DAT_005d856c) {
        fVar2 = _DAT_005d856c;
      }
      *(float *)((int)param_1 + 0x280) = fVar2 * *(float *)((int)param_1 + 0x280);
    }
    if (((*(float *)((int)param_1 + 0x118) < _DAT_005d8bd4) &&
        (*(float *)((int)param_1 + 0x280) < _DAT_005d856c)) &&
       (*(int *)(*(int *)((int)param_1 + 0x57c) + 0x2c) == 0)) {
      fVar2 = _DAT_005d8568 -
              ABS((*(float *)((int)param_1 + 0x118) + _DAT_005d8bdc) * _DAT_005d8bd8);
      if (fVar2 < (float)_DAT_005d87b0) {
LAB_00407e83:
        fVar2 = _DAT_005d856c;
      }
LAB_00407e8b:
      fVar2 = fVar2 * *(float *)((int)param_1 + 0x280);
      goto LAB_00407e91;
    }
  }
  *pfVar1 = *(float *)((int)param_1 + 0x278) + *pfVar1;
  *(float *)((int)param_1 + 0x118) =
       *(float *)((int)param_1 + 0x280) + *(float *)((int)param_1 + 0x118);
  *(float *)((int)param_1 + 0x11c) =
       *(float *)((int)param_1 + 0x11c) + *(float *)((int)param_1 + 0x27c);
  CGame__UpdateMouseLookAngles(param_1);
  if (_DAT_005d85e8 < *pfVar1) {
    *pfVar1 = *pfVar1 - _DAT_005d85e0;
  }
  if (*pfVar1 < _DAT_005d85dc) {
    *pfVar1 = *pfVar1 + _DAT_005d85e0;
  }
  if (_DAT_005d85e8 < *(float *)((int)param_1 + 0x118)) {
    *(float *)((int)param_1 + 0x118) = *(float *)((int)param_1 + 0x118) - _DAT_005d85e0;
  }
  if (*(float *)((int)param_1 + 0x118) < _DAT_005d85dc) {
    *(float *)((int)param_1 + 0x118) = *(float *)((int)param_1 + 0x118) + _DAT_005d85e0;
  }
  if (_DAT_005d85e8 < *(float *)((int)param_1 + 0x11c)) {
    *(float *)((int)param_1 + 0x11c) = *(float *)((int)param_1 + 0x11c) - _DAT_005d85e0;
  }
  if (*(float *)((int)param_1 + 0x11c) < _DAT_005d85dc) {
    *(float *)((int)param_1 + 0x11c) = *(float *)((int)param_1 + 0x11c) + _DAT_005d85e0;
  }
  *(float *)((int)param_1 + 0x278) = *(float *)((int)param_1 + 0x278) * _DAT_005d85f8;
  *(float *)((int)param_1 + 0x280) = *(float *)((int)param_1 + 0x280) * _DAT_005d85f8;
  *(float *)((int)param_1 + 0x27c) = *(float *)((int)param_1 + 0x27c) * _DAT_005d85f8;
  if (*(int *)((int)param_1 + 0x260) == 3) {
    iVar6 = CMonitor__Unk_00412900(*(int *)((int)param_1 + 0x57c));
    if (iVar6 == 0) goto LAB_00408000;
    fVar2 = *(float *)((int)param_1 + 0x11c) * _DAT_005d8bd0;
  }
  else {
    fVar2 = *(float *)((int)param_1 + 0x11c) * _DAT_005d85f8;
  }
  *(float *)((int)param_1 + 0x11c) = fVar2;
LAB_00408000:
  fVar9 = (float10)fcos((float10)*(float *)((int)param_1 + 0x4c4));
  CSquadNormal__Helper_004062d0
            (auStack_30,
             (void *)(float)(fVar9 * (float10)*(float *)((int)param_1 + 0x4b8) + (float10)*pfVar1),
             (float)(fVar9 * (float10)*(float *)((int)param_1 + 0x4bc) +
                    (float10)*(float *)((int)param_1 + 0x118)),
             (float)(fVar9 * (float10)*(float *)((int)param_1 + 0x4c0) +
                    (float10)*(float *)((int)param_1 + 0x11c)),unaff_EDI);
  fVar4 = _DAT_005d8580;
  fVar2 = *(float *)((int)param_1 + 0x4b8);
  puVar7 = auStack_30;
  puVar8 = (undefined4 *)((int)param_1 + 0x3c);
  for (iVar6 = 0xc; iVar6 != 0; iVar6 = iVar6 + -1) {
    *puVar8 = *puVar7;
    puVar7 = puVar7 + 1;
    puVar8 = puVar8 + 1;
  }
  if (((fVar4 < ABS(fVar2)) || (_DAT_005d8580 < ABS(*(float *)((int)param_1 + 0x4bc)))) ||
     (_DAT_005d8580 < ABS(*(float *)((int)param_1 + 0x4c0)))) {
    *(float *)((int)param_1 + 0x4b8) = *(float *)((int)param_1 + 0x4b8) * _DAT_005d85f8;
    *(float *)((int)param_1 + 0x4bc) = *(float *)((int)param_1 + 0x4bc) * _DAT_005d85f8;
    *(float *)((int)param_1 + 0x4c0) = *(float *)((int)param_1 + 0x4c0) * _DAT_005d85f8;
    *(float *)((int)param_1 + 0x4c4) = *(float *)((int)param_1 + 0x4c4) + _DAT_005d85f8;
  }
  return;
}
