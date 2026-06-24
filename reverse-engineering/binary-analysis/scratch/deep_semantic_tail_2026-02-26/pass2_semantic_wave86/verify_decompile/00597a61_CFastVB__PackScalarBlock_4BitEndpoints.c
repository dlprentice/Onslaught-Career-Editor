/* address: 0x00597a61 */
/* name: CFastVB__PackScalarBlock_4BitEndpoints */
/* signature: void __stdcall CFastVB__PackScalarBlock_4BitEndpoints(void * param_1, int param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CFastVB__PackScalarBlock_4BitEndpoints(void *param_1,int param_2)

{
  uint *puVar1;
  float fVar2;
  void *pvVar3;
  int iVar4;
  uint uVar5;
  float *pfVar6;
  undefined2 in_FPUControlWord;
  float local_58 [16];
  int local_18;
  int local_14;
  float local_10;
  undefined4 local_c;
  float *local_8;

  pvVar3 = param_1;
  *(undefined4 *)param_1 = 0;
  *(undefined4 *)((int)param_1 + 4) = 0;
  pfVar6 = local_58;
  for (iVar4 = 0x10; iVar4 != 0; iVar4 = iVar4 + -1) {
    *pfVar6 = 0.0;
    pfVar6 = pfVar6 + 1;
  }
  local_c = CONCAT22(local_c._2_2_,in_FPUControlWord);
  _DAT_009d241c = local_c;
  param_1 = (void *)0x0;
  local_8 = (float *)(param_2 + 0xc);
  do {
    local_10 = local_58[(int)param_1] + *local_8;
    local_18 = (int)ROUND(local_10 * _DAT_005e9f04 + _DAT_005e72d4);
    puVar1 = (uint *)((int)pvVar3 + ((uint)param_1 >> 3) * 4);
    local_14 = local_18;
    fVar2 = (float)local_18;
    *puVar1 = *puVar1 >> 4 | local_18 << 0x1c;
    if (local_18 < 0) {
      fVar2 = fVar2 + _DAT_005e72d8;
    }
    uVar5 = (uint)param_1 & 3;
    fVar2 = local_10 - fVar2 * _DAT_005e9f28;
    if (uVar5 != 3) {
      local_58[(int)param_1 + 1] = _DAT_005ef0a0 * fVar2 + local_58[(int)param_1 + 1];
    }
    if (param_1 < (void *)0xc) {
      if (uVar5 != 0) {
        local_58[(int)param_1 + 3] = _DAT_005ef09c * fVar2 + local_58[(int)param_1 + 3];
      }
      local_58[(int)param_1 + 4] = _DAT_005ef098 * fVar2 + local_58[(int)param_1 + 4];
      if (uVar5 != 3) {
        local_58[(int)param_1 + 5] = fVar2 * _DAT_005ef094 + local_58[(int)param_1 + 5];
      }
    }
    param_1 = (void *)((int)param_1 + 1);
    local_8 = local_8 + 4;
  } while (param_1 < (void *)0x10);
  CFastVB__QuantizeScalarBlockIndices((void *)((int)pvVar3 + 8),0.0);
  return;
}
