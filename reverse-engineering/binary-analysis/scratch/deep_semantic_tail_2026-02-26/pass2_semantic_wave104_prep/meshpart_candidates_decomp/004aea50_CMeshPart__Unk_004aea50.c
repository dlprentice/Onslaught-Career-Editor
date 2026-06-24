/* address: 0x004aea50 */
/* name: CMeshPart__Unk_004aea50 */
/* signature: void __fastcall CMeshPart__Unk_004aea50(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CMeshPart__Unk_004aea50(int param_1)

{
  float fVar1;
  float fVar2;
  float fVar3;
  undefined4 *puVar4;
  float fVar5;
  int iVar6;
  float *pfVar7;
  float local_3c;
  float local_38;
  float local_34;
  float local_30;
  float local_2c;
  float local_28;
  float local_14;

  fVar5 = _DAT_005d856c;
  if (*(int *)(param_1 + 0x84) != 0) {
    *(undefined4 *)(*(int *)(param_1 + 0xfc) + 0x20) = 0;
    local_3c = 999999.0;
    pfVar7 = (float *)**(undefined4 **)(param_1 + 0x84);
    iVar6 = 0;
    local_34 = 999999.0;
    local_2c = 999999.0;
    local_38 = -999999.0;
    local_30 = -999999.0;
    local_28 = -999999.0;
    if (0 < *(int *)(param_1 + 0xac)) {
      do {
        fVar1 = *pfVar7;
        fVar2 = pfVar7[1];
        fVar3 = pfVar7[2];
        local_14 = pfVar7[3];
        if (fVar1 < local_3c) {
          local_3c = fVar1;
        }
        if (fVar2 < local_34) {
          local_34 = fVar2;
        }
        if (fVar3 < local_2c) {
          local_2c = fVar3;
        }
        if (local_38 < fVar1) {
          local_38 = fVar1;
        }
        if (local_30 < fVar2) {
          local_30 = fVar2;
        }
        if (local_28 < fVar3) {
          local_28 = fVar3;
        }
        fVar1 = fVar1 + *(float *)(param_1 + 0x60);
        fVar2 = fVar2 + *(float *)(param_1 + 100);
        fVar3 = fVar3 + *(float *)(param_1 + 0x68);
        fVar1 = fVar1 * fVar1 + fVar2 * fVar2 + fVar3 * fVar3;
        if (fVar5 < fVar1) {
          fVar5 = fVar1;
        }
        pfVar7 = pfVar7 + 4;
        iVar6 = iVar6 + 1;
        *(undefined4 *)(*(int *)(param_1 + 0xfc) + 0x20) = 1;
      } while (iVar6 < *(int *)(param_1 + 0xac));
    }
    pfVar7 = *(float **)(param_1 + 0xfc);
    fVar1 = (local_30 + local_34) * _DAT_005d85ec;
    *pfVar7 = (local_38 + local_3c) * _DAT_005d85ec;
    fVar2 = (local_28 + local_2c) * _DAT_005d85ec;
    pfVar7[1] = fVar1;
    pfVar7[2] = fVar2;
    pfVar7[3] = local_14;
    iVar6 = *(int *)(param_1 + 0xfc);
    fVar1 = (local_34 - local_30) * _DAT_005d85ec;
    *(float *)(iVar6 + 0x10) = (local_3c - local_38) * _DAT_005d85ec;
    fVar2 = (local_2c - local_28) * _DAT_005d85ec;
    *(float *)(iVar6 + 0x14) = fVar1;
    *(float *)(iVar6 + 0x18) = fVar2;
    *(float *)(iVar6 + 0x1c) = local_14;
    fVar1 = *(float *)(*(int *)(param_1 + 0xfc) + 0x10);
    if (fVar1 <= _DAT_005d856c) {
      fVar1 = -fVar1;
    }
    *(float *)(*(int *)(param_1 + 0xfc) + 0x10) = fVar1;
    fVar1 = *(float *)(*(int *)(param_1 + 0xfc) + 0x14);
    if (fVar1 <= _DAT_005d856c) {
      fVar1 = -fVar1;
    }
    *(float *)(*(int *)(param_1 + 0xfc) + 0x14) = fVar1;
    fVar1 = *(float *)(*(int *)(param_1 + 0xfc) + 0x18);
    if (fVar1 <= _DAT_005d856c) {
      fVar1 = -fVar1;
    }
    *(float *)(*(int *)(param_1 + 0xfc) + 0x18) = fVar1;
    puVar4 = *(undefined4 **)(param_1 + 0xfc);
    *(undefined4 *)(param_1 + 0x130) = puVar4[6];
    if ((((float)puVar4[4] <= (float)puVar4[5]) && ((float)puVar4[5] <= (float)puVar4[6])) ||
       (((float)puVar4[6] <= (float)puVar4[5] && ((float)puVar4[5] <= (float)puVar4[4])))) {
      *(undefined4 *)(param_1 + 0x130) = puVar4[5];
    }
    if ((((float)puVar4[5] <= (float)puVar4[4]) && ((float)puVar4[4] <= (float)puVar4[6])) ||
       (((float)puVar4[6] <= (float)puVar4[4] && ((float)puVar4[4] <= (float)puVar4[5])))) {
      *(undefined4 *)(param_1 + 0x130) = puVar4[4];
    }
    *(float *)(param_1 + 300) = SQRT(fVar5);
    if (puVar4[8] == 0) {
      *puVar4 = 0;
      puVar4[1] = 0;
      puVar4[2] = 0;
      iVar6 = *(int *)(param_1 + 0xfc);
      *(undefined4 *)(iVar6 + 0x10) = 0;
      *(undefined4 *)(iVar6 + 0x14) = 0;
      *(undefined4 *)(iVar6 + 0x18) = 0;
      *(undefined4 *)(param_1 + 300) = 0;
    }
    fVar1 = _DAT_005d856c;
    iVar6 = *(int *)(param_1 + 0xfc);
    fVar5 = *(float *)(iVar6 + 0x18) * *(float *)(iVar6 + 0x18) +
            *(float *)(iVar6 + 0x14) * *(float *)(iVar6 + 0x14) +
            *(float *)(iVar6 + 0x10) * *(float *)(iVar6 + 0x10);
    *(float *)(iVar6 + 0x24) = fVar5;
    if (fVar1 < fVar5) {
      *(float *)(iVar6 + 0x24) = SQRT(fVar5);
      return;
    }
  }
  return;
}
