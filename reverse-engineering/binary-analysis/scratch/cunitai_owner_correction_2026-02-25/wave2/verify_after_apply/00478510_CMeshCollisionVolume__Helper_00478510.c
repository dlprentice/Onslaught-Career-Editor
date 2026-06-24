/* address: 0x00478510 */
/* name: CMeshCollisionVolume__Helper_00478510 */
/* signature: int CMeshCollisionVolume__Helper_00478510(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CMeshCollisionVolume__Helper_00478510(void)

{
  float fVar1;
  void *this;
  int iVar2;
  float *extraout_EAX;
  void *this_00;
  void *extraout_EAX_00;
  void *this_01;
  float *extraout_EAX_01;
  void *unaff_EDI;
  float10 extraout_ST0;
  double dVar3;
  double dVar4;
  double dVar5;
  void *in_stack_00000004;
  void *in_stack_00000008;
  void *in_stack_0000000c;
  void *in_stack_00000010;
  float *in_stack_00000014;
  float in_stack_00000018;
  int in_stack_0000001c;
  undefined1 *puVar6;
  void *pvVar7;
  float local_cc;
  float local_c8;
  float local_c4;
  float local_c0;
  undefined4 local_bc;
  float local_b8;
  float local_b4;
  float local_b0;
  float local_ac;
  float local_a8;
  float local_a4;
  float local_a0;
  float local_9c;
  float local_98;
  float local_94;
  float local_90;
  float local_8c;
  undefined1 local_88 [16];
  float local_78;
  undefined1 local_74 [16];
  int local_64;
  undefined1 local_40 [16];
  float local_30;
  float local_2c;
  float local_28;
  float local_20;
  float local_1c;
  float local_18;
  undefined1 local_10 [16];

  local_64 = 0;
  Vec3__SetXYZ();
  Vec3__SetXYZ();
  Vec3__SetXYZ();
  fVar1 = SQRT(local_c8 * local_c8 + local_c4 * local_c4 + local_c0 * local_c0);
  if (fVar1 != _DAT_005d856c) {
    fVar1 = _DAT_005d8568 / fVar1;
    local_c8 = local_c8 * fVar1;
    local_c4 = local_c4 * fVar1;
    local_c0 = local_c0 * fVar1;
  }
  if (_DAT_005d8574 <=
      local_c8 * *in_stack_00000014 +
      local_c0 * in_stack_00000014[2] + local_c4 * in_stack_00000014[1]) {
    return 0;
  }
  Vec3__SetXYZ();
  if (_DAT_005d8574 <= local_30 * local_c8 + local_c0 * local_28 + local_c4 * local_2c) {
    return 0;
  }
  Vec3__SetXYZ();
  Vec3__SetXYZ();
  Vec3__SetXYZ();
  if (local_20 * local_c8 + local_c0 * local_18 + local_c4 * local_1c <= _DAT_005d8570) {
    local_b8 = *in_stack_00000014;
    local_b4 = in_stack_00000014[1];
    local_b0 = in_stack_00000014[2];
    local_ac = in_stack_00000014[3];
    fVar1 = SQRT(local_b4 * local_b4 + local_b0 * local_b0 + local_b8 * local_b8);
    if (fVar1 != _DAT_005d856c) {
      fVar1 = _DAT_005d8568 / fVar1;
      local_b8 = local_b8 * fVar1;
      local_b4 = local_b4 * fVar1;
      local_b0 = local_b0 * fVar1;
    }
    pvVar7 = in_stack_00000004;
    CUnitAI__Unk_004404f0(&local_c8,local_40,in_stack_00000004);
    dVar3 = CGeneralVolume__Unk_0040d180(this_01,pvVar7,unaff_EDI);
    dVar4 = CGeneralVolume__Unk_0040d180(&local_c8,local_88,unaff_EDI);
    dVar5 = CGeneralVolume__Unk_0040d180(&local_c8,&local_b8,unaff_EDI);
    if ((float)dVar5 == _DAT_005d856c) {
      local_cc = -1.0;
    }
    else {
      local_cc = -(((float)dVar4 + (float)dVar3) / (float)dVar5);
    }
    Vec3__SetXYZ();
    Vec3__Add(local_88,local_40,local_74,unaff_EDI);
    local_98 = *extraout_EAX_01;
    local_78 = local_cc * local_cc;
    local_94 = extraout_EAX_01[1];
    local_90 = extraout_EAX_01[2];
    local_8c = extraout_EAX_01[3];
    CUnitAI__Helper_00477ba0();
    if (extraout_ST0 < (float10)local_78) {
      return 0;
    }
  }
  else {
    pvVar7 = in_stack_00000004;
    CUnitAI__Unk_004404f0(&local_c8,local_40,in_stack_00000004);
    dVar3 = CGeneralVolume__Unk_0040d180(this,pvVar7,unaff_EDI);
    dVar4 = CGeneralVolume__Unk_0040d180(&local_c8,local_88,unaff_EDI);
    dVar5 = CGeneralVolume__Unk_0040d180(&local_c8,&local_c8,unaff_EDI);
    if ((float)dVar5 == _DAT_005d856c) {
      local_cc = -1.0;
    }
    else {
      local_cc = -(((float)dVar4 + (float)dVar3) / (float)dVar5);
    }
    Vec3__SetXYZ();
    Vec3__SetXYZ();
    local_98 = local_b8;
    local_94 = local_b4;
    local_90 = local_b0;
    local_8c = local_ac;
  }
  if (ABS(local_cc) < (float)_DAT_005d87d8) {
    local_cc = _DAT_005d856c;
  }
  local_a4 = local_94;
  local_a0 = local_90;
  local_a8 = local_98;
  local_9c = local_8c;
  iVar2 = CUnitAI__Unk_00479020
                    (&local_98,in_stack_00000004,in_stack_00000008,in_stack_0000000c,&local_c8);
  if (iVar2 == 0) {
    CUnitAI__Unk_00479200(local_10,in_stack_00000004,in_stack_00000008,in_stack_0000000c,&local_98);
    local_a8 = *extraout_EAX;
    local_a4 = extraout_EAX[1];
    local_a0 = extraout_EAX[2];
    local_b8 = *in_stack_00000014;
    local_9c = extraout_EAX[3];
    local_b4 = in_stack_00000014[1];
    local_b0 = in_stack_00000014[2];
    local_ac = in_stack_00000014[3];
    CGeneralVolume__Unk_0040d120(&local_a8,local_40,in_stack_00000010,unaff_EDI);
    puVar6 = local_74;
    pvVar7 = in_stack_00000010;
    CGeneralVolume__Unk_0040d120(&local_a8,local_10,&local_b8,puVar6);
    CGeneralVolume__Unk_0040d120(this_00,puVar6,pvVar7,unaff_EDI);
    dVar3 = CUnitAI__Unk_00479630(local_40,local_74,in_stack_00000018);
    local_cc = (float)dVar3;
  }
  CGeneralVolume__Unk_0040d120(&local_a8,local_10,in_stack_00000010,unaff_EDI);
  dVar3 = SQRT__Wrapper_004026b0(extraout_EAX_00);
  if ((double)_DAT_005dae90 <= dVar3 - (double)in_stack_00000018) {
    if (local_cc < (float)_DAT_005dbc68) {
      return 0;
    }
    dVar3 = SQRT__Wrapper_004026b0(in_stack_00000014);
    if (dVar3 < (double)local_cc) {
      return 0;
    }
  }
  else {
    *(undefined4 *)(in_stack_0000001c + 200) = 1;
    local_64 = 1;
  }
  if (((*(int *)(in_stack_0000001c + 0xa8) != 0) &&
      (*(float *)(in_stack_0000001c + 0xc4) <= local_cc)) && (local_64 != 1)) {
    return 0;
  }
  *(float *)(in_stack_0000001c + 0xc4) = local_cc;
  *(undefined4 *)(in_stack_0000001c + 0xa8) = 1;
  *(float *)(in_stack_0000001c + 0x84) = local_a8;
  *(undefined4 *)(in_stack_0000001c + 0x94) = 1;
  *(float *)(in_stack_0000001c + 0x88) = local_a4;
  *(float *)(in_stack_0000001c + 0x8c) = local_a0;
  *(float *)(in_stack_0000001c + 0x90) = local_9c;
  *(float *)(in_stack_0000001c + 0xd4) = local_c8;
  *(float *)(in_stack_0000001c + 0xd8) = local_c4;
  *(float *)(in_stack_0000001c + 0xdc) = local_c0;
  *(undefined4 *)(in_stack_0000001c + 0xe0) = local_bc;
  return 1;
}
