/* address: 0x005968a4 */
/* name: CFastVB__SolveVectorEndpointPairFromSamples */
/* signature: void __stdcall CFastVB__SolveVectorEndpointPairFromSamples(void * param_1, void * param_2, float param_3, int param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CFastVB__SolveVectorEndpointPairFromSamples
               (void *param_1,void *param_2,float param_3,int param_4)

{
  float *pfVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  float fVar9;
  int iVar10;
  float *pfVar11;
  int iVar12;
  uint uVar13;
  int iVar14;
  uint uVar15;
  float *pfVar16;
  int iVar17;
  undefined2 in_FPUControlWord;
  float local_c8 [16];
  int local_88;
  float *local_84;
  float local_80;
  float local_7c;
  float local_78;
  undefined4 *local_70;
  uint local_6c;
  undefined4 local_68;
  float *local_64;
  float local_60;
  float local_5c;
  float local_58;
  float local_54;
  float local_50;
  float local_4c;
  float local_44;
  float local_40;
  float local_3c;
  float local_34 [6];
  float local_1c;
  float local_14;
  float local_10;
  float local_c;
  undefined4 uStack_8;

  if (param_4 == 3) {
    local_64 = (float *)&DAT_005ef068;
    local_70 = &DAT_005ef05c;
  }
  else {
    local_64 = (float *)&DAT_005ef04c;
    local_70 = (undefined4 *)&DAT_005ef03c;
  }
  local_34[4] = 0.0;
  local_34[5] = 0.0;
  local_14 = DAT_00659ca0;
  local_10 = DAT_00659ca4;
  local_1c = 0.0;
  local_c = DAT_00659ca8;
  uStack_8 = DAT_00659cac;
  pfVar16 = (float *)((int)param_3 + 8);
  iVar10 = 0x10;
  local_84 = pfVar16;
  pfVar11 = pfVar16;
  iVar12 = iVar10;
  do {
    if (pfVar11[-2] < local_14) {
      local_14 = pfVar11[-2];
    }
    if (pfVar11[-1] < local_10) {
      local_10 = pfVar11[-1];
    }
    fVar3 = local_10;
    if (*pfVar11 < local_c) {
      local_c = *pfVar11;
    }
    if (local_34[4] < pfVar11[-2]) {
      local_34[4] = pfVar11[-2];
    }
    if (local_34[5] < pfVar11[-1]) {
      local_34[5] = pfVar11[-1];
    }
    if (local_1c < *pfVar11) {
      local_1c = *pfVar11;
    }
    fVar9 = local_1c;
    pfVar11 = pfVar11 + 4;
    iVar12 = iVar12 + -1;
  } while (iVar12 != 0);
  fVar5 = local_34[4] - local_14;
  fVar7 = local_34[5] - local_10;
  fVar4 = local_1c - local_c;
  local_5c = fVar5 * fVar5 + fVar7 * fVar7 + fVar4 * fVar4;
  if ((float)PTR_DAT_005e932c <= local_5c) {
    fVar8 = 1.0 / local_5c;
    local_80 = fVar5 * fVar8;
    local_7c = fVar7 * fVar8;
    local_78 = fVar8 * fVar4;
    local_54 = (local_34[4] + local_14) * _DAT_005e72d4;
    local_50 = (local_34[5] + local_10) * _DAT_005e72d4;
    local_4c = (local_1c + local_c) * _DAT_005e72d4;
    local_34[3] = 0.0;
    local_34[2] = 0.0;
    local_34[1] = 0.0;
    local_34[0] = 0.0;
    do {
      local_44 = (pfVar16[-2] - local_54) * fVar5 * fVar8;
      local_40 = (pfVar16[-1] - local_50) * fVar7 * fVar8;
      fVar2 = *pfVar16;
      pfVar16 = pfVar16 + 4;
      iVar10 = iVar10 + -1;
      fVar2 = (fVar2 - local_4c) * fVar8 * fVar4;
      fVar6 = local_40 + fVar2 + local_44;
      local_34[0] = fVar6 * fVar6 + local_34[0];
      fVar6 = (local_40 + local_44) - fVar2;
      local_34[1] = fVar6 * fVar6 + local_34[1];
      fVar6 = (local_44 - local_40) + fVar2;
      local_34[2] = fVar6 * fVar6 + local_34[2];
      fVar2 = (local_44 - local_40) - fVar2;
      local_34[3] = fVar2 * fVar2 + local_34[3];
    } while (iVar10 != 0);
    uVar15 = 0;
    uVar13 = 1;
    do {
      if (local_34[0] < local_34[uVar13]) {
        local_34[0] = local_34[uVar13];
        uVar15 = uVar13;
      }
      uVar13 = uVar13 + 1;
    } while (uVar13 < 4);
    if ((uVar15 & 2) != 0) {
      local_10 = local_34[5];
      local_34[5] = fVar3;
    }
    if ((uVar15 & 1) != 0) {
      local_1c = local_c;
      local_c = fVar9;
    }
    if (_DAT_005ef038 <= local_5c) {
      iVar10 = param_4 + -1;
      local_5c = (float)iVar10;
      if (iVar10 < 0) {
        local_5c = local_5c + _DAT_005e72d8;
      }
      local_68 = CONCAT22(local_68._2_2_,in_FPUControlWord);
      local_6c = 0;
      _DAT_009d241c = local_68;
      while( true ) {
        iVar12 = 0x10;
        if (param_4 != 0) {
          pfVar11 = local_c8 + 1;
          iVar14 = (int)local_70 - (int)local_64;
          pfVar16 = local_64;
          iVar17 = param_4;
          do {
            pfVar11[-1] = local_14 * *pfVar16 + local_34[4] * *(float *)(iVar14 + (int)pfVar16);
            *pfVar11 = local_10 * *pfVar16 + local_34[5] * *(float *)(iVar14 + (int)pfVar16);
            pfVar1 = (float *)(iVar14 + (int)pfVar16);
            fVar3 = *pfVar16;
            pfVar16 = pfVar16 + 1;
            pfVar11[1] = local_c * fVar3 + local_1c * *pfVar1;
            pfVar11 = pfVar11 + 4;
            iVar17 = iVar17 + -1;
          } while (iVar17 != 0);
        }
        fVar9 = local_34[4] - local_14;
        fVar3 = local_34[5] - local_10;
        fVar7 = local_1c - local_c;
        fVar5 = fVar9 * fVar9 + fVar3 * fVar3 + fVar7 * fVar7;
        if (fVar5 < _DAT_005ef038) break;
        fVar5 = local_5c / fVar5;
        local_44 = fVar5 * fVar9;
        local_40 = fVar3 * fVar5;
        local_3c = fVar5 * fVar7;
        local_34[2] = 0.0;
        local_34[1] = 0.0;
        local_34[0] = 0.0;
        local_4c = 0.0;
        local_50 = 0.0;
        local_54 = 0.0;
        local_58 = 0.0;
        param_3 = 0.0;
        pfVar11 = local_84;
        do {
          fVar4 = (pfVar11[-2] - local_14) * fVar5 * fVar9 +
                  (pfVar11[-1] - local_10) * fVar3 * fVar5 + (*pfVar11 - local_c) * fVar5 * fVar7;
          local_60 = fVar4;
          local_88 = iVar10;
          if (fVar4 < local_5c) {
            local_60 = fVar4 + _DAT_005e72d4;
            local_88 = (int)ROUND(fVar4 + _DAT_005e72d4);
          }
          pfVar16 = pfVar11 + -2;
          local_7c = local_c8[local_88 * 4 + 1] - pfVar11[-1];
          fVar4 = *pfVar11;
          fVar2 = local_64[local_88] * _DAT_005e72e8;
          pfVar11 = pfVar11 + 4;
          iVar12 = iVar12 + -1;
          fVar8 = (float)local_70[local_88] * _DAT_005e72e8;
          param_3 = fVar2 * local_64[local_88] + param_3;
          local_54 = fVar2 * (local_c8[local_88 * 4] - *pfVar16) + local_54;
          local_50 = fVar2 * local_7c + local_50;
          local_4c = fVar2 * (local_c8[local_88 * 4 + 2] - fVar4) + local_4c;
          local_58 = fVar8 * (float)local_70[local_88] + local_58;
          local_34[0] = fVar8 * (local_c8[local_88 * 4] - *pfVar16) + local_34[0];
          local_34[1] = local_7c * fVar8 + local_34[1];
          local_34[2] = fVar8 * (local_c8[local_88 * 4 + 2] - fVar4) + local_34[2];
        } while (iVar12 != 0);
        if (DAT_005e6a3c < param_3) {
          fVar3 = _DAT_005e6a38 / param_3;
          local_14 = local_54 * fVar3 + local_14;
          local_10 = local_50 * fVar3 + local_10;
          local_c = fVar3 * local_4c + local_c;
        }
        if (DAT_005e6a3c < local_58) {
          local_58 = _DAT_005e6a38 / local_58;
          local_34[4] = local_34[0] * local_58 + local_34[4];
          local_34[5] = local_34[1] * local_58 + local_34[5];
          local_1c = local_58 * local_34[2] + local_1c;
        }
        if (((((local_54 * local_54 < _DAT_005ef034) && (local_50 * local_50 < _DAT_005ef034)) &&
             (local_4c * local_4c < _DAT_005ef034)) &&
            (((local_34[0] * local_34[0] < _DAT_005ef034 &&
              (local_34[1] * local_34[1] < _DAT_005ef034)) &&
             (local_34[2] * local_34[2] < _DAT_005ef034)))) ||
           (local_6c = local_6c + 1, 7 < local_6c)) break;
      }
      *(float *)param_1 = local_14;
      *(float *)((int)param_1 + 4) = local_10;
      *(float *)((int)param_1 + 8) = local_c;
      *(float *)param_2 = local_34[4];
      *(float *)((int)param_2 + 4) = local_34[5];
    }
    else {
      *(float *)param_1 = local_14;
      *(float *)((int)param_1 + 4) = local_10;
      *(float *)((int)param_1 + 8) = local_c;
      *(float *)((int)param_2 + 4) = local_34[5];
      *(float *)param_2 = local_34[4];
    }
  }
  else {
    *(float *)param_1 = local_14;
    *(float *)((int)param_1 + 4) = local_10;
    *(float *)((int)param_1 + 8) = local_c;
    *(float *)((int)param_2 + 4) = local_34[5];
    *(float *)param_2 = local_34[4];
  }
  *(float *)((int)param_2 + 8) = local_1c;
  return;
}
