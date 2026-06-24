/* address: 0x00597b87 */
/* name: CFastVB__PackScalarBlock_InterpolatedEndpoints */
/* signature: int __stdcall CFastVB__PackScalarBlock_InterpolatedEndpoints(void * param_1, float param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int CFastVB__PackScalarBlock_InterpolatedEndpoints(void *param_1,float param_2)

{
  undefined1 *puVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  char cVar6;
  char cVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  float *pfVar11;
  float *pfVar12;
  uint uVar13;
  ushort in_FPUControlWord;
  float local_a8 [32];
  int local_28;
  float local_24;
  float local_20;
  float *local_1c;
  float *local_18;
  float *local_14;
  undefined *local_10;
  undefined4 local_c;
  undefined4 local_8;

  puVar1 = param_1;
  pfVar12 = (float *)((int)param_2 + 0xc);
  param_2 = *pfVar12;
  local_14 = (float *)param_2;
  local_1c = pfVar12;
  pfVar11 = local_a8;
  for (iVar8 = 0x10; iVar8 != 0; iVar8 = iVar8 + -1) {
    *pfVar11 = 0.0;
    pfVar11 = pfVar11 + 1;
  }
  uRam009d241e = local_c._2_2_;
  local_8._0_2_ = in_FPUControlWord | 0xc00;
  local_8._2_2_ = uRam009d241e;
  uVar10 = 0;
  local_18 = pfVar12;
  do {
    local_c = local_a8[uVar10] + *local_18;
    local_10 = (undefined *)(int)ROUND(local_c * _DAT_005e9f08 + _DAT_005e72d4);
    local_8 = local_10;
    fVar2 = (float)(int)local_10 * _DAT_005e9ee0;
    local_a8[uVar10 + 0x10] = fVar2;
    fVar5 = fVar2;
    if ((param_2 <= fVar2) && (fVar5 = param_2, (float)local_14 < fVar2)) {
      local_14 = (float *)fVar2;
    }
    param_2 = fVar5;
    fVar2 = local_c - fVar2;
    uVar9 = uVar10 & 3;
    if (uVar9 != 3) {
      local_a8[uVar10 + 1] = _DAT_005ef0a0 * fVar2 + local_a8[uVar10 + 1];
    }
    if (uVar10 < 0xc) {
      if (uVar9 != 0) {
        local_a8[uVar10 + 3] = _DAT_005ef09c * fVar2 + local_a8[uVar10 + 3];
      }
      local_a8[uVar10 + 4] = _DAT_005ef098 * fVar2 + local_a8[uVar10 + 4];
      if (uVar9 != 3) {
        local_a8[uVar10 + 5] = fVar2 * _DAT_005ef094 + local_a8[uVar10 + 5];
      }
    }
    local_18 = local_18 + 4;
    uVar10 = uVar10 + 1;
  } while (uVar10 < 0x10);
  _DAT_009d241c = in_FPUControlWord;
  iVar8 = CFastVB__QuantizeScalarBlockIndices((void *)((int)param_1 + 8),0.0);
  if (iVar8 < 0) {
    return iVar8;
  }
  if (param_2 == 1.0) {
    *puVar1 = 0xff;
    *(undefined1 *)((int)puVar1 + 1) = 0xff;
LAB_00597d89:
    *(undefined4 *)((int)puVar1 + 2) = 0;
    *(undefined2 *)((int)puVar1 + 6) = 0;
  }
  else {
    if ((param_2 == 0.0) || ((float)local_14 == 1.0)) {
      param_2 = 8.40779e-45;
      iVar8 = 6;
    }
    else {
      iVar8 = 8;
      param_2 = 1.12104e-44;
    }
    CFastVB__SolveScalarEndpointPairFromSamples(&local_10,&param_1,(int)(local_a8 + 0x10));
    uRam009d241e = local_c._2_2_;
    uVar10 = (uint)ROUND((float)local_10 * _DAT_005e9f08 + _DAT_005e72d4);
    uVar9 = (uint)ROUND((float)param_1 * _DAT_005e9f08 + _DAT_005e72d4);
    fVar2 = (float)(uVar10 & 0xff) * _DAT_005e9ee0;
    fVar5 = (float)(uVar9 & 0xff) * _DAT_005e9ee0;
    cVar6 = (char)uVar10;
    cVar7 = (char)uVar9;
    _DAT_009d241c = in_FPUControlWord;
    if (iVar8 == 8) {
      if (cVar6 == cVar7) {
        *puVar1 = cVar6;
        *(char *)((int)puVar1 + 1) = cVar7;
        goto LAB_00597d89;
      }
LAB_00597dfe:
      *(char *)((int)puVar1 + 1) = cVar6;
      local_a8[0x18] = fVar5;
      local_a8[0x19] = fVar2;
      *puVar1 = cVar7;
      uVar10 = 1;
      do {
        fVar3 = (float)(int)(7 - uVar10);
        if ((int)(7 - uVar10) < 0) {
          fVar3 = fVar3 + _DAT_005e72d8;
        }
        fVar4 = (float)(int)uVar10;
        if ((int)uVar10 < 0) {
          fVar4 = fVar4 + _DAT_005e72d8;
        }
        uVar9 = uVar10 + 1;
        local_a8[uVar10 + 0x19] = (fVar4 * fVar2 + fVar3 * fVar5) * _DAT_005e9f38;
        uVar10 = uVar9;
      } while (uVar9 < 7);
      local_10 = &DAT_005ef0a8;
    }
    else {
      if (iVar8 != 6) goto LAB_00597dfe;
      *puVar1 = cVar6;
      local_a8[0x18] = fVar2;
      local_a8[0x19] = fVar5;
      *(char *)((int)puVar1 + 1) = cVar7;
      uVar10 = 1;
      do {
        fVar3 = (float)(int)(5 - uVar10);
        if ((int)(5 - uVar10) < 0) {
          fVar3 = fVar3 + _DAT_005e72d8;
        }
        fVar4 = (float)(int)uVar10;
        if ((int)uVar10 < 0) {
          fVar4 = fVar4 + _DAT_005e72d8;
        }
        uVar9 = uVar10 + 1;
        local_a8[uVar10 + 0x19] = (fVar4 * fVar5 + fVar3 * fVar2) * _DAT_005ef0a4;
        uVar10 = uVar9;
      } while (uVar9 < 5);
      local_10 = &DAT_005ef0c8;
      local_a8[0x1e] = 0.0;
      local_a8[0x1f] = 1.0;
    }
    local_24 = (float)(iVar8 + -1);
    if (iVar8 + -1 < 0) {
      local_24 = local_24 + _DAT_005e72d8;
    }
    if (local_a8[0x18] == local_a8[0x19]) {
      local_20 = 0.0;
    }
    else {
      local_20 = local_24 / (local_a8[0x19] - local_a8[0x18]);
    }
    pfVar12 = local_a8;
    for (iVar8 = 0x10; iVar8 != 0; iVar8 = iVar8 + -1) {
      *pfVar12 = 0.0;
      pfVar12 = pfVar12 + 1;
    }
    uRam009d241e = local_c._2_2_;
    local_18 = local_1c;
    uVar10 = 0;
    do {
      uVar9 = 0;
      param_1._2_1_ = 0;
      local_8 = (undefined *)(uVar10 + 8);
      if (uVar10 < uVar10 + 8) {
        local_14 = local_18;
        do {
          fVar2 = local_a8[uVar10] + *local_14;
          fVar5 = (fVar2 - local_a8[0x18]) * local_20;
          if (fVar5 < DAT_005e6a3c == (fVar5 == DAT_005e6a3c)) {
            if (fVar5 < local_24) {
              local_1c = (float *)(fVar5 + _DAT_005e72d4);
              local_28 = (int)ROUND(fVar5 + _DAT_005e72d4);
              iVar8 = *(int *)(local_10 + local_28 * 4);
            }
            else if ((param_2 == 8.40779e-45) &&
                    (fVar5 = (local_a8[0x19] + _DAT_005e6a34) * _DAT_005e72d4,
                    fVar5 < fVar2 != (fVar5 == fVar2))) {
              iVar8 = 7;
            }
            else {
              iVar8 = 1;
            }
          }
          else if ((param_2 != 8.40779e-45) || (local_a8[0x18] * _DAT_005e72d4 < fVar2)) {
            iVar8 = 0;
          }
          else {
            iVar8 = 6;
          }
          fVar2 = fVar2 - local_a8[iVar8 + 0x18];
          uVar9 = uVar9 >> 3 | iVar8 << 0x15;
          uVar13 = uVar10 & 3;
          if (uVar13 != 3) {
            local_a8[uVar10 + 1] = _DAT_005ef0a0 * fVar2 + local_a8[uVar10 + 1];
          }
          if (uVar10 < 0xc) {
            if (uVar13 != 0) {
              local_a8[uVar10 + 3] = _DAT_005ef09c * fVar2 + local_a8[uVar10 + 3];
            }
            local_a8[uVar10 + 4] = _DAT_005ef098 * fVar2 + local_a8[uVar10 + 4];
            if (uVar13 != 3) {
              local_a8[uVar10 + 5] = fVar2 * _DAT_005ef094 + local_a8[uVar10 + 5];
            }
          }
          local_14 = local_14 + 4;
          uVar10 = uVar10 + 1;
        } while (uVar10 < local_8);
        param_1._2_1_ = (undefined1)(uVar9 >> 0x10);
      }
      local_18 = local_18 + 0x20;
      puVar1[4] = param_1._2_1_;
      puVar1[2] = (char)uVar9;
      puVar1[3] = (char)(uVar9 >> 8);
      uVar10 = (uint)local_8;
      puVar1 = puVar1 + 3;
    } while (local_8 < 0x10);
  }
  return 0;
}
