/* address: 0x004ab360 */
/* name: CMesh__OptimizeParts */
/* signature: undefined CMesh__OptimizeParts(void) */


void __fastcall CMesh__OptimizeParts(int param_1)

{
  int iVar1;
  float fVar2;
  float fVar3;
  bool bVar4;
  bool bVar5;
  int iVar6;
  int *piVar7;
  int iVar8;
  int *piVar9;
  undefined3 extraout_var;
  float *pfVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  float *pfVar15;
  float *pfVar16;
  bool bVar17;
  int local_298;
  int local_294;
  int *local_290;
  int local_28c;
  int local_288;
  int local_284;
  float local_274;
  float local_240 [4];
  float local_230;
  float local_22c;
  float local_228;
  float local_220;
  float local_21c;
  float local_218;
  float local_20c;
  float local_208;
  char local_200 [256];
  char local_100 [256];

  DAT_00704af0 = DAT_00704af0 + *(int *)(param_1 + 0x15c);
  sprintf(local_200,s_Optimising_mesh__s_parts_0062fe04);
  DebugTrace(local_200);
  iVar6 = *(int *)(param_1 + 0x15c);
  local_288 = 0;
  if (0 < iVar6) {
    local_298 = 0;
    do {
      local_294 = 0;
      if (0 < iVar6) {
        do {
          iVar6 = *(int *)(param_1 + 0x160);
          if (((*(int *)(*(int *)(local_298 + iVar6) + 0x8c) == 1) &&
              (iVar8 = *(int *)(iVar6 + local_294 * 4), *(int *)(iVar8 + 0x8c) == 1)) &&
             (local_288 != local_294)) {
            iVar6 = *(int *)(local_298 + iVar6);
            if ((*(int *)(iVar6 + 0xbc) == 1) || (*(int *)(iVar8 + 0xbc) == 1)) {
              bVar4 = false;
              for (; iVar6 != 0; iVar6 = *(int *)(iVar6 + 0x98)) {
                for (iVar8 = *(int *)(*(int *)(param_1 + 0x160) + local_294 * 4); iVar8 != 0;
                    iVar8 = *(int *)(iVar8 + 0x98)) {
                  if (iVar6 == iVar8) {
                    bVar4 = true;
                  }
                  iVar12 = CMeshPart__CanMergeInOptimizePass(iVar8);
                  if ((iVar12 == 0) || (1 < *(int *)(iVar8 + 0xbc))) break;
                }
                iVar8 = CMeshPart__CanMergeInOptimizePass(iVar6);
                if ((iVar8 == 0) || (1 < *(int *)(iVar6 + 0xbc))) break;
              }
            }
            else {
              bVar4 = false;
            }
            local_290 = *(int **)(param_1 + 0x160);
            iVar6 = *(int *)(local_298 + (int)local_290);
            if (*(int *)(iVar6 + 0xa4) != 0) {
              bVar4 = false;
            }
            iVar8 = local_290[local_294];
            if (*(int *)(iVar8 + 0xa4) != 0) {
              bVar4 = false;
            }
            if (*(int *)(iVar6 + 0xb4) != 1) {
              bVar4 = false;
            }
            if (*(int *)(iVar8 + 0xb4) != 1) {
              bVar4 = false;
            }
            local_28c = *(int *)(param_1 + 0x15c);
            if (0 < local_28c) {
              do {
                iVar12 = *local_290;
                if (*(int *)(iVar12 + 0x8c) == 6) {
                  if (*(int *)(iVar12 + 0x124) == iVar6) {
                    bVar4 = false;
                  }
                  if (*(int *)(iVar12 + 0x124) == iVar8) {
                    bVar4 = false;
                  }
                }
                if ((*(int *)(iVar12 + 0x8c) == 3) && (iVar14 = *(int *)(iVar12 + 0xc0), 0 < iVar14)
                   ) {
                  piVar9 = *(int **)(iVar12 + 0xd0);
                  do {
                    if (*piVar9 == iVar6) {
                      bVar4 = false;
                    }
                    if (*piVar9 == iVar8) {
                      bVar4 = false;
                    }
                    piVar9 = piVar9 + 1;
                    iVar14 = iVar14 + -1;
                  } while (iVar14 != 0);
                }
                local_290 = local_290 + 1;
                local_28c = local_28c + -1;
              } while (local_28c != 0);
            }
            iVar6 = CMeshPart__CanOptimizePart_Strict(iVar8);
            if (iVar6 == 0) {
              bVar4 = false;
            }
            iVar6 = CMeshPart__CanMergeInOptimizePass
                              (*(int *)(*(int *)(param_1 + 0x160) + local_298));
            if (iVar6 == 0) {
              bVar4 = false;
            }
            iVar6 = stricmp((char *)(*(int *)(*(int *)(param_1 + 0x160) + local_298) + 0xdc),
                            s_Nexus_0062fdfc);
            if (iVar6 == 0) {
              bVar4 = false;
            }
            iVar6 = stricmp((char *)(*(int *)(*(int *)(param_1 + 0x160) + local_294 * 4) + 0xdc),
                            s_Nexus_0062fdfc);
            if ((iVar6 != 0) && (bVar4)) {
              CMeshPart__Merge(*(undefined4 *)(*(int *)(param_1 + 0x160) + local_294 * 4));
              *(undefined4 *)(*(int *)(*(int *)(param_1 + 0x160) + local_294 * 4) + 0xac) = 0;
              *(undefined4 *)(*(int *)(*(int *)(param_1 + 0x160) + local_294 * 4) + 0xa8) = 0;
              *(undefined4 *)(*(int *)(*(int *)(param_1 + 0x160) + local_294 * 4) + 0xb0) = 0;
              *(undefined4 *)(*(int *)(*(int *)(param_1 + 0x160) + local_294 * 4) + 0x8c) = 2;
            }
          }
          local_294 = local_294 + 1;
        } while (local_294 < *(int *)(param_1 + 0x15c));
      }
      iVar6 = *(int *)(param_1 + 0x15c);
      local_288 = local_288 + 1;
      local_298 = local_298 + 4;
    } while (local_288 < iVar6);
  }
  do {
    local_28c = *(int *)(param_1 + 0x15c);
    iVar6 = 0;
    bVar4 = true;
    local_288 = 0;
    if (local_28c < 1) break;
    local_290 = (int *)0x1;
    do {
      piVar9 = *(int **)(param_1 + 0x160);
      iVar8 = *(int *)((int)piVar9 + iVar6);
      if ((*(int *)(iVar8 + 0x8c) == 2) &&
         ((*(int *)(iVar8 + 0x98) != 0 || (*(int *)(iVar8 + 0x90) == 1)))) {
        bVar17 = *(int *)(iVar8 + 0xa4) == 0;
        if (0 < local_28c) {
          do {
            iVar12 = *piVar9;
            if ((*(int *)(iVar12 + 0x8c) == 6) && (*(int *)(iVar12 + 0x124) == iVar8)) {
              bVar17 = false;
            }
            if ((*(int *)(iVar12 + 0x8c) == 3) && (iVar14 = *(int *)(iVar12 + 0xc0), 0 < iVar14)) {
              piVar7 = *(int **)(iVar12 + 0xd0);
              do {
                if (*piVar7 == iVar8) {
                  bVar17 = false;
                }
                piVar7 = piVar7 + 1;
                iVar14 = iVar14 + -1;
              } while (iVar14 != 0);
            }
            piVar9 = piVar9 + 1;
            local_28c = local_28c + -1;
          } while (local_28c != 0);
        }
        iVar8 = stricmp((char *)(iVar8 + 0xdc),s_Nexus_0062fdfc);
        if (iVar8 == 0) {
          bVar17 = false;
        }
        iVar8 = *(int *)(*(int *)(param_1 + 0x160) + iVar6);
        if ((1 < *(int *)(iVar8 + 0xbc)) && (0 < *(int *)(iVar8 + 0x90))) {
          bVar17 = false;
        }
        iVar12 = *(int *)(param_1 + 0x1c);
        if (0 < iVar12) {
          piVar9 = (int *)(*(int *)(param_1 + 0x20) + 0x40);
          do {
            if (*piVar9 == iVar8) {
              bVar17 = false;
            }
            piVar9 = piVar9 + 0x54;
            iVar12 = iVar12 + -1;
          } while (iVar12 != 0);
        }
        iVar8 = CMeshPart__CanOptimizePart_Strict(iVar8);
        if (iVar8 == 0) {
          bVar17 = false;
        }
        if (((*(int *)(*(int *)(*(int *)(param_1 + 0x160) + iVar6) + 0x98) != 0) ||
            (bVar5 = CMesh__HasSpecialOptimizationConstraints(param_1),
            CONCAT31(extraout_var,bVar5) == 0)) && (bVar17)) {
          sprintf(local_100,s_Removing_part__s_0062fde8);
          DebugTrace(local_100);
          iVar8 = *(int *)(param_1 + 0x160);
          local_294 = 0;
          if (0 < *(int *)(*(int *)(iVar8 + iVar6) + 0x90)) {
            do {
              local_284 = 0;
              iVar8 = *(int *)(*(int *)(*(int *)(iVar8 + iVar6) + 0x94) + local_294 * 4);
              if (0 < *(int *)(iVar8 + 0xbc)) {
                local_28c = 0;
                local_298 = 0;
                do {
                  pfVar10 = (float *)(*(int *)(iVar8 + 200) + local_298);
                  iVar12 = *(int *)(*(int *)(param_1 + 0x160) + iVar6);
                  pfVar16 = *(float **)(iVar12 + 0x10c);
                  local_20c = pfVar16[4] * *pfVar10 +
                              pfVar16[5] * pfVar10[1] + pfVar16[6] * pfVar10[2];
                  pfVar15 = *(float **)(iVar12 + 200);
                  local_208 = pfVar16[8] * *pfVar10 +
                              pfVar16[9] * pfVar10[1] + pfVar16[10] * pfVar10[2];
                  fVar2 = pfVar15[1];
                  fVar3 = pfVar15[2];
                  *pfVar10 = *pfVar10 * *pfVar16 + pfVar16[1] * pfVar10[1] + pfVar16[2] * pfVar10[2]
                             + *pfVar15;
                  pfVar10[1] = local_20c + fVar2;
                  pfVar10[2] = local_208 + fVar3;
                  pfVar10[3] = local_274;
                  pfVar16 = (float *)(*(int *)(iVar8 + 0x10c) + local_28c);
                  pfVar15 = *(float **)(*(int *)(*(int *)(param_1 + 0x160) + iVar6) + 0x10c);
                  local_240[0] = pfVar15[1] * pfVar16[4] +
                                 *pfVar15 * *pfVar16 + pfVar16[8] * pfVar15[2];
                  local_240[1] = pfVar15[1] * pfVar16[5] +
                                 pfVar15[2] * pfVar16[9] + *pfVar15 * pfVar16[1];
                  local_240[2] = *pfVar15 * pfVar16[2] +
                                 pfVar15[1] * pfVar16[6] + pfVar15[2] * pfVar16[10];
                  local_22c = pfVar15[5] * pfVar16[5] +
                              pfVar15[6] * pfVar16[9] + pfVar16[1] * pfVar15[4];
                  local_230 = pfVar15[5] * pfVar16[4] +
                              *pfVar16 * pfVar15[4] + pfVar15[6] * pfVar16[8];
                  local_228 = pfVar16[2] * pfVar15[4] +
                              pfVar15[5] * pfVar16[6] + pfVar15[6] * pfVar16[10];
                  local_21c = pfVar16[1] * pfVar15[8] +
                              pfVar16[5] * pfVar15[9] + pfVar16[9] * pfVar15[10];
                  local_220 = pfVar16[8] * pfVar15[10] +
                              pfVar16[4] * pfVar15[9] + *pfVar16 * pfVar15[8];
                  local_218 = pfVar16[6] * pfVar15[9] +
                              pfVar15[10] * pfVar16[10] + pfVar16[2] * pfVar15[8];
                  pfVar15 = local_240;
                  for (iVar12 = 0xc; iVar12 != 0; iVar12 = iVar12 + -1) {
                    *pfVar16 = *pfVar15;
                    pfVar15 = pfVar15 + 1;
                    pfVar16 = pfVar16 + 1;
                  }
                  local_284 = local_284 + 1;
                  local_298 = local_298 + 0x10;
                  local_28c = local_28c + 0x30;
                } while (local_284 < *(int *)(iVar8 + 0xbc));
              }
              iVar8 = *(int *)(param_1 + 0x160);
              local_294 = local_294 + 1;
            } while (local_294 < *(int *)(*(int *)(iVar8 + iVar6) + 0x90));
          }
          iVar12 = 0;
          iVar8 = *(int *)(*(int *)(param_1 + 0x160) + iVar6);
          if (0 < *(int *)(iVar8 + 0x90)) {
            do {
              iVar14 = iVar12 * 4;
              iVar12 = iVar12 + 1;
              *(undefined4 *)(*(int *)(*(int *)(iVar8 + 0x94) + iVar14) + 0x98) =
                   *(undefined4 *)(iVar8 + 0x98);
              iVar8 = *(int *)(*(int *)(param_1 + 0x160) + iVar6);
            } while (iVar12 < *(int *)(iVar8 + 0x90));
          }
          piVar9 = *(int **)(param_1 + 0x160);
          iVar8 = *(int *)(*(int *)((int)piVar9 + iVar6) + 0x98);
          if (iVar8 == 0) {
            iVar8 = *(int *)(**(int **)(*piVar9 + 0x94) + 0x88);
            *piVar9 = **(int **)(*piVar9 + 0x94);
            iVar8 = iVar8 + 1;
            *(undefined4 *)(**(int **)(param_1 + 0x160) + 0x88) = 0;
            if (iVar8 < *(int *)(param_1 + 0x15c)) {
              do {
                *(undefined4 *)(*(int *)(param_1 + 0x160) + iVar8 * 4 + -4) =
                     *(undefined4 *)(*(int *)(param_1 + 0x160) + iVar8 * 4);
                iVar12 = *(int *)(*(int *)(param_1 + 0x160) + -4 + iVar8 * 4);
                iVar8 = iVar8 + 1;
                *(int *)(iVar12 + 0x88) = *(int *)(iVar12 + 0x88) + -1;
              } while (iVar8 < *(int *)(param_1 + 0x15c));
            }
          }
          else {
            iVar12 = *(int *)(iVar8 + 0x90);
            iVar14 = 0;
            if (0 < iVar12) {
              local_298 = 1;
              do {
                if (*(int *)(*(int *)(iVar8 + 0x94) + iVar14 * 4) ==
                    *(int *)(*(int *)(param_1 + 0x160) + iVar6)) {
                  iVar11 = local_298;
                  if (local_298 < iVar12) {
                    do {
                      iVar12 = iVar11 * 4;
                      iVar1 = iVar11 * 4;
                      iVar11 = iVar11 + 1;
                      *(undefined4 *)(*(int *)(iVar8 + 0x94) + iVar1 + -4) =
                           *(undefined4 *)(*(int *)(iVar8 + 0x94) + iVar12);
                    } while (iVar11 < *(int *)(iVar8 + 0x90));
                  }
                  iVar14 = iVar14 + -1;
                  local_298 = local_298 + -1;
                  *(int *)(iVar8 + 0x90) = *(int *)(iVar8 + 0x90) + -1;
                }
                iVar14 = iVar14 + 1;
                local_298 = local_298 + 1;
                iVar12 = *(int *)(iVar8 + 0x90);
              } while (iVar14 < iVar12);
            }
            iVar12 = OID__AllocObject((*(int *)(*(int *)(*(int *)(param_1 + 0x160) + iVar6) + 0x90)
                                      + *(int *)(iVar8 + 0x90)) * 4,1,
                                      s_C__dev_ONSLAUGHT2_mesh_cpp_0062f8e8,0xe56);
            iVar14 = 0;
            if (0 < *(int *)(iVar8 + 0x90)) {
              do {
                iVar14 = iVar14 + 1;
                *(undefined4 *)(iVar12 + -4 + iVar14 * 4) =
                     *(undefined4 *)(*(int *)(iVar8 + 0x94) + -4 + iVar14 * 4);
              } while (iVar14 < *(int *)(iVar8 + 0x90));
            }
            iVar11 = 0;
            iVar14 = *(int *)(*(int *)(param_1 + 0x160) + iVar6);
            if (0 < *(int *)(iVar14 + 0x90)) {
              do {
                iVar13 = *(int *)(iVar8 + 0x90) + iVar11;
                iVar1 = iVar11 * 4;
                iVar11 = iVar11 + 1;
                *(undefined4 *)(iVar12 + iVar13 * 4) =
                     *(undefined4 *)(*(int *)(iVar14 + 0x94) + iVar1);
                iVar14 = *(int *)(*(int *)(param_1 + 0x160) + iVar6);
              } while (iVar11 < *(int *)(iVar14 + 0x90));
            }
            if (*(void **)(iVar8 + 0x94) != (void *)0x0) {
              OID__FreeObject(*(void **)(iVar8 + 0x94));
              *(undefined4 *)(iVar8 + 0x94) = 0;
            }
            *(int *)(iVar8 + 0x94) = iVar12;
            *(int *)(iVar8 + 0x90) =
                 *(int *)(iVar8 + 0x90) +
                 *(int *)(*(int *)(*(int *)(param_1 + 0x160) + iVar6) + 0x90);
            piVar9 = local_290;
            if ((int)local_290 < *(int *)(param_1 + 0x15c)) {
              do {
                *(undefined4 *)(*(int *)(param_1 + 0x160) + (int)piVar9 * 4 + -4) =
                     *(undefined4 *)(*(int *)(param_1 + 0x160) + (int)piVar9 * 4);
                iVar8 = *(int *)(*(int *)(param_1 + 0x160) + -4 + (int)piVar9 * 4);
                piVar9 = (int *)((int)piVar9 + 1);
                *(int *)(iVar8 + 0x88) = *(int *)(iVar8 + 0x88) + -1;
              } while ((int)piVar9 < *(int *)(param_1 + 0x15c));
            }
          }
          DAT_00704af4 = DAT_00704af4 + 1;
          local_288 = local_288 + -1;
          iVar6 = iVar6 + -4;
          local_290 = (int *)((int)local_290 + -1);
          bVar4 = false;
          *(int *)(param_1 + 0x15c) = *(int *)(param_1 + 0x15c) + -1;
        }
      }
      local_28c = *(int *)(param_1 + 0x15c);
      local_288 = local_288 + 1;
      iVar6 = iVar6 + 4;
      local_290 = (int *)((int)local_290 + 1);
    } while (local_288 < local_28c);
  } while (!bVar4);
  sprintf(local_200,s_OptimiseParts___removed__d_of__d_0062fdb8);
  DebugTrace(local_200);
  return;
}
