/* address: 0x004b1eb0 */
/* name: CMeshPart__RebuildPerVertexNormalsAndTangents */
/* signature: void __thiscall CMeshPart__RebuildPerVertexNormalsAndTangents(void * this, int param_1, int param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CMeshPart__RebuildPerVertexNormalsAndTangents(void *this,int param_1,int param_2)

{
  undefined4 *puVar1;
  int iVar2;
  int iVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  int iVar8;
  float *pfVar9;
  int iVar10;
  int *piVar11;
  float *pfVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  float local_f4;
  float local_f0;
  float local_ec;
  float local_e8;
  float local_e4;
  float local_e0;
  float local_dc;
  float local_d8;
  int local_d4;
  int local_d0;
  int local_cc;
  int local_c8;
  int local_c4;
  float local_b8;
  float local_b4;
  float local_a8;
  float local_a4;
  float local_44;
  float local_34;
  float local_24;
  float local_14;
  undefined4 local_4;

  if ((*(int *)((int)this + 0xa8) < 0x2711) && (local_cc = 0, 0 < *(int *)((int)this + 0xa8))) {
    local_c4 = 0;
    do {
      local_e4 = DAT_00704d90;
      local_e0 = DAT_00704d94;
      local_f4 = DAT_00704d90;
      local_c8 = *(int *)((int)this + 0xb0);
      local_f0 = DAT_00704d94;
      local_dc = DAT_00704d98;
      local_d8 = DAT_00704d9c;
      local_ec = DAT_00704d98;
      local_e8 = DAT_00704d9c;
      local_d0 = 0;
      local_d4 = 0;
      if (0 < local_c8) {
        iVar10 = *(int *)((int)this + 0x134) + local_c4;
        iVar2 = *(int *)(iVar10 + 0x20);
        piVar11 = *(int **)((int)this + 0x80);
        do {
          iVar15 = *(int *)(*piVar11 + 0x20);
          if ((iVar15 == iVar2) || (iVar8 = *(int *)(piVar11[1] + 0x20), iVar8 == iVar2)) {
LAB_004b1f87:
            iVar13 = piVar11[2];
            iVar14 = *(int *)(iVar13 + 0x20);
            iVar3 = **(int **)((int)this + 0x84);
            pfVar12 = (float *)(iVar15 * 0x10 + iVar3);
            fVar4 = *pfVar12 - *(float *)(iVar14 * 0x10 + iVar3);
            iVar8 = iVar14 * 0x10 + iVar3;
            fVar5 = pfVar12[1] - *(float *)(iVar8 + 4);
            fVar6 = pfVar12[2] - *(float *)(iVar8 + 8);
            iVar8 = *(int *)(piVar11[1] + 0x20);
            pfVar9 = (float *)(iVar8 * 0x10 + iVar3);
            fVar7 = (pfVar12[1] - pfVar9[1]) * fVar6 - (pfVar12[2] - pfVar9[2]) * fVar5;
            local_b8 = (pfVar12[2] - pfVar9[2]) * fVar4 - fVar6 * (*pfVar12 - *pfVar9);
            local_b4 = fVar5 * (*pfVar12 - *pfVar9) - (pfVar12[1] - pfVar9[1]) * fVar4;
            fVar4 = SQRT(local_b4 * local_b4 + local_b8 * local_b8 + fVar7 * fVar7);
            if (fVar4 != _DAT_005d856c) {
              fVar4 = _DAT_005d8568 / fVar4;
              fVar7 = fVar7 * fVar4;
              local_b8 = local_b8 * fVar4;
              local_b4 = local_b4 * fVar4;
            }
            local_f4 = local_f4 + fVar7;
            local_f0 = local_f0 + local_b8;
            local_ec = local_ec + local_b4;
            local_e8 = local_14;
            local_d4 = local_d4 + 1;
          }
          else {
            iVar13 = piVar11[2];
            iVar14 = *(int *)(iVar13 + 0x20);
            if (iVar14 == iVar2) goto LAB_004b1f87;
          }
          if (((*piVar11 == iVar10) || (piVar11[1] == iVar10)) || (iVar13 == iVar10)) {
            iVar13 = **(int **)((int)this + 0x84);
            fVar4 = *(float *)(iVar15 * 0x10 + iVar13) - *(float *)(iVar14 * 0x10 + iVar13);
            pfVar9 = (float *)(iVar15 * 0x10 + iVar13);
            iVar15 = iVar14 * 0x10 + iVar13;
            fVar5 = pfVar9[1] - *(float *)(iVar15 + 4);
            pfVar12 = (float *)(iVar8 * 0x10 + iVar13);
            fVar6 = pfVar9[2] - *(float *)(iVar15 + 8);
            fVar7 = (pfVar9[1] - pfVar12[1]) * fVar6 - (pfVar9[2] - pfVar12[2]) * fVar5;
            local_a8 = (pfVar9[2] - pfVar12[2]) * fVar4 - fVar6 * (*pfVar9 - *pfVar12);
            local_a4 = fVar5 * (*pfVar9 - *pfVar12) - (pfVar9[1] - pfVar12[1]) * fVar4;
            fVar4 = SQRT(fVar7 * fVar7 + local_a4 * local_a4 + local_a8 * local_a8);
            if (fVar4 != _DAT_005d856c) {
              fVar4 = _DAT_005d8568 / fVar4;
              fVar7 = fVar7 * fVar4;
              local_a8 = local_a8 * fVar4;
              local_a4 = local_a4 * fVar4;
            }
            local_e4 = local_e4 + fVar7;
            local_e0 = local_e0 + local_a8;
            local_dc = local_dc + local_a4;
            local_d8 = local_44;
            local_d0 = local_d0 + 1;
          }
          piVar11 = piVar11 + 3;
          local_c8 = local_c8 + -1;
        } while (local_c8 != 0);
      }
      if ((char)param_1 != '\0') {
        if (local_d0 == 0) {
          pfVar9 = (float *)(*(int *)((int)this + 0x134) + local_c4);
          *pfVar9 = 1.0;
          pfVar9[1] = 0.0;
          pfVar9[2] = 0.0;
          local_d8 = local_34;
        }
        else {
          fVar4 = SQRT(local_e4 * local_e4 + local_e0 * local_e0 + local_dc * local_dc);
          if (_DAT_005d8580 <= fVar4) {
            if (fVar4 != _DAT_005d856c) {
              fVar4 = _DAT_005d8568 / fVar4;
              local_e4 = local_e4 * fVar4;
              local_e0 = local_e0 * fVar4;
              local_dc = local_dc * fVar4;
            }
            pfVar9 = (float *)(*(int *)((int)this + 0x134) + local_c4);
            *pfVar9 = local_e4;
            pfVar9[1] = local_e0;
            pfVar9[2] = local_dc;
          }
          else {
            pfVar9 = (float *)(*(int *)((int)this + 0x134) + local_c4);
            *pfVar9 = 1.0;
            pfVar9[1] = 0.0;
            pfVar9[2] = 0.0;
            local_d8 = local_24;
          }
        }
        pfVar9[3] = local_d8;
      }
      if (local_d4 == 0) {
        puVar1 = (undefined4 *)(*(int *)((int)this + 0x134) + 0x10 + local_c4);
        *puVar1 = 0x3f800000;
        puVar1[1] = 0;
        puVar1[2] = 0;
        puVar1[3] = local_4;
      }
      else {
        fVar4 = SQRT(local_f4 * local_f4 + local_f0 * local_f0 + local_ec * local_ec);
        if (fVar4 != _DAT_005d856c) {
          fVar4 = _DAT_005d8568 / fVar4;
          local_f4 = fVar4 * local_f4;
          local_f0 = local_f0 * fVar4;
          local_ec = local_ec * fVar4;
        }
        pfVar9 = (float *)(*(int *)((int)this + 0x134) + 0x10 + local_c4);
        *pfVar9 = local_f4;
        pfVar9[1] = local_f0;
        pfVar9[2] = local_ec;
        pfVar9[3] = local_e8;
      }
      local_cc = local_cc + 1;
      local_c4 = local_c4 + 0x60;
    } while (local_cc < *(int *)((int)this + 0xa8));
  }
  return;
}
