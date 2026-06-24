/* address: 0x00596589 */
/* name: CFastVB__SolveScalarEndpointPairFromSamples */
/* signature: void __stdcall CFastVB__SolveScalarEndpointPairFromSamples(void * param_1, void * param_2, int param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CFastVB__SolveScalarEndpointPairFromSamples(void *param_1,void *param_2,int param_3)

{
  float fVar1;
  float *pfVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  uint unaff_EBX;
  uint uVar6;
  undefined2 in_FPUControlWord;
  float local_5c [6];
  undefined4 local_44;
  undefined4 local_40;
  uint local_3c;
  float local_38;
  float local_34;
  float local_30;
  undefined4 local_2c;
  uint local_28;
  undefined4 *local_24;
  float *local_20;
  float local_1c;
  float local_18;
  float local_14;
  float local_10;
  float local_c;
  float local_8;

  if (unaff_EBX == 6) {
    local_20 = (float *)&DAT_005ef01c;
    local_24 = &DAT_005ef004;
  }
  else {
    local_20 = (float *)&DAT_005eefe4;
    local_24 = (undefined4 *)&DAT_005eefc4;
  }
  uVar4 = 0;
  local_8 = 1.0;
  local_c = 0.0;
  if (unaff_EBX == 8) {
    do {
      pfVar2 = (float *)(param_3 + uVar4 * 4);
      if (*pfVar2 < local_8) {
        local_8 = *pfVar2;
      }
      if (local_c < *pfVar2) {
        local_c = *pfVar2;
      }
      uVar4 = uVar4 + 1;
    } while (uVar4 < 0x10);
  }
  else {
    do {
      pfVar2 = (float *)(param_3 + uVar4 * 4);
      if ((*pfVar2 < local_8) && (DAT_005e6a3c < *pfVar2)) {
        local_8 = *pfVar2;
      }
      if ((local_c < *pfVar2) && (*pfVar2 < _DAT_005e6a34)) {
        local_c = *pfVar2;
      }
      uVar4 = uVar4 + 1;
    } while (uVar4 < 0x10);
  }
  uVar4 = unaff_EBX - 1;
  local_3c = uVar4;
  local_30 = (float)(int)uVar4;
  if ((int)uVar4 < 0) {
    local_30 = local_30 + _DAT_005e72d8;
  }
  local_2c = CONCAT22(local_2c._2_2_,in_FPUControlWord);
  local_28 = 0;
  _DAT_009d241c = local_2c;
  while (_DAT_005eefc0 <= local_c - local_8) {
    local_34 = local_30 / (local_c - local_8);
    if (unaff_EBX != 0) {
      iVar5 = (int)local_24 - (int)local_20;
      iVar3 = (int)local_5c - (int)local_20;
      pfVar2 = local_20;
      uVar6 = unaff_EBX;
      do {
        *(float *)(iVar3 + (int)pfVar2) =
             local_8 * *pfVar2 + local_c * *(float *)(iVar5 + (int)pfVar2);
        pfVar2 = pfVar2 + 1;
        uVar6 = uVar6 - 1;
      } while (uVar6 != 0);
    }
    if (unaff_EBX == 6) {
      local_44 = 0;
      local_40 = 0x3f800000;
    }
    uVar6 = 0;
    local_10 = 0.0;
    local_14 = 0.0;
    local_18 = 0.0;
    local_1c = 0.0;
    do {
      pfVar2 = (float *)(param_3 + uVar6 * 4);
      fVar1 = (*pfVar2 - local_8) * local_34;
      if (fVar1 < DAT_005e6a3c == (fVar1 == DAT_005e6a3c)) {
        if (fVar1 < local_30) {
          local_38 = fVar1 + _DAT_005e72d4;
          local_3c = (uint)ROUND(fVar1 + _DAT_005e72d4);
        }
        else {
          local_3c = uVar4;
          if ((unaff_EBX == 6) &&
             (fVar1 = (local_c + _DAT_005e6a34) * _DAT_005e72d4,
             fVar1 < *pfVar2 != (fVar1 == *pfVar2))) goto LAB_005967a3;
        }
LAB_0059675e:
        if (local_3c < unaff_EBX) {
          local_10 = (*pfVar2 - local_5c[local_3c]) * local_20[local_3c] + local_10;
          fVar1 = local_20[local_3c];
          local_18 = fVar1 * fVar1 + local_18;
          local_14 = (*pfVar2 - local_5c[local_3c]) * (float)local_24[local_3c] + local_14;
          fVar1 = (float)local_24[local_3c];
          local_1c = fVar1 * fVar1 + local_1c;
        }
      }
      else if ((unaff_EBX != 6) || (local_8 * _DAT_005e72d4 < *pfVar2)) {
        local_3c = 0;
        goto LAB_0059675e;
      }
LAB_005967a3:
      uVar6 = uVar6 + 1;
    } while (uVar6 < 0x10);
    if (DAT_005e6a3c < local_18) {
      local_8 = local_8 - local_10 / local_18;
    }
    if (DAT_005e6a3c < local_1c) {
      local_c = local_c - local_14 / local_1c;
    }
    fVar1 = local_c;
    if (local_c < local_8) {
      local_c = local_8;
      local_8 = fVar1;
    }
    if (((local_10 * local_10 < _DAT_005eefbc) && (local_14 * local_14 < _DAT_005eefbc)) ||
       (local_28 = local_28 + 1, 7 < local_28)) break;
  }
  if (DAT_005e6a3c <= local_8) {
    if (_DAT_005e6a34 < local_8) {
      local_8 = 1.0;
    }
  }
  else {
    local_8 = 0.0;
  }
  *(float *)param_1 = local_8;
  if (DAT_005e6a3c <= local_c) {
    if (_DAT_005e6a34 < local_c) {
      local_c = 1.0;
    }
  }
  else {
    local_c = 0.0;
  }
  *(float *)param_2 = local_c;
  return;
}
