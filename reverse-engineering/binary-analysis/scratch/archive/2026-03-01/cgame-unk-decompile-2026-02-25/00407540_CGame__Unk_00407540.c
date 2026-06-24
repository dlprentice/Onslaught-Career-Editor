/* address: 0x00407540 */
/* name: CGame__Unk_00407540 */
/* signature: void __fastcall CGame__Unk_00407540(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CGame__Unk_00407540(void *param_1)

{
  float fVar1;
  float fVar2;
  float fVar3;
  int iVar4;
  undefined4 *puVar5;
  float unaff_EDI;
  undefined4 *puVar6;
  float10 fVar7;
  float fStack_6c;
  float fStack_68;
  float fStack_50;
  float fStack_4c;
  float fStack_48;
  undefined1 auStack_40 [8];
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

  if (g_bDevModeEnabled == 0) {
    DAT_006601f8 = DAT_006601f8 + 1;
    if ((((((DAT_008a9ac4 == 0) && (DAT_008a9ac0 == 3)) &&
          ((*(byte *)((int)param_1 + 0x2c) & 4) == 0)) &&
         ((*(int *)((int)param_1 + 0x580) != 0 && (*(int *)((int)param_1 + 0x260) == 2)))) &&
        (((&DAT_00889304)[(*(int *)(*(int *)((int)param_1 + 0x574) + 0x2c) + -1) * 3] == 0xe ||
         ((&DAT_00889304)[(*(int *)(*(int *)((int)param_1 + 0x574) + 0x2c) + -1) * 3] == 0xd)))) &&
       ((iVar4 = (**(code **)(*(int *)param_1 + 0x10c))(), iVar4 != 0 ||
        (iVar4 = HeightDelta__Below015_D4((int)param_1), iVar4 != 0)))) {
      if (DAT_006601f8 == DAT_00622f0c + 1) {
        iVar4 = PLATFORM__GetWindowWidth();
        *(float *)((int)param_1 + 0x114) =
             *(float *)((int)param_1 + 0x114) -
             g_MouseSensitivity * _DAT_005d8bbc * (float)(DAT_0089bda8 - iVar4 / 2);
        iVar4 = PLATFORM__GetWindowHeight();
        fVar1 = g_MouseSensitivity * _DAT_005d8bbc * (float)(DAT_0089bda4 - iVar4 / 2) *
                _DAT_005d85ec;
        if ((&CAREER_mInvertYFlight_P2)[*(int *)(*(int *)((int)param_1 + 0x574) + 0x2c)] == 0) {
          *(float *)((int)param_1 + 0x118) = *(float *)((int)param_1 + 0x118) - fVar1;
        }
        else {
          *(float *)((int)param_1 + 0x118) = fVar1 + *(float *)((int)param_1 + 0x118);
        }
        fVar7 = (float10)fcos((float10)*(float *)((int)param_1 + 0x4c4));
        CBattleEngine__Unk_004062d0
                  (auStack_30,
                   (void *)(float)(fVar7 * (float10)*(float *)((int)param_1 + 0x4b8) +
                                  (float10)*(float *)((int)param_1 + 0x114)),
                   (float)(fVar7 * (float10)*(float *)((int)param_1 + 0x4bc) +
                          (float10)*(float *)((int)param_1 + 0x118)),
                   (float)(fVar7 * (float10)*(float *)((int)param_1 + 0x4c0) +
                          (float10)*(float *)((int)param_1 + 0x11c)),unaff_EDI);
        fVar1 = *(float *)((int)param_1 + 0x114);
        fVar7 = (float10)fcos((float10)fVar1);
        puVar5 = auStack_30;
        puVar6 = (undefined4 *)((int)param_1 + 0x3c);
        for (iVar4 = 0xc; iVar4 != 0; iVar4 = iVar4 + -1) {
          *puVar6 = *puVar5;
          puVar5 = puVar5 + 1;
          puVar6 = puVar6 + 1;
        }
        puVar5 = auStack_30;
        puVar6 = (undefined4 *)((int)param_1 + 0x9c);
        for (iVar4 = 0xc; iVar4 != 0; iVar4 = iVar4 + -1) {
          *puVar6 = *puVar5;
          puVar5 = puVar5 + 1;
          puVar6 = puVar6 + 1;
        }
        fStack_50 = (float)fVar7;
        fVar7 = (float10)fsin((float10)fVar1);
        fStack_4c = (float)-fVar7;
        puVar5 = (undefined4 *)Vec3__SetXYZ();
        uStack_20 = *puVar5;
        fStack_1c = (float)puVar5[1];
        uStack_18 = puVar5[2];
        uStack_14 = puVar5[3];
        puVar5 = (undefined4 *)Vec3__SetXYZ();
        fVar3 = fStack_1c;
        fVar2 = fStack_4c;
        uStack_10 = *puVar5;
        fVar1 = (float)puVar5[1];
        uStack_8 = puVar5[2];
        uStack_4 = puVar5[3];
        fStack_c = fVar1;
        iVar4 = (**(code **)(*(int *)param_1 + 0x10c))();
        if ((iVar4 == 0) || (iVar4 = HeightDelta__Below015_D4((int)param_1), iVar4 != 0)) {
          fStack_50 = 0.0;
          fStack_6c = 0.0;
          fStack_68 = -1.0;
        }
        else {
          CHeightField__Unk_0047ec60(0x6fadc8,&fStack_50,(void *)((int)param_1 + 0x1c));
          fStack_6c = fStack_4c;
          fStack_68 = fStack_48;
        }
        fStack_4c = fVar1 * fStack_50 - fStack_68 * fVar2;
        fStack_48 = fStack_6c * fVar2 - fVar3 * fStack_50;
        Vec3__SetXYZ();
        SQRT__Wrapper_00406d50(auStack_40);
        fStack_38 = -fStack_38;
        fVar1 = *(float *)((int)param_1 + 0x118) - fStack_38;
        if (fVar1 <= _DAT_005d8bb8) {
          if (fVar1 < _DAT_005d8bb4) {
            *(float *)((int)param_1 + 0x118) = fStack_38 - _DAT_005d8bb0;
          }
        }
        else {
          *(float *)((int)param_1 + 0x118) = fStack_38 + _DAT_005d8bb8;
        }
      }
      iVar4 = PLATFORM__GetWindowWidth();
      DAT_0089bda8 = iVar4 / 2;
      iVar4 = PLATFORM__GetWindowHeight();
      DAT_00622f0c = DAT_006601f8;
      DAT_0089bda4 = iVar4 / 2;
    }
  }
  return;
}
