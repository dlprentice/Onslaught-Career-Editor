/* address: 0x00579184 */
/* name: CFastVB__Unk_00579184 */
/* signature: void __stdcall CFastVB__Unk_00579184(void * param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CFastVB__Unk_00579184(void *param_1,void *param_2)

{
  float *pfVar1;
  float fVar2;
  int iVar3;
  float local_14;
  float local_10;
  float local_c;
  float local_8;

  fVar2 = *(float *)((int)param_2 + 0xc) * *(float *)((int)param_2 + 0xc) +
          *(float *)((int)param_2 + 8) * *(float *)((int)param_2 + 8) +
          *(float *)((int)param_2 + 4) * *(float *)((int)param_2 + 4) +
          *(float *)param_2 * *(float *)param_2;
  iVar3 = CDXTexture__Helper_00575986(fVar2,1.0);
  if (iVar3 == 0) {
    if (fVar2 <= (float)PTR_DAT_005e932c) {
      *(undefined4 *)param_1 = 0;
      *(undefined4 *)((int)param_1 + 4) = 0;
      *(undefined4 *)((int)param_1 + 8) = 0;
      *(undefined4 *)((int)param_1 + 0xc) = 0;
      return;
    }
    fVar2 = _DAT_005e6a34 / SQRT(fVar2);
    local_14 = fVar2 * *(float *)param_2;
    local_10 = fVar2 * *(float *)((int)param_2 + 4);
    local_c = fVar2 * *(float *)((int)param_2 + 8);
    pfVar1 = (float *)((int)param_2 + 0xc);
    param_2 = &local_14;
    local_8 = fVar2 * *pfVar1;
  }
  else if (param_1 == param_2) {
    return;
  }
  *(float *)param_1 = *(float *)param_2;
  *(float *)((int)param_1 + 4) = *(float *)((int)param_2 + 4);
  *(float *)((int)param_1 + 8) = *(float *)((int)param_2 + 8);
  *(float *)((int)param_1 + 0xc) = *(float *)((int)param_2 + 0xc);
  return;
}
