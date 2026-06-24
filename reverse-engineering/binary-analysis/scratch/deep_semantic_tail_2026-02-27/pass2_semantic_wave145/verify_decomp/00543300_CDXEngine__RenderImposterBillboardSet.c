/* address: 0x00543300 */
/* name: CDXEngine__RenderImposterBillboardSet */
/* signature: void __thiscall CDXEngine__RenderImposterBillboardSet(void * this, int param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CDXEngine__RenderImposterBillboardSet(void *this,int param_1,void *param_2)

{
  float fVar1;
  float fVar2;
  float fVar3;
  undefined4 *puVar4;
  float *extraout_EAX;
  float *extraout_EAX_00;
  undefined4 *extraout_EAX_01;
  float *extraout_EAX_02;
  int iVar5;
  undefined1 *puVar6;
  int iVar7;
  float *pfVar8;
  float *pfVar9;
  float10 fVar10;
  float10 fVar11;
  float10 fVar12;
  undefined1 *puVar13;
  float fStack_248;
  float fStack_244;
  float fStack_240;
  float fStack_23c;
  undefined4 uStack_238;
  undefined4 uStack_234;
  undefined4 uStack_230;
  undefined4 uStack_22c;
  float afStack_228 [4];
  float fStack_218;
  float fStack_210;
  float fStack_208;
  float fStack_200;
  float fStack_1f8;
  float fStack_1f4;
  float local_1f0 [2];
  undefined4 uStack_1e8;
  undefined4 uStack_1e4;
  undefined4 uStack_1e0;
  undefined4 uStack_1dc;
  undefined4 uStack_1d8;
  undefined4 uStack_1d4;
  undefined4 uStack_1d0;
  undefined4 uStack_1cc;
  undefined4 uStack_1c8;
  undefined4 uStack_1c4;
  undefined4 uStack_1c0;
  undefined4 uStack_1bc;
  undefined4 uStack_1b8;
  undefined4 uStack_1b4;
  undefined4 uStack_1b0;
  undefined4 uStack_1ac;
  undefined4 uStack_1a8;
  undefined4 uStack_1a4;
  undefined4 uStack_1a0;
  undefined4 uStack_19c;
  undefined4 uStack_198;
  undefined4 uStack_194;
  undefined4 uStack_190;
  undefined4 uStack_18c;
  float fStack_188;
  undefined1 auStack_184 [52];
  float fStack_150;
  float fStack_148;
  float fStack_144;
  float fStack_140;
  float fStack_138;
  float fStack_134;
  float fStack_130;
  float fStack_128;
  float fStack_124;
  float fStack_120;
  undefined1 auStack_e8 [64];
  undefined1 auStack_a8 [16];
  undefined1 auStack_98 [48];
  undefined1 auStack_68 [48];
  undefined1 auStack_38 [56];

  if ((DAT_0067a67c != 0) && (*(int *)((int)this + 0x38) != 0)) {
    (*(code *)**(undefined4 **)param_1)(local_1f0);
    puVar13 = auStack_184;
    (**(code **)(*(int *)param_1 + 4))();
    fVar10 = (float10)fcos((float10)_DAT_005dc478);
    fVar11 = (float10)fsin((float10)_DAT_005dc478);
    fVar1 = (float)fVar11;
    fVar11 = (float10)fcos((float10)_DAT_005d87b0);
    fVar2 = (float)fVar11;
    fVar12 = (float10)fsin((float10)_DAT_005d87b0);
    fStack_124 = (float)fVar12;
    fVar3 = (float)fVar12;
    fStack_120 = (float)fVar11;
    fVar11 = (float10)fStack_124 * (float10)fVar3;
    fStack_148 = (float)((float10)fVar2 * fVar10 - fVar11 * (float10)fVar1);
    fStack_144 = -(fStack_120 * fVar1);
    fVar12 = (float10)fStack_124 * (float10)fVar2;
    fStack_140 = (float)((float10)fVar3 * fVar10 + fVar12 * (float10)fVar1);
    fStack_138 = (float)((float10)fVar2 * (float10)fVar1 + fVar11 * fVar10);
    fStack_134 = (float)((float10)fStack_120 * fVar10);
    fStack_130 = (float)((float10)fVar3 * (float10)fVar1 - (float10)(float)fVar12 * fVar10);
    fStack_128 = -(fStack_120 * fVar3);
    fStack_120 = fStack_120 * fVar2;
    Vec3__SetXYZ();
    fStack_1f8 = fStack_248 + fStack_1f8;
    iVar7 = 0;
    fStack_1f4 = fStack_1f4 + fStack_244;
    local_1f0[0] = local_1f0[0] + fStack_240;
    do {
      pfVar8 = &fStack_188;
      pfVar9 = afStack_228;
      for (iVar5 = 0xc; iVar5 != 0; iVar5 = iVar5 + -1) {
        *pfVar9 = *pfVar8;
        pfVar8 = pfVar8 + 1;
        pfVar9 = pfVar9 + 1;
      }
      if (iVar7 == 4) {
        vector_constructor_iterator_nothrow(&uStack_1e8,0x10,3,&LAB_00402d20);
        puVar4 = (undefined4 *)Vec3__SetXYZ();
        fsin((float10)_DAT_005e50c0);
        uStack_1e8 = *puVar4;
        uStack_1e4 = puVar4[1];
        uStack_1e0 = puVar4[2];
        uStack_1dc = puVar4[3];
        fcos((float10)_DAT_005e50c0);
        puVar4 = (undefined4 *)Vec3__SetXYZ();
        uStack_1d8 = *puVar4;
        uStack_1d4 = puVar4[1];
        uStack_1d0 = puVar4[2];
        uStack_1cc = puVar4[3];
        puVar4 = (undefined4 *)Vec3__SetXYZ();
        uStack_1c8 = *puVar4;
        uStack_1c4 = puVar4[1];
        uStack_1c0 = puVar4[2];
        puVar6 = auStack_98;
        uStack_1bc = puVar4[3];
        puVar4 = &uStack_1e8;
LAB_005436f9:
        CMCBuggy__Helper_0040d320(afStack_228,puVar6,puVar4,puVar13);
        pfVar8 = extraout_EAX;
        pfVar9 = afStack_228;
        for (iVar5 = 0xc; iVar5 != 0; iVar5 = iVar5 + -1) {
          *pfVar9 = *pfVar8;
          pfVar8 = pfVar8 + 1;
          pfVar9 = pfVar9 + 1;
        }
      }
      else if (iVar7 == 5) {
        vector_constructor_iterator_nothrow(&uStack_1b8,0x10,3,&LAB_00402d20);
        puVar4 = (undefined4 *)Vec3__SetXYZ();
        fsin((float10)_DAT_005e50b8);
        uStack_1b8 = *puVar4;
        uStack_1b4 = puVar4[1];
        uStack_1b0 = puVar4[2];
        uStack_1ac = puVar4[3];
        fcos((float10)_DAT_005e50b8);
        puVar4 = (undefined4 *)Vec3__SetXYZ();
        uStack_1a8 = *puVar4;
        uStack_1a4 = puVar4[1];
        uStack_1a0 = puVar4[2];
        uStack_19c = puVar4[3];
        puVar4 = (undefined4 *)Vec3__SetXYZ();
        uStack_198 = *puVar4;
        uStack_194 = puVar4[1];
        uStack_190 = puVar4[2];
        puVar6 = auStack_68;
        uStack_18c = puVar4[3];
        puVar4 = &uStack_1b8;
        goto LAB_005436f9;
      }
      fVar1 = *(float *)(*(int *)((int)this + 0x3c) + 0x10 + iVar7 * 0x18) * _DAT_005d8cc4;
      fStack_150 = *(float *)(*(int *)((int)this + 0x3c) + 0x14 + iVar7 * 0x18) * _DAT_005d8cc4;
      afStack_228[0] = afStack_228[0] * fVar1;
      fStack_248 = 1.0;
      fStack_244 = 0.0;
      fStack_240 = 0.0;
      afStack_228[2] = afStack_228[2] * fStack_150;
      uStack_238 = 0;
      uStack_234 = 0;
      uStack_230 = 0x3f800000;
      fStack_218 = fStack_218 * fVar1;
      fStack_210 = fStack_210 * fStack_150;
      fStack_208 = fStack_208 * fVar1;
      fStack_200 = fStack_200 * fStack_150;
      CSquadNormal__Helper_0040d2c0(afStack_228,auStack_a8,&fStack_248,puVar13);
      fStack_248 = *extraout_EAX_00;
      fStack_244 = extraout_EAX_00[1];
      fStack_240 = extraout_EAX_00[2];
      fStack_23c = extraout_EAX_00[3];
      CSquadNormal__Helper_0040d2c0(afStack_228,auStack_e8,&uStack_238,puVar13);
      uStack_238 = *extraout_EAX_01;
      uStack_234 = extraout_EAX_01[1];
      uStack_230 = extraout_EAX_01[2];
      uStack_22c = extraout_EAX_01[3];
      CDXImposter__BuildQuadGeometry();
      if (iVar7 < 4) {
        CMCBuggy__Helper_0040d320(&fStack_148,auStack_38,&fStack_188,puVar13);
        pfVar8 = extraout_EAX_02;
        pfVar9 = &fStack_188;
        for (iVar5 = 0xc; iVar5 != 0; iVar5 = iVar5 + -1) {
          *pfVar9 = *pfVar8;
          pfVar8 = pfVar8 + 1;
          pfVar9 = pfVar9 + 1;
        }
      }
      iVar7 = iVar7 + 1;
    } while (iVar7 < 6);
  }
  return;
}
