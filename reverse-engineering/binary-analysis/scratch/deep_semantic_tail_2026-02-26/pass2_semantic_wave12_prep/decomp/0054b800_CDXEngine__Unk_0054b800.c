/* address: 0x0054b800 */
/* name: CDXEngine__Unk_0054b800 */
/* signature: void __cdecl CDXEngine__Unk_0054b800(int param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl CDXEngine__Unk_0054b800(int param_1,void *param_2)

{
  float *pfVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int *piVar8;
  float fVar9;
  int iVar10;
  float10 fVar11;
  float10 fVar12;
  float10 extraout_ST0;
  float10 extraout_ST0_00;
  float10 extraout_ST0_01;
  float10 extraout_ST0_02;
  float10 extraout_ST0_03;
  float10 extraout_ST0_04;
  float10 fVar13;
  float10 fVar14;
  float10 fVar15;
  double dVar16;
  float fStack_258;
  float fStack_254;
  float fStack_250;
  float fStack_24c;
  longlong lStack_248;
  float fStack_240;
  longlong lStack_23c;
  float fStack_234;
  float fStack_230;
  float fStack_22c;
  int iStack_228;
  int iStack_224;
  int iStack_220;
  float fStack_21c;
  float fStack_218;
  float fStack_214;
  float fStack_20c;
  float fStack_208;
  float fStack_204;
  float fStack_1fc;
  float fStack_1f8;
  float fStack_1f4;
  float fStack_1ec;
  int iStack_1e8;
  float fStack_1e4;
  float fStack_1e0;
  float fStack_1d4;
  float fStack_1d0;
  float fStack_1c4;
  float fStack_1c0;
  undefined4 uStack_1bc;
  undefined4 uStack_1b8;
  int iStack_1b4;
  float fStack_1b0;
  float fStack_1ac;
  float fStack_1a8;
  float fStack_1a4;
  undefined4 uStack_1a0;
  undefined4 uStack_19c;
  int iStack_198;
  float fStack_194;
  float fStack_190;
  float fStack_18c;
  float fStack_188;
  undefined4 uStack_184;
  undefined4 uStack_180;
  int iStack_17c;
  float fStack_178;
  float fStack_174;
  float fStack_16c;
  float fStack_168;
  float fStack_15c;
  float fStack_158;
  float fStack_14c;
  float fStack_148;
  float fStack_13c;
  float fStack_12c;
  float fStack_128;
  float fStack_11c;
  float fStack_118;
  float fStack_10c;
  float fStack_108;
  char acStack_100 [256];

  piVar8 = (int *)0x0;
  if (param_2 != (void *)0x0) {
    piVar8 = (int *)(**(code **)(*(int *)param_2 + 0x70))();
  }
  iVar5 = *(int *)(param_1 + 0x8c);
  if ((iVar5 != 2) && (iVar5 != 4)) {
    if (iVar5 == 1) {
      fVar9 = fStack_250;
      if ((((param_2 != (void *)0x0) && (1 < *(int *)(param_1 + 0xb8))) &&
          (*(int *)(*(int *)(param_1 + 0x128) + 0x14) != 0)) &&
         (iVar5 = (**(code **)(*(int *)param_2 + 0x1c))(), fVar9 = fStack_250, -1 < iVar5)) {
        fVar11 = (float10)(**(code **)(*(int *)param_2 + 0x18))();
        iVar10 = *(int *)(*(int *)(param_1 + 0x128) + 0x18);
        fStack_254 = (float)*(int *)(iVar10 + iVar5 * 0x24 + 0x14) +
                     (float)*(int *)(iVar10 + 0x1c + iVar5 * 0x24) * (float)fVar11;
        if (piVar8 != (int *)0x0) {
          (**(code **)(*piVar8 + 0x14))(param_1,&fStack_254);
        }
        CDXEngine__Helper_0055dfe7((double)fStack_254);
        dVar16 = CDXEngine__Helper_0055dfe7((double)fStack_254);
        fStack_250 = fStack_254 - (float)dVar16;
        dVar16 = CDXEngine__Helper_0055dfe7(0.0);
        lStack_23c = (longlong)ROUND(dVar16);
        fVar9 = (float)lStack_23c;
        dVar16 = CDXEngine__Helper_0055dfe7(0.0);
        lStack_23c = (longlong)ROUND(dVar16);
        if ((int)(float)lStack_23c < (int)fVar9 + 1) {
          CDXEngine__Helper_0055dfe7(0.0);
        }
        fStack_258 = 1.0;
      }
      iVar5 = *(int *)(*(int *)(param_1 + 0x84) + (int)fVar9 * 4);
      iVar10 = *(int *)(*(int *)(param_1 + 0x84) + (int)fVar9 * 4);
      iStack_1e8 = iVar10;
      dVar16 = CDXEngine__Helper_0055dfe7((double)fStack_258);
      fVar3 = fStack_258 - (float)dVar16;
      pfVar1 = *(float **)(param_1 + 0xfc);
      fVar4 = _DAT_005d8568 - fVar3;
      fVar2 = pfVar1[5];
      fVar9 = pfVar1[4];
      fStack_22c = *pfVar1 - fVar9;
      fStack_230 = pfVar1[1] - fVar2;
      iStack_220 = 0;
      fStack_24c = (float)DAT_00888a0c;
      fStack_240 = (float)DAT_00888a08 / (fVar9 + fVar9);
      fStack_234 = fStack_24c / (fVar2 + fVar2);
      if (0 < *(int *)(param_1 + 0xb0)) {
        fStack_1ec = SQRT((float)_DAT_005dbe40);
        fStack_258 = 0.0;
        do {
          piVar8 = (int *)(*(int *)(param_1 + 0x80) + (int)fStack_258);
          fStack_250 = (float)*piVar8;
          iStack_224 = piVar8[2];
          iStack_228 = piVar8[1];
          iVar6 = *(int *)((int)fStack_250 + 0x20) * 0x10;
          fStack_16c = fVar3 * *(float *)(iVar6 + 4 + iVar10);
          fStack_168 = fVar3 * *(float *)(iVar6 + 8 + iVar10);
          fStack_11c = fVar4 * *(float *)(iVar6 + 4 + iVar5);
          fStack_118 = fVar4 * *(float *)(iVar6 + 8 + iVar5);
          iVar7 = *(int *)(iStack_228 + 0x20) * 0x10;
          fVar9 = fVar4 * *(float *)(iVar6 + iVar5) + fVar3 * *(float *)(iVar6 + iVar10);
          fStack_13c = fStack_11c + fStack_16c;
          fStack_10c = fVar3 * *(float *)(iVar7 + 4 + iVar10);
          fStack_108 = fVar3 * *(float *)(iVar7 + 8 + iVar10);
          fStack_14c = fVar4 * *(float *)(iVar7 + 4 + iVar5);
          fStack_148 = fVar4 * *(float *)(iVar7 + 8 + iVar5);
          iVar6 = *(int *)(iStack_224 + 0x20) * 0x10;
          fStack_1d4 = fVar4 * *(float *)(iVar7 + iVar5) + fVar3 * *(float *)(iVar7 + iVar10);
          fStack_1d0 = fStack_14c + fStack_10c;
          fStack_15c = fVar3 * *(float *)(iVar6 + 4 + iVar10);
          fStack_1e4 = 1.0;
          fStack_1e0 = 1.0;
          fStack_158 = fVar3 * *(float *)(iVar6 + 8 + iVar10);
          fStack_12c = fVar4 * *(float *)(iVar6 + 4 + iVar5);
          fStack_128 = fVar4 * *(float *)(iVar6 + 8 + iVar5);
          fStack_1fc = fVar4 * *(float *)(iVar6 + iVar5) + fVar3 * *(float *)(iVar6 + iVar10);
          fStack_1f8 = fStack_12c + fStack_15c;
          fStack_1f4 = fStack_128 + fStack_158;
          fStack_21c = fStack_1d4 - fVar9;
          fStack_218 = fStack_1d0 - fStack_13c;
          fStack_214 = (fStack_148 + fStack_108) - (fStack_118 + fStack_168);
          fStack_20c = fStack_1fc - fVar9;
          fStack_208 = fStack_1f8 - fStack_13c;
          fStack_204 = fStack_1f4 - (fStack_118 + fStack_168);
          fVar13 = (float10)fStack_204 * (float10)fStack_218 -
                   (float10)fStack_208 * (float10)fStack_214;
          fVar14 = (float10)fStack_214 * (float10)fStack_20c -
                   (float10)fStack_204 * (float10)fStack_21c;
          fVar15 = (float10)fStack_208 * (float10)fStack_21c -
                   (float10)fStack_218 * (float10)fStack_20c;
          fVar12 = (float10)_DAT_005d8568;
          fVar11 = (float10)(float)SQRT(fVar15 * fVar15 +
                                        (float10)(float)fVar14 * (float10)(float)fVar14 +
                                        fVar13 * fVar13);
          if (fVar11 != (float10)_DAT_005d856c) {
            fVar11 = (float10)_DAT_005d8568 / fVar11;
            fVar13 = fVar13 * fVar11;
            fVar14 = fVar14 * fVar11;
            fVar15 = fVar15 * fVar11;
          }
          if (fStack_1ec != _DAT_005d856c) {
            fVar12 = (float10)_DAT_005d8568 / (float10)fStack_1ec;
            fStack_1e4 = (float)fVar12;
            fStack_1e0 = (float)fVar12;
          }
          uStack_1bc = 0x3f800000;
          uStack_1b8 = 0x3f800000;
          fVar11 = (float10)fcos(((float10)fStack_1e0 * fVar14 +
                                 fVar12 * fVar15 + (float10)fStack_1e4 * fVar13) *
                                 (float10)_DAT_005db4f4);
          lStack_248 = (longlong)ROUND(ABS(fVar11) * (float10)_DAT_005e50f4);
          iVar6 = (int)lStack_248 * -0x10101 + -0x808081;
          fStack_1c4 = (fVar9 - fStack_22c) * fStack_240;
          fStack_1c0 = fStack_24c - (fStack_13c - fStack_230) * fStack_234;
          iStack_1b4 = iVar6;
          CDXEngine__Helper_004b5250(*(float *)((int)fStack_250 + 0x24));
          fStack_1b0 = (float)extraout_ST0;
          dVar16 = CDXEngine__Helper_004b52a0(*(float *)((int)fStack_250 + 0x28));
          CDXEngine__Helper_004b5250(_DAT_005d8568 - (float)dVar16);
          fStack_1ac = (float)extraout_ST0_00;
          uStack_1a0 = 0x3f800000;
          uStack_19c = 0x3f800000;
          fStack_1a8 = (fStack_1d4 - fStack_22c) * fStack_240;
          fStack_1a4 = fStack_24c - (fStack_1d0 - fStack_230) * fStack_234;
          iStack_198 = iVar6;
          CDXEngine__Helper_004b5250(*(float *)(iStack_228 + 0x24));
          fStack_194 = (float)extraout_ST0_01;
          dVar16 = CDXEngine__Helper_004b52a0(*(float *)(iStack_228 + 0x28));
          CDXEngine__Helper_004b5250(_DAT_005d8568 - (float)dVar16);
          iVar10 = iStack_224;
          fStack_190 = (float)extraout_ST0_02;
          uStack_184 = 0x3f800000;
          uStack_180 = 0x3f800000;
          fStack_18c = (fStack_1fc - fStack_22c) * fStack_240;
          fStack_188 = fStack_24c - (fStack_1f8 - fStack_230) * fStack_234;
          iStack_17c = iVar6;
          CDXEngine__Helper_004b5250(*(float *)(iStack_224 + 0x24));
          fStack_178 = (float)extraout_ST0_03;
          dVar16 = CDXEngine__Helper_004b52a0(*(float *)(iVar10 + 0x28));
          CDXEngine__Helper_004b5250(_DAT_005d8568 - (float)dVar16);
          fStack_174 = (float)extraout_ST0_04;
          (**(code **)(*(int *)**(undefined4 **)
                                 (**(int **)(param_1 + 0x128) + 4 + *(int *)(*piVar8 + 0x30) * 0x24)
                      + 0x20))();
          lStack_23c = CONCAT26(lStack_23c._6_2_,0x200010000);
          CVBufTexture__SetVBFormat(0x144,0x208,0x1c,4,0);
          CVBufTexture__SetIBFormat(0x65,0x208,2,0);
          CVBufTexture__AddVertices(&fStack_1c4,3);
          CVBufTexture__AddIndices(&lStack_23c,3);
          CVBufTexture__Render();
          iStack_220 = iStack_220 + 1;
          fStack_258 = (float)((int)fStack_258 + 0xc);
          iVar10 = iStack_1e8;
        } while (iStack_220 < *(int *)(param_1 + 0xb0));
        return;
      }
    }
    else {
      if (iVar5 == 3) {
        DebugTrace(s_Error___2D_renderer_doesn_t_supp_00651190);
        return;
      }
      sprintf(acStack_100,s_Attempt_to_render_unknown_mesh_p_00651160);
      DebugTrace(acStack_100);
    }
  }
  return;
}
