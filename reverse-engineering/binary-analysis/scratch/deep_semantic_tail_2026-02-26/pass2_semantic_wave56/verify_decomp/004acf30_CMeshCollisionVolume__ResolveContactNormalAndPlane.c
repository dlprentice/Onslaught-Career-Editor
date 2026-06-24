/* address: 0x004acf30 */
/* name: CMeshCollisionVolume__ResolveContactNormalAndPlane */
/* signature: int CMeshCollisionVolume__ResolveContactNormalAndPlane(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CMeshCollisionVolume__ResolveContactNormalAndPlane(void)

{
  float *pfVar1;
  float fVar2;
  bool bVar3;
  float *extraout_EAX;
  float *pfVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  void *unaff_EDI;
  double dVar8;
  float *in_stack_00000004;
  float in_stack_00000008;
  float in_stack_0000000c;
  float in_stack_00000010;
  float in_stack_00000014;
  float in_stack_00000018;
  float in_stack_0000001c;
  float in_stack_00000020;
  float in_stack_00000024;
  float *in_stack_0000002c;
  float *in_stack_00000030;
  float local_40;
  float local_3c;
  float local_38;
  float local_24;
  float local_20;
  float local_1c;
  float local_18;
  float local_14;
  float local_10;
  float local_c;
  float local_8;
  float local_4;

  local_40 = in_stack_00000018;
  bVar3 = false;
  fVar2 = SQRT(in_stack_00000018 * in_stack_00000018 +
               in_stack_00000020 * in_stack_00000020 + in_stack_0000001c * in_stack_0000001c);
  local_20 = 0.0;
  local_1c = 0.0;
  local_18 = 0.0;
  local_3c = in_stack_0000001c;
  local_38 = in_stack_00000020;
  if (fVar2 != _DAT_005d856c) {
    fVar2 = _DAT_005d8568 / fVar2;
    local_40 = in_stack_00000018 * fVar2;
    local_3c = in_stack_0000001c * fVar2;
    local_38 = in_stack_00000020 * fVar2;
  }
  if (in_stack_00000004[0x32] == 1.4013e-45) {
    local_20 = in_stack_00000008 - in_stack_00000004[0x21];
    local_1c = in_stack_0000000c - in_stack_00000004[0x22];
    local_18 = in_stack_00000010 - in_stack_00000004[0x23];
    fVar2 = SQRT(local_20 * local_20 + local_1c * local_1c + local_18 * local_18);
    local_40 = local_20;
    local_3c = local_1c;
    local_38 = local_18;
    if (fVar2 != _DAT_005d856c) {
      fVar2 = _DAT_005d8568 / fVar2;
      local_40 = local_20 * fVar2;
      local_3c = local_1c * fVar2;
      local_38 = fVar2 * local_18;
    }
    bVar3 = true;
    Vec3__SetXYZ();
    local_14 = local_24;
  }
  else {
    Vec3__SetXYZ();
    local_24 = in_stack_00000024;
    if ((float)_DAT_005dc678 < in_stack_00000004[(int)in_stack_00000004[0x20] + 0x2b]) {
      Vec3__SetXYZ();
      local_20 = local_10;
      local_1c = local_c;
      local_18 = local_8;
      local_14 = local_4;
    }
  }
  Vec3__SetXYZ();
  *in_stack_0000002c = local_10;
  in_stack_0000002c[1] = local_c;
  in_stack_0000002c[2] = local_8;
  in_stack_0000002c[3] = local_4;
  if (in_stack_00000004[0x33] == 1.4013e-45) {
    *in_stack_00000030 = DAT_00704cb8;
    in_stack_00000030[1] = DAT_00704cbc;
    in_stack_00000030[2] = DAT_00704cc0;
    in_stack_00000030[3] = DAT_00704cc4;
    return 1;
  }
  if (!bVar3) {
    Vec3__SetXYZ();
    Vec3__SetXYZ();
    local_40 = in_stack_00000008;
    local_3c = in_stack_0000000c;
    local_38 = in_stack_00000010;
    local_24 = in_stack_00000014;
  }
  fVar2 = SQRT(local_3c * local_3c + local_38 * local_38 + local_40 * local_40);
  if (fVar2 != _DAT_005d856c) {
    fVar2 = _DAT_005d8568 / fVar2;
    local_40 = fVar2 * local_40;
    local_3c = local_3c * fVar2;
    local_38 = fVar2 * local_38;
  }
  if ((_DAT_005dc674 < in_stack_00000004[0x37]) && (in_stack_00000004[0x37] < _DAT_005d95b4)) {
    Vec3__SetXYZ();
    Vec3__SetXYZ();
    in_stack_00000008 = local_20;
    in_stack_0000000c = local_1c;
    in_stack_00000014 = local_14;
    in_stack_00000010 = local_18;
    if (local_18 <= _DAT_005d856c) {
      local_38 = 0.0;
      fVar2 = SQRT(local_3c * local_3c + local_40 * local_40);
      if (fVar2 != _DAT_005d856c) {
        fVar2 = _DAT_005d8568 / fVar2;
        local_38 = 0.0;
        local_40 = fVar2 * local_40;
        local_3c = local_3c * fVar2;
      }
    }
  }
  pfVar1 = in_stack_00000004 + (int)in_stack_00000004[0x20] * 4 + 2;
  *pfVar1 = local_40;
  pfVar1[1] = local_3c;
  pfVar1[2] = local_38;
  pfVar1[3] = local_24;
  iVar6 = (int)in_stack_00000004[0x20] + 1;
  iVar7 = 0;
  pfVar1 = in_stack_00000004;
  if (0 < iVar6) {
    do {
      Vec3__SetXYZ();
      Vec3__SetXYZ();
      in_stack_00000008 = local_20;
      in_stack_0000000c = local_1c;
      in_stack_00000010 = local_18;
      in_stack_00000014 = local_14;
      iVar5 = 0;
      pfVar4 = in_stack_00000004 + 3;
      do {
        if (((iVar5 != iVar7) &&
            (((pfVar1[2] != pfVar4[-1] || (pfVar1[3] != *pfVar4)) || (pfVar1[4] != pfVar4[1])))) &&
           (local_20 * pfVar4[-1] + local_1c * *pfVar4 + local_18 * pfVar4[1] < _DAT_005d856c))
        break;
        iVar5 = iVar5 + 1;
        pfVar4 = pfVar4 + 4;
      } while (iVar5 < iVar6);
    } while ((iVar5 != iVar6) && (iVar7 = iVar7 + 1, pfVar1 = pfVar1 + 4, iVar7 < iVar6));
  }
  if (iVar7 != iVar6) {
    *in_stack_00000030 = in_stack_00000008;
    in_stack_00000030[1] = in_stack_0000000c;
    in_stack_00000030[2] = in_stack_00000010;
    in_stack_00000030[3] = in_stack_00000014;
    return 1;
  }
  if (iVar6 == 2) {
    Vec3__Cross(in_stack_00000004 + 2,&stack0x00000008,in_stack_00000004 + 6,unaff_EDI);
    SQRT__Wrapper_00406d50(&stack0x00000008);
    dVar8 = CMeshCollisionVolume__Helper_0040d180(&stack0x00000008,&stack0x00000018,unaff_EDI);
    CExplosionInitThing__Helper_0040d150
              (&stack0x00000008,&local_10,(void *)(float)dVar8,(float)unaff_EDI);
    *in_stack_00000030 = *extraout_EAX;
    in_stack_00000030[1] = extraout_EAX[1];
    in_stack_00000030[2] = extraout_EAX[2];
    in_stack_00000030[3] = extraout_EAX[3];
    return 1;
  }
  return 0;
}
