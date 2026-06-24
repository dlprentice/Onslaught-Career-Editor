/* address: 0x00597949 */
/* name: CTexture__EncodeDxt5AlphaIndices_ErrorDiffusion */
/* signature: int __stdcall CTexture__EncodeDxt5AlphaIndices_ErrorDiffusion(void * param_1, int param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int CTexture__EncodeDxt5AlphaIndices_ErrorDiffusion(void *param_1,int param_2)

{
  uint uVar1;
  float fVar2;
  float fVar3;
  float *pfVar4;
  int iVar5;
  float *pfVar6;
  uint uVar7;
  undefined2 in_FPUControlWord;
  float local_150 [64];
  float local_50 [17];
  uint local_c;
  uint local_8;

  pfVar4 = local_50;
  for (iVar5 = 0x10; iVar5 != 0; iVar5 = iVar5 + -1) {
    *pfVar4 = 0.0;
    pfVar4 = pfVar4 + 1;
  }
  local_8 = CONCAT22(local_8._2_2_,in_FPUControlWord);
  local_c = local_8 | 0xc00;
  _DAT_009d241c = local_8;
  uVar7 = 0;
  pfVar6 = local_150 + 1;
  pfVar4 = (float *)(param_2 + 0xc);
  do {
    fVar2 = local_50[uVar7];
    pfVar6[-1] = pfVar4[-3];
    fVar3 = *pfVar4;
    *pfVar6 = pfVar4[-2];
    local_50[0x10] = fVar2 + fVar3;
    pfVar6[1] = pfVar4[-1];
    iVar5 = (int)ROUND(fVar2 + fVar3 + _DAT_005e72d4);
    local_c = iVar5;
    uVar1 = uVar7 & 3;
    *(float *)(((int)local_150 - param_2) + (int)pfVar4) = (float)iVar5;
    fVar2 = local_50[0x10] - (float)iVar5;
    if (uVar1 != 3) {
      local_50[uVar7 + 1] = _DAT_005ef0a0 * fVar2 + local_50[uVar7 + 1];
    }
    if (uVar7 < 0xc) {
      if (uVar1 != 0) {
        local_50[uVar7 + 3] = _DAT_005ef09c * fVar2 + local_50[uVar7 + 3];
      }
      local_50[uVar7 + 4] = _DAT_005ef098 * fVar2 + local_50[uVar7 + 4];
      if (uVar1 != 3) {
        local_50[uVar7 + 5] = fVar2 * _DAT_005ef094 + local_50[uVar7 + 5];
      }
    }
    uVar7 = uVar7 + 1;
    pfVar6 = pfVar6 + 4;
    pfVar4 = pfVar4 + 4;
  } while (uVar7 < 0x10);
  iVar5 = CFastVB__QuantizeScalarBlockIndices(param_1,1.4013e-45);
  if (-1 < iVar5) {
    iVar5 = 0;
  }
  return iVar5;
}
