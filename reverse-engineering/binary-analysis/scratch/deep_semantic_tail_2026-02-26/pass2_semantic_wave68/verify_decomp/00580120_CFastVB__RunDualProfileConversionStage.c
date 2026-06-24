/* address: 0x00580120 */
/* name: CFastVB__RunDualProfileConversionStage */
/* signature: int __fastcall CFastVB__RunDualProfileConversionStage(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __fastcall CFastVB__RunDualProfileConversionStage(void *param_1)

{
  float fVar1;
  float fVar2;
  int iVar3;
  float fVar4;
  int *ptr;
  int *extraout_EAX;
  void *extraout_EAX_00;
  void *extraout_EAX_01;
  void *pvVar5;
  int *piVar6;
  int *piVar7;
  uint uVar8;
  int iVar9;
  int *piVar10;
  float *pfVar11;
  float *pfVar12;
  int iVar13;
  int unaff_EDI;
  undefined4 *puVar14;
  int *piVar15;
  int *piVar16;
  int local_20;
  int *local_1c;
  int *local_18;
  void *local_10;
  int *local_c;
  int *local_8;

  local_1c = (int *)0x0;
  local_c = (int *)0x0;
  local_18 = (int *)0x0;
  local_10 = (void *)0x0;
  if ((*(int *)(*(int *)((int)param_1 + 4) + 0x1068) != 1) ||
     (*(int *)(*(int *)param_1 + 0x1068) != 1)) {
    return -0x7fffbffb;
  }
  uVar8 = *(uint *)((int)param_1 + 8);
  ptr = CFastVB__Helper_0057cca4
                  (*(uint *)(*(int *)param_1 + 0x1060),*(int *)(*(int *)((int)param_1 + 4) + 0x1060)
                   ,~(uVar8 >> 0x10) & 1);
  if ((ptr == (int *)0x0) ||
     (local_1c = CFastVB__Helper_0057cca4
                           (*(uint *)(*(int *)param_1 + 0x1064),
                            *(int *)(*(int *)((int)param_1 + 4) + 0x1064),~(uVar8 >> 0x11) & 1),
     local_1c == (int *)0x0)) {
    iVar13 = -0x7fffbffb;
  }
  else {
    iVar13 = *ptr;
    iVar3 = *local_1c;
    iVar9 = *(int *)(*(int *)((int)param_1 + 4) + 0x1064);
    CFastVB__Helper_00426fd0(iVar9 * 0xc + 4);
    if (extraout_EAX == (int *)0x0) {
      local_c = (int *)0x0;
    }
    else {
      *extraout_EAX = iVar9;
      local_c = extraout_EAX + 1;
      _vector_constructor_iterator_(local_c,0xc,iVar9,CFastVB__Helper_0057cc8e);
    }
    if (local_c != (int *)0x0) {
      iVar9 = *(int *)(*(int *)param_1 + 0x1060);
      CFastVB__Helper_00426fd0(iVar9 << 4);
      if (extraout_EAX_00 == (void *)0x0) {
        local_10 = (void *)0x0;
      }
      else {
        _vector_constructor_iterator_(extraout_EAX_00,0x10,iVar9,CFastVB__Helper_00574577);
        local_10 = extraout_EAX_00;
      }
      if (local_10 != (void *)0x0) {
        piVar16 = local_1c + 1;
        while (piVar16 < (int *)(iVar3 + (int)local_1c)) {
          piVar10 = (int *)(*piVar16 + (int)piVar16);
          for (piVar6 = piVar16 + 1; piVar16 = piVar10, piVar6 < piVar10; piVar6 = piVar6 + 2) {
            local_c[*piVar6 * 3 + 2] = local_c[*piVar6 * 3 + 2] + 1;
          }
        }
        local_20 = 0;
        piVar16 = local_1c + 1;
        while (piVar16 < (int *)(iVar3 + (int)local_1c)) {
          piVar10 = (int *)(*piVar16 + (int)piVar16);
          piVar16 = piVar16 + 1;
          for (piVar6 = piVar16; piVar6 < piVar10; piVar6 = piVar6 + 2) {
            piVar15 = local_c + *piVar6 * 3;
            if (*piVar15 == 0) {
              if (local_18 == (int *)0x0) {
                iVar9 = *(int *)(*(int *)((int)param_1 + 4) + 0x1060);
                CFastVB__Helper_00426fd0(iVar9 << 4);
                if (extraout_EAX_01 == (void *)0x0) {
                  pvVar5 = (void *)0x0;
                }
                else {
                  _vector_constructor_iterator_(extraout_EAX_01,0x10,iVar9,CFastVB__Helper_00574577)
                  ;
                  pvVar5 = extraout_EAX_01;
                }
                *piVar15 = (int)pvVar5;
                if (pvVar5 == (void *)0x0) goto LAB_005806c4;
              }
              else {
                *piVar15 = *local_18;
                *local_18 = 0;
                local_18 = (int *)local_18[1];
              }
              puVar14 = (undefined4 *)*piVar15;
              for (uVar8 = (uint)(*(int *)(*(int *)((int)param_1 + 4) + 0x1060) << 4) >> 2;
                  uVar8 != 0; uVar8 = uVar8 - 1) {
                *puVar14 = 0;
                puVar14 = puVar14 + 1;
              }
              for (iVar9 = 0; iVar9 != 0; iVar9 = iVar9 + -1) {
                *(undefined1 *)puVar14 = 0;
                puVar14 = (undefined4 *)((int)puVar14 + 1);
              }
            }
          }
          (**(code **)(**(int **)param_1 + 4))(local_20,0,local_10);
          if (ptr + 1 < (int *)(iVar13 + (int)ptr)) {
            pfVar11 = (float *)((int)local_10 + 8);
            piVar6 = ptr + 1;
            do {
              piVar15 = (int *)(*piVar6 + (int)piVar6);
              if (piVar16 < piVar10) {
                local_8 = piVar16;
                do {
                  iVar9 = local_c[*local_8 * 3];
                  for (piVar7 = piVar6 + 1; piVar7 < piVar15; piVar7 = piVar7 + 2) {
                    fVar4 = (float)piVar7[1] * (float)local_8[1];
                    pfVar12 = (float *)(*piVar7 * 0x10 + iVar9);
                    *pfVar12 = fVar4 * pfVar11[-2] + *pfVar12;
                    pfVar12 = (float *)(*piVar7 * 0x10 + 4 + iVar9);
                    *pfVar12 = fVar4 * pfVar11[-1] + *pfVar12;
                    pfVar12 = (float *)(*piVar7 * 0x10 + 8 + iVar9);
                    *pfVar12 = fVar4 * *pfVar11 + *pfVar12;
                    pfVar12 = (float *)(*piVar7 * 0x10 + 0xc + iVar9);
                    *pfVar12 = fVar4 * pfVar11[1] + *pfVar12;
                  }
                  local_8 = local_8 + 2;
                } while (local_8 < piVar10);
              }
              pfVar11 = pfVar11 + 4;
              piVar6 = piVar15;
            } while (piVar15 < (int *)(iVar13 + (int)ptr));
          }
          for (; piVar16 < piVar10; piVar16 = piVar16 + 2) {
            piVar15 = local_c + *piVar16 * 3;
            piVar6 = piVar15 + 2;
            *piVar6 = *piVar6 + -1;
            fVar2 = _DAT_005e6a38;
            fVar4 = _DAT_005e6a34;
            if (*piVar6 == 0) {
              iVar9 = *(int *)(*(int *)param_1 + 8);
              if (iVar9 == 1) {
                iVar9 = 0;
                uVar8 = 0;
                if (*(int *)(*(int *)((int)param_1 + 4) + 0x1060) != 0) {
                  do {
                    pfVar11 = (float *)(*piVar15 + iVar9);
                    if (0.0 <= *pfVar11) {
                      if (fVar4 <= *pfVar11) {
                        fVar2 = 1.0;
                      }
                      else {
                        fVar2 = *pfVar11;
                      }
                    }
                    else {
                      fVar2 = 0.0;
                    }
                    *pfVar11 = fVar2;
                    pfVar11 = (float *)(*piVar15 + 4 + iVar9);
                    if (0.0 <= *pfVar11) {
                      if (fVar4 <= *pfVar11) {
                        fVar2 = 1.0;
                      }
                      else {
                        fVar2 = *pfVar11;
                      }
                    }
                    else {
                      fVar2 = 0.0;
                    }
                    *pfVar11 = fVar2;
                    pfVar11 = (float *)(*piVar15 + 8 + iVar9);
                    if (0.0 <= *pfVar11) {
                      if (fVar4 <= *pfVar11) {
                        fVar2 = 1.0;
                      }
                      else {
                        fVar2 = *pfVar11;
                      }
                    }
                    else {
                      fVar2 = 0.0;
                    }
                    *pfVar11 = fVar2;
                    pfVar11 = (float *)(*piVar15 + 0xc + iVar9);
                    if (0.0 <= *pfVar11) {
                      if (fVar4 <= *pfVar11) {
                        fVar2 = 1.0;
                      }
                      else {
                        fVar2 = *pfVar11;
                      }
                    }
                    else {
                      fVar2 = 0.0;
                    }
                    *pfVar11 = fVar2;
                    uVar8 = uVar8 + 1;
                    iVar9 = iVar9 + 0x10;
                  } while (uVar8 < *(uint *)(*(int *)((int)param_1 + 4) + 0x1060));
                }
              }
              else if (iVar9 == 2) {
                iVar9 = 0;
                uVar8 = 0;
                if (*(int *)(*(int *)((int)param_1 + 4) + 0x1060) != 0) {
                  do {
                    pfVar11 = (float *)(*piVar15 + iVar9);
                    fVar1 = fVar2;
                    if (fVar2 <= *pfVar11) {
                      if (fVar4 <= *pfVar11) {
                        fVar1 = 1.0;
                      }
                      else {
                        fVar1 = *pfVar11;
                      }
                    }
                    *pfVar11 = fVar1;
                    pfVar11 = (float *)(*piVar15 + 4 + iVar9);
                    fVar1 = fVar2;
                    if (fVar2 <= *pfVar11) {
                      if (fVar4 <= *pfVar11) {
                        fVar1 = 1.0;
                      }
                      else {
                        fVar1 = *pfVar11;
                      }
                    }
                    *pfVar11 = fVar1;
                    pfVar11 = (float *)(*piVar15 + 8 + iVar9);
                    fVar1 = fVar2;
                    if (fVar2 <= *pfVar11) {
                      if (fVar4 <= *pfVar11) {
                        fVar1 = 1.0;
                      }
                      else {
                        fVar1 = *pfVar11;
                      }
                    }
                    *pfVar11 = fVar1;
                    pfVar11 = (float *)(*piVar15 + 0xc + iVar9);
                    if (0.0 <= *pfVar11) {
                      if (fVar4 <= *pfVar11) {
                        fVar1 = 1.0;
                      }
                      else {
                        fVar1 = *pfVar11;
                      }
                    }
                    else {
                      fVar1 = 0.0;
                    }
                    *pfVar11 = fVar1;
                    uVar8 = uVar8 + 1;
                    iVar9 = iVar9 + 0x10;
                  } while (uVar8 < *(uint *)(*(int *)((int)param_1 + 4) + 0x1060));
                }
              }
              else if (iVar9 == 3) {
                iVar9 = 0;
                uVar8 = 0;
                if (*(int *)(*(int *)((int)param_1 + 4) + 0x1060) != 0) {
                  do {
                    pfVar11 = (float *)(*piVar15 + iVar9);
                    fVar1 = fVar2;
                    if (fVar2 <= *pfVar11) {
                      if (fVar4 <= *pfVar11) {
                        fVar1 = 1.0;
                      }
                      else {
                        fVar1 = *pfVar11;
                      }
                    }
                    *pfVar11 = fVar1;
                    pfVar11 = (float *)(*piVar15 + 4 + iVar9);
                    fVar1 = fVar2;
                    if (fVar2 <= *pfVar11) {
                      if (fVar4 <= *pfVar11) {
                        fVar1 = 1.0;
                      }
                      else {
                        fVar1 = *pfVar11;
                      }
                    }
                    *pfVar11 = fVar1;
                    pfVar11 = (float *)(*piVar15 + 8 + iVar9);
                    fVar1 = fVar2;
                    if (fVar2 <= *pfVar11) {
                      if (fVar4 <= *pfVar11) {
                        fVar1 = 1.0;
                      }
                      else {
                        fVar1 = *pfVar11;
                      }
                    }
                    *pfVar11 = fVar1;
                    pfVar11 = (float *)(*piVar15 + 0xc + iVar9);
                    fVar1 = fVar2;
                    if (fVar2 <= *pfVar11) {
                      if (fVar4 <= *pfVar11) {
                        fVar1 = 1.0;
                      }
                      else {
                        fVar1 = *pfVar11;
                      }
                    }
                    *pfVar11 = fVar1;
                    uVar8 = uVar8 + 1;
                    iVar9 = iVar9 + 0x10;
                  } while (uVar8 < *(uint *)(*(int *)((int)param_1 + 4) + 0x1060));
                }
              }
              (**(code **)(**(int **)((int)param_1 + 4) + 8))(*piVar16,0,*piVar15);
              piVar15[1] = (int)local_18;
              local_18 = piVar15;
            }
          }
          local_20 = local_20 + 1;
          piVar16 = piVar10;
        }
        iVar13 = 0;
        goto LAB_005806d0;
      }
    }
LAB_005806c4:
    iVar13 = -0x7ff8fff2;
  }
LAB_005806d0:
  if (local_c != (int *)0x0) {
    CFastVB__Helper_0057fa10(local_c,(void *)0x3,unaff_EDI);
  }
  OID__FreeObject_Callback(local_1c);
  OID__FreeObject_Callback(ptr);
  OID__FreeObject_Callback(local_10);
  OID__FreeObject_Callback((void *)0x0);
  return iVar13;
}
