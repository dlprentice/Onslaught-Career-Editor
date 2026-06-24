/* address: 0x0047eff0 */
/* name: CLandscapeTexture__BlitTileRegionWithLightingMask */
/* signature: int __thiscall CLandscapeTexture__BlitTileRegionWithLightingMask(void * this, byte lod_shift, int * tile_ctx, int src_base, int dst_stride, uint tile_flags, int min_x, int min_y, int max_x, int max_y) */


/* Blits a landscape tile region with lighting-mask/culling parameters into destination buffer
   stride.
   High-arity render helper used by landscape texture composition. */

int __thiscall
CLandscapeTexture__BlitTileRegionWithLightingMask
          (void *this,byte lod_shift,int *tile_ctx,int src_base,int dst_stride,uint tile_flags,
          int min_x,int min_y,int max_x,int max_y)

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

  iVar5 = tile_ctx[6];
  iVar24 = 1 << (lod_shift & 0x1f);
  local_60 = 0;
  iVar9 = iVar5 * iVar24;
  if ((tile_flags & 1) != 0) {
    local_60 = iVar24 * 8;
  }
  if ((tile_flags & 0x40) != 0) {
    local_60 = local_60 + iVar9 * 8;
  }
  uVar28 = tile_flags & 0x8000003f;
  if ((int)uVar28 < 0) {
    uVar28 = (uVar28 - 1 | 0xffffffc0) + 1;
  }
  local_68 = (undefined2 *)(src_base + (dst_stride * max_x + min_y) * iVar24 * 2);
  piVar1 = (int *)(DAT_0089bd80 + tile_flags * 0x14);
  iVar6 = *(int *)(&DAT_009c8028 + ((tile_flags & 0x3f) * 0x40 + ((int)tile_flags >> 6 & 0x3fU)) * 4
                  );
  iVar10 = (int)(0x80 / (longlong)(iVar24 * 8));
  local_48 = max_x << 4;
  if (max_x < in_stack_00000028) {
    local_44 = iVar9 * max_x;
    local_40 = max_x * 9 + piVar1[1];
    iVar21 = (((int)(tile_flags + ((int)tile_flags >> 0x1f & 0x3fU)) >> 6) * 8 + max_x) * 0x200 +
             DAT_0089bd84 + uVar28 * 8;
    local_24 = in_stack_00000028 - max_x;
    do {
      local_70 = min_y;
      if (min_y < max_y) {
        iVar29 = iVar24 * min_y + local_44 + local_60;
        local_4c = min_y << 4;
        do {
          iVar13 = tile_ctx[2];
          pbVar26 = (byte *)(iVar29 + *tile_ctx);
          puVar11 = (undefined4 *)((int)this + 0x28);
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
              iVar25 = (uint)*local_50 * 0x400 + tile_ctx[2];
              iVar30 = (int)*pcVar23;
              iVar22 = pcVar23[1] * 0x1000000 + iVar30 * -0x1000000;
              cVar3 = pcVar23[9];
              cVar4 = pcVar23[10];
              iVar12 = iVar22 >> (lod_shift & 0x1f);
              pbVar26 = (byte *)(tile_ctx[4] * (uint)*local_50 + iVar29 + *tile_ctx);
              puVar32 = (uint *)((int)this + 0x28);
              uVar28 = iVar30 * 0x1000000;
              for (iVar13 = iVar24; iVar13 != 0; iVar13 = iVar13 + -1) {
                uVar17 = uVar28 + (cVar3 * 0x1000000 + iVar30 * -0x1000000 >> (lod_shift & 0x1f));
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
                                  (lod_shift * '\x02' & 0x1f));
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
          iVar12 = iVar13 >> (lod_shift & 0x1f);
          iVar25 = (int)(uVar17 * 0x100 + uVar28 * -0x100) >> (lod_shift & 0x1f);
          iVar27 = (int)(((uint)*(byte *)(iVar21 + 0x201 + local_70) * 0x100 + uVar17 * -0x100) -
                        iVar13) >> (lod_shift * '\x02' & 0x1f);
          pbVar26 = (byte *)((int)this + 0x28);
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
                piVar2 = (int *)((int)this + (iVar22 >> 8) * 0xc + 0x10d0);
                *puVar34 = (short)(((uint)pbVar14[1] * piVar2[1] & 0x7e00000) +
                                   ((uint)pbVar14[2] *
                                    *(int *)((int)this + (iVar22 >> 8) * 0xc + 0x10d8) & 0x1f0000) +
                                   ((uint)*pbVar14 * *piVar2 & 0xf8000000) >> 0x10);
                local_30 = local_30 + -1;
                pbVar14 = pbVar26;
                puVar34 = puVar33;
              } while (local_30 != 0);
              puVar34 = puVar33 + (dst_stride - iVar24);
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
                piVar2 = (int *)((int)this + iVar20 * 0xc + 0x10d0);
                *puVar34 = (short)(((uint)pbVar14[1] * piVar2[1] & 0x7e00000) +
                                   ((uint)pbVar14[2] * *(int *)((int)this + iVar20 * 0xc + 0x10d8) &
                                   0x1f0000) + ((uint)*pbVar14 * *piVar2 & 0xf8000000) >> 0x10);
                iVar16 = iVar16 + iVar10;
                local_38 = local_38 + -1;
                pbVar14 = pbVar26;
                puVar34 = puVar33;
              } while (local_38 != 0);
              iVar22 = iVar22 + iVar10;
              puVar34 = puVar33 + (dst_stride - iVar24);
            }
          }
          local_4c = local_4c + 0x10;
          local_68 = local_68 + iVar24;
          iVar29 = iVar29 + iVar24;
          local_70 = local_70 + 1;
        } while (local_70 < max_y);
      }
      local_48 = local_48 + 0x10;
      local_68 = local_68 + (dst_stride - (max_y - min_y)) * iVar24;
      local_40 = local_40 + 9;
      local_44 = local_44 + iVar9;
      iVar21 = iVar21 + 0x200;
      local_24 = local_24 + -1;
      in_stack_00000028 = min_y;
    } while (local_24 != 0);
  }
  return in_stack_00000028;
}
