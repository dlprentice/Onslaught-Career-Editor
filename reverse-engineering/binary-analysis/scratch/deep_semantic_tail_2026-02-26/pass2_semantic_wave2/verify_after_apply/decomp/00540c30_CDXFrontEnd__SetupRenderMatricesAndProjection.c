/* address: 0x00540c30 */
/* name: CDXFrontEnd__SetupRenderMatricesAndProjection */
/* signature: void CDXFrontEnd__SetupRenderMatricesAndProjection(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CDXFrontEnd__SetupRenderMatricesAndProjection(void)

{
  int iVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  float in_stack_ffffff44;
  float in_stack_ffffff48;
  float in_stack_ffffff4c;
  float in_stack_ffffff50;
  float fVar4;
  float in_stack_ffffff54;
  float m20;
  float in_stack_ffffff58;
  float m21;
  float in_stack_ffffff5c;
  float in_stack_ffffff60;
  float in_stack_ffffff64;
  float in_stack_ffffff68;
  float m31;
  float in_stack_ffffff6c;
  float m32;
  float in_stack_ffffff70;
  float m33;
  float local_78;
  float local_74;
  float local_60;
  undefined4 local_5c [9];
  undefined4 local_38;
  undefined4 local_34;
  undefined4 local_30;
  undefined4 local_2c;
  undefined4 local_28;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;

  puVar2 = &DAT_008a9788;
  puVar3 = (undefined4 *)&stack0xffffff44;
  for (iVar1 = 0xc; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar3 = *puVar2;
    puVar2 = puVar2 + 1;
    puVar3 = puVar3 + 1;
  }
  CDXEngine__SetWorldMatrixElements
            (&DAT_009c65c0,DAT_008a97b8,DAT_008a97bc,DAT_008a97c0,DAT_008a97c4,in_stack_ffffff44,
             in_stack_ffffff48,in_stack_ffffff4c,in_stack_ffffff50,in_stack_ffffff54,
             in_stack_ffffff58,in_stack_ffffff5c,in_stack_ffffff60,in_stack_ffffff64,
             in_stack_ffffff68,in_stack_ffffff6c,in_stack_ffffff70);
  local_5c[0] = 0;
  CDXEngine__Helper_0044a5f0();
  local_38 = 0;
  local_34 = 0;
  local_30 = 0;
  local_2c = 0;
  CDXEngine__Helper_0044a5f0();
  local_28 = 0;
  local_24 = 0;
  local_20 = 0;
  local_1c = 0;
  local_18 = 0;
  local_14 = 0;
  CDXEngine__Helper_0044a5f0();
  DAT_009c68a8 = 0;
  DAT_009c690c = 1;
  CUnitAI__Unk_004901e0();
  puVar2 = local_5c;
  puVar3 = &DAT_009c65c0;
  for (iVar1 = 0x17; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar3 = *puVar2;
    puVar2 = puVar2 + 1;
    puVar3 = puVar3 + 1;
  }
  DAT_009c68fc = 1;
  DAT_009c68a0 = 1;
  DAT_009c6904 = 1;
  CUnitAI__Unk_004901e0();
  fVar4 = (float)_DAT_005db360;
  local_74 = 200.0;
  puVar2 = local_5c;
  puVar3 = &DAT_009c661c;
  for (iVar1 = 0x17; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar3 = *puVar2;
    puVar2 = puVar2 + 1;
    puVar3 = puVar3 + 1;
  }
  local_78 = 1000.0;
  DAT_009c68fd = 1;
  DAT_009c68a1 = 1;
  DAT_009c6905 = 1;
  if (SQRT(fVar4) != _DAT_005d856c) {
    local_74 = _DAT_005d8568 / SQRT(fVar4);
    local_78 = local_74 * 1000.0;
    local_74 = local_74 * 200.0;
  }
  m32 = 0.24000001;
  m31 = 0.24000001;
  m20 = 0.0;
  m21 = 0.0;
  fVar4 = 7.719427e-39;
  CUnitAI__Unk_004901e0();
  puVar2 = local_5c;
  puVar3 = &DAT_009c6678;
  for (iVar1 = 0x17; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar3 = *puVar2;
    puVar2 = puVar2 + 1;
    puVar3 = puVar3 + 1;
  }
  DAT_009c68fe = 1;
  DAT_009c68a2 = 1;
  DAT_009c6906 = 1;
  DAT_009c68ad = 1;
  DAT_009c6910 = 1;
  CParticleManager__InterpolatePositions();
  m33 = 7.719519e-39;
  CParticleManager__Unk_004cbc60();
  puVar2 = &DAT_008a9788;
  puVar3 = (undefined4 *)&stack0xffffff44;
  for (iVar1 = 0xc; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar3 = *puVar2;
    puVar2 = puVar2 + 1;
    puVar3 = puVar3 + 1;
  }
  CDXEngine__SetWorldMatrixElements
            (&DAT_009c65c0,DAT_008a97b8,DAT_008a97bc,DAT_008a97c0,DAT_008a97c4,in_stack_ffffff44,
             in_stack_ffffff48,in_stack_ffffff4c,fVar4,m20,m21,local_78,local_74,local_60,m31,m32,
             m33);
  (**(code **)(*DAT_00888a50 + 0xc4))();
  DAT_009c68ad = 0;
  DAT_009c6910 = 1;
  RenderState_Set(0xf,0);
  CDXEngine__Unk_0054f7e0(0x9c63e8);
  RenderState_Set(0xf,1);
  return;
}
