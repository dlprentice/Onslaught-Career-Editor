/* address: 0x00425760 */
/* name: CUnitAI__OrthonormalizeMat34Axes */
/* signature: void __fastcall CUnitAI__OrthonormalizeMat34Axes(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CUnitAI__OrthonormalizeMat34Axes(void *param_1)

{
  float *pfVar1;
  float *pfVar2;
  float fVar3;
  undefined4 local_4;

  fVar3 = SQRT(*(float *)((int)param_1 + 8) * *(float *)((int)param_1 + 8) +
               *(float *)((int)param_1 + 4) * *(float *)((int)param_1 + 4) +
               *(float *)param_1 * *(float *)param_1);
  if (fVar3 != _DAT_005d856c) {
    fVar3 = _DAT_005d8568 / fVar3;
    *(float *)param_1 = fVar3 * *(float *)param_1;
    *(float *)((int)param_1 + 4) = fVar3 * *(float *)((int)param_1 + 4);
    *(float *)((int)param_1 + 8) = fVar3 * *(float *)((int)param_1 + 8);
  }
  pfVar1 = (float *)((int)param_1 + 0x10);
  fVar3 = SQRT(*(float *)((int)param_1 + 0x18) * *(float *)((int)param_1 + 0x18) +
               *(float *)((int)param_1 + 0x14) * *(float *)((int)param_1 + 0x14) +
               *(float *)((int)param_1 + 0x10) * *(float *)((int)param_1 + 0x10));
  if (fVar3 != _DAT_005d856c) {
    fVar3 = _DAT_005d8568 / fVar3;
    *pfVar1 = fVar3 * *pfVar1;
    *(float *)((int)param_1 + 0x14) = fVar3 * *(float *)((int)param_1 + 0x14);
    *(float *)((int)param_1 + 0x18) = fVar3 * *(float *)((int)param_1 + 0x18);
  }
  pfVar2 = (float *)((int)param_1 + 0x20);
  *pfVar2 = *(float *)((int)param_1 + 0x18) * *(float *)((int)param_1 + 4) -
            *(float *)((int)param_1 + 0x14) * *(float *)((int)param_1 + 8);
  *(float *)((int)param_1 + 0x24) =
       *pfVar1 * *(float *)((int)param_1 + 8) - *(float *)((int)param_1 + 0x18) * *(float *)param_1;
  *(float *)((int)param_1 + 0x28) =
       *(float *)((int)param_1 + 0x14) * *(float *)param_1 - *(float *)((int)param_1 + 4) * *pfVar1;
  *(undefined4 *)((int)param_1 + 0x2c) = local_4;
  fVar3 = SQRT(*(float *)((int)param_1 + 0x28) * *(float *)((int)param_1 + 0x28) +
               *(float *)((int)param_1 + 0x24) * *(float *)((int)param_1 + 0x24) + *pfVar2 * *pfVar2
              );
  if (fVar3 != _DAT_005d856c) {
    fVar3 = _DAT_005d8568 / fVar3;
    *pfVar2 = fVar3 * *pfVar2;
    *(float *)((int)param_1 + 0x24) = fVar3 * *(float *)((int)param_1 + 0x24);
    *(float *)((int)param_1 + 0x28) = fVar3 * *(float *)((int)param_1 + 0x28);
  }
  *pfVar1 = *(float *)((int)param_1 + 0x24) * *(float *)((int)param_1 + 8) -
            *(float *)((int)param_1 + 0x28) * *(float *)((int)param_1 + 4);
  *(float *)((int)param_1 + 0x14) =
       *(float *)((int)param_1 + 0x28) * *(float *)param_1 - *pfVar2 * *(float *)((int)param_1 + 8);
  *(float *)((int)param_1 + 0x18) =
       *(float *)((int)param_1 + 4) * *pfVar2 - *(float *)((int)param_1 + 0x24) * *(float *)param_1;
  *(undefined4 *)((int)param_1 + 0x1c) = local_4;
  return;
}
