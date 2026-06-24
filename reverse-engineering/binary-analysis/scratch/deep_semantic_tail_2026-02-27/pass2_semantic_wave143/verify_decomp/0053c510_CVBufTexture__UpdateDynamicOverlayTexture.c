/* address: 0x0053c510 */
/* name: CVBufTexture__UpdateDynamicOverlayTexture */
/* signature: void __thiscall CVBufTexture__UpdateDynamicOverlayTexture(void * this, int param_1, int param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CVBufTexture__UpdateDynamicOverlayTexture(void *this,int param_1,int param_2)

{
  float fVar1;
  float fVar2;
  short sVar3;
  int *piVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  short *psVar11;
  short *psVar12;
  short sVar13;
  int iVar14;
  uint uVar15;
  undefined4 *puVar16;
  int iVar17;
  ulonglong uVar18;
  short *local_b8;
  uint uStack_b4;
  uint uStack_b0;
  uint local_ac;
  uint uStack_a8;
  uint uStack_a4;
  uint uStack_a0;
  int iStack_9c;
  uint uStack_98;
  int iStack_94;
  uint uStack_90;
  uint uStack_8c;
  uint local_88;
  uint uStack_84;
  int local_80;
  int iStack_7c;
  int iStack_78;
  uint uStack_74;
  int iStack_70;
  int iStack_6c;
  int iStack_68;
  int iStack_64;
  int iStack_60;
  short sStack_58;
  short sStack_54;
  int iStack_50;
  short sStack_4c;
  int iStack_34;
  undefined4 *puStack_30;
  int local_20;
  int iStack_1c;
  int iStack_18;
  int iStack_10;

  CDXCompass__Helper_004f99f0(param_1);
  CDXCompass__Helper_00406040(param_1);
  CDXCompass__Helper_0040c630(param_1);
  piVar4 = CDXTexture__GetAnimatedFrame
                     (*(void **)((int)this + *(int *)((int)this + 0x3c10) * 4 + 0x3f04));
  iVar5 = (**(code **)(*piVar4 + 0x4c))(piVar4,0,&local_20,0,0x800);
  if (-1 < iVar5) {
    iStack_60 = 8;
    uVar8 = DAT_0065042c * 2;
    puVar16 = puStack_30;
    for (uVar7 = uVar8 >> 2; uVar7 != 0; uVar7 = uVar7 - 1) {
      *puVar16 = 0;
      puVar16 = puVar16 + 1;
    }
    iStack_70 = 3;
    for (uVar8 = uVar8 & 3; uVar8 != 0; uVar8 = uVar8 - 1) {
      *(undefined1 *)puVar16 = 0;
      puVar16 = (undefined4 *)((int)puVar16 + 1);
    }
    iVar17 = 1;
    local_b8 = (short *)((int)puStack_30 + iStack_34);
    iStack_6c = 3;
    iStack_68 = 3;
    local_80 = 3;
    uVar8 = (uint)(*(int *)(*(int *)(iStack_10 + 0x574) + 0x2c) != 1);
    iStack_7c = 3;
    iStack_78 = 3;
    iStack_64 = 1;
    iVar5 = 1;
    iVar14 = 8;
    if (iStack_9c < *(int *)(iStack_50 + 0x3c14 + uVar8 * 4)) {
      iStack_64 = 0xf;
      iStack_60 = 1;
    }
    fVar1 = DAT_00672fd0 - *(float *)(iStack_10 + 0x2d4);
    if (_DAT_005d8ba0 < fVar1) {
      fVar1 = _DAT_005d8ba0;
    }
    fVar2 = _DAT_005d8568 - fVar1 * _DAT_005d85ec;
    if (_DAT_005d8ba0 <= fVar1) {
      if (*(int *)(iStack_50 + 0x3c1c + uVar8 * 4) < iStack_94) {
        iVar5 = 1;
        iVar17 = 5;
        iVar14 = 8;
      }
    }
    else {
      fVar1 = _DAT_005d8568 - fVar2;
      iVar5 = (int)(longlong)ROUND(fVar2 * _DAT_005d85d4 + fVar1);
      iVar17 = (int)(longlong)ROUND(fVar1 + fVar2);
      iVar14 = (int)(longlong)ROUND(fVar1 * _DAT_005d8c44 + fVar2);
    }
    *(int *)(iStack_50 + 0x3c1c + uVar8 * 4) = iStack_94;
    *(int *)(iStack_50 + 0x3c14 + uVar8 * 4) = iStack_9c;
    iVar6 = CVBufTexture__Helper_004881e0(&DAT_008aa4e8,0,(int)piVar4);
    if (iVar6 == 0) {
      iStack_60 = 0;
      iStack_64 = 0;
      iStack_68 = 0;
      iStack_6c = 0;
      iStack_70 = 0;
    }
    uVar8 = (uint)(iVar6 != 0);
    iVar6 = CVBufTexture__Helper_004881e0(&DAT_008aa4e8,1,(int)piVar4);
    if (iVar6 == 0) {
      iVar14 = 0;
      iVar17 = 0;
      iVar5 = 0;
      iStack_78 = 0;
      iStack_7c = 0;
      local_80 = 0;
    }
    iVar6 = DAT_00650430 + -2;
    if (iVar6 != 0) {
      uStack_a4 = iVar6 * iVar14;
      local_ac = iVar6 * iVar17;
      uStack_b0 = iVar6 * iVar5;
      local_88 = iVar6 * iStack_78;
      uStack_98 = iVar6 * iStack_7c;
      uStack_b4 = iVar6 * local_80;
      uStack_a0 = iVar6 * uVar8;
      uStack_84 = iVar6 * iStack_60;
      uStack_a8 = iVar6 * iStack_64;
      uStack_90 = iVar6 * iStack_68;
      uStack_74 = iVar6 * iStack_6c;
      uStack_8c = iVar6 * iStack_70;
      uVar7 = iVar6 * 4;
      iStack_1c = -local_80;
      local_20 = -iStack_60;
      iStack_18 = -iStack_70;
      uVar18 = (ulonglong)(uint)-iVar14;
      do {
        uVar15 = DAT_00650430 - 2;
        sVar3 = (short)(uVar7 / uVar15) * 0x1000;
        sStack_4c = ((short)(uStack_8c / uVar15) * 0x10 + (short)(uStack_74 / uVar15)) * 0x10 +
                    (short)(uStack_90 / uVar15);
        sVar13 = ((short)(uStack_a8 / uVar15) * 0x10 + (short)(uStack_84 / uVar15)) * 0x10 +
                 (short)(uStack_a0 / uVar15);
        sStack_54 = ((short)(uStack_b4 / uVar15) * 0x10 + (short)(uStack_98 / uVar15)) * 0x10 +
                    (short)(local_88 / uVar15);
        sStack_58 = ((short)(uStack_b0 / uVar15) * 0x10 + (short)(local_ac / uVar15)) * 0x10 +
                    (short)(uStack_a4 / uVar15);
        iVar14 = CVBufTexture__Helper_004881e0(&DAT_008aa4e8,0,(int)piVar4);
        if (iVar14 != 0) {
          sStack_4c = sStack_4c + sVar3;
          sVar13 = sVar13 + sVar3;
        }
        iVar14 = CVBufTexture__Helper_004881e0(&DAT_008aa4e8,1,(int)piVar4);
        if (iVar14 != 0) {
          sStack_54 = sStack_54 + sVar3;
          sStack_58 = sStack_58 + sVar3;
        }
        uVar15 = 0;
        psVar11 = local_b8;
        if ((uint)(DAT_0065042c * 0x3c) / 0x168 != 0) {
          do {
            *psVar11 = 0;
            psVar11 = psVar11 + 1;
            uVar15 = uVar15 + 1;
          } while (uVar15 < (uint)(DAT_0065042c * 0x3c) / 0x168);
        }
        if ((int)uVar15 < iStack_9c) {
          uVar9 = iStack_9c - uVar15;
          psVar12 = psVar11;
          for (uVar10 = uVar9 >> 1; uVar10 != 0; uVar10 = uVar10 - 1) {
            *(uint *)psVar12 = CONCAT22(sStack_4c,sStack_4c);
            psVar12 = psVar12 + 2;
          }
          for (uVar10 = (uint)((uVar9 & 1) != 0); uVar10 != 0; uVar10 = uVar10 - 1) {
            *psVar12 = sStack_4c;
            psVar12 = psVar12 + 1;
          }
          uVar15 = uVar15 + uVar9;
          psVar11 = psVar11 + uVar9;
        }
        if (uVar15 < (uint)(DAT_0065042c * 0x96) / 0x168) {
          do {
            *psVar11 = sVar13;
            psVar11 = psVar11 + 1;
            uVar15 = uVar15 + 1;
          } while (uVar15 < (uint)(DAT_0065042c * 0x96) / 0x168);
        }
        if (uVar15 < (uint)(DAT_0065042c * 0xe1) / 0x168) {
          do {
            *psVar11 = 0;
            psVar11 = psVar11 + 1;
            uVar15 = uVar15 + 1;
          } while (uVar15 < (uint)(DAT_0065042c * 0xe1) / 0x168);
        }
        psVar12 = psVar11;
        if ((int)uVar15 < iStack_94) {
          uVar10 = iStack_94 - uVar15;
          psVar12 = psVar11 + uVar10;
          for (uVar9 = uVar10 >> 1; uVar9 != 0; uVar9 = uVar9 - 1) {
            *(uint *)psVar11 = CONCAT22(sStack_58,sStack_58);
            psVar11 = psVar11 + 2;
          }
          uVar15 = uVar15 + uVar10;
          for (uVar9 = (uint)((uVar10 & 1) != 0); uVar9 != 0; uVar9 = uVar9 - 1) {
            *psVar11 = sStack_58;
            psVar11 = psVar11 + 1;
          }
        }
        if (uVar15 < (uint)(DAT_0065042c * 0x168) / 0x168) {
          do {
            *psVar12 = sStack_54;
            psVar12 = psVar12 + 1;
            uVar15 = uVar15 + 1;
          } while (uVar15 < (uint)(DAT_0065042c * 0x168) / 0x168);
        }
        local_b8 = (short *)((int)local_b8 + iStack_34);
        uStack_8c = uStack_8c + iStack_18;
        uStack_90 = uStack_90 - iStack_68;
        uStack_74 = uStack_74 - iStack_6c;
        uVar7 = uVar7 - 4;
        uStack_a8 = uStack_a8 - iStack_64;
        uStack_a0 = uStack_a0 - uVar8;
        uStack_84 = uStack_84 + local_20;
        uStack_98 = uStack_98 - iStack_7c;
        uStack_b4 = uStack_b4 + iStack_1c;
        local_88 = local_88 - iStack_78;
        uStack_b0 = uStack_b0 - iVar5;
        local_ac = local_ac - iVar17;
        uStack_a4 = uStack_a4 + (int)uVar18;
        iVar6 = iVar6 + -1;
      } while (iVar6 != 0);
    }
    uVar8 = DAT_0065042c * 2;
    for (uVar7 = uVar8 >> 2; uVar7 != 0; uVar7 = uVar7 - 1) {
      local_b8[0] = 0;
      local_b8[1] = 0;
      local_b8 = local_b8 + 2;
    }
    for (uVar8 = uVar8 & 3; uVar8 != 0; uVar8 = uVar8 - 1) {
      *(undefined1 *)local_b8 = 0;
      local_b8 = (short *)((int)local_b8 + 1);
    }
    piVar4 = CDXTexture__GetAnimatedFrame
                       (*(void **)(iStack_50 + 0x3f04 + *(int *)(iStack_50 + 0x3c10) * 4));
    (**(code **)(*piVar4 + 0x50))(piVar4,0);
  }
  return;
}
