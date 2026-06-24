/* address: 0x005088b0 */
/* name: OID__Unk_005088b0 */
/* signature: int __thiscall OID__Unk_005088b0(void * this, void * param_1, int param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __thiscall OID__Unk_005088b0(void *this,void *param_1,int param_2)

{
  float fVar1;
  float fVar2;
  float fVar3;
  int iVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  int extraout_EAX;
  int iVar9;
  int extraout_EAX_00;
  float *extraout_EAX_01;
  undefined4 *puVar10;
  undefined4 *extraout_EAX_02;
  void *pvVar11;
  void *unaff_EDI;
  float10 extraout_ST0;
  float10 extraout_ST0_00;
  float10 extraout_ST0_01;
  float10 fVar12;
  float10 fVar13;
  float10 fVar14;
  float10 fVar15;
  double dVar16;
  int in_stack_fffffe70;
  float local_130;
  float local_128;
  float local_124;
  float local_120;
  float local_11c;
  float local_110;
  float local_10c;
  float local_108;
  float local_100;
  float local_fc;
  float local_f8;
  float local_f0;
  float local_ec;
  float local_e8;
  undefined4 local_e4;
  float local_e0;
  float local_dc;
  float local_d8;
  int local_d0;
  undefined4 local_cc;
  undefined4 local_c8;
  undefined4 local_c4;
  undefined **local_c0;
  undefined4 local_bc;
  undefined4 local_b8;
  undefined4 local_b4;
  undefined4 local_ac;
  undefined4 local_a8;
  undefined4 local_a4;
  undefined4 local_a0;
  float local_9c;
  float local_98;
  float local_94;
  undefined4 local_90;
  undefined1 local_8c [32];
  undefined4 local_6c;
  float local_68;
  undefined4 local_64;
  undefined4 local_60;
  undefined1 local_5c [4];
  float local_58;
  float local_48;
  undefined1 local_1c [16];
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  fVar3 = DAT_006fbdfc;
  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d597b;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  OID__Helper_0044a850(this,(int)&local_110,unaff_EDI);
  if (fVar3 < *(float *)(extraout_EAX + 8)) {
    ExceptionList = local_c;
    return 0;
  }
  if (((*(int *)((int)this + 0xa0) != 0) &&
      (iVar9 = *(int *)(*(int *)((int)this + 0xa0) + 0x18), iVar9 != 0)) &&
     (*(int *)(iVar9 + 0x58) != 0)) {
    pvVar11 = DAT_008a9d7c;
    if (*(int *)(*(int *)((int)this + 8) + 0x138) != 0) {
      pvVar11 = DAT_008a9d80;
    }
    if ((pvVar11 != (void *)0x0) &&
       (iVar9 = OID__Helper_0044c780
                          (pvVar11,*(int *)((int)param_1 + 0x1c),*(float *)((int)param_1 + 0x20),
                           *(float *)((int)param_1 + 0x24),*(float *)((int)param_1 + 0x28)),
       iVar9 == 0)) {
      ExceptionList = local_c;
      return 0;
    }
  }
  fVar3 = *(float *)(*(int *)(*(int *)((int)this + 0xa0) + 0x18) + 0x2c);
  OID__Helper_0044a930(this,(int)local_5c,unaff_EDI);
  local_d8 = fVar3 * *(float *)(extraout_EAX_00 + 0x24);
  local_dc = fVar3 * *(float *)(extraout_EAX_00 + 0x14);
  local_e0 = fVar3 * *(float *)(extraout_EAX_00 + 4);
  OID__Helper_0050a0e0(this,&local_f0,(int)param_1,unaff_EDI);
  OID__Helper_0044a850(this,(int)&local_110,unaff_EDI);
  local_f8 = local_e8 - extraout_EAX_01[2];
  local_fc = local_ec - extraout_EAX_01[1];
  local_100 = local_f0 - *extraout_EAX_01;
  dVar16 = SQRT__Wrapper_004026b0(&local_100);
  if ((float)dVar16 <= _DAT_005d856c) {
    local_128 = 0.0;
  }
  else {
    OID__Helper_0055dcb0();
    local_128 = (float)extraout_ST0;
  }
  if (*(int *)((int)this + 0x98) == 0) {
    dVar16 = SQRT__Wrapper_004026b0(&local_e0);
    if ((float)dVar16 <= _DAT_005d856c) {
      fVar12 = (float10)_DAT_005d856c;
    }
    else {
      OID__Helper_0055dcb0();
      fVar12 = extraout_ST0_00;
    }
    local_128 = (float)((float10)local_128 - fVar12);
    dVar16 = SQRT__Wrapper_004026b0(&local_e0);
    if ((float)dVar16 <= _DAT_005d856c) goto LAB_00508a9d;
    OID__Helper_0055dcb0();
    fVar12 = extraout_ST0_01;
  }
  else {
    local_128 = *(float *)(*(int *)((int)this + 8) + 0xe8);
LAB_00508a9d:
    fVar12 = (float10)_DAT_005d856c;
  }
  iVar9 = *(int *)((int)this + 0xa0);
  iVar4 = *(int *)(iVar9 + 0x18);
  if (((*(float *)(iVar4 + 0x3c) * _DAT_005d8c6c == _DAT_005d856c) || (*(int *)(iVar4 + 0x50) != 0))
     || (*(int *)(iVar4 + 0x6c) != 0)) {
    if (*(int *)(*(int *)(iVar9 + 0x18) + 0x6c) != 0) {
      dVar16 = CStaticShadows__Helper_0047eb80(0x6fadc8,(void *)(*(int *)((int)this + 8) + 0x1c));
      if (dVar16 <= (double)DAT_006fbdfc) {
        ExceptionList = local_c;
        return 0;
      }
      ExceptionList = local_c;
      return 1;
    }
    if (*(int *)((int)this + 0x98) != 0) {
      iVar9 = *(int *)((int)this + 8);
      pvVar11 = *(void **)(iVar9 + 0xe0);
      vector_constructor_iterator_nothrow(local_8c,0x10,3,&LAB_00402d20);
      CSquadNormal__Helper_004062d0(local_8c,pvVar11,0.0,0.0,(float)unaff_EDI);
      CMCBuggy__Helper_0040d320(local_8c,local_5c,(void *)(iVar9 + 0x3c),unaff_EDI);
      fVar13 = (float10)fpatan((float10)local_58,(float10)local_48);
      fVar12 = (float10)fcos(-fVar13);
      fVar13 = (float10)fsin((float10)(float)-fVar13);
      puVar10 = (undefined4 *)Vec3__SetXYZ();
      local_6c = *puVar10;
      fVar3 = (float)puVar10[1];
      local_64 = puVar10[2];
      local_60 = puVar10[3];
      local_68 = fVar3;
      CMonitor__Helper_0047ec60(0x6fadc8,&local_110,(void *)(*(int *)((int)this + 8) + 0x1c));
      local_128 = (local_10c * (local_108 * (float)fVar12 - local_10c * fVar3) -
                  (local_110 * fVar3 - local_108 * (float)-fVar13) * local_110) + local_128;
    }
    iVar9 = *(int *)((int)this + 0xa0);
    if (*(float *)(iVar9 + 0x7c) < local_128) {
      ExceptionList = local_c;
      return 0;
    }
    if (local_128 < *(float *)(iVar9 + 0x80)) {
      ExceptionList = local_c;
      return 0;
    }
    if (*(int *)(*(int *)(iVar9 + 0x18) + 0x48) != 0) {
      ExceptionList = local_c;
      return 1;
    }
    OID__Helper_0044a850(this,(int)local_1c,unaff_EDI);
    local_bc = 0;
    local_b8 = 0;
    local_b4 = 0;
    local_ac = *extraout_EAX_02;
    local_a8 = extraout_EAX_02[1];
    local_a4 = extraout_EAX_02[2];
    local_a0 = extraout_EAX_02[3];
    local_9c = local_f0;
    local_98 = local_ec;
    local_94 = local_e8;
    local_90 = local_e4;
    local_c0 = &PTR_VFuncSlot_00_00426340_005d8bfc;
    local_4 = 0;
    local_d0 = 0;
    local_cc = 0xffffffff;
    local_c8 = 0;
    local_c4 = 0xbf800000;
    CGeneralVolume__ctor_like_004098e0(&stack0xfffffe70,&local_c0,in_stack_fffffe70);
    iVar9 = OID__Helper_0050b030();
    if (iVar9 != 3) {
      ExceptionList = local_c;
      return 0;
    }
    if (local_d0 == 0) {
      ExceptionList = local_c;
      return 0;
    }
    if ((*(byte *)(local_d0 + 0x34) & 0x10) == 0) {
      ExceptionList = local_c;
      return 0;
    }
    if (*(int *)(local_d0 + 0x138) != *(int *)((int)param_1 + 0x138)) {
      ExceptionList = local_c;
      return 0;
    }
    ExceptionList = local_c;
    return 1;
  }
  fVar5 = *(float *)(*(int *)((int)this + 8) + 0x24) - *(float *)((int)param_1 + 0x24);
  fVar7 = *(float *)(*(int *)(iVar9 + 0x18) + 0x2c) * _DAT_005d8584;
  fVar8 = *(float *)(*(int *)(iVar9 + 0x18) + 0x3c) * _DAT_005d8c6c;
  fVar6 = SQRT(local_fc * local_fc + local_100 * local_100);
  fVar3 = (float)(fVar12 + (float10)*(float *)(iVar9 + 0x7c));
  fVar1 = (float)(fVar12 + (float10)*(float *)(iVar9 + 0x80));
  if (((_DAT_005d8dec < fVar3) && (_DAT_005d8dec < fVar1)) ||
     ((fVar3 < _DAT_005d8dec && (fVar1 < _DAT_005d8dec)))) {
    fVar12 = (float10)fsin((float10)fVar3);
    fVar2 = (float)(fVar12 * (float10)fVar7);
    fVar12 = (float10)fVar8 * (float10)fVar5;
    fVar12 = fVar12 + fVar12;
    fVar13 = (float10)fVar2 * (float10)fVar2 + fVar12;
    if (fVar13 == (float10)_DAT_005d856c) {
LAB_00508bdd:
      local_130 = 0.0;
    }
    else {
      fVar14 = (float10)fcos((float10)fVar3);
      fVar13 = fVar14 * (float10)fVar7 * ((SQRT(fVar13) - (float10)fVar2) / (float10)fVar8);
      local_130 = (float)fVar13;
      if (fVar13 < (float10)_DAT_005d856c) goto LAB_00508bdd;
    }
    fVar13 = (float10)fsin((float10)fVar1);
    fVar3 = (float)(fVar13 * (float10)fVar7);
    fVar12 = fVar13 * (float10)fVar7 * (float10)fVar3 + fVar12;
    if (fVar12 == (float10)_DAT_005d856c) {
LAB_00508c2d:
      fVar12 = (float10)_DAT_005d856c;
    }
    else {
      fVar13 = (float10)fcos((float10)fVar1);
      fVar12 = fVar13 * (float10)fVar7 * ((SQRT(fVar12) - (float10)fVar3) / (float10)fVar8);
      if (fVar12 < (float10)_DAT_005d856c) goto LAB_00508c2d;
    }
    if (fVar12 < (float10)local_130) {
      fVar3 = (float)fVar12;
      fVar12 = (float10)local_130;
      local_130 = fVar3;
    }
    goto LAB_00508e06;
  }
  fVar12 = (float10)fsin((float10)fVar3);
  fVar2 = (float)(fVar12 * (float10)fVar7);
  fVar12 = (float10)fVar8 * (float10)fVar5;
  fVar12 = fVar12 + fVar12;
  fVar13 = (float10)fVar2 * (float10)fVar2 + fVar12;
  if (fVar13 <= (float10)_DAT_005d856c) {
LAB_00508cb9:
    local_11c = 0.0;
  }
  else {
    fVar14 = (float10)fcos((float10)fVar3);
    fVar13 = fVar14 * (float10)fVar7 * ((SQRT(fVar13) - (float10)fVar2) / (float10)fVar8);
    local_11c = (float)fVar13;
    if (fVar13 < (float10)_DAT_005d856c) goto LAB_00508cb9;
  }
  fVar13 = (float10)fsin((float10)fVar1);
  fVar13 = fVar13 * (float10)fVar7;
  fVar14 = fVar13 * fVar13 + fVar12;
  if (fVar14 <= (float10)_DAT_005d856c) {
LAB_00508d0d:
    local_120 = 0.0;
  }
  else {
    fVar15 = (float10)fcos((float10)fVar1);
    fVar13 = fVar15 * (float10)fVar7 * ((SQRT(fVar14) - fVar13) / (float10)fVar8);
    local_120 = (float)fVar13;
    if (fVar13 < (float10)_DAT_005d856c) goto LAB_00508d0d;
  }
  fVar13 = (float10)fsin((float10)_DAT_005dfca8);
  local_130 = (float)(fVar13 * (float10)fVar7);
  fVar12 = fVar13 * (float10)fVar7 * (float10)local_130 + fVar12;
  if (fVar12 <= (float10)_DAT_005d856c) {
LAB_00508d69:
    local_124 = 0.0;
  }
  else {
    fVar13 = (float10)fcos((float10)_DAT_005dfca8);
    fVar12 = fVar13 * (float10)fVar7 * ((SQRT(fVar12) - (float10)local_130) / (float10)fVar8);
    local_124 = (float)fVar12;
    if (fVar12 < (float10)_DAT_005d856c) goto LAB_00508d69;
  }
  if (local_11c != _DAT_005d856c) {
    local_130 = local_11c;
  }
  if (local_120 < local_130) {
    local_130 = local_120;
  }
  if ((local_124 < local_130) && (local_124 != _DAT_005d856c)) {
    local_130 = local_124;
  }
  if (local_11c < local_120) {
    local_11c = local_120;
  }
  fVar12 = (float10)local_11c;
  if (fVar12 < (float10)local_124) {
    fVar12 = (float10)local_124;
  }
LAB_00508e06:
  if (((float10)fVar6 <= fVar12) && (local_130 <= fVar6)) {
    ExceptionList = local_c;
    return 1;
  }
  ExceptionList = local_c;
  return 0;
}
