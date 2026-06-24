/* address: 0x0059f5b3 */
/* name: CFastVB__BuildOrthonormalBasisFromCovariance */
/* signature: void __stdcall CFastVB__BuildOrthonormalBasisFromCovariance(void * param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CFastVB__BuildOrthonormalBasisFromCovariance(void *param_1,void *param_2)

{
  float *pfVar1;
  int iVar2;
  float fVar3;
  void *pvVar4;
  int iVar5;
  int iVar6;
  float local_18 [4];
  int local_8;

  pvVar4 = param_2;
  fVar3 = *(float *)((int)param_2 + 0x14) + *(float *)param_2 + *(float *)((int)param_2 + 0x28);
  if (fVar3 <= DAT_005e6a3c) {
    local_18[1] = *(float *)((int)param_2 + 0x14);
    pfVar1 = (float *)((int)param_2 + 0x28);
    local_18[0] = *(float *)param_2;
    local_18[2] = *pfVar1;
    param_2 = (void *)(uint)(*(float *)param_2 < *(float *)((int)param_2 + 0x14));
    if (local_18[(int)param_2] < *pfVar1) {
      param_2 = (void *)0x2;
    }
    iVar5 = (int)param_2 * 4;
    iVar2 = *(int *)(&DAT_005f4310 + iVar5);
    iVar6 = iVar2 * 4;
    local_8 = *(int *)(&DAT_005f4310 + iVar6);
    fVar3 = SQRT(((local_18[(int)param_2] - local_18[iVar2]) - local_18[local_8]) + _DAT_005e6a34) *
            _DAT_005e72d4;
    *(float *)(iVar5 + (int)param_1) = fVar3;
    fVar3 = _DAT_005e9328 / fVar3;
    *(float *)(iVar6 + (int)param_1) =
         (*(float *)((int)pvVar4 + (int)((int)param_2 + iVar6) * 4) +
         *(float *)((int)pvVar4 + (iVar2 + iVar5) * 4)) * fVar3;
    *(float *)(local_8 * 4 + (int)param_1) =
         (*(float *)((int)pvVar4 + (int)((int)param_2 + local_8 * 4) * 4) +
         *(float *)((int)pvVar4 + (iVar5 + local_8) * 4)) * fVar3;
    *(float *)((int)param_1 + 0xc) =
         (*(float *)((int)pvVar4 + (iVar6 + local_8) * 4) -
         *(float *)((int)pvVar4 + (local_8 * 4 + iVar2) * 4)) * fVar3;
  }
  else {
    fVar3 = SQRT(fVar3 + _DAT_005e6a34) * _DAT_005e72d4;
    *(float *)((int)param_1 + 0xc) = fVar3;
    fVar3 = _DAT_005e9328 / fVar3;
    *(float *)param_1 = (*(float *)((int)param_2 + 0x18) - *(float *)((int)param_2 + 0x24)) * fVar3;
    *(float *)((int)param_1 + 4) =
         (*(float *)((int)param_2 + 0x20) - *(float *)((int)param_2 + 8)) * fVar3;
    *(float *)((int)param_1 + 8) =
         (*(float *)((int)param_2 + 4) - *(float *)((int)param_2 + 0x10)) * fVar3;
  }
  return;
}
