/* address: 0x0047eff0 */
/* name: CLandscapeTexture__BlitTileRegionWithLightingMask */
/* signature: int CLandscapeTexture__BlitTileRegionWithLightingMask(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CLandscapeTexture__BlitTileRegionWithLightingMask(void)

{
  int *piVar1;
  int *piVar2;
  char cVar3;
  char cVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  byte bVar8;
  int iVar9;
  int iVar10;
  undefined4 *puVar11;
  int iVar12;
  int iVar13;
  byte *pbVar14;
  int in_ECX;
  undefined4 *puVar15;
  int iVar16;
  uint uVar17;
  uint uVar18;
  int iVar19;
  int iVar20;
  int iVar21;
  int iVar22;
  char *pcVar23;
  int iVar24;
  int iVar25;
  byte *pbVar26;
  int iVar27;
  uint uVar28;
  int iVar29;
  int iVar30;
  uint *puVar31;
  uint *puVar32;
  undefined2 *puVar33;
  undefined2 *puVar34;
  byte in_stack_00000004;
  int *in_stack_00000008;
  int in_stack_0000000c;
  int in_stack_00000010;
  uint in_stack_00000014;
  int in_stack_0000001c;
  int in_stack_00000020;
  int in_stack_00000024;
  int in_stack_00000028;
  int local_7c;
  int local_70;
  undefined2 *local_68;
  int local_60;
  ushort *local_50;
  int local_4c;
  int local_48;
  int local_44;
  int local_40;
  int local_38;
  int local_30;
  int local_24;

  iVar5 = in_stack_00000008[6];
  iVar24 = 1 << (in_stack_00000004 & 0x1f);
  local_60 = 0;
  iVar9 = iVar5 * iVar24;
  if ((in_stack_00000014 & 1) != 0) {
    local_60 = iVar24 * 8;
  }
  if ((in_stack_00000014 & 0x40) != 0) {
    local_60 = local_60 + iVar9 * 8;
  }
  uVar28 = in_stack_00000014 & 0x8000003f;
  if ((int)uVar28 < 0) {
    uVar28 = (uVar28 - 1 | 0xffffffc0) + 1;
  }
  local_68 = (undefined2 *)
             (in_stack_0000000c +
             (in_stack_00000010 * in_stack_00000020 + in_stack_0000001c) * iVar24 * 2);
  piVar1 = (int *)(DAT_0089bd80 + in_stack_00000014 * 0x14);
  iVar6 = *(int *)(&DAT_009c8028 +
                  ((in_stack_00000014 & 0x3f) * 0x40 + ((int)in_stack_00000014 >> 6 & 0x3fU)) * 4);
  iVar10 = (int)(0x80 / (longlong)(iVar24 * 8));
  local_48 = in_stack_00000020 << 4;
  if (in_stack_00000020 < in_stack_00000028) {
    local_44 = iVar9 * in_stack_00000020;
    local_40 = in_stack_00000020 * 9 + piVar1[1];
    iVar21 = (((int)(in_stack_00000014 + ((int)in_stack_00000014 >> 0x1f & 0x3fU)) >> 6) * 8 +
             in_stack_00000020) * 0x200 + DAT_0089bd84 + uVar28 * 8;
    local_24 = in_stack_00000028 - in_stack_00000020;
    do {
      local_70 = in_stack_0000001c;
      if (in_stack_0000001c < in_stack_00000024) {
        iVar29 = iVar24 * in_stack_0000001c + local_44 + local_60;
        local_4c = in_stack_0000001c << 4;
        do {
          iVar13 = in_stack_00000008[2];
          pbVar26 = (byte *)(iVar29 + *in_stack_00000008);
          puVar11 = (undefined4 *)(in_ECX + 0x28);
          for (iVar12 = iVar24; iVar12 != 0; iVar12 = iVar12 + -1) {
            pbVar14 = pbVar26;
            puVar15 = puVar11;
            iVar30 = iVar24;
            if (0 < iVar24) {
              do {
                iVar30 = iVar30 + -1;
                *puVar15 = *(undefined4 *)(iVar13 + (uint)*pbVar14 * 4);
                pbVar14 = pbVar14 + 1;
                puVar15 = puVar15 + 1;
              } while (iVar30 != 0);
            }
            pbVar26 = pbVar26 + iVar5;
            puVar11 = puVar11 + iVar24;
          }
          local_30 = 0;
          pcVar23 = (char *)(local_40 + local_70);
          if (0 < *piVar1) {
            local_50 = (ushort *)(piVar1 + 2);
            do {
              iVar25 = (uint)*local_50 * 0x400 + in_stack_00000008[2];
              iVar30 = (int)*pcVar23;
              iVar22 = pcVar23[1] * 0x1000000 + iVar30 * -0x1000000;
              cVar3 = pcVar23[9];
              cVar4 = pcVar23[10];
              iVar12 = iVar22 >> (in_stack_00000004 & 0x1f);
              pbVar26 = (byte *)(in_stack_00000008[4] * (uint)*local_50 + iVar29 +
                                *in_stack_00000008);
              puVar32 = (uint *)(in_ECX + 0x28);
              uVar28 = iVar30 * 0x1000000;
              for (iVar13 = iVar24; iVar13 != 0; iVar13 = iVar13 + -1) {
                uVar17 = uVar28 + (cVar3 * 0x1000000 + iVar30 * -0x1000000 >>
                                  (in_stack_00000004 & 0x1f));
                puVar31 = puVar32;
                local_7c = iVar24;
                do {
                  uVar18 = *(int *)(iVar25 + (uint)*pbVar26 * 4) + (uVar28 & 0xff000000);
                  uVar7 = *puVar31;
                  iVar27 = uVar18 - uVar7;
                  if (0 < iVar27) {
                    while( true ) {
                      while (0x1fffffff < iVar27) {
                        *puVar31 = uVar18;
                        puVar32 = puVar31 + 1;
                        pbVar26 = pbVar26 + 1;
                        uVar28 = uVar28 + iVar12;
                        local_7c = local_7c + -1;
                        if (local_7c == 0) goto LAB_0047f410;
                        uVar18 = *(int *)(iVar25 + (uint)*pbVar26 * 4) + (uVar28 & 0xff000000);
                        uVar7 = *puVar32;
                        puVar31 = puVar32;
                        iVar27 = uVar18 - uVar7;
                      }
                      if (iVar27 < 0) break;
                      puVar32 = puVar31 + 1;
                      *puVar31 = ((int)((uVar7 & 0xf8f8ff) * (7 - (iVar27 >> 0x1a)) +
                                       (uVar18 & 0xf8f8ff) * (iVar27 >> 0x1a)) >> 3) +
                                 (uVar18 & 0xff000000);
                      pbVar26 = pbVar26 + 1;
                      uVar28 = uVar28 + iVar12;
                      local_7c = local_7c + -1;
                      if (local_7c == 0) goto LAB_0047f410;
                      uVar18 = *(int *)(iVar25 + (uint)*pbVar26 * 4) + (uVar28 & 0xff000000);
                      uVar7 = *puVar32;
                      iVar27 = uVar18 - uVar7;
                      puVar31 = puVar32;
                    }
                  }
                  puVar32 = puVar31 + 1;
                  pbVar26 = pbVar26 + 1;
                  uVar28 = uVar28 + iVar12;
                  local_7c = local_7c + -1;
                  puVar31 = puVar32;
                } while (local_7c != 0);
LAB_0047f410:
                iVar12 = iVar12 + ((cVar4 * 0x1000000 + cVar3 * -0x1000000) - iVar22 >>
                                  (in_stack_00000004 * '\x02' & 0x1f));
                pbVar26 = pbVar26 + (iVar5 - iVar24);
                uVar28 = uVar17;
              }
              pcVar23 = pcVar23 + 0x51;
              local_30 = local_30 + 1;
              local_50 = local_50 + 1;
            } while (local_30 < *piVar1);
          }
          uVar28 = (uint)*(byte *)(iVar21 + local_70);
          iVar30 = uVar28 * 0x100;
          uVar17 = (uint)*(byte *)(iVar21 + 0x200 + local_70);
          iVar13 = (uint)*(byte *)(iVar21 + 1 + local_70) * 0x100 + uVar28 * -0x100;
          iVar12 = iVar13 >> (in_stack_00000004 & 0x1f);
          iVar25 = (int)(uVar17 * 0x100 + uVar28 * -0x100) >> (in_stack_00000004 & 0x1f);
          iVar27 = (int)(((uint)*(byte *)(iVar21 + 0x201 + local_70) * 0x100 + uVar17 * -0x100) -
                        iVar13) >> (in_stack_00000004 * '\x02' & 0x1f);
          pbVar26 = (byte *)(in_ECX + 0x28);
          iVar13 = iVar24;
          puVar34 = local_68;
          iVar22 = local_48;
          if (iVar6 == 0) {
            for (; iVar13 != 0; iVar13 = iVar13 + -1) {
              iVar30 = iVar30 + iVar25;
              iVar12 = iVar12 + iVar27;
              pbVar14 = pbVar26;
              iVar22 = iVar30;
              local_30 = iVar24;
              do {
                iVar22 = iVar22 + iVar12;
                puVar33 = puVar34 + 1;
                pbVar26 = pbVar14 + 4;
                piVar2 = (int *)(in_ECX + 0x10d0 + (iVar22 >> 8) * 0xc);
                *puVar34 = (short)(((uint)pbVar14[1] * piVar2[1] & 0x7e00000) +
                                   ((uint)pbVar14[2] *
                                    *(int *)(in_ECX + 0x10d8 + (iVar22 >> 8) * 0xc) & 0x1f0000) +
                                   ((uint)*pbVar14 * *piVar2 & 0xf8000000) >> 0x10);
                local_30 = local_30 + -1;
                pbVar14 = pbVar26;
                puVar34 = puVar33;
              } while (local_30 != 0);
              puVar34 = puVar33 + (in_stack_00000010 - iVar24);
            }
          }
          else {
            for (; iVar13 != 0; iVar13 = iVar13 + -1) {
              iVar30 = iVar30 + iVar25;
              iVar12 = iVar12 + iVar27;
              pbVar14 = pbVar26;
              iVar16 = local_4c;
              iVar19 = iVar30;
              local_38 = iVar24;
              do {
                iVar19 = iVar19 + iVar12;
                bVar8 = (byte)(iVar16 >> 1);
                puVar33 = puVar34 + 1;
                pbVar26 = pbVar14 + 4;
                iVar20 = (iVar19 >> 8) >>
                         ((byte)((*(uint *)(iVar6 + ((iVar16 >> 6) + (iVar22 >> 1) * 2) * 4) &
                                 1 << (bVar8 & 0x1f)) >> (bVar8 & 0x1f)) & 0x1f);
                piVar2 = (int *)(in_ECX + 0x10d0 + iVar20 * 0xc);
                *puVar34 = (short)(((uint)pbVar14[1] * piVar2[1] & 0x7e00000) +
                                   ((uint)pbVar14[2] * *(int *)(in_ECX + 0x10d8 + iVar20 * 0xc) &
                                   0x1f0000) + ((uint)*pbVar14 * *piVar2 & 0xf8000000) >> 0x10);
                iVar16 = iVar16 + iVar10;
                local_38 = local_38 + -1;
                pbVar14 = pbVar26;
                puVar34 = puVar33;
              } while (local_38 != 0);
              iVar22 = iVar22 + iVar10;
              puVar34 = puVar33 + (in_stack_00000010 - iVar24);
            }
          }
          local_4c = local_4c + 0x10;
          local_68 = local_68 + iVar24;
          iVar29 = iVar29 + iVar24;
          local_70 = local_70 + 1;
        } while (local_70 < in_stack_00000024);
      }
      local_48 = local_48 + 0x10;
      local_68 = local_68 + (in_stack_00000010 - (in_stack_00000024 - in_stack_0000001c)) * iVar24;
      local_40 = local_40 + 9;
      local_44 = local_44 + iVar9;
      iVar21 = iVar21 + 0x200;
      local_24 = local_24 + -1;
      in_stack_00000028 = in_stack_0000001c;
    } while (local_24 != 0);
  }
  return in_stack_00000028;
}
