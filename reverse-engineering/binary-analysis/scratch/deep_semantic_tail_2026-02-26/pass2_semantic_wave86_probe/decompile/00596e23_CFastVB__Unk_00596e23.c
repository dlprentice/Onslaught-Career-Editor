/* address: 0x00596e23 */
/* name: CFastVB__Unk_00596e23 */
/* signature: int __stdcall CFastVB__Unk_00596e23(void * param_1, float param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int CFastVB__Unk_00596e23(void *param_1,float param_2)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  int in_EAX;
  float *pfVar5;
  uint uVar6;
  uint uVar7;
  ushort uVar8;
  int iVar9;
  ushort uVar10;
  int iVar11;
  undefined2 in_FPUControlWord;
  undefined2 uVar12;
  float local_2d8 [64];
  float local_1d8;
  float local_1d4;
  undefined1 local_1d0 [4];
  undefined1 local_1cc [4];
  undefined1 local_1c8 [4];
  undefined1 local_1c4 [20];
  undefined1 local_1b0 [4];
  undefined1 local_1ac [4];
  undefined1 local_1a8 [4];
  undefined1 local_1a4 [4];
  undefined1 local_1a0 [4];
  undefined1 local_19c [4];
  undefined1 local_198 [4];
  float local_194;
  undefined1 local_190 [4];
  undefined1 local_18c [4];
  undefined1 local_188 [4];
  undefined1 local_184 [172];
  int local_d8;
  float local_d4;
  float local_d0;
  float local_cc;
  undefined1 *local_c4;
  undefined1 *local_c0;
  undefined1 *local_bc;
  undefined1 *local_b8;
  undefined1 *local_b4;
  undefined1 *local_b0;
  int local_ac;
  undefined1 *local_a8;
  undefined1 *local_a4;
  float local_a0 [4];
  float local_90;
  float local_8c;
  float local_88;
  float local_84;
  float local_80;
  float local_7c;
  float local_78;
  float local_74;
  float local_70;
  float local_6c;
  float local_68;
  float local_64;
  undefined1 *local_60;
  undefined1 *local_5c;
  undefined1 *local_58;
  undefined1 *local_54;
  float local_50;
  float local_4c;
  float local_48;
  float fStack_44;
  float local_40;
  float local_3c;
  float local_38;
  undefined *local_30;
  undefined1 *local_2c;
  undefined1 *local_28;
  float local_24;
  float local_20;
  float local_1c;
  float fStack_18;
  int local_14;
  float *local_10;
  uint local_c;
  float local_8;

  if (param_2 == 0.0) {
    local_14 = 4;
  }
  else {
    iVar9 = 0;
    pfVar5 = (float *)(in_EAX + 0xc);
    iVar11 = 0x10;
    do {
      if (*pfVar5 < _DAT_005e72d4) {
        iVar9 = iVar9 + 1;
      }
      pfVar5 = pfVar5 + 4;
      iVar11 = iVar11 + -1;
    } while (iVar11 != 0);
    if (iVar9 == 0x10) {
      *(undefined2 *)((int)param_1 + 2) = 0xffff;
      *(undefined4 *)((int)param_1 + 4) = 0xffffffff;
      *(undefined2 *)param_1 = 0;
      return 0;
    }
    local_14 = 4 - (uint)(iVar9 != 0);
  }
  pfVar5 = &local_1d8;
  for (iVar11 = 0x40; iVar11 != 0; iVar11 = iVar11 + -1) {
    *pfVar5 = 0.0;
    pfVar5 = pfVar5 + 1;
  }
  local_10 = (float *)CONCAT22(local_10._2_2_,in_FPUControlWord);
  local_58 = local_1d0 + -in_EAX;
  local_b8 = local_1cc + -in_EAX;
  local_b4 = local_1c8 + -in_EAX;
  local_5c = local_1b0 + -in_EAX;
  local_b0 = local_1ac + -in_EAX;
  local_bc = local_1a8 + -in_EAX;
  local_28 = local_1a0 + -in_EAX;
  local_c4 = local_19c + -in_EAX;
  local_c0 = local_198 + -in_EAX;
  local_2c = local_190 + -in_EAX;
  local_a8 = local_18c + -in_EAX;
  param_2 = 0.0;
  _DAT_009d241c = local_10;
  local_a4 = local_188 + -in_EAX;
  pfVar5 = (float *)(in_EAX + 8);
  local_ac = (int)&local_1d8 - in_EAX;
  uVar6 = 0;
  do {
    local_24 = *(float *)((int)&local_1d8 + uVar6) + pfVar5[-2];
    fVar1 = pfVar5[-1];
    fVar2 = *(float *)(local_1d0 + (uVar6 - 4));
    local_20 = fVar1 + fVar2;
    local_1c = *(float *)(local_ac + (int)pfVar5) + *pfVar5;
    local_d8 = (int)ROUND(local_24 * _DAT_005e9f00 + _DAT_005e72d4);
    local_30 = (undefined *)((float)local_d8 * _DAT_005e9efc);
    *(undefined **)((int)local_2d8 + uVar6) = local_30;
    local_60 = (undefined1 *)(int)ROUND((fVar1 + fVar2) * _DAT_005e9ef8 + _DAT_005e72d4);
    local_8 = (float)(int)local_60 * _DAT_005e9ef4;
    *(float *)((int)local_2d8 + uVar6 + 4) = local_8;
    local_54 = (undefined1 *)(int)ROUND(local_1c * _DAT_005e9f00 + _DAT_005e72d4);
    fVar1 = (float)(int)local_54 * _DAT_005e9efc;
    local_c = (uint)param_2 & 3;
    *(float *)(((int)local_2d8 - in_EAX) + (int)pfVar5) = fVar1;
    *(undefined4 *)((int)local_2d8 + (4 - in_EAX) + (int)pfVar5) = 0x3f800000;
    fVar4 = local_24 - (float)local_30;
    fVar3 = local_20 - local_8;
    local_3c = fVar3;
    fVar2 = local_1c - fVar1;
    local_38 = fVar2;
    if (((uint)param_2 & 3) != 3) {
      *(float *)(local_58 + (int)pfVar5) =
           fVar4 * _DAT_005ef0a0 + *(float *)(local_58 + (int)pfVar5);
      *(float *)(local_b8 + (int)pfVar5) =
           fVar3 * _DAT_005ef0a0 + *(float *)(local_b8 + (int)pfVar5);
      *(float *)(local_b4 + (int)pfVar5) =
           fVar2 * _DAT_005ef0a0 + *(float *)(local_b4 + (int)pfVar5);
    }
    if (uVar6 < 0xc0) {
      if (local_c != 0) {
        *(float *)(local_5c + (int)pfVar5) =
             fVar4 * _DAT_005ef09c + *(float *)(local_5c + (int)pfVar5);
        *(float *)(local_b0 + (int)pfVar5) =
             fVar3 * _DAT_005ef09c + *(float *)(local_b0 + (int)pfVar5);
        *(float *)(local_bc + (int)pfVar5) =
             fVar2 * _DAT_005ef09c + *(float *)(local_bc + (int)pfVar5);
      }
      *(float *)(local_28 + (int)pfVar5) =
           fVar4 * _DAT_005ef098 + *(float *)(local_28 + (int)pfVar5);
      *(float *)(local_c4 + (int)pfVar5) =
           fVar3 * _DAT_005ef098 + *(float *)(local_c4 + (int)pfVar5);
      *(float *)(local_c0 + (int)pfVar5) =
           fVar2 * _DAT_005ef098 + *(float *)(local_c0 + (int)pfVar5);
      if (local_c != 3) {
        *(float *)(local_2c + (int)pfVar5) =
             fVar4 * _DAT_005ef094 + *(float *)(local_2c + (int)pfVar5);
        *(float *)(local_a8 + (int)pfVar5) =
             fVar3 * _DAT_005ef094 + *(float *)(local_a8 + (int)pfVar5);
        *(float *)(local_a4 + (int)pfVar5) =
             fVar2 * _DAT_005ef094 + *(float *)(local_a4 + (int)pfVar5);
      }
    }
    param_2 = (float)((int)param_2 + 1);
    uVar7 = uVar6 + 0x10;
    *(float *)((int)local_2d8 + uVar6) = (float)local_30 * DAT_00659ca0;
    *(float *)((int)local_2d8 + uVar6 + 4) = local_8 * DAT_00659ca4;
    *(float *)(((int)local_2d8 - in_EAX) + (int)pfVar5) = fVar1 * DAT_00659ca8;
    pfVar5 = pfVar5 + 4;
    uVar6 = uVar7;
  } while (uVar7 < 0x100);
  param_2._0_2_ = SUB42(local_10,0);
  CFastVB__SolveVectorEndpointPairFromSamples(&local_50,&local_24,(float)local_2d8,local_14);
  local_d4 = local_50 * _DAT_00659cb0;
  local_d0 = local_4c * _DAT_00659cb4;
  local_cc = local_48 * _DAT_00659cb8;
  local_40 = local_24 * _DAT_00659cb0;
  local_3c = local_20 * _DAT_00659cb4;
  local_38 = local_1c * _DAT_00659cb8;
  uVar6 = CFastVB__Helper_00596480(&local_d4);
  local_28 = (undefined1 *)uVar6;
  uVar7 = CFastVB__Helper_00596480(&local_40);
  uVar8 = (ushort)uVar6;
  uVar10 = (ushort)uVar7;
  if ((local_14 == 4) && (uVar8 == uVar10)) {
    *(undefined4 *)((int)param_1 + 4) = 0;
    *(ushort *)param_1 = uVar8;
    *(ushort *)((int)param_1 + 2) = uVar10;
  }
  else {
    local_2c = (undefined1 *)uVar7;
    CDXTexture__Unk_00596386(uVar6);
    uVar12 = param_2._0_2_;
    CDXTexture__Unk_00596386(uVar7);
    local_50 = local_d4 * DAT_00659ca0;
    local_4c = local_d0 * DAT_00659ca4;
    local_48 = local_cc * DAT_00659ca8;
    local_24 = local_40 * DAT_00659ca0;
    local_20 = local_3c * DAT_00659ca4;
    local_1c = local_38 * DAT_00659ca8;
    if ((local_14 == 3) == uVar8 <= uVar10) {
      *(ushort *)param_1 = uVar8;
      *(ushort *)((int)param_1 + 2) = uVar10;
      local_a0[0] = local_50;
      local_a0[1] = local_4c;
      local_a0[2] = local_48;
      local_a0[3] = fStack_44;
      pfVar5 = &local_24;
    }
    else {
      *(ushort *)((int)param_1 + 2) = uVar8;
      *(ushort *)param_1 = uVar10;
      local_a0[0] = local_24;
      local_a0[1] = local_20;
      local_a0[2] = local_1c;
      local_a0[3] = fStack_18;
      pfVar5 = &local_50;
    }
    local_90 = *pfVar5;
    local_8c = pfVar5[1];
    local_88 = pfVar5[2];
    local_84 = pfVar5[3];
    fVar1 = *pfVar5 - local_a0[0];
    if (local_14 == 3) {
      local_30 = &DAT_005ef088;
      local_80 = _DAT_005e72d4 * fVar1 + local_a0[0];
      local_7c = (local_8c - local_a0[1]) * _DAT_005e72d4 + local_a0[1];
      local_78 = (local_88 - local_a0[2]) * _DAT_005e72d4 + local_a0[2];
      local_74 = (local_84 - local_a0[3]) * _DAT_005e72d4 + local_a0[3];
    }
    else {
      local_30 = &DAT_005ef078;
      local_80 = _DAT_005e9f2c * fVar1 + local_a0[0];
      local_7c = _DAT_005e9f2c * (local_8c - local_a0[1]) + local_a0[1];
      local_78 = _DAT_005e9f2c * (local_88 - local_a0[2]) + local_a0[2];
      local_74 = _DAT_005e9f2c * (local_84 - local_a0[3]) + local_a0[3];
      local_70 = fVar1 * _DAT_005ef074 + local_a0[0];
      local_6c = (local_8c - local_a0[1]) * _DAT_005ef074 + local_a0[1];
      local_68 = (local_88 - local_a0[2]) * _DAT_005ef074 + local_a0[2];
      local_64 = (local_84 - local_a0[3]) * _DAT_005ef074 + local_a0[3];
    }
    param_2 = local_88 - local_a0[2];
    fVar2 = local_8c - local_a0[1];
    local_8 = (float)(local_14 + -1);
    if (local_14 + -1 < 0) {
      local_8 = local_8 + _DAT_005e72d8;
    }
    if ((short)local_28 == (short)local_2c) {
      fVar3 = 0.0;
    }
    else {
      fVar3 = local_8 / (fVar1 * fVar1 + fVar2 * fVar2 + param_2 * param_2);
    }
    local_24 = fVar1 * fVar3;
    uVar6 = 0;
    pfVar5 = &local_1d8;
    for (iVar11 = 0x40; iVar11 != 0; iVar11 = iVar11 + -1) {
      *pfVar5 = 0.0;
      pfVar5 = pfVar5 + 1;
    }
    local_20 = fVar3 * fVar2;
    local_1c = fVar3 * param_2;
    local_c = CONCAT22(local_c._2_2_,uVar12);
    _DAT_009d241c = local_c;
    local_10 = &local_1d8;
    local_2c = local_1d0 + (-4 - in_EAX);
    local_58 = local_1c4 + -in_EAX;
    local_54 = local_1a4 + -in_EAX;
    iVar11 = (int)local_2d8 + (8 - in_EAX);
    param_2 = 0.0;
    pfVar5 = (float *)(in_EAX + 4);
    local_60 = local_184 + -in_EAX;
    do {
      if ((local_14 != 3) || (_DAT_005e72d4 <= pfVar5[2])) {
        local_50 = DAT_00659ca0 * pfVar5[-1] + *local_10;
        local_4c = DAT_00659ca4 * *pfVar5 + *(float *)((int)pfVar5 + local_ac);
        local_48 = DAT_00659ca8 * pfVar5[1] + *(float *)(local_2c + (int)pfVar5);
        fVar1 = (local_4c - local_a0[1]) * local_20 +
                (local_48 - local_a0[2]) * local_1c + (local_50 - local_a0[0]) * local_24;
        if (fVar1 < DAT_005e6a3c == (fVar1 == DAT_005e6a3c)) {
          if (fVar1 < local_8) {
            local_28 = (undefined1 *)(fVar1 + _DAT_005e72d4);
            local_5c = (undefined1 *)(int)ROUND(fVar1 + _DAT_005e72d4);
            iVar9 = *(int *)(local_30 + (int)local_5c * 4);
          }
          else {
            iVar9 = 1;
          }
        }
        else {
          iVar9 = 0;
        }
        uVar6 = uVar6 >> 2 | iVar9 << 0x1e;
        fVar2 = (local_50 - local_a0[iVar9 * 4]) * *(float *)(iVar11 + (int)pfVar5);
        uVar7 = (uint)param_2 & 3;
        fVar3 = (local_4c - local_a0[iVar9 * 4 + 1]) * *(float *)(iVar11 + (int)pfVar5);
        local_3c = fVar3;
        fVar1 = (local_48 - local_a0[iVar9 * 4 + 2]) * *(float *)(iVar11 + (int)pfVar5);
        local_38 = fVar1;
        if (uVar7 != 3) {
          *(float *)(local_b8 + (int)pfVar5) =
               fVar2 * _DAT_005ef0a0 + *(float *)(local_b8 + (int)pfVar5);
          *(float *)(local_b4 + (int)pfVar5) =
               _DAT_005ef0a0 * fVar3 + *(float *)(local_b4 + (int)pfVar5);
          *(float *)(local_58 + (int)pfVar5) =
               fVar1 * _DAT_005ef0a0 + *(float *)(local_58 + (int)pfVar5);
        }
        if ((uint)param_2 < 0xc) {
          if (uVar7 != 0) {
            *(float *)(local_b0 + (int)pfVar5) =
                 fVar2 * _DAT_005ef09c + *(float *)(local_b0 + (int)pfVar5);
            *(float *)(local_bc + (int)pfVar5) =
                 _DAT_005ef09c * fVar3 + *(float *)(local_bc + (int)pfVar5);
            *(float *)(local_54 + (int)pfVar5) =
                 fVar1 * _DAT_005ef09c + *(float *)(local_54 + (int)pfVar5);
          }
          *(float *)(local_c4 + (int)pfVar5) =
               fVar2 * _DAT_005ef098 + *(float *)(local_c4 + (int)pfVar5);
          *(float *)(local_c0 + (int)pfVar5) =
               fVar3 * _DAT_005ef098 + *(float *)(local_c0 + (int)pfVar5);
          *(float *)(((int)&local_194 - in_EAX) + (int)pfVar5) =
               fVar1 * _DAT_005ef098 + *(float *)(((int)&local_194 - in_EAX) + (int)pfVar5);
          if (uVar7 != 3) {
            *(float *)(local_a8 + (int)pfVar5) =
                 fVar2 * _DAT_005ef094 + *(float *)(local_a8 + (int)pfVar5);
            *(float *)(local_a4 + (int)pfVar5) =
                 local_3c * _DAT_005ef094 + *(float *)(local_a4 + (int)pfVar5);
            *(float *)(local_60 + (int)pfVar5) =
                 local_38 * _DAT_005ef094 + *(float *)(local_60 + (int)pfVar5);
          }
        }
      }
      else {
        uVar6 = uVar6 >> 2 | 0xc0000000;
      }
      param_2 = (float)((int)param_2 + 1);
      local_10 = local_10 + 4;
      pfVar5 = pfVar5 + 4;
    } while ((uint)param_2 < 0x10);
    *(uint *)((int)param_1 + 4) = uVar6;
  }
  return 0;
}
