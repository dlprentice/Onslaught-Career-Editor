/* address: 0x00453780 */
/* name: Controls__ApplyPreset */
/* signature: void __cdecl Controls__ApplyPreset(int scheme) */


/* Applies a control-scheme preset.

   - Sets g_ControlSchemeIndex = scheme.
   - scheme==0: no-op.
   - scheme>0: copies preset binding records from a table (base DAT_00677af0) into the
   options/binding entries (via OptionsEntries__FindById). */

void __cdecl Controls__ApplyPreset(int scheme)

{
  char *pcVar1;
  bool bVar2;
  bool bVar3;
  int iVar4;
  int *piVar5;
  undefined4 *puVar6;
  int *piVar7;
  int iVar8;
  int iVar9;
  int *piVar10;

  g_ControlSchemeIndex = scheme;
  if (scheme == 0) {
    return;
  }
  PTR_DAT_006290b0 = (undefined *)&DAT_00677af0;
  bVar3 = false;
  iVar8 = DAT_00888ff8;
  do {
    if (*(int *)(PTR_DAT_006290b0 + 4) == -1) {
      iVar9 = 0;
      PTR_DAT_006290b0 = (undefined *)&DAT_00677af0;
      if (0 < iVar8) {
        do {
          if ((&DAT_00889024)[iVar9] != '\0') {
            if (DAT_006778d4 != -1) {
              piVar5 = &DAT_006778d4;
              do {
                piVar7 = OptionsEntries__FindById(*piVar5);
                if (piVar7 != (int *)0x0) {
                  piVar7[2] = piVar5[1];
                  piVar7[3] = piVar5[2];
                  piVar7[4] = piVar5[3];
                  piVar7[2] = iVar9;
                }
                piVar7 = piVar5 + 8;
                piVar5 = piVar5 + 8;
                iVar8 = DAT_00888ff8;
              } while (*piVar7 != -1);
            }
            do {
              iVar4 = iVar9 + 1;
              if (iVar8 <= iVar4) {
                if (DAT_008892dc == -1) {
                  return;
                }
                puVar6 = &DAT_008892dc;
                do {
                  puVar6[4] = 0xffffffff;
                  piVar5 = puVar6 + 8;
                  puVar6 = puVar6 + 8;
                } while (*piVar5 != -1);
                return;
              }
              pcVar1 = &DAT_00889025 + iVar9;
              iVar9 = iVar4;
            } while (*pcVar1 == '\0');
            if (DAT_006778d4 == -1) {
              return;
            }
            piVar5 = &DAT_006778d4;
            do {
              piVar7 = OptionsEntries__FindById(*piVar5);
              if (piVar7 != (int *)0x0) {
                piVar7[5] = piVar5[1];
                piVar7[6] = piVar5[2];
                piVar7[7] = piVar5[3];
                piVar7[5] = iVar4;
              }
              piVar7 = piVar5 + 8;
              piVar5 = piVar5 + 8;
            } while (*piVar7 != -1);
            return;
          }
          iVar9 = iVar9 + 1;
        } while (iVar9 < iVar8);
      }
    }
    iVar9 = *(int *)(PTR_DAT_006290b0 + 4);
    while (iVar9 != -1) {
      piVar5 = OptionsEntries__FindById(iVar9);
      if (piVar5 != (int *)0x0) {
        piVar7 = (int *)PTR_DAT_006290b0;
        piVar10 = piVar5;
        for (iVar8 = 8; iVar8 != 0; iVar8 = iVar8 + -1) {
          *piVar10 = *piVar7;
          piVar7 = piVar7 + 1;
          piVar10 = piVar10 + 1;
        }
        if (piVar5[5] != -1) {
          bVar3 = true;
        }
      }
      iVar9 = *(int *)(PTR_DAT_006290b0 + 0x24);
      iVar8 = DAT_00888ff8;
      PTR_DAT_006290b0 = PTR_DAT_006290b0 + 0x20;
    }
    PTR_DAT_006290b0 = PTR_DAT_006290b0 + 0x20;
    bVar2 = 1 < scheme;
    scheme = scheme + -1;
  } while (bVar2);
  if (bVar3) {
    return;
  }
  iVar9 = 0;
  if (iVar8 < 1) {
    return;
  }
  while ((&DAT_00889024)[iVar9] == '\0') {
    iVar9 = iVar9 + 1;
    if (iVar8 <= iVar9) {
      return;
    }
  }
  if (DAT_006778d4 == -1) {
    return;
  }
  piVar5 = &DAT_006778d4;
  do {
    piVar7 = OptionsEntries__FindById(*piVar5);
    if (piVar7 != (int *)0x0) {
      piVar7[5] = piVar5[1];
      piVar7[6] = piVar5[2];
      piVar7[7] = piVar5[3];
      piVar7[5] = iVar9;
    }
    piVar7 = piVar5 + 8;
    piVar5 = piVar5 + 8;
  } while (*piVar7 != -1);
  return;
}
