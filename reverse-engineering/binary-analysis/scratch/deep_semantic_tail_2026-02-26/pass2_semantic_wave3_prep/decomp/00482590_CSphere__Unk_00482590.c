/* address: 0x00482590 */
/* name: CSphere__Unk_00482590 */
/* signature: void __fastcall CSphere__Unk_00482590(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CSphere__Unk_00482590(int param_1)

{
  bool bVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  char *a;
  int iVar5;
  uint uVar6;
  int *piVar7;
  float *pfVar8;
  undefined4 *puVar9;
  float *pfVar10;
  undefined4 *puVar11;
  float10 fVar12;
  float10 fVar13;
  float10 fVar14;
  double dVar15;
  float fVar16;
  float fVar17;
  void *pvVar18;
  float fVar19;
  float fVar20;
  float fVar21;
  float fVar22;
  float fVar23;
  float fVar24;
  float fVar25;
  float fVar26;
  char *b;
  float fVar27;
  float fStack_1e8;
  float fStack_1e0;
  float fStack_1dc;
  int iStack_1d4;
  int *local_1c8;
  float fStack_1c4;
  int *local_1bc;
  int iStack_14c;
  int iStack_148;
  int iStack_144;
  int iStack_140;
  undefined4 uStack_13c;
  undefined4 uStack_138;
  undefined4 auStack_134 [5];
  float fStack_120;
  float fStack_11c;
  float fStack_118;
  undefined4 uStack_110;
  undefined4 uStack_10c;
  undefined4 uStack_108;
  undefined4 uStack_104;
  undefined4 uStack_100;
  undefined4 uStack_fc;
  undefined4 uStack_f8;
  undefined4 uStack_f4;
  undefined4 uStack_f0;
  undefined4 uStack_ec;
  undefined4 uStack_e8;
  undefined4 uStack_e4;
  undefined4 uStack_e0;
  float fStack_d8;
  float fStack_d4;
  float fStack_d0;
  float fStack_c8;
  float fStack_c4;
  float fStack_c0;
  float afStack_b8 [4];
  float fStack_a8;
  float fStack_a4;
  float fStack_a0;
  float fStack_98;
  float fStack_94;
  float fStack_90;
  undefined4 auStack_88 [6];
  float afStack_70 [12];
  undefined4 auStack_40 [16];

  iVar2 = *(int *)(param_1 + 0x50);
  piVar7 = *(int **)(iVar2 + 0x4e0);
  if ((((piVar7 == (int *)0x0) || ((*(byte *)(piVar7 + 0xd) & 0x10) == 0)) &&
      (piVar7 = *(int **)(iVar2 + 0x4c8), piVar7 != (int *)0x0)) &&
     ((*(byte *)(piVar7 + 0xd) & 0x10) == 0)) {
    piVar7 = (int *)0x0;
  }
  uVar6 = (uint)(*(int *)(*(int *)(iVar2 + 0x574) + 0x2c) != 1);
  if (piVar7 == (int *)0x0) {
    fVar16 = PLATFORM__GetSysTimeFloat();
    if (_DAT_005d8ba0 < fVar16 - *(float *)(param_1 + 0xa4 + uVar6 * 4)) {
      CGenericActiveReader__SetReader((void *)(param_1 + 0x9c + uVar6 * 4),(void *)0x0);
    }
    piVar7 = *(int **)(param_1 + 0x9c + uVar6 * 4);
  }
  else {
    CGenericActiveReader__SetReader((void *)(param_1 + 0x9c + uVar6 * 4),piVar7);
    fVar16 = PLATFORM__GetSysTimeFloat();
    *(float *)(param_1 + 0xa4 + uVar6 * 4) = fVar16;
  }
  if (piVar7 == (int *)0x0) {
    return;
  }
  local_1c8 = (int *)0x0;
  local_1bc = piVar7;
  if ((piVar7[0xd] & 0x80000U) != 0) {
    local_1bc = (int *)piVar7[0x9b];
    local_1c8 = piVar7;
  }
  if (local_1bc == (int *)0x0) {
    return;
  }
  piVar7 = (int *)local_1bc[0xc];
  if (piVar7 == (int *)0x0) {
    return;
  }
  iVar2 = (**(code **)(*piVar7 + 0x24))();
  if (iVar2 == 0) {
    return;
  }
  fStack_1c4 = 7.105427e-15;
  if (uVar6 == 0) {
    fVar16 = _DAT_0067a62c + _DAT_005dbe48;
  }
  else {
    iVar2 = PLATFORM__GetWindowHeight();
    fVar16 = (float)iVar2 * _DAT_005d85ec + _DAT_0067a62c + _DAT_005d8610;
  }
  if ((local_1bc[0x59] == 0) || (uVar3 = *(uint *)(local_1bc[0x59] + 0x1a8), uVar3 == 0xffffffff)) {
    if (local_1bc[0x4e] == 0) {
      uVar3 = 1;
    }
    else {
      uVar3 = -(uint)(local_1bc[0x4e] != 1) & 2;
    }
LAB_0048271e:
                    /* WARNING: Could not recover jumptable at 0x0048271e. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (**(code **)(&DAT_00483508 + uVar3 * 4))();
    return;
  }
  if (uVar3 < 4) goto LAB_0048271e;
  RenderState_Set(0x17,8);
  RenderState_Set(7,1);
  RenderState_Set(0xe,1);
  CVBufTexture__DrawSpriteEx
            (_DAT_0067a628 + _DAT_005dbe48,fVar16,1.0,*(void **)(param_1 + 0x168),4,0,1.0,0.0,
             (float)local_1c8,1.0,1.0,0.0,1.0,0.0,1.0);
  RenderState_Set(0xe,1);
  RenderState_Set(7,1);
  RenderState_Set(0x17,4);
  iVar2 = piVar7[6];
  iVar4 = (**(code **)(*piVar7 + 0x24))();
  b = s_m_thunderhead_msh_0062d304;
  a = CDestructableSegmentsController__Helper_004aa6b0(iVar4);
  iVar5 = stricmp(a,b);
  if (iVar5 == 0) {
    if (((iVar2 == 0) || (iVar2 = *(int *)(iVar2 + 0x3c), iVar2 == 0)) ||
       ((float *)(iVar2 + 0x18) == (float *)0x0)) goto LAB_00482fee;
    fVar16 = *(float *)(iVar2 + 0x1c);
    fVar17 = *(float *)(iVar2 + 0x18);
    fVar19 = *(float *)(iVar2 + 0x24);
    fStack_1dc = fVar16 - fVar17;
    fVar20 = *(float *)(iVar2 + 0x20);
    fStack_1e0 = fVar19 - fVar20;
    if (*(float *)(iVar2 + 0x28) <= *(float *)(iVar2 + 0x2c)) {
      fStack_1dc = (*(float *)(iVar2 + 0x28) / *(float *)(iVar2 + 0x2c)) * fStack_1dc;
    }
    else {
      fStack_1e0 = (*(float *)(iVar2 + 0x2c) / *(float *)(iVar2 + 0x28)) * fStack_1e0;
    }
    fVar24 = 1.9999999;
    fVar23 = 0.0;
    fVar22 = 1.0;
    iVar4 = 0;
    iVar2 = 4;
    fStack_1c4 = 1.9999999;
    fVar21 = 0.011;
    if (uVar6 != 0) {
      pvVar18 = DAT_008aa8b8;
      iVar5 = PLATFORM__GetWindowHeight();
      CVBufTexture__DrawSpriteEx
                (_DAT_0067a628 + _DAT_005dbe48,
                 (float)iVar5 * _DAT_005d85ec + _DAT_0067a62c + _DAT_005d8610,fVar21,pvVar18,iVar2,
                 iVar4,fVar22,fVar23,fVar24,fStack_1dc,fStack_1e0,fVar17,fVar16,fVar20,fVar19);
      goto LAB_00482fee;
    }
    CVBufTexture__DrawSpriteEx
              (_DAT_0067a628 + _DAT_005dbe48,_DAT_0067a62c + _DAT_005dbe48,0.011,DAT_008aa8b8,4,0,
               1.0,0.0,1.9999999,fStack_1dc,fStack_1e0,fVar17,fVar16,fVar20,fVar19);
  }
  else {
    iVar2 = 0;
    do {
      (&DAT_009c68a0)[iVar2] = 0;
      (&DAT_009c6904)[iVar2] = 1;
      iVar2 = iVar2 + 1;
    } while (iVar2 < 8);
    fVar16 = SQRT((float)_DAT_005dbe40);
    DAT_009c68a8 = 0xff606060;
    DAT_009c690c = 1;
    uStack_104 = 0;
    auStack_134[1] = 0;
    auStack_134[2] = 0;
    auStack_134[3] = 0;
    uStack_100 = 0;
    uStack_fc = 0;
    uStack_f8 = 0;
    uStack_f4 = 0;
    uStack_f0 = 0;
    uStack_ec = 0;
    uStack_e8 = 0;
    uStack_e4 = 0;
    uStack_e0 = 0;
    auStack_134[0] = 0;
    fStack_120 = 1.0;
    fStack_11c = 1.0;
    fStack_118 = -1.0;
    if (fVar16 != _DAT_005d856c) {
      fStack_120 = _DAT_005d8568 / fVar16;
      fStack_11c = fStack_120;
      fStack_118 = fStack_120 * _DAT_005d8be0;
    }
    bVar1 = fVar16 != _DAT_005d856c;
    uStack_110 = 0x3e20a0a1;
    uStack_10c = 0x3e20a0a1;
    uStack_108 = 0x3e20a0a1;
    puVar9 = auStack_134;
    puVar11 = &DAT_009c65c0;
    for (iVar2 = 0x17; iVar2 != 0; iVar2 = iVar2 + -1) {
      *puVar11 = *puVar9;
      puVar9 = puVar9 + 1;
      puVar11 = puVar11 + 1;
    }
    DAT_009c68fc = 1;
    DAT_009c68a0 = 1;
    DAT_009c6904 = 1;
    auStack_134[0] = 0;
    fStack_120 = -1.0;
    fStack_11c = -1.0;
    fStack_118 = 1.0;
    if (bVar1) {
      fStack_120 = (_DAT_005d8568 / fVar16) * _DAT_005d8be0;
      fStack_11c = fStack_120;
      fStack_118 = _DAT_005d8568 / fVar16;
    }
    uStack_110 = 0;
    uStack_10c = 0;
    uStack_108 = 0;
    puVar9 = auStack_134;
    puVar11 = &DAT_009c661c;
    for (iVar2 = 0x17; iVar2 != 0; iVar2 = iVar2 + -1) {
      *puVar11 = *puVar9;
      puVar9 = puVar9 + 1;
      puVar11 = puVar11 + 1;
    }
    DAT_009c68fd = 1;
    DAT_009c68a1 = 1;
    DAT_009c6905 = 1;
    DAT_009c68ad = 1;
    DAT_009c6910 = 1;
    iVar2 = *(int *)(param_1 + 0x168);
    puVar9 = &DAT_0089ce14;
    puVar11 = auStack_88;
    for (iVar5 = 6; iVar5 != 0; iVar5 = iVar5 + -1) {
      *puVar11 = *puVar9;
      puVar9 = puVar9 + 1;
      puVar11 = puVar11 + 1;
    }
    iStack_14c = *(int *)(iVar2 + 0xac);
    iStack_148 = (int)*(short *)(iVar2 + 0xb0);
    fStack_120 = fStack_11c;
    if (uVar6 == 0) {
      iStack_1d4 = (int)(longlong)ROUND(_DAT_0067a628 + _DAT_005dbe48);
      iStack_144 = iStack_1d4;
      iStack_1d4 = (int)(longlong)ROUND(_DAT_0067a62c + _DAT_005dbe48);
    }
    else {
      iStack_1d4 = (int)(longlong)ROUND(_DAT_0067a628 + _DAT_005dbe48);
      iStack_144 = iStack_1d4;
      iVar2 = PLATFORM__GetWindowHeight();
      iStack_1d4 = (int)(longlong)
                        ROUND((float)iVar2 * _DAT_005d85ec + _DAT_0067a62c + _DAT_005d8610);
    }
    uStack_13c = 0;
    iStack_144 = iStack_144 - iStack_14c / 2;
    iStack_140 = iStack_1d4 - iStack_148 / 2;
    uStack_138 = 0x3f800000;
    D3DDevice__SetViewport(&iStack_14c);
    puVar9 = &DAT_009c6994;
    puVar11 = auStack_134;
    for (iVar2 = 0x10; iVar2 != 0; iVar2 = iVar2 + -1) {
      *puVar11 = *puVar9;
      puVar9 = puVar9 + 1;
      puVar11 = puVar11 + 1;
    }
    CDXEngine__SetProjectionMatrix(&DAT_009c65c0,0.2,100.0,0.2,0.2);
    fStack_c0 = *(float *)(*(int *)(iVar4 + 0x150) + 0x24);
    if (fStack_c0 < _DAT_005d85ec) {
      fStack_c0 = _DAT_005d85ec;
    }
    fStack_c4 = fStack_c0 * _DAT_005dbe3c;
    fStack_c8 = 0.0;
    puVar9 = &DAT_009c6954;
    puVar11 = auStack_40;
    for (iVar2 = 0x10; iVar2 != 0; iVar2 = iVar2 + -1) {
      *puVar11 = *puVar9;
      puVar9 = puVar9 + 1;
      puVar11 = puVar11 + 1;
    }
    fStack_c0 = fStack_c0 * _DAT_005dbe38;
    fVar12 = (float10)fcos((float10)_DAT_005db280);
    fVar13 = (float10)fsin((float10)_DAT_005db280);
    fVar16 = (float)fVar13;
    fVar13 = (float10)fcos((float10)_DAT_005d87b0);
    fVar17 = (float)fVar13;
    fVar19 = (float)fVar13;
    fVar14 = (float10)fsin((float10)_DAT_005d87b0);
    fVar20 = (float)fVar14;
    fVar21 = (float)fVar14;
    fVar14 = (float10)fcos((float10)_DAT_005db568);
    fVar22 = (float)fVar14;
    fVar14 = (float10)fsin((float10)_DAT_005db568);
    fVar23 = (float)fVar14 * (float)fVar13;
    fStack_d8 = (float)((float10)-(fVar22 * fVar21) * (float10)fVar16 +
                       (float10)(fVar20 * fVar19 + fVar23 * fVar21) * fVar12);
    fStack_d4 = (float)((float10)(fVar20 * fVar21 - fVar23 * fVar19) * fVar12 +
                       (float10)(fVar22 * fVar19) * (float10)fVar16);
    fStack_d0 = (float)((float10)fVar16 * (float10)(float)fVar14 +
                       (float10)(fVar22 * (float)fVar13) * fVar12);
    Mat34__SetRows();
    CDXEngine__SetViewAndProjection(&DAT_009c65c0,afStack_70,&fStack_c8);
    pfVar8 = (float *)&DAT_0067a5e8;
    pfVar10 = afStack_b8;
    for (iVar2 = 0xc; iVar2 != 0; iVar2 = iVar2 + -1) {
      *pfVar10 = *pfVar8;
      pfVar8 = pfVar8 + 1;
      pfVar10 = pfVar10 + 1;
    }
    dVar15 = CDXMeshVB__Helper_0044a0c0();
    fVar12 = (float10)fcos((float10)dVar15 * (float10)_DAT_005d8c1c);
    fVar16 = (float)fVar12;
    fVar12 = (float10)fsin((float10)dVar15 * (float10)_DAT_005d8c1c);
    fVar13 = (float10)fVar20 * (float10)fVar20;
    afStack_b8[0] = (float)((float10)fVar17 * (float10)fVar16 - fVar13 * fVar12);
    afStack_b8[1] = (float)-((float10)fVar17 * fVar12);
    fVar19 = (float)((float10)fVar20 * (float10)fVar17);
    afStack_b8[2] = (float)((float10)fVar19 * fVar12 + (float10)fVar20 * (float10)fVar16);
    fStack_a8 = (float)(fVar13 * (float10)fVar16 + (float10)fVar17 * fVar12);
    fStack_a4 = fVar17 * fVar16;
    fStack_a0 = (float)((float10)fVar20 * fVar12 - (float10)fVar19 * (float10)fVar16);
    fStack_98 = -(fVar17 * fVar20);
    fStack_90 = fVar17 * fVar17;
    fStack_94 = fVar20;
    RenderState_Set(0x1b,1);
    DAT_00630130 = 0;
    DAT_00704e48 = 0;
    CSphere__Helper_004b6260();
    puVar9 = auStack_40;
    puVar11 = &DAT_009c6954;
    for (iVar2 = 0x10; iVar2 != 0; iVar2 = iVar2 + -1) {
      *puVar11 = *puVar9;
      puVar9 = puVar9 + 1;
      puVar11 = puVar11 + 1;
    }
    DAT_00630130 = 100;
    DAT_009c73e9 = 1;
    D3DDevice__SetViewport(auStack_88);
    puVar9 = auStack_134;
    puVar11 = &DAT_009c6994;
    for (iVar2 = 0x10; iVar2 != 0; iVar2 = iVar2 + -1) {
      *puVar11 = *puVar9;
      puVar9 = puVar9 + 1;
      puVar11 = puVar11 + 1;
    }
    DAT_009c73ea = 1;
    DAT_009c68ad = 0;
    DAT_009c6910 = 1;
    DAT_009c68ac = 0;
    DAT_009c690d = 1;
    RenderState_Set(7,1);
LAB_00482fee:
    if (uVar6 != 0) {
      fVar27 = 1.0;
      fVar26 = 0.0;
      pvVar18 = *(void **)(param_1 + 0x168);
      fVar25 = 1.0;
      fVar24 = 0.0;
      fVar23 = 0.07;
      fVar22 = 0.9;
      fVar21 = -1.7014118e+38;
      fVar20 = 0.0;
      fVar19 = 1.0;
      iVar4 = 0;
      iVar2 = 4;
      fVar17 = 0.011;
      iVar5 = PLATFORM__GetWindowHeight();
      fVar16 = (float)iVar5 * _DAT_005d85ec + _DAT_0067a62c + _DAT_005d8610;
      goto LAB_004831bf;
    }
  }
  fVar27 = 1.0;
  fVar26 = 0.0;
  pvVar18 = *(void **)(param_1 + 0x168);
  fVar25 = 1.0;
  fVar24 = 0.0;
  fVar23 = 0.07;
  fVar16 = _DAT_0067a62c + _DAT_005dbe48;
  fVar22 = 0.9;
  fVar21 = -1.7014118e+38;
  fVar20 = 0.0;
  fVar19 = 1.0;
  iVar4 = 0;
  iVar2 = 4;
  fVar17 = 0.011;
LAB_004831bf:
  CVBufTexture__DrawSpriteEx
            (_DAT_0067a628 + _DAT_005dbe48,fVar16 + _DAT_005dbe34,fVar17,pvVar18,iVar2,iVar4,fVar19,
             fVar20,fVar21,fVar22,fVar23,fVar24,fVar25,fVar26,fVar27);
  fVar12 = (float10)(**(code **)(*local_1bc + 0x138))();
  if ((float10)_DAT_005d8570 < fVar12) {
    dVar15 = CSphere__Helper_004f9a40((int)local_1bc);
    fVar12 = (float10)(**(code **)(*local_1bc + 0x138))();
    fStack_1e8 = (float)((float10)(float)dVar15 / fVar12);
    if ((float10)_DAT_005d856c <= (float10)(float)dVar15 / fVar12) {
      if (_DAT_005d8568 < fStack_1e8) {
        fStack_1e8 = 1.0;
      }
    }
    else {
      fStack_1e8 = 0.0;
    }
    switch(uVar3) {
    case 0:
      fStack_1c4 = -NAN;
      break;
    case 1:
      fStack_1c4 = -2.835711e+38;
      break;
    case 2:
      fStack_1c4 = -3.2893961e+38;
      break;
    case 3:
      fStack_1c4 = -2.842021e+38;
    }
    fVar22 = 1.0;
    fVar21 = 0.0;
    fVar20 = 1.0;
    fVar19 = 0.0;
    fVar17 = 0.07;
    fVar16 = 0.9;
    if (uVar6 == 0) {
      CVBufTexture__DrawSpriteEx
                (_DAT_0067a628 + _DAT_005dbe48,_DAT_0067a62c + _DAT_005dbe48 + _DAT_005dbe34,0.011,
                 *(void **)(param_1 + 0x168),4,1,fStack_1e8,0.0,fStack_1c4,0.9,0.07,0.0,1.0,0.0,1.0)
      ;
    }
    else {
      pvVar18 = *(void **)(param_1 + 0x168);
      fVar25 = 0.0;
      iVar5 = 1;
      iVar4 = 4;
      fVar24 = 0.011;
      fVar23 = fStack_1c4;
      iVar2 = PLATFORM__GetWindowHeight();
      CVBufTexture__DrawSpriteEx
                (_DAT_0067a628 + _DAT_005dbe48,
                 (float)iVar2 * _DAT_005d85ec + _DAT_0067a62c + _DAT_005d8610 + _DAT_005dbe34,fVar24
                 ,pvVar18,iVar4,iVar5,fStack_1e8,fVar25,fVar23,fVar16,fVar17,fVar19,fVar20,fVar21,
                 fVar22);
    }
    if (local_1c8 != (int *)0x0) {
      fVar25 = 1.0;
      fVar24 = 0.0;
      fVar23 = 1.0;
      fVar22 = 0.0;
      fVar21 = 0.07;
      fVar20 = 0.9;
      fVar19 = -1.7014118e+38;
      fVar17 = 0.0;
      fVar16 = 1.0;
      iVar4 = 0;
      iVar2 = 4;
      if (uVar6 == 0) {
        pvVar18 = *(void **)(param_1 + 0x168);
        fVar26 = _DAT_0067a62c + _DAT_005dbe48;
        fVar27 = 0.011;
      }
      else {
        pvVar18 = *(void **)(param_1 + 0x168);
        fVar27 = 0.011;
        iVar5 = PLATFORM__GetWindowHeight();
        fVar26 = (float)iVar5 * _DAT_005d85ec + _DAT_0067a62c + _DAT_005d8610;
      }
      CVBufTexture__DrawSpriteEx
                (_DAT_0067a628 + _DAT_005dbe48,fVar26 + _DAT_005dbe30,fVar27,pvVar18,iVar2,iVar4,
                 fVar16,fVar17,fVar19,fVar20,fVar21,fVar22,fVar23,fVar24,fVar25);
      fVar12 = (float10)(**(code **)(*local_1c8 + 0x138))();
      if ((float10)_DAT_005d8570 < fVar12) {
        dVar15 = CDXCompass__Helper_004f99f0((int)local_1c8);
        fVar12 = (float10)(**(code **)(*local_1c8 + 0x138))();
        fStack_1e8 = (float)((float10)(float)dVar15 / fVar12);
        if ((float10)_DAT_005d856c <= (float10)(float)dVar15 / fVar12) {
          if (_DAT_005d8568 < fStack_1e8) {
            fStack_1e8 = 1.0;
          }
        }
        else {
          fStack_1e8 = 0.0;
        }
        fVar23 = 1.0;
        fVar22 = 0.0;
        fVar21 = 1.0;
        fVar20 = 0.0;
        fVar19 = 0.07;
        fVar17 = 0.9;
        fVar16 = 0.0;
        if (uVar6 == 0) {
          pvVar18 = *(void **)(param_1 + 0x168);
          fVar24 = _DAT_0067a62c + _DAT_005dbe48;
          iVar5 = 1;
          iVar4 = 4;
          fVar25 = 0.011;
        }
        else {
          pvVar18 = *(void **)(param_1 + 0x168);
          iVar5 = 1;
          iVar4 = 4;
          fVar25 = 0.011;
          iVar2 = PLATFORM__GetWindowHeight();
          fVar24 = (float)iVar2 * _DAT_005d85ec + _DAT_0067a62c + _DAT_005d8610;
        }
        CVBufTexture__DrawSpriteEx
                  (_DAT_0067a628 + _DAT_005dbe48,fVar24 + _DAT_005dbe30,fVar25,pvVar18,iVar4,iVar5,
                   fStack_1e8,fVar16,fStack_1c4,fVar17,fVar19,fVar20,fVar21,fVar22,fVar23);
      }
    }
  }
  return;
}
