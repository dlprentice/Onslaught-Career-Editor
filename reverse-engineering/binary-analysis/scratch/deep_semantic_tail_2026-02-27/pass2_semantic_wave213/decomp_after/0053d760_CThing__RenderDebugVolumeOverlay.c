/* address: 0x0053d760 */
/* name: CThing__RenderDebugVolumeOverlay */
/* signature: void __stdcall CThing__RenderDebugVolumeOverlay(void * param_1, void * param_2, void * param_3, void * param_4) */


void CThing__RenderDebugVolumeOverlay(void *param_1,void *param_2,void *param_3,void *param_4)

{
  int iVar1;
  undefined1 *extraout_EAX;
  float *extraout_EAX_00;
  float *pfVar2;
  void *this;
  void *extraout_EAX_01;
  undefined1 *extraout_EAX_02;
  float *extraout_EAX_03;
  void *this_00;
  void *extraout_EAX_04;
  void *pvVar3;
  undefined4 uVar4;
  uint uVar5;
  undefined1 *puVar6;
  void *unaff_EDI;
  float in_stack_00000020;
  float in_stack_00000030;
  undefined4 in_stack_00000040;
  undefined1 *puVar7;
  undefined1 *puVar8;
  int local_218;
  undefined4 *local_214;
  float local_210;
  float local_20c;
  float local_208;
  undefined1 local_200 [16];
  undefined1 local_1f0 [16];
  undefined4 local_1e0;
  float local_1dc;
  float local_1d8;
  float local_1d4;
  void *local_1c4;
  undefined4 local_1c0;
  undefined4 local_1bc;
  undefined2 local_1b8;
  undefined2 local_1b6;
  undefined2 local_1b4;
  undefined2 local_1b2;
  undefined2 local_1b0;
  undefined2 local_1ae;
  undefined2 local_1ac;
  undefined2 local_1aa;
  undefined2 local_1a8;
  undefined2 local_1a6;
  undefined2 local_1a4;
  undefined2 local_1a2;
  undefined4 local_1a0 [4];
  float local_190;
  float local_18c;
  float local_188;
  float local_180;
  float local_17c;
  float local_178;
  float local_160;
  float local_15c;
  float local_158;
  float local_150;
  float local_14c;
  float local_148;
  undefined1 local_80 [16];
  undefined1 local_70 [16];
  undefined1 local_60 [16];
  undefined1 local_50 [16];
  undefined1 local_40 [16];
  undefined1 local_30 [16];
  undefined1 local_20 [16];
  undefined1 local_10 [16];

  RenderState_Set(0x1b,1);
  RenderState_Set(0x13,2);
  RenderState_Set(0x14,1);
  CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
  local_1e0 = 0;
  local_208 = *(float *)param_2;
  local_210 = (float)param_4 * local_208;
  local_20c = in_stack_00000020 * local_208;
  local_208 = in_stack_00000030 * local_208;
  Vec3__SetXYZ();
  Vec3__SetXYZ();
  iVar1 = CVBufTexture__GetOrCreate(in_stack_00000040,0);
  CVBufTexture__SetVBFormat(0x152,0x208,0x24,4,0);
  CVBufTexture__SetIBFormat(0x65,0x208,2,0);
  local_218 = 0;
  do {
    local_214 = local_1a0;
    uVar5 = 0;
    do {
      switch(local_218) {
      case 0:
        if ((uVar5 & 2) == 0) {
          Vec3__SetXYZ();
        }
        if ((uVar5 & 1) == 0) {
          Vec3__SetXYZ();
        }
        Vec3__SetXYZ();
        Vec3__SetXYZ();
        local_1dc = local_190;
        local_1d8 = local_18c;
        local_1d4 = local_188;
        break;
      case 1:
        if ((uVar5 & 2) == 0) {
          Vec3__SetXYZ();
        }
        if ((uVar5 & 1) == 0) {
          Vec3__SetXYZ();
        }
        Vec3__SetXYZ();
        Vec3__SetXYZ();
        Vec3__SetXYZ();
        local_1dc = local_160;
        local_1d8 = local_15c;
        local_1d4 = local_158;
        break;
      case 2:
        if ((uVar5 & 2) == 0) {
          Vec3__SetXYZ();
        }
        if ((uVar5 & 1) == 0) {
          Vec3__SetXYZ();
        }
        Vec3__SetXYZ();
        Vec3__SetXYZ();
        local_1dc = local_180;
        local_1d8 = local_17c;
        local_1d4 = local_178;
        break;
      case 3:
        if ((uVar5 & 2) == 0) {
          Vec3__SetXYZ();
        }
        if ((uVar5 & 1) == 0) {
          Vec3__SetXYZ();
        }
        Vec3__SetXYZ();
        Vec3__SetXYZ();
        local_1dc = local_150;
        local_1d8 = local_14c;
        local_1d4 = local_148;
        break;
      case 4:
        if ((uVar5 & 2) == 0) {
          CThing__Helper_004404f0(local_200,local_10,unaff_EDI);
          puVar6 = extraout_EAX;
        }
        else {
          puVar6 = local_200;
        }
        if ((uVar5 & 1) == 0) {
          CThing__Helper_004404f0(&local_210,local_30,unaff_EDI);
          pfVar2 = extraout_EAX_00;
        }
        else {
          pfVar2 = &local_210;
        }
        puVar8 = local_1f0;
        puVar7 = local_80;
        Vec3__Add(pfVar2,local_60,puVar6,puVar7);
        Vec3__Add(this,puVar7,puVar8,unaff_EDI);
        pvVar3 = extraout_EAX_01;
        goto LAB_0053ddaf;
      case 5:
        if ((uVar5 & 2) == 0) {
          CThing__Helper_004404f0(local_200,local_20,unaff_EDI);
          puVar6 = extraout_EAX_02;
        }
        else {
          puVar6 = local_200;
        }
        if ((uVar5 & 1) == 0) {
          CThing__Helper_004404f0(&local_210,local_40,unaff_EDI);
          pfVar2 = extraout_EAX_03;
        }
        else {
          pfVar2 = &local_210;
        }
        puVar8 = local_1f0;
        puVar7 = local_70;
        Vec3__Add(pfVar2,local_50,puVar6,puVar7);
        Vec3__SubtractToOut(this_00,puVar7,puVar8,unaff_EDI);
        pvVar3 = extraout_EAX_04;
LAB_0053ddaf:
        Vec3__CopyXYZ(&local_1dc,pvVar3,unaff_EDI);
      }
      local_1c0 = 0x3f800000;
      local_1dc = local_1dc + *(float *)param_3;
      local_1d8 = local_1d8 + *(float *)((int)param_3 + 4);
      local_1d4 = local_1d4 + *(float *)((int)param_3 + 8);
      if ((uVar5 & 1) == 0) {
        local_1c0 = 0;
      }
      local_1bc = 0;
      if ((uVar5 & 2) == 0) {
        local_1bc = 0x3f800000;
      }
      if (local_218 == 2) {
        local_1c4 = (void *)0xffffffff;
      }
      else {
        local_1c4 = param_1;
      }
      uVar4 = CVBufTexture__AddVertices(&local_1dc,1);
      uVar5 = uVar5 + 1;
      *local_214 = uVar4;
      local_214 = local_214 + 1;
    } while ((int)uVar5 < 4);
    local_1b6 = (undefined2)local_1a0[3];
    local_1b8 = (undefined2)local_1a0[0];
    local_1b4 = (undefined2)local_1a0[2];
    local_1b0 = (undefined2)local_1a0[1];
    local_1b2 = local_1b8;
    local_1ae = local_1b6;
    local_1ac = local_1b8;
    local_1aa = local_1b4;
    local_1a8 = local_1b6;
    local_1a6 = local_1b8;
    local_1a4 = local_1b6;
    local_1a2 = local_1b0;
    CVBufTexture__AddIndices(&local_1b8,0xc);
    local_218 = local_218 + 1;
    if (5 < local_218) {
      CVBufTexture__Render(1);
      if (iVar1 != 0) {
        CDXEngine__DecrementResourceRefCount(iVar1);
      }
      RenderState_Set(0x13,5);
      RenderState_Set(0x14,6);
      CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
      return;
    }
  } while( true );
}
