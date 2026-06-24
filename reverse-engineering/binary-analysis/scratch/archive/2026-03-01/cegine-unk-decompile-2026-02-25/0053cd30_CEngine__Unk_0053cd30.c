/* address: 0x0053cd30 */
/* name: CEngine__Unk_0053cd30 */
/* signature: void __thiscall CEngine__Unk_0053cd30(void * this, void * param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CEngine__Unk_0053cd30(void *this,void *param_1,void *param_2)

{
  void *pvVar1;
  float *extraout_EAX;
  int iVar2;
  uint uVar3;
  int unaff_EBP;
  float unaff_ESI;
  float *pfVar4;
  float *pfVar5;
  float *pfVar6;
  undefined4 *puVar7;
  int unaff_EDI;
  float *pfVar8;
  undefined4 *puVar9;
  float10 fVar10;
  float10 fVar11;
  float fVar12;
  float m01;
  float m12;
  float m13;
  float in_stack_fffffe94;
  float in_stack_fffffe98;
  float in_stack_fffffe9c;
  float in_stack_fffffea0;
  float in_stack_fffffea4;
  float in_stack_fffffea8;
  float in_stack_fffffeac;
  float in_stack_fffffeb0;
  undefined1 *m33;
  float fVar13;
  int *piVar14;
  float fVar15;
  uint local_124;
  float fStack_120;
  float fStack_11c;
  float fStack_118;
  float fStack_114;
  float local_110 [4];
  float local_100 [3];
  uint uStack_f4;
  float local_f0;
  float local_ec;
  float local_e8;
  undefined4 uStack_e4;
  undefined4 uStack_e0;
  undefined4 uStack_dc;
  undefined4 uStack_d8;
  undefined4 uStack_d4;
  undefined4 auStack_d0 [4];
  undefined4 local_c0 [12];
  undefined4 auStack_90 [4];
  undefined4 local_80 [12];
  undefined4 auStack_50 [4];
  undefined4 local_40 [16];

  fVar12 = DAT_00888a40;
  fVar13 = 7.696005e-39;
  D3DStateCache__SetStateCached(0,1,4);
  CEngine__Unk_0053c2e0(this,param_1,unaff_EDI);
  CVBufTexture__Unk_0053c510(this,(int)param_1,unaff_EDI);
  pfVar6 = local_100;
  puVar7 = &DAT_009c6954;
  puVar9 = local_c0;
  for (iVar2 = 0x10; iVar2 != 0; iVar2 = iVar2 + -1) {
    *puVar9 = *puVar7;
    puVar7 = puVar7 + 1;
    puVar9 = puVar9 + 1;
  }
  local_110[0] = 0.0;
  puVar7 = &DAT_009c6994;
  puVar9 = local_40;
  for (iVar2 = 0x10; iVar2 != 0; iVar2 = iVar2 + -1) {
    *puVar9 = *puVar7;
    puVar7 = puVar7 + 1;
    puVar9 = puVar9 + 1;
  }
  local_110[1] = 0.0;
  puVar7 = &DAT_009c6914;
  puVar9 = local_80;
  for (iVar2 = 0x10; iVar2 != 0; iVar2 = iVar2 + -1) {
    *puVar9 = *puVar7;
    puVar7 = puVar7 + 1;
    puVar9 = puVar9 + 1;
  }
  local_110[2] = 0.0;
  pfVar4 = (float *)&DAT_0089c928;
  pfVar5 = local_100;
  for (iVar2 = 0xc; iVar2 != 0; iVar2 = iVar2 + -1) {
    *pfVar5 = *pfVar4;
    pfVar4 = pfVar4 + 1;
    pfVar5 = pfVar5 + 1;
  }
  pfVar4 = local_110;
  fVar15 = 7.696197e-39;
  CDXEngine__SetViewAndProjection(&DAT_009c65c0,pfVar6,pfVar4);
  m01 = local_110[1];
  local_f0 = local_f0 * fVar12;
  local_ec = local_ec * fVar12;
  local_e8 = local_e8 * fVar12;
  pfVar5 = local_100;
  pfVar8 = (float *)&stack0xfffffe94;
  for (iVar2 = 0xc; iVar2 != 0; iVar2 = iVar2 + -1) {
    *pfVar8 = *pfVar5;
    pfVar5 = pfVar5 + 1;
    pfVar8 = pfVar8 + 1;
  }
  fVar12 = local_110[0];
  m12 = local_110[2];
  CDXEngine__SetWorldMatrixElements
            (&DAT_009c65c0,local_110[0],m01,local_110[2],local_110[3],in_stack_fffffe94,
             in_stack_fffffe98,in_stack_fffffe9c,in_stack_fffffea0,in_stack_fffffea4,
             in_stack_fffffea8,in_stack_fffffeac,in_stack_fffffeb0,fVar13,fVar15,(float)pfVar6,
             (float)pfVar4);
  iVar2 = CGame__Unk_004725d0(0x8a9a98);
  if (iVar2 == 0) {
    iVar2 = PLATFORM__GetWindowHeight();
    fVar13 = (float)iVar2 * _DAT_005db05c;
    iVar2 = PLATFORM__GetWindowWidth();
    fVar15 = (float)iVar2 * _DAT_005db05c;
    m13 = local_110[3];
  }
  else {
    iVar2 = PLATFORM__GetWindowHeight();
    fVar13 = (float)iVar2 * _DAT_005e4fbc;
    iVar2 = PLATFORM__GetWindowWidth();
    fVar15 = (float)iVar2 * _DAT_005e4fb8;
    m13 = local_110[3];
  }
  CDXEngine__SetProjectionMatrix(&DAT_009c65c0,0.5,100.0,fVar15,fVar13);
  D3DStateCache__SetState114Raw(0,1,3);
  D3DStateCache__SetState114Raw(0,2,3);
  RenderState_Set(0xf,0);
  iVar2 = CGame__Unk_004725d0(0x8a9a98);
  if (iVar2 == 0) {
    local_124 = *(int *)((int)this + 0x3c10) + 1U & 0x80000001;
    if ((int)local_124 < 0) {
      local_124 = (local_124 - 1 | 0xfffffffe) + 1;
    }
  }
  else {
    local_124 = 0;
  }
  pvVar1 = CDXTexture__GetAnimatedFrame(*(void **)((int)this + local_124 * 4 + 0x3f04));
  CEngine__SetRenderStateCached(&DAT_00855bb0,0,(int)pvVar1);
  CVBuffer__SetStreamSource();
  RenderState_Set(0x13,2);
  RenderState_Set(0x14,6);
  CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
  piVar14 = DAT_00888a50;
  (**(code **)(*DAT_00888a50 + 0x144))();
  m33 = &stack0xfffffed0;
  fVar13 = 7.696838e-39;
  CGeneralVolume__Unk_0040d660(param_1,(int)m33,piVar14);
  fVar10 = (float10)fcos(-(float10)*extraout_EAX);
  local_110[2] = 0.0;
  uStack_e0 = 0;
  uStack_dc = 0;
  uStack_d8 = 0x3f800000;
  fVar11 = (float10)fsin((float10)(float)-(float10)*extraout_EAX);
  local_110[0] = (float)fVar10;
  local_110[3] = (float)local_124;
  local_ec = 0.0;
  local_110[1] = (float)-fVar11;
  uStack_f4 = local_124;
  local_100[0] = (float)fVar11 * unaff_ESI;
  local_f0 = 0.0;
  local_e8 = 1.0;
  uStack_e4 = uStack_d4;
  local_100[1] = (float)fVar10 * unaff_ESI;
  local_100[2] = unaff_ESI * 0.0;
  pfVar6 = local_110;
  pfVar4 = (float *)&stack0xfffffe84;
  for (iVar2 = 0xc; iVar2 != 0; iVar2 = iVar2 + -1) {
    *pfVar4 = *pfVar6;
    pfVar6 = pfVar6 + 1;
    pfVar4 = pfVar4 + 1;
  }
  CDXEngine__SetWorldMatrixElements
            (&DAT_009c65c0,fStack_120,fStack_11c,fStack_118,fStack_114,fVar12,m01,m12,m13,
             in_stack_fffffe94,in_stack_fffffe98,in_stack_fffffe9c,in_stack_fffffea0,
             in_stack_fffffea4,in_stack_fffffea8,fVar13,(float)m33);
  pvVar1 = CDXTexture__GetAnimatedFrame(*(void **)((int)this + unaff_EBP * 4 + 0x3c00));
  CEngine__SetRenderStateCached(&DAT_00855bb0,0,(int)pvVar1);
  CVBuffer__SetStreamSource();
  CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
  iVar2 = CHLCollisionDetector__Unk_004881e0(&DAT_008aa4e8,2,(int)piVar14);
  if (iVar2 != 0) {
    (**(code **)(*DAT_00888a50 + 0x144))();
  }
  RenderState_Set(0x13,5);
  RenderState_Set(0x14,6);
  if (DAT_0089ce50 != 0) {
    RenderState_Set(0xf,1);
  }
  D3DStateCache__SetState114Raw(0,1,1);
  D3DStateCache__SetState114Raw(0,2,1);
  D3DStateCache__SetStateCached(0,1,4);
  puVar7 = auStack_d0;
  puVar9 = &DAT_009c6954;
  for (iVar2 = 0x10; iVar2 != 0; iVar2 = iVar2 + -1) {
    *puVar9 = *puVar7;
    puVar7 = puVar7 + 1;
    puVar9 = puVar9 + 1;
  }
  DAT_009c73e9 = 1;
  puVar7 = auStack_90;
  puVar9 = &DAT_009c6914;
  for (iVar2 = 0x10; iVar2 != 0; iVar2 = iVar2 + -1) {
    *puVar9 = *puVar7;
    puVar7 = puVar7 + 1;
    puVar9 = puVar9 + 1;
  }
  DAT_009c73e8 = 1;
  puVar7 = auStack_50;
  puVar9 = &DAT_009c6994;
  for (iVar2 = 0x10; iVar2 != 0; iVar2 = iVar2 + -1) {
    *puVar9 = *puVar7;
    puVar7 = puVar7 + 1;
    puVar9 = puVar9 + 1;
  }
  DAT_009c73ea = 1;
  CDXCompass__Render();
  iVar2 = CGame__Unk_004725d0(0x8a9a98);
  if (iVar2 == 0) {
    uVar3 = *(int *)((int)this + 0x3c10) + 1U & 0x80000001;
    if ((int)uVar3 < 0) {
      uVar3 = (uVar3 - 1 | 0xfffffffe) + 1;
    }
    *(uint *)((int)this + 0x3c10) = uVar3;
    return;
  }
  *(undefined4 *)((int)this + 0x3c10) = 0;
  return;
}
