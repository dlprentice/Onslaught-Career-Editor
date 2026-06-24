/* address: 0x0057cca4 */
/* name: CFastVB__Helper_0057cca4 */
/* signature: int * __stdcall CFastVB__Helper_0057cca4(uint param_1, int param_2, int param_3) */


/* WARNING: Removing unreachable block (ram,0x0057cd19) */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int * CFastVB__Helper_0057cca4(uint param_1,int param_2,int param_3)

{
  int *piVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  float fVar9;
  int iVar10;
  int *extraout_EAX;
  int iVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  uint uVar16;
  float local_24;
  uint local_1c;
  float local_18;
  uint local_10;
  float local_c;
  float local_8;

  uVar16 = 0;
  if ((param_1 != 0) && (param_2 != 0)) {
    fVar2 = (float)param_2;
    if (param_2 < 0) {
      fVar2 = fVar2 + _DAT_005e72d8;
    }
    fVar3 = (float)(int)param_1;
    if ((int)param_1 < 0) {
      fVar3 = fVar3 + _DAT_005e72d8;
    }
    fVar4 = fVar2 / fVar3;
    iVar15 = 0x10;
    fVar5 = _DAT_005e72d4 / fVar4;
    if (param_1 != 0) {
      do {
        iVar10 = __ftol();
        uVar16 = uVar16 + 1;
        iVar15 = iVar15 + 0xc + iVar10 * 0x10;
      } while (uVar16 < param_1);
    }
    CFastVB__Helper_00426fd0(iVar15);
    if (extraout_EAX != (int *)0x0) {
      iVar10 = 0;
      local_1c = 0;
      iVar15 = 4;
      iVar14 = iVar15;
      if (param_1 != 0) {
        do {
          local_8 = 0.0;
          local_10 = 0;
          fVar6 = (float)(int)local_1c;
          iVar15 = iVar14 + 4;
          if ((int)local_1c < 0) {
            fVar6 = fVar6 + _DAT_005e72d8;
          }
          do {
            fVar7 = (float)(int)local_10;
            if ((int)local_10 < 0) {
              fVar7 = fVar7 + _DAT_005e72d8;
            }
            fVar7 = (fVar7 + fVar6) - _DAT_005e72d4;
            local_24 = fVar7 * fVar4;
            local_c = fVar4 + local_24;
            if (param_3 == 0) {
              if (local_24 < DAT_005e6a3c) {
                local_24 = 0.0;
              }
              if (fVar2 < local_c) {
                local_c = fVar2;
              }
            }
            CFastVB__Helper_0057cc7b(local_24);
            iVar11 = __ftol();
            fVar8 = (float)iVar11;
            if (fVar8 < local_c) {
              iVar12 = iVar11 - param_2;
              do {
                local_18 = _DAT_005e6a34 + fVar8;
                if (iVar11 < 0) {
                  iVar13 = iVar11 + param_2;
                }
                else {
                  iVar13 = iVar12;
                  if (iVar11 < param_2) {
                    iVar13 = iVar11;
                  }
                }
                if (iVar13 != iVar10) {
                  if (_DAT_005e96c8 < local_8) {
                    piVar1 = (int *)(iVar15 + (int)extraout_EAX);
                    *piVar1 = iVar10;
                    iVar15 = iVar15 + 8;
                    piVar1[1] = (int)local_8;
                  }
                  local_8 = 0.0;
                  iVar10 = iVar13;
                }
                if (fVar8 < local_24) {
                  fVar8 = local_24;
                }
                if (local_c < local_18) {
                  local_18 = local_c;
                }
                if (param_3 == 0) {
                  if (DAT_005e6a3c <= fVar7) {
                    if (fVar7 + _DAT_005e6a34 < fVar3) goto LAB_0057cec8;
                    fVar9 = 0.0;
                  }
                  else {
                    fVar9 = 1.0;
                  }
                }
                else {
LAB_0057cec8:
                  fVar9 = (local_18 + fVar8) * fVar5 - fVar7;
                }
                if (local_10 != 0) {
                  fVar9 = 1.0 - fVar9;
                }
                iVar11 = iVar11 + 1;
                iVar12 = iVar12 + 1;
                local_8 = (local_18 - fVar8) * fVar9 + local_8;
                fVar8 = (float)iVar11;
              } while (fVar8 < local_c);
            }
            local_10 = local_10 + 1;
          } while (local_10 < 2);
          if (_DAT_005e96c8 < local_8) {
            piVar1 = (int *)(iVar15 + (int)extraout_EAX);
            iVar15 = iVar15 + 8;
            *piVar1 = iVar10;
            piVar1[1] = (int)local_8;
          }
          local_1c = local_1c + 1;
          *(int *)(iVar14 + (int)extraout_EAX) = iVar15 - iVar14;
          iVar14 = iVar15;
        } while (local_1c < param_1);
      }
      *extraout_EAX = iVar15;
      return extraout_EAX;
    }
  }
  return (int *)0x0;
}
