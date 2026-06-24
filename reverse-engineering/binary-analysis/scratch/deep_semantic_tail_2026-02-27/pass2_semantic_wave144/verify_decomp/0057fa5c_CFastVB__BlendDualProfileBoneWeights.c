/* address: 0x0057fa5c */
/* name: CFastVB__BlendDualProfileBoneWeights */
/* signature: int __fastcall CFastVB__BlendDualProfileBoneWeights(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __fastcall CFastVB__BlendDualProfileBoneWeights(void *param_1)

{
  float fVar1;
  float fVar2;
  int iVar3;
  int iVar4;
  int *ptr;
  int *extraout_EAX;
  void *extraout_EAX_00;
  void *extraout_EAX_01;
  void *pvVar5;
  int *piVar6;
  int iVar7;
  int iVar8;
  int *piVar9;
  uint uVar10;
  int iVar11;
  int *piVar12;
  int *piVar13;
  float *pfVar14;
  int *piVar15;
  int *piVar16;
  int iVar17;
  int unaff_EDI;
  undefined4 *puVar18;
  float *pfVar19;
  int local_38;
  int local_2c;
  int *local_28;
  int *local_20;
  int *local_1c;
  int *local_18;
  void *local_10;
  int *local_c;
  int *local_8;

  uVar10 = *(uint *)((int)param_1 + 8);
  local_20 = (int *)0x0;
  local_1c = (int *)0x0;
  local_c = (int *)0x0;
  local_18 = (int *)0x0;
  local_10 = (void *)0x0;
  ptr = CFastVB__Helper_0057cca4
                  (*(uint *)(*(int *)param_1 + 0x1060),*(int *)(*(int *)((int)param_1 + 4) + 0x1060)
                   ,~(uVar10 >> 0x10) & 1);
  if (((ptr == (int *)0x0) ||
      (local_20 = CFastVB__Helper_0057cca4
                            (*(uint *)(*(int *)param_1 + 0x1064),
                             *(int *)(*(int *)((int)param_1 + 4) + 0x1064),~(uVar10 >> 0x11) & 1),
      local_20 == (int *)0x0)) ||
     (local_1c = CFastVB__Helper_0057cca4
                           (*(uint *)(*(int *)param_1 + 0x1068),
                            *(int *)(*(int *)((int)param_1 + 4) + 0x1068),~(uVar10 >> 0x12) & 1),
     local_1c == (int *)0x0)) {
    iVar17 = -0x7fffbffb;
  }
  else {
    iVar17 = *ptr;
    iVar3 = *local_20;
    iVar4 = *local_1c;
    iVar11 = *(int *)(*(int *)((int)param_1 + 4) + 0x1068);
    CFastVB__Helper_00426fd0(iVar11 * 0xc + 4);
    if (extraout_EAX == (int *)0x0) {
      local_c = (int *)0x0;
    }
    else {
      *extraout_EAX = iVar11;
      local_c = extraout_EAX + 1;
      _vector_constructor_iterator_(local_c,0xc,iVar11,CFastVB__Helper_0057cc8e);
    }
    if (local_c != (int *)0x0) {
      iVar11 = *(int *)(*(int *)param_1 + 0x1060);
      CFastVB__Helper_00426fd0(iVar11 << 4);
      if (extraout_EAX_00 == (void *)0x0) {
        local_10 = (void *)0x0;
      }
      else {
        _vector_constructor_iterator_(extraout_EAX_00,0x10,iVar11,CFastVB__Helper_00574577);
        local_10 = extraout_EAX_00;
      }
      if (local_10 != (void *)0x0) {
        piVar16 = local_1c + 1;
        while (piVar16 < (int *)(iVar4 + (int)local_1c)) {
          piVar13 = (int *)(*piVar16 + (int)piVar16);
          for (piVar9 = piVar16 + 1; piVar16 = piVar13, piVar9 < piVar13; piVar9 = piVar9 + 2) {
            local_c[*piVar9 * 3 + 2] = local_c[*piVar9 * 3 + 2] + 1;
          }
        }
        local_38 = 0;
        piVar16 = local_1c + 1;
        fVar2 = _DAT_005e6a38;
        while (piVar16 < (int *)(iVar4 + (int)local_1c)) {
          piVar13 = (int *)(*piVar16 + (int)piVar16);
          piVar16 = piVar16 + 1;
          for (piVar9 = piVar16; piVar9 < piVar13; piVar9 = piVar9 + 2) {
            piVar6 = local_c + *piVar9 * 3;
            if (*piVar6 == 0) {
              if (local_18 == (int *)0x0) {
                iVar11 = *(int *)(*(int *)((int)param_1 + 4) + 0x1064) *
                         *(int *)(*(int *)((int)param_1 + 4) + 0x1060);
                CFastVB__Helper_00426fd0(iVar11 * 0x10);
                if (extraout_EAX_01 == (void *)0x0) {
                  pvVar5 = (void *)0x0;
                }
                else {
                  _vector_constructor_iterator_
                            (extraout_EAX_01,0x10,iVar11,CFastVB__Helper_00574577);
                  pvVar5 = extraout_EAX_01;
                }
                *piVar6 = (int)pvVar5;
                fVar2 = _DAT_005e6a38;
                if (pvVar5 == (void *)0x0) goto LAB_005800d5;
              }
              else {
                *piVar6 = *local_18;
                *local_18 = 0;
                local_18 = (int *)local_18[1];
              }
              puVar18 = (undefined4 *)*piVar6;
              for (uVar10 = (uint)(*(int *)(*(int *)((int)param_1 + 4) + 0x1064) *
                                   *(int *)(*(int *)((int)param_1 + 4) + 0x1060) * 0x10) >> 2;
                  uVar10 != 0; uVar10 = uVar10 - 1) {
                *puVar18 = 0;
                puVar18 = puVar18 + 1;
              }
              for (iVar11 = 0; iVar11 != 0; iVar11 = iVar11 + -1) {
                *(undefined1 *)puVar18 = 0;
                puVar18 = (undefined4 *)((int)puVar18 + 1);
              }
            }
          }
          local_2c = 0;
          piVar9 = local_20 + 1;
          while (piVar9 < (int *)(iVar3 + (int)local_20)) {
            iVar11 = *piVar9;
            (**(code **)(**(int **)param_1 + 4))(local_2c,local_38,local_10);
            if (ptr + 1 < (int *)(iVar17 + (int)ptr)) {
              pfVar14 = (float *)((int)local_10 + 8);
              local_28 = ptr + 1;
              do {
                piVar6 = (int *)(*local_28 + (int)local_28);
                for (local_8 = piVar16; local_8 < piVar13; local_8 = local_8 + 2) {
                  for (piVar15 = piVar9 + 1; piVar15 < (int *)(iVar11 + (int)piVar9);
                      piVar15 = piVar15 + 2) {
                    iVar7 = *(int *)(*(int *)((int)param_1 + 4) + 0x1060) * *piVar15 * 0x10 +
                            local_c[*local_8 * 3];
                    for (piVar12 = local_28 + 1; piVar12 < piVar6; piVar12 = piVar12 + 2) {
                      fVar2 = (float)piVar12[1] * (float)piVar15[1] * (float)local_8[1];
                      pfVar19 = (float *)(*piVar12 * 0x10 + iVar7);
                      *pfVar19 = fVar2 * pfVar14[-2] + *pfVar19;
                      pfVar19 = (float *)(*piVar12 * 0x10 + 4 + iVar7);
                      *pfVar19 = fVar2 * pfVar14[-1] + *pfVar19;
                      pfVar19 = (float *)(*piVar12 * 0x10 + 8 + iVar7);
                      *pfVar19 = fVar2 * *pfVar14 + *pfVar19;
                      pfVar19 = (float *)(*piVar12 * 0x10 + 0xc + iVar7);
                      *pfVar19 = fVar2 * pfVar14[1] + *pfVar19;
                    }
                  }
                }
                pfVar14 = pfVar14 + 4;
                local_28 = piVar6;
              } while (piVar6 < (int *)(iVar17 + (int)ptr));
            }
            local_2c = local_2c + 1;
            piVar9 = (int *)(iVar11 + (int)piVar9);
            fVar2 = _DAT_005e6a38;
          }
          for (; piVar16 < piVar13; piVar16 = piVar16 + 2) {
            piVar6 = local_c + *piVar16 * 3;
            piVar9 = piVar6 + 2;
            *piVar9 = *piVar9 + -1;
            if (*piVar9 == 0) {
              iVar11 = *(int *)((int)param_1 + 4);
              local_8 = (int *)0x0;
              if (*(int *)(iVar11 + 0x1064) != 0) {
                do {
                  fVar1 = _DAT_005e6a34;
                  iVar11 = *(int *)(iVar11 + 0x1060);
                  iVar7 = *(int *)(*(int *)param_1 + 8);
                  iVar8 = iVar11 * (int)local_8 * 0x10 + *piVar6;
                  if (iVar7 == 1) {
                    uVar10 = 0;
                    if (iVar11 != 0) {
                      pfVar14 = (float *)(iVar8 + 8);
                      do {
                        if (0.0 <= pfVar14[-2]) {
                          if (fVar1 <= pfVar14[-2]) {
                            fVar2 = 1.0;
                          }
                          else {
                            fVar2 = pfVar14[-2];
                          }
                        }
                        else {
                          fVar2 = 0.0;
                        }
                        pfVar14[-2] = fVar2;
                        if (0.0 <= pfVar14[-1]) {
                          if (fVar1 <= pfVar14[-1]) {
                            fVar2 = 1.0;
                          }
                          else {
                            fVar2 = pfVar14[-1];
                          }
                        }
                        else {
                          fVar2 = 0.0;
                        }
                        pfVar14[-1] = fVar2;
                        if (0.0 <= *pfVar14) {
                          if (fVar1 <= *pfVar14) {
                            fVar2 = 1.0;
                          }
                          else {
                            fVar2 = *pfVar14;
                          }
                        }
                        else {
                          fVar2 = 0.0;
                        }
                        *pfVar14 = fVar2;
                        if (0.0 <= pfVar14[1]) {
                          if (fVar1 <= pfVar14[1]) {
                            fVar2 = 1.0;
                          }
                          else {
                            fVar2 = pfVar14[1];
                          }
                        }
                        else {
                          fVar2 = 0.0;
                        }
                        pfVar14[1] = fVar2;
                        uVar10 = uVar10 + 1;
                        pfVar14 = pfVar14 + 4;
                      } while (uVar10 < *(uint *)(*(int *)((int)param_1 + 4) + 0x1060));
                    }
                  }
                  else if (iVar7 == 2) {
                    uVar10 = 0;
                    if (iVar11 != 0) {
                      pfVar14 = (float *)(iVar8 + 8);
                      do {
                        fVar1 = fVar2;
                        if (fVar2 <= pfVar14[-2]) {
                          if (_DAT_005e6a34 <= pfVar14[-2]) {
                            fVar1 = 1.0;
                          }
                          else {
                            fVar1 = pfVar14[-2];
                          }
                        }
                        pfVar14[-2] = fVar1;
                        fVar1 = fVar2;
                        if (fVar2 <= pfVar14[-1]) {
                          if (_DAT_005e6a34 <= pfVar14[-1]) {
                            fVar1 = 1.0;
                          }
                          else {
                            fVar1 = pfVar14[-1];
                          }
                        }
                        pfVar14[-1] = fVar1;
                        fVar1 = fVar2;
                        if (fVar2 <= *pfVar14) {
                          if (_DAT_005e6a34 <= *pfVar14) {
                            fVar1 = 1.0;
                          }
                          else {
                            fVar1 = *pfVar14;
                          }
                        }
                        *pfVar14 = fVar1;
                        if (0.0 <= pfVar14[1]) {
                          if (_DAT_005e6a34 <= pfVar14[1]) {
                            fVar1 = 1.0;
                          }
                          else {
                            fVar1 = pfVar14[1];
                          }
                        }
                        else {
                          fVar1 = 0.0;
                        }
                        pfVar14[1] = fVar1;
                        uVar10 = uVar10 + 1;
                        pfVar14 = pfVar14 + 4;
                      } while (uVar10 < *(uint *)(*(int *)((int)param_1 + 4) + 0x1060));
                    }
                  }
                  else if ((iVar7 == 3) && (uVar10 = 0, iVar11 != 0)) {
                    pfVar14 = (float *)(iVar8 + 8);
                    do {
                      fVar1 = fVar2;
                      if (fVar2 <= pfVar14[-2]) {
                        if (_DAT_005e6a34 <= pfVar14[-2]) {
                          fVar1 = 1.0;
                        }
                        else {
                          fVar1 = pfVar14[-2];
                        }
                      }
                      pfVar14[-2] = fVar1;
                      fVar1 = fVar2;
                      if (fVar2 <= pfVar14[-1]) {
                        if (_DAT_005e6a34 <= pfVar14[-1]) {
                          fVar1 = 1.0;
                        }
                        else {
                          fVar1 = pfVar14[-1];
                        }
                      }
                      pfVar14[-1] = fVar1;
                      fVar1 = fVar2;
                      if (fVar2 <= *pfVar14) {
                        if (_DAT_005e6a34 <= *pfVar14) {
                          fVar1 = 1.0;
                        }
                        else {
                          fVar1 = *pfVar14;
                        }
                      }
                      *pfVar14 = fVar1;
                      fVar1 = fVar2;
                      if (fVar2 <= pfVar14[1]) {
                        if (_DAT_005e6a34 <= pfVar14[1]) {
                          fVar1 = 1.0;
                        }
                        else {
                          fVar1 = pfVar14[1];
                        }
                      }
                      pfVar14[1] = fVar1;
                      uVar10 = uVar10 + 1;
                      pfVar14 = pfVar14 + 4;
                    } while (uVar10 < *(uint *)(*(int *)((int)param_1 + 4) + 0x1060));
                  }
                  (**(code **)(**(int **)((int)param_1 + 4) + 8))
                            (local_8,*piVar16,
                             (*(int **)((int)param_1 + 4))[0x418] * (int)local_8 * 0x10 + *piVar6);
                  local_8 = (int *)((int)local_8 + 1);
                  iVar11 = *(int *)((int)param_1 + 4);
                  fVar2 = _DAT_005e6a38;
                } while (local_8 < *(uint *)(iVar11 + 0x1064));
              }
              piVar6[1] = (int)local_18;
              local_18 = piVar6;
            }
          }
          local_38 = local_38 + 1;
          piVar16 = piVar13;
        }
        iVar17 = 0;
        goto LAB_005800e1;
      }
    }
LAB_005800d5:
    iVar17 = -0x7ff8fff2;
  }
LAB_005800e1:
  if (local_c != (int *)0x0) {
    CFastVB__Helper_0057fa10(local_c,(void *)0x3,unaff_EDI);
  }
  OID__FreeObject_Callback(local_1c);
  OID__FreeObject_Callback(local_20);
  OID__FreeObject_Callback(ptr);
  OID__FreeObject_Callback(local_10);
  OID__FreeObject_Callback((void *)0x0);
  return iVar17;
}
