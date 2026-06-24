/* address: 0x00542a50 */
/* name: CDXEngine__BuildDirectionalSampleRing */
/* signature: void __cdecl CDXEngine__BuildDirectionalSampleRing(float param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl CDXEngine__BuildDirectionalSampleRing(float param_1)

{
  void *pvVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  undefined4 *extraout_EAX;
  int iVar4;
  undefined4 *puVar5;
  float *pfVar6;
  int *piVar7;
  void *unaff_EDI;
  float10 fVar8;
  int local_108;
  float local_fc;
  float local_f8;
  float local_f4;
  float local_f0;
  undefined1 local_ec [16];
  undefined4 local_dc;
  undefined4 local_d8;
  undefined4 local_d4;
  undefined4 local_d0;
  undefined4 local_cc;
  undefined4 local_c8;
  undefined4 local_c4;
  undefined4 local_c0;
  undefined4 local_bc [4];
  undefined4 local_ac;
  undefined4 local_a8;
  undefined4 local_a4;
  undefined4 local_a0;
  undefined4 local_9c;
  undefined4 local_98;
  undefined4 local_94;
  undefined4 local_90;
  undefined4 local_7c [5];
  undefined1 local_68 [16];
  undefined4 local_58;
  undefined4 local_54;
  undefined4 local_50;
  undefined4 local_4c;
  undefined4 local_48;
  undefined4 local_44;
  undefined4 local_40;
  undefined4 local_3c;
  undefined4 local_38;
  undefined4 local_34;
  undefined1 local_20 [32];

  fVar8 = (float10)fcos((float10)param_1);
  _DAT_0067a680 = param_1;
  local_fc = (float)fVar8;
  fVar8 = (float10)fsin((float10)param_1);
  local_f8 = (float)-fVar8;
  puVar2 = (undefined4 *)Vec3__SetXYZ();
  local_dc = *puVar2;
  local_d8 = puVar2[1];
  local_d4 = puVar2[2];
  local_d0 = puVar2[3];
  puVar2 = (undefined4 *)Vec3__SetXYZ();
  _DAT_00650890 = *puVar2;
  local_108 = 0;
  _DAT_006508a0 = puVar2[1];
  _DAT_006508b0 = puVar2[2];
  local_c0 = puVar2[3];
  DAT_00650888 = local_fc;
  DAT_0065088c = local_dc;
  _DAT_00650898 = local_f8;
  _DAT_0065089c = local_d8;
  _DAT_006508a8 = 0;
  _DAT_006508ac = local_d4;
  _DAT_006508b4 = 0;
  _DAT_006508a4 = 0;
  _DAT_00650894 = 0;
  _DAT_006508b8 = 0;
  _DAT_006508bc = 0;
  _DAT_006508c0 = 0;
  _DAT_006508c4 = 0x3f800000;
  puVar2 = &DAT_008aa790;
  local_cc = _DAT_00650890;
  local_c8 = _DAT_006508a0;
  local_c4 = _DAT_006508b0;
  do {
    fVar8 = (float10)local_108 * (float10)_DAT_005d85e4 + (float10)_DAT_0067a680;
    fsin(fVar8);
    fcos(fVar8);
    puVar3 = (undefined4 *)Vec3__SetXYZ();
    local_bc[0] = *puVar3;
    local_bc[1] = puVar3[1];
    local_bc[2] = puVar3[2];
    local_bc[3] = puVar3[3];
    puVar3 = (undefined4 *)Vec3__SetXYZ();
    local_ac = *puVar3;
    local_a8 = puVar3[1];
    local_a4 = puVar3[2];
    local_a0 = puVar3[3];
    puVar3 = (undefined4 *)Vec3__SetXYZ();
    local_9c = *puVar3;
    puVar5 = puVar2 + 0xc;
    local_98 = puVar3[1];
    local_94 = puVar3[2];
    local_90 = puVar3[3];
    local_108 = local_108 + 1;
    puVar3 = local_bc;
    for (iVar4 = 0xc; iVar4 != 0; iVar4 = iVar4 + -1) {
      *puVar2 = *puVar3;
      puVar3 = puVar3 + 1;
      puVar2 = puVar2 + 1;
    }
    puVar2 = puVar5;
  } while ((int)puVar5 < 0x8aa850);
  Vec3__SetXYZ();
  DAT_008aa864 = local_f8;
  DAT_008aa860 = local_fc;
  DAT_008aa868 = local_f4;
  DAT_008aa86c = local_f0;
  Vec3__SetXYZ();
  DAT_008aa850 = local_fc;
  DAT_008aa858 = local_f4;
  DAT_008aa854 = local_f8;
  DAT_008aa85c = local_f0;
  local_7c[0] = 0;
  CDXEngine__Helper_0044a5f0();
  local_58 = 0;
  local_54 = 0;
  local_50 = 0;
  local_4c = 0;
  CDXEngine__Helper_0044a5f0();
  local_48 = 0;
  local_44 = 0;
  local_40 = 0;
  local_3c = 0;
  local_38 = 0;
  local_34 = 0;
  CDXEngine__Helper_0044a5f0();
  puVar2 = &DAT_009c65c0;
  puVar3 = local_7c;
  for (iVar4 = 0x17; iVar4 != 0; iVar4 = iVar4 + -1) {
    *puVar3 = *puVar2;
    puVar2 = puVar2 + 1;
    puVar3 = puVar3 + 1;
  }
  CThing__Helper_004404f0(local_68,local_20,unaff_EDI);
  _DAT_008aa780 = *extraout_EAX;
  _DAT_008aa784 = extraout_EAX[1];
  _DAT_008aa788 = extraout_EAX[2];
  _DAT_008aa78c = extraout_EAX[3];
  SQRT__Wrapper_00406d50(&DAT_008aa780);
  local_108 = 0;
  piVar7 = &DAT_008aa770;
  pfVar6 = (float *)&DAT_008aa730;
  do {
    pvVar1 = (void *)((float)local_108 * _DAT_005d85e4 + _DAT_0067a680);
    vector_constructor_iterator_nothrow(local_bc,0x10,3,&LAB_00402d20);
    CDXEngine__BuildZRotationMatrix(local_bc,pvVar1,(float)unaff_EDI);
    puVar2 = (undefined4 *)CMCBuggy__InvertMatrix(local_ec);
    puVar3 = local_bc;
    for (iVar4 = 0xc; iVar4 != 0; iVar4 = iVar4 + -1) {
      *puVar3 = *puVar2;
      puVar2 = puVar2 + 1;
      puVar3 = puVar3 + 1;
    }
    CSquadNormal__Helper_0040d2c0(local_bc,&local_fc,&DAT_008aa780,unaff_EDI);
    *pfVar6 = local_fc;
    pfVar6[1] = local_f8;
    pfVar6[2] = local_f4;
    pfVar6[3] = local_f0;
    iVar4 = CDXEngine__Helper_004b52c0(&local_fc,1.0);
    *piVar7 = iVar4;
    pfVar6 = pfVar6 + 4;
    local_108 = local_108 + 1;
    piVar7 = piVar7 + 1;
  } while ((int)pfVar6 < 0x8aa770);
  _DAT_008aa8b0 = 0xffffffff;
  return;
}
