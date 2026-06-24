/* address: 0x004a5670 */
/* name: CMesh__OptimizeTextures */
/* signature: void __fastcall CMesh__OptimizeTextures(void * param_1) */


void __fastcall CMesh__OptimizeTextures(void *param_1)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  float *pfVar10;
  int *piVar11;
  int iVar12;
  int iVar13;
  int *piVar14;
  int iVar15;
  int local_140;
  int local_138;
  int local_134;
  int local_130;
  int local_12c;
  int local_128;
  char local_100 [256];

  local_138 = 0;
  if (0 < *(int *)((int)param_1 + 4)) {
    local_140 = 0;
    do {
      iVar2 = local_140;
      local_128 = -1;
      local_130 = 0;
      if (0 < local_140) {
        piVar11 = *(int **)param_1;
        iVar15 = *(int *)(local_140 + 8 + (int)piVar11);
        piVar14 = piVar11;
        do {
          if ((iVar15 == piVar14[2]) && (*(int *)(local_140 + (int)piVar11) == *piVar14)) {
            bVar1 = true;
            if (0 < iVar15) {
              pfVar10 = (float *)piVar14[3];
              iVar3 = *(int *)(local_140 + 0xc + (int)piVar11) - (int)pfVar10;
              iVar4 = piVar14[5] - (int)pfVar10;
              iVar12 = *(int *)(local_140 + 0x10 + (int)piVar11) - (int)pfVar10;
              iVar13 = piVar14[4] - (int)pfVar10;
              iVar5 = *(int *)(local_140 + 0x18 + (int)piVar11) - (int)pfVar10;
              iVar9 = *(int *)(local_140 + 0x14 + (int)piVar11) - (int)pfVar10;
              iVar6 = piVar14[6] - (int)pfVar10;
              iVar7 = *(int *)(local_140 + 0x1c + (int)piVar11) - (int)pfVar10;
              iVar8 = piVar14[7] - (int)pfVar10;
              local_134 = iVar15;
              do {
                if (*(float *)(iVar3 + (int)pfVar10) != *pfVar10) {
                  bVar1 = false;
                }
                if (*(float *)(iVar12 + (int)pfVar10) != *(float *)((int)pfVar10 + iVar13)) {
                  bVar1 = false;
                }
                if (*(float *)(iVar9 + (int)pfVar10) != *(float *)(iVar4 + (int)pfVar10)) {
                  bVar1 = false;
                }
                if (*(float *)(iVar5 + (int)pfVar10) != *(float *)(iVar6 + (int)pfVar10)) {
                  bVar1 = false;
                }
                if (*(float *)(iVar7 + (int)pfVar10) != *(float *)(iVar8 + (int)pfVar10)) {
                  bVar1 = false;
                }
                pfVar10 = pfVar10 + 1;
                local_134 = local_134 + -1;
              } while (local_134 != 0);
            }
            if (bVar1) {
              local_128 = local_130;
            }
          }
          local_130 = local_130 + 1;
          piVar14 = piVar14 + 9;
        } while (local_130 < local_138);
        if (local_128 != -1) {
          iVar15 = 0;
          local_134 = 0;
          if (0 < *(int *)((int)param_1 + 0x15c)) {
            do {
              local_12c = 0;
              if (0 < *(int *)(*(int *)(iVar15 + *(int *)((int)param_1 + 0x160)) + 0xa8)) {
                local_140 = 0x30;
                do {
                  local_130 = 6;
                  iVar3 = local_140;
                  do {
                    piVar11 = (int *)(*(int *)((int)param_1 + 0x160) + iVar15);
                    if (*(int *)(*(int *)(*piVar11 + 0x134) + iVar3) == local_138) {
                      *(int *)(*(int *)(*piVar11 + 0x134) + iVar3) = local_128;
                    }
                    iVar3 = iVar3 + 4;
                    local_130 = local_130 + -1;
                  } while (local_130 != 0);
                  local_140 = local_140 + 0x60;
                  local_12c = local_12c + 1;
                } while (local_12c <
                         *(int *)(*(int *)(iVar15 + *(int *)((int)param_1 + 0x160)) + 0xa8));
              }
              local_134 = local_134 + 1;
              iVar15 = iVar15 + 4;
            } while (local_134 < *(int *)((int)param_1 + 0x15c));
          }
        }
      }
      local_138 = local_138 + 1;
      local_140 = iVar2 + 0x24;
    } while (local_138 < *(int *)((int)param_1 + 4));
  }
  sprintf(local_100,s_OptimiseTextures___reduced_textu_0062fa9c);
  DebugTrace(local_100);
  return;
}
