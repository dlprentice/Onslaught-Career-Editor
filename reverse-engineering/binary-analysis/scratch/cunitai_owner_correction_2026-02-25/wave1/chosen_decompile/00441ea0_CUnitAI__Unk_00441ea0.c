/* address: 0x00441ea0 */
/* name: CUnitAI__Unk_00441ea0 */
/* signature: void __fastcall CUnitAI__Unk_00441ea0(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CUnitAI__Unk_00441ea0(void *param_1)

{
  char cVar1;
  undefined4 uVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  int iVar6;
  undefined4 *puVar7;
  undefined4 *puVar8;
  float *pfVar9;
  undefined4 *puVar10;
  char *pcVar11;
  float *pfVar12;
  void *m03;
  float in_stack_fffffde4;
  float in_stack_fffffde8;
  short *in_stack_fffffdec;
  float in_stack_fffffdf0;
  float in_stack_fffffdf4;
  float in_stack_fffffdf8;
  char *in_stack_fffffdfc;
  float *in_stack_fffffe00;
  float *pfVar13;
  undefined1 *m31;
  undefined1 *m32;
  undefined1 *m33;
  float fStack_1c8;
  float fStack_1c4;
  float local_1c0 [4];
  undefined4 local_1b0;
  float local_1ac;
  float fStack_1a0;
  float fStack_19c;
  float fStack_198;
  float fStack_190;
  float fStack_18c;
  float fStack_188;
  undefined4 uStack_184;
  undefined4 uStack_180;
  undefined4 uStack_17c;
  undefined4 uStack_178;
  undefined4 uStack_174;
  float fStack_170;
  undefined4 uStack_16c;
  undefined4 uStack_168;
  undefined4 uStack_164;
  float afStack_160 [2];
  undefined4 local_158;
  undefined4 local_154;
  float local_150;
  undefined4 local_14c;
  undefined4 local_148;
  float local_144;
  float fStack_140;
  float fStack_138;
  float fStack_134;
  float local_130;
  float afStack_128 [4];
  float fStack_118;
  float fStack_114;
  float fStack_110;
  float fStack_108;
  float fStack_104;
  float fStack_100;
  undefined1 *puStack_f4;
  undefined1 *puStack_e4;
  undefined1 *puStack_d4;
  undefined1 auStack_c8 [8];
  undefined4 local_c0 [14];
  undefined1 auStack_88 [8];
  undefined4 local_80 [14];
  undefined1 auStack_48 [8];
  undefined4 local_40 [16];

  pfVar13 = (float *)&DAT_0089ce14;
  pfVar9 = local_1c0;
  for (iVar6 = 6; iVar6 != 0; iVar6 = iVar6 + -1) {
    *pfVar9 = *pfVar13;
    pfVar13 = pfVar13 + 1;
    pfVar9 = pfVar9 + 1;
  }
  puVar7 = &DAT_009c6994;
  puVar8 = local_40;
  for (iVar6 = 0x10; iVar6 != 0; iVar6 = iVar6 + -1) {
    *puVar8 = *puVar7;
    puVar7 = puVar7 + 1;
    puVar8 = puVar8 + 1;
  }
  puVar7 = &DAT_009c6914;
  puVar8 = local_80;
  for (iVar6 = 0x10; iVar6 != 0; iVar6 = iVar6 + -1) {
    *puVar8 = *puVar7;
    puVar7 = puVar7 + 1;
    puVar8 = puVar8 + 1;
  }
  local_14c = local_1c0[1];
  local_148 = local_1b0;
  puVar7 = &DAT_009c6954;
  puVar8 = local_c0;
  for (iVar6 = 0x10; iVar6 != 0; iVar6 = iVar6 + -1) {
    *puVar8 = *puVar7;
    puVar7 = puVar7 + 1;
    puVar8 = puVar8 + 1;
  }
  local_144 = local_1ac;
  local_150 = local_1c0[0];
  local_158 = local_1c0[2];
  local_154 = local_1c0[3];
  (*(code *)**(undefined4 **)(&DAT_0089c9a4)[DAT_0089ce4c])();
  (**(code **)(*(int *)(&DAT_0089c9a4)[DAT_0089ce4c] + 4))();
  pfVar13 = (float *)0x441f93;
  Vec3__SetXYZ();
  puVar7 = *(undefined4 **)param_1;
  m31 = puStack_f4;
  m32 = puStack_e4;
  m33 = puStack_d4;
  do {
    if (puVar7 == (undefined4 *)0x0) {
      return;
    }
    puVar8 = puVar7 + 0x15;
    puVar10 = (undefined4 *)&stack0xfffffde4;
    for (iVar6 = 0xc; iVar6 != 0; iVar6 = iVar6 + -1) {
      *puVar10 = *puVar8;
      puVar8 = puVar8 + 1;
      puVar10 = puVar10 + 1;
    }
    m03 = (void *)puVar7[0x14];
    CDXEngine__SetWorldMatrixElements
              (&DAT_009c65c0,(float)puVar7[0x11],(float)puVar7[0x12],(float)puVar7[0x13],(float)m03,
               in_stack_fffffde4,in_stack_fffffde8,(float)in_stack_fffffdec,in_stack_fffffdf0,
               in_stack_fffffdf4,in_stack_fffffdf8,(float)in_stack_fffffdfc,(float)in_stack_fffffe00
               ,(float)pfVar13,(float)m31,(float)m32,(float)m33);
    if (DAT_0089ce84 == (float *)0x0) {
      in_stack_fffffdfc = s_meshtex_default_tga_00625498;
      in_stack_fffffdf8 = 6.25627e-39;
      in_stack_fffffe00 = DAT_0089ce84;
      pfVar13 = DAT_0089ce84;
      DAT_0089ce84 = (float *)CTexture__FindTexture(s_meshtex_default_tga_00625498,0,0,-1,1,1);
    }
    fStack_170 = (float)puVar7[1];
    uStack_16c = puVar7[2];
    uStack_168 = puVar7[3];
    uStack_164 = puVar7[4];
    uStack_180 = puVar7[0x21];
    uStack_17c = puVar7[0x22];
    uStack_178 = puVar7[0x23];
    uVar2 = puVar7[0x24];
    puVar8 = puVar7 + 5;
    puVar10 = (undefined4 *)&stack0xfffffde0;
    for (iVar6 = 0xc; iVar6 != 0; iVar6 = iVar6 + -1) {
      *puVar10 = *puVar8;
      puVar8 = puVar8 + 1;
      puVar10 = puVar10 + 1;
    }
    uStack_174 = uVar2;
    CDXEngine__Unk_0053d760((void *)puVar7[0x25],&uStack_180,&fStack_170,m03);
    RenderState_Set(0x13,5);
    m33 = (undefined1 *)0x6;
    m32 = (undefined1 *)0x14;
    m31 = (undefined1 *)0x44209d;
    RenderState_Set(0x14,6);
    iVar6 = -1;
    pcVar11 = (char *)(puVar7 + 0x26);
    do {
      if (iVar6 == 0) break;
      iVar6 = iVar6 + -1;
      cVar1 = *pcVar11;
      pcVar11 = pcVar11 + 1;
    } while (cVar1 != '\0');
    if (iVar6 != -2) {
      fStack_18c = (float)puVar7[0x12];
      fStack_190 = (float)puVar7[0x11];
      fVar3 = (float)puVar7[1];
      fStack_188 = (float)puVar7[0x13];
      uStack_184 = puVar7[0x14];
      fVar4 = (float)puVar7[3];
      fVar5 = (float)puVar7[2];
      pfVar9 = (float *)(puVar7 + 0x15);
      pfVar12 = afStack_128;
      for (iVar6 = 0xc; iVar6 != 0; iVar6 = iVar6 + -1) {
        *pfVar12 = *pfVar9;
        pfVar9 = pfVar9 + 1;
        pfVar12 = pfVar12 + 1;
      }
      local_144 = fStack_118 * fVar3 + fStack_114 * fVar5 + fStack_110 * fVar4;
      fStack_140 = fStack_108 * fVar3 + fVar5 * fStack_104 + fVar4 * fStack_100;
      fStack_1a0 = afStack_128[0] * fVar3 + afStack_128[1] * fVar5 + afStack_128[2] * fVar4 +
                   fStack_190;
      fStack_19c = fStack_18c + local_144;
      fStack_198 = fStack_188 + fStack_140;
      if (_DAT_005d856c <
          (fStack_1a0 - fStack_138) * fStack_1c8 +
          fStack_1c4 * (fStack_19c - fStack_134) + local_1c0[0] * (fStack_198 - local_130)) {
        m33 = auStack_88;
        m32 = auStack_c8;
        m31 = auStack_48;
        pfVar13 = afStack_160;
        in_stack_fffffe00 = &fStack_1a0;
        in_stack_fffffdfc = (char *)&local_1b0;
        in_stack_fffffdf8 = 6.257053e-39;
        CDXTexture__Unk_00576297();
        if (_DAT_005d856c <= fStack_1c8) {
          in_stack_fffffdf8 = 6.257096e-39;
          m32 = (undefined1 *)PLATFORM__GetWindowWidth();
          if ((fStack_1c8 < (float)(int)m32) && (_DAT_005d856c <= fStack_1c4)) {
            in_stack_fffffdf8 = 6.25716e-39;
            m32 = (undefined1 *)PLATFORM__GetWindowHeight();
            if (fStack_1c4 < (float)(int)m32) {
              in_stack_fffffde8 = (float)puVar7[0x25];
              in_stack_fffffdf8 = 1.0;
              in_stack_fffffdf4 = 0.0;
              in_stack_fffffdf0 = 0.0;
              in_stack_fffffdec = Text__AsciiToWideScratch((char *)(puVar7 + 0x26));
              in_stack_fffffde4 = fStack_1c4;
              CDXFont__DrawText();
            }
          }
        }
      }
    }
    puVar7 = (undefined4 *)*puVar7;
  } while( true );
}
