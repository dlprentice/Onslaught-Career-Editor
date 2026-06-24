/* address: 0x0057b182 */
/* name: CDXTexture__Unk_0057b182 */
/* signature: int __thiscall CDXTexture__Unk_0057b182(void * this, void * param_1, void * param_2, uint param_3) */


int __thiscall CDXTexture__Unk_0057b182(void *this,void *param_1,void *param_2,uint param_3)

{
  short *psVar1;
  undefined1 *puVar2;
  byte bVar3;
  ushort uVar4;
  bool bVar5;
  void *pvVar6;
  byte bVar7;
  uint uVar8;
  void *pvVar9;
  uint uVar10;
  undefined4 *extraout_EAX;
  undefined1 *puVar11;
  void *pvVar12;
  undefined4 *extraout_EAX_00;
  uint uVar13;
  int iVar14;
  uint *puVar15;
  uint uVar16;
  undefined4 *puVar17;
  uint uVar18;
  undefined4 *puVar19;
  uint *puVar20;
  undefined4 *puVar21;
  bool bVar22;
  bool bVar23;
  uint local_2c;
  uint local_28;
  undefined1 *local_24;
  uint local_20;
  uint local_1c;
  int local_18;
  uint *local_14;
  int local_10;
  uint local_c;

  pvVar6 = param_1;
  if (param_2 < (void *)0x12) {
    return -0x7fffbffb;
  }
  if ((*(byte *)((int)param_1 + 1) & 0xfe) != 0) {
    return -0x7fffbffb;
  }
  bVar3 = *(byte *)((int)param_1 + 2);
  if ((bVar3 & 0xf4) != 0) {
    return -0x7fffbffb;
  }
  if (*(short *)((int)param_1 + 0xc) == 0) {
    return -0x7fffbffb;
  }
  if (*(short *)((int)param_1 + 0xe) == 0) {
    return -0x7fffbffb;
  }
  uVar8 = (uint)*(byte *)((int)param_1 + 7);
  local_18 = 0;
  if (*(byte *)((int)param_1 + 1) != 0) {
    if (uVar8 == 0xf) {
      local_18 = 0x18;
    }
    else if (uVar8 == 0x10) {
      local_18 = 0x19;
    }
    else if (uVar8 == 0x18) {
      local_18 = 0x14;
    }
    else {
      if (uVar8 != 0x20) {
        return -0x7fffbffb;
      }
      local_18 = 0x15;
    }
  }
  uVar13 = (uint)*(byte *)((int)param_1 + 0x10);
  pvVar9 = (void *)(uVar13 + 7 >> 3);
  bVar7 = bVar3 & 3;
  if (bVar7 == 1) {
    if (*(char *)((int)param_1 + 1) == '\0') {
      return -0x7fffbffb;
    }
    if (*(char *)((int)param_1 + 0x10) != '\b') {
      return -0x7fffbffb;
    }
    local_10 = 0x29;
  }
  else if (bVar7 == 2) {
    if (uVar13 == 0xf) {
      local_10 = 0x18;
    }
    else if (uVar13 == 0x10) {
      local_10 = 0x19;
    }
    else if (uVar13 == 0x18) {
      local_10 = 0x14;
    }
    else {
      if (uVar13 != 0x20) {
        return -0x7fffbffb;
      }
      local_10 = 0x15;
    }
  }
  else {
    if (bVar7 != 3) {
      return -0x7fffbffb;
    }
    if (*(char *)((int)param_1 + 0x10) != '\b') {
      return -0x7fffbffb;
    }
    local_10 = 0x32;
  }
  bVar22 = (*(byte *)((int)param_1 + 0x11) & 0x20) != 0x20;
  bVar23 = (*(byte *)((int)param_1 + 0x11) & 0x10) == 0x10;
  uVar10 = (uint)*(byte *)param_1;
  if ((int)param_2 - 0x12U < uVar10) {
    return -0x7fffbffb;
  }
  uVar18 = ((int)param_2 - 0x12U) - uVar10;
  puVar15 = (uint *)(uVar10 + 0x12 + (int)param_1);
  uVar8 = (uint)*(ushort *)((int)param_1 + 5) * (uVar8 + 7 >> 3);
  if (uVar18 < uVar8) {
    return -0x7fffbffb;
  }
  if ((*(int *)((int)this + 0x40) != 0) && (local_10 == 0x29)) {
    if (0x100 < (uint)*(ushort *)((int)param_1 + 3) + (uint)*(ushort *)((int)param_1 + 5)) {
      return -0x7fffbffb;
    }
    CFastVB__Helper_00426fd0(0x400);
    *(undefined4 **)((int)this + 8) = extraout_EAX;
    if (extraout_EAX == (undefined4 *)0x0) {
      return -0x7ff8fff2;
    }
    bVar5 = false;
    *(undefined4 *)((int)this + 0x3c) = 1;
    puVar17 = extraout_EAX;
    for (iVar14 = 0x100; iVar14 != 0; iVar14 = iVar14 + -1) {
      *puVar17 = 0xffffffff;
      puVar17 = puVar17 + 1;
    }
    local_24 = (undefined1 *)(*(int *)((int)this + 8) + (uint)*(ushort *)((int)param_1 + 3) * 4);
    puVar2 = local_24 + (uint)*(ushort *)((int)param_1 + 5) * 4;
    uVar10 = uVar18;
    puVar20 = puVar15;
    local_14 = puVar15;
    if (local_24 < puVar2) {
      do {
        if (local_18 == 0x14) {
          local_c = (uint)(byte)*puVar20;
          uVar10 = (uint)*(byte *)((int)puVar20 + 2);
          local_1c = (uint)*(byte *)((int)puVar20 + 1);
          puVar20 = (uint *)((int)puVar20 + 3);
LAB_0057b466:
          local_20 = 0xff;
          local_14 = puVar20;
        }
        else if (local_18 == 0x15) {
          uVar10 = *puVar20;
          local_20 = uVar10 >> 0x18;
          local_1c = uVar10 >> 8 & 0xff;
          local_c = uVar10 & 0xff;
          uVar10 = uVar10 >> 0x10 & 0xff;
          puVar20 = puVar20 + 1;
          local_14 = puVar20;
        }
        else {
          if (local_18 == 0x18) {
            uVar4 = (ushort)*puVar20;
            uVar10 = uVar4 >> 10 & 0x1f;
            uVar16 = uVar4 >> 5 & 0x1f;
            uVar10 = uVar10 >> 2 | uVar10 << 3;
            local_1c = uVar16 >> 2 | uVar16 << 3;
            local_c = (uVar4 & 0x1f) >> 2 | (uVar4 & 0x1f) << 3;
            puVar20 = (uint *)((int)local_14 + 2);
            goto LAB_0057b466;
          }
          if (local_18 == 0x19) {
            uVar4 = (ushort)*puVar20;
            local_20 = (uint)(uVar4 >> 0xf) * 0xff;
            uVar10 = uVar4 >> 10 & 0x1f;
            uVar16 = uVar4 >> 5 & 0x1f;
            uVar10 = uVar10 >> 2 | uVar10 << 3;
            local_1c = uVar16 >> 2 | uVar16 << 3;
            local_c = (uVar4 & 0x1f) >> 2 | (uVar4 & 0x1f) << 3;
            puVar20 = (uint *)((int)local_14 + 2);
            local_14 = puVar20;
          }
        }
        local_24[1] = (char)local_1c;
        local_24[2] = (undefined1)local_c;
        local_24[3] = (char)local_20;
        *local_24 = (char)uVar10;
        local_24 = local_24 + 4;
        bVar5 = (bool)(bVar5 | local_20 != 0);
      } while (local_24 < puVar2);
      if (bVar5) goto LAB_0057b4bf;
    }
    for (puVar11 = (undefined1 *)(*(int *)((int)this + 8) + (uint)*(ushort *)((int)param_1 + 3) * 4)
        ; puVar11 < puVar2; puVar11 = puVar11 + 4) {
      puVar11[3] = 0xff;
    }
  }
LAB_0057b4bf:
  param_2 = (void *)(uVar18 - uVar8);
  puVar15 = (uint *)((int)puVar15 + uVar8);
  pvVar12 = (void *)((uint)*(ushort *)((int)param_1 + 0xe) * (uint)*(ushort *)((int)param_1 + 0xc) *
                    (int)pvVar9);
  *(int *)this = local_10;
  *(uint **)((int)this + 4) = puVar15;
  *(uint *)((int)this + 0x30) = (uint)*(ushort *)((int)param_1 + 0xc) * (int)pvVar9;
  *(undefined4 *)((int)this + 0x34) = 0;
  *(uint *)((int)this + 0xc) = (uint)*(ushort *)((int)param_1 + 0xc);
  *(uint *)((int)this + 0x10) = (uint)*(ushort *)((int)param_1 + 0xe);
  *(undefined4 *)((int)this + 0x14) = 1;
  if (*(int *)((int)this + 0x40) != 0) {
    if ((((bVar3 & 8) != 0) || (bVar22)) || (bVar23)) {
      CFastVB__Helper_00426fd0((int)pvVar12);
      *(undefined4 **)((int)this + 4) = extraout_EAX_00;
      if (extraout_EAX_00 == (undefined4 *)0x0) {
        return -0x7ff8fff2;
      }
      *(undefined4 *)((int)this + 0x38) = 1;
      puVar17 = extraout_EAX_00;
      if (bVar22) {
        puVar17 = (undefined4 *)
                  ((*(ushort *)((int)param_1 + 0xe) - 1) * *(int *)((int)this + 0x30) +
                  (int)extraout_EAX_00);
      }
      psVar1 = (short *)((int)param_1 + 0xe);
      local_24 = (undefined1 *)0x0;
      param_1 = puVar15;
      if (*psVar1 != 0) {
        do {
          local_14 = puVar17;
          if (bVar23) {
            local_14 = (undefined4 *)((*(int *)((int)this + 0x30) - (int)pvVar9) + (int)puVar17);
          }
          uVar8 = (uint)*(ushort *)((int)pvVar6 + 0xc);
          local_28 = 0;
          if (uVar8 != 0) {
            do {
              if ((bVar3 & 8) == 0) {
                local_2c = 0;
              }
              else {
                if (param_2 == (void *)0x0) {
                  return -0x7fffbffb;
                }
                local_2c = *(byte *)param_1 & 0x80;
                uVar8 = (*(byte *)param_1 & 0x7f) + 1;
                param_1 = (void *)((int)param_1 + 1);
                param_2 = (void *)((int)param_2 + -1);
              }
              local_28 = local_28 + uVar8;
              while (uVar8 != 0) {
                uVar8 = uVar8 - 1;
                if (param_2 < pvVar9) {
                  return -0x7fffbffb;
                }
                puVar19 = param_1;
                puVar21 = local_14;
                for (uVar10 = uVar13 + 7 >> 5; uVar10 != 0; uVar10 = uVar10 - 1) {
                  *puVar21 = *puVar19;
                  puVar19 = puVar19 + 1;
                  puVar21 = puVar21 + 1;
                }
                for (uVar10 = (uint)pvVar9 & 3; uVar10 != 0; uVar10 = uVar10 - 1) {
                  *(undefined1 *)puVar21 = *(undefined1 *)puVar19;
                  puVar19 = (undefined4 *)((int)puVar19 + 1);
                  puVar21 = (undefined4 *)((int)puVar21 + 1);
                }
                if (local_2c == 0) {
                  param_1 = (void *)((int)param_1 + (int)pvVar9);
                  param_2 = (void *)((int)param_2 - (int)pvVar9);
                }
                pvVar12 = pvVar9;
                if (bVar23) {
                  pvVar12 = (void *)-(int)pvVar9;
                }
                local_14 = (uint *)((int)local_14 + (int)pvVar12);
              }
              if (local_2c != 0) {
                param_1 = (void *)((int)param_1 + (int)pvVar9);
                param_2 = (void *)((int)param_2 - (int)pvVar9);
              }
              uVar8 = (uint)*(ushort *)((int)pvVar6 + 0xc);
            } while (local_28 < uVar8);
          }
          if (bVar22) {
            iVar14 = -*(int *)((int)this + 0x30);
          }
          else {
            iVar14 = *(int *)((int)this + 0x30);
          }
          puVar17 = (undefined4 *)((int)puVar17 + iVar14);
          local_24 = (undefined1 *)((int)local_24 + 1);
        } while (local_24 < (uint)*(ushort *)((int)pvVar6 + 0xe));
      }
    }
    else {
      if (param_2 < pvVar12) {
        return -0x7fffbffb;
      }
      *(uint **)((int)this + 4) = puVar15;
      *(undefined4 *)((int)this + 0x38) = 0;
    }
    if (*(int *)this == 0x15) {
      uVar8 = *(uint *)((int)this + 4);
      uVar13 = *(int *)((int)this + 0x10) * *(int *)((int)this + 0x30) + uVar8;
      if (uVar8 < uVar13) {
        do {
          uVar10 = *(int *)((int)this + 0xc) * 4 + uVar8;
          uVar18 = uVar8;
          if (uVar8 < uVar10) {
            do {
              if (*(char *)(uVar18 + 3) != '\0') break;
              uVar18 = uVar18 + 4;
            } while (uVar18 < uVar10);
            if (uVar18 < uVar10) break;
          }
          uVar8 = uVar8 + *(int *)((int)this + 0x30);
        } while (uVar8 < uVar13);
      }
      if (uVar8 == uVar13) {
        *(undefined4 *)this = 0x16;
      }
    }
    else if (*(int *)this == 0x19) {
      uVar8 = *(uint *)((int)this + 4);
      uVar13 = *(int *)((int)this + 0x10) * *(int *)((int)this + 0x30) + uVar8;
      if (uVar8 < uVar13) {
        do {
          uVar10 = *(int *)((int)this + 0xc) * 2 + uVar8;
          uVar18 = uVar8;
          if (uVar8 < uVar10) {
            do {
              if ((*(byte *)(uVar18 + 1) & 0x80) != 0) break;
              uVar18 = uVar18 + 2;
            } while (uVar18 < uVar10);
            if (uVar18 < uVar10) break;
          }
          uVar8 = uVar8 + *(int *)((int)this + 0x30);
        } while (uVar8 < uVar13);
      }
      if (uVar8 == uVar13) {
        *(undefined4 *)this = 0x18;
      }
    }
  }
  return 0;
}
