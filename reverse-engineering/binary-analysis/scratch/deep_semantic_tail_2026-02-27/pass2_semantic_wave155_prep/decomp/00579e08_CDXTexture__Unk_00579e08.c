/* address: 0x00579e08 */
/* name: CDXTexture__Unk_00579e08 */
/* signature: int __thiscall CDXTexture__Unk_00579e08(void * this, void * param_1, void * param_2, void * param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __thiscall CDXTexture__Unk_00579e08(void *this,void *param_1,void *param_2,void *param_3)

{
  undefined1 uVar1;
  byte bVar2;
  ushort uVar3;
  short sVar4;
  float fVar5;
  uint uVar6;
  int extraout_EAX;
  undefined1 *puVar7;
  void *pvVar8;
  byte *extraout_EAX_00;
  uint3 *puVar9;
  byte bVar10;
  int iVar11;
  byte *pbVar12;
  byte *pbVar13;
  uint *puVar14;
  byte *pbVar15;
  ushort *puVar16;
  uint3 *puVar17;
  uint uVar18;
  byte *pbVar19;
  int local_98 [4];
  uint local_88;
  int local_84;
  int local_80;
  undefined2 local_7c;
  undefined2 local_7a;
  undefined4 local_78;
  undefined4 local_74;
  undefined4 local_70;
  undefined4 local_6c;
  undefined4 local_68;
  undefined4 local_64;
  float local_60 [4];
  uint local_50 [4];
  uint3 *local_40;
  uint3 *local_3c;
  uint *local_38;
  void *local_34;
  uint local_30;
  uint local_2c;
  uint local_28;
  byte *local_24;
  void *local_20;
  byte *local_1c;
  byte *local_18;
  uint local_14;
  uint local_10;
  int local_c;
  int local_8;

  if (param_2 < (void *)0x4) {
    return -0x7fffbffb;
  }
  pvVar8 = *(void **)param_1;
  local_38 = param_1;
  if (param_2 < pvVar8) {
    return -0x7fffbffb;
  }
  if (pvVar8 == (void *)0xc) {
    local_84 = (int)*(short *)((int)param_1 + 4);
    local_80 = (int)*(short *)((int)param_1 + 6);
    local_7c = *(undefined2 *)((int)param_1 + 8);
    local_88 = 0xc;
    local_7a = *(undefined2 *)((int)param_1 + 10);
    local_78 = 0;
    local_74 = 0;
    local_70 = 0;
    local_6c = 0;
    local_68 = 0;
    local_64 = 0;
    local_38 = &local_88;
    puVar14 = &local_88;
  }
  else {
    puVar14 = param_1;
    if (pvVar8 < (void *)0x28) {
      return -0x7fffbffb;
    }
  }
  local_20 = (void *)puVar14[1];
  local_30 = puVar14[2];
  if ((int)local_30 < 1) {
    local_30 = -local_30;
  }
  uVar18 = *puVar14;
  uVar3 = *(ushort *)((int)puVar14 + 0xe);
  uVar6 = puVar14[8];
  local_c = (uVar18 != 0xc) + 3;
  if ((uVar3 < 9) && (uVar6 == 0)) {
    uVar6 = 1 << ((byte)uVar3 & 0x1f);
  }
  local_24 = (byte *)(local_c * uVar6 + uVar18);
  if (param_2 < local_24) {
    return -0x7fffbffb;
  }
  if ((short)puVar14[3] != 1) {
    return -0x7fffbffb;
  }
  if (puVar14[4] < 3) {
    local_2c = (uint)uVar3;
    if (((local_2c == 1) || (local_2c == 4)) || (local_2c == 8)) {
      local_8 = 0x29;
      goto LAB_0057a272;
    }
    if (local_2c == 0x10) goto LAB_0057a17d;
    if (local_2c == 0x18) goto LAB_0057a0f1;
    if (local_2c != 0x20) {
      return -0x7fffbffb;
    }
  }
  else {
    if (puVar14[4] != 3) {
      return -0x7fffbffb;
    }
    if (uVar18 < 0x34) {
      return -0x7fffbffb;
    }
    local_14 = puVar14[0xb];
    local_34 = (void *)puVar14[0xc];
    local_10 = puVar14[10];
    if (uVar18 < 0x38) {
      local_28 = 0;
    }
    else {
      local_28 = puVar14[0xd];
    }
    local_2c = (uint)*(ushort *)((int)puVar14 + 0xe);
    local_8 = 0x74;
    if (local_2c == 0x10) {
      if (local_34 == (void *)0xff) {
        if (((local_14 == 0xff) && (local_10 == 0xff)) && (local_28 == 0xff00)) {
          local_8 = 0x33;
        }
        goto LAB_0057a272;
      }
      if (local_34 != (void *)0x1f) {
        if (local_34 == (void *)0xf) {
          if ((local_14 == 0xf0) && (local_10 == 0xf00)) {
            if (local_28 == 0xf000) {
              local_8 = 0x1a;
            }
            else if (local_28 == 0) {
              local_8 = 0x1e;
            }
          }
        }
        else if (local_34 == (void *)0x3) {
          if (((local_14 == 0x1c) && (local_10 == 0xe0)) && (local_28 == 0xff00)) {
            local_8 = 0x1d;
          }
        }
        else if (((local_34 == (void *)0xffff) && (local_14 == 0xffff)) &&
                ((local_10 == 0xffff && (local_28 == 0)))) {
          local_8 = 0x51;
        }
        goto LAB_0057a272;
      }
      if (local_14 == 0x7e0) {
        if ((local_10 == 0xf800) && (local_28 == 0)) {
          local_8 = 0x17;
        }
        goto LAB_0057a272;
      }
      if ((local_14 != 0x3e0) || (local_10 != 0x7c00)) goto LAB_0057a272;
      if (local_28 != 0) {
        if (local_28 == 0x8000) {
          local_8 = 0x19;
        }
        goto LAB_0057a272;
      }
LAB_0057a17d:
      local_8 = 0x18;
      goto LAB_0057a272;
    }
    if (local_2c == 0x18) {
      if (((local_34 != (void *)0xff) || (local_14 != 0xff00)) ||
         ((local_10 != 0xff0000 || (local_28 != 0)))) goto LAB_0057a272;
LAB_0057a0f1:
      local_8 = 0x14;
      goto LAB_0057a272;
    }
    if (local_2c != 0x20) {
      return -0x7fffbffb;
    }
    if (local_34 != (void *)0xff) {
      if (local_34 == (void *)0x3ff00000) {
        if (((local_14 == 0xffc00) && (local_10 == 0x3ff)) && (local_28 == 0xc0000000)) {
          local_8 = 0x1f;
        }
      }
      else if (local_34 == (void *)0xff0000) {
        if ((local_14 == 0xff00) && (local_10 == 0xff)) {
          if (local_28 == 0xff000000) {
            local_8 = 0x20;
          }
          else if (local_28 == 0) {
            local_8 = 0x21;
          }
        }
      }
      else if (local_34 == (void *)0x0) {
        if (((local_14 == 0xffff0000) && (local_10 == 0xffff)) && (local_28 == 0)) {
          local_8 = 0x22;
        }
      }
      else if (local_34 == (void *)0x3ff) {
        if (((local_14 == 0xffc00) && (local_10 == 0x3ff00000)) && (local_28 == 0xc0000000)) {
          local_8 = 0x23;
        }
      }
      else if (((local_34 == (void *)0xff00) && (local_14 == 0xff0000)) &&
              ((local_10 == 0xff000000 && (local_28 == 0)))) {
        local_8 = 0x16;
        local_24 = (void *)((int)local_24 + 1);
      }
      goto LAB_0057a272;
    }
    if ((local_14 != 0xff00) || (local_10 != 0xff0000)) goto LAB_0057a272;
    if (local_28 != 0) {
      if (local_28 == 0xff000000) {
        local_8 = 0x15;
      }
      goto LAB_0057a272;
    }
  }
  local_8 = 0x16;
LAB_0057a272:
  local_38 = puVar14;
  if ((*(int *)((int)this + 0x40) != 0) && (local_8 == 0x29)) {
    uVar18 = puVar14[8];
    if (uVar18 == 0) {
      uVar18 = 1 << ((byte)local_2c & 0x1f);
    }
    *(undefined4 *)((int)this + 0x3c) = 1;
    CFastVB__Helper_00426fd0(0x400);
    *(int *)((int)this + 8) = extraout_EAX;
    if (extraout_EAX == 0) {
      return -0x7ff8fff2;
    }
    puVar7 = (undefined1 *)(*puVar14 + (int)param_1);
    local_18 = (byte *)0x0;
    if (uVar18 != 0) {
      do {
        iVar11 = (int)local_18 * 4;
        *(undefined1 *)(iVar11 + *(int *)((int)this + 8)) = puVar7[2];
        *(undefined1 *)(iVar11 + 1 + *(int *)((int)this + 8)) = puVar7[1];
        uVar1 = *puVar7;
        puVar7 = puVar7 + local_c;
        *(undefined1 *)(iVar11 + 2 + *(int *)((int)this + 8)) = uVar1;
        *(undefined1 *)(iVar11 + 3 + *(int *)((int)this + 8)) = 0xff;
        local_18 = (byte *)((int)local_18 + 1);
        puVar14 = local_38;
      } while (local_18 < uVar18);
    }
    for (; uVar18 < 0x100; uVar18 = uVar18 + 1) {
      iVar11 = uVar18 * 4;
      *(undefined1 *)(iVar11 + *(int *)((int)this + 8)) = 0xff;
      *(undefined1 *)(iVar11 + 1 + *(int *)((int)this + 8)) = 0xff;
      *(undefined1 *)(iVar11 + 2 + *(int *)((int)this + 8)) = 0xff;
      *(undefined1 *)(iVar11 + 3 + *(int *)((int)this + 8)) = 0xff;
    }
  }
  uVar3 = *(ushort *)((int)puVar14 + 0xe);
  if (uVar3 == 1) {
    local_18 = local_20;
    pvVar8 = (void *)((int)local_20 + 7U >> 3);
  }
  else if (uVar3 == 4) {
    local_18 = local_20;
    pvVar8 = (void *)((int)local_20 + 1U >> 1);
  }
  else {
    pvVar8 = (void *)((uint)(uVar3 >> 3) * (int)local_20);
    local_18 = pvVar8;
  }
  if (local_8 == 0x74) {
    local_18 = (void *)((int)local_20 << 4);
  }
  local_2c = (int)pvVar8 + 3U & 0xfffffffc;
  if (((puVar14[4] == 0) || (puVar14[4] == 3)) &&
     (param_2 < (void *)((int)((local_30 - 1) * local_2c + (int)pvVar8) + (int)local_24))) {
    return -0x7fffbffb;
  }
  if (((puVar14[4] == 0) && (local_8 == 0x16)) && (local_1c = (byte *)0x0, local_30 != 0)) {
    local_c = (int)local_24 + (int)param_1;
    do {
      pvVar8 = (void *)0x0;
      if (local_20 != (void *)0x0) {
        do {
          if (*(char *)(local_c + 3 + (int)pvVar8 * 4) != '\0') {
            local_8 = 0x15;
            break;
          }
          pvVar8 = (void *)((int)pvVar8 + 1);
        } while (pvVar8 < local_20);
        if (pvVar8 < local_20) break;
      }
      local_1c = (byte *)((int)local_1c + 1);
      local_c = local_c + local_2c;
    } while (local_1c < local_30);
  }
  *(undefined4 *)((int)this + 0x34) = 0;
  uVar18 = (int)local_18 + 3U & 0xfffffffc;
  *(int *)this = local_8;
  *(uint *)((int)this + 0x30) = uVar18;
  *(void **)((int)this + 0xc) = local_20;
  *(uint *)((int)this + 0x10) = local_30;
  *(undefined4 *)((int)this + 0x14) = 1;
  if (*(int *)((int)this + 0x40) != 0) {
    if (((puVar14[4] == 0) || (puVar14[4] == 3)) &&
       (((int)puVar14[2] < 0 && ((7 < *(ushort *)((int)puVar14 + 0xe) && (local_8 != 0x74)))))) {
      *(undefined4 *)((int)this + 0x38) = 0;
      *(int *)((int)this + 4) = (int)local_24 + (int)param_1;
    }
    else {
      *(undefined4 *)((int)this + 0x38) = 1;
      CFastVB__Helper_00426fd0(uVar18 * local_30);
      local_1c = extraout_EAX_00;
      *(byte **)((int)this + 4) = extraout_EAX_00;
      if (extraout_EAX_00 == (byte *)0x0) {
        return -0x7ff8fff2;
      }
      iVar11 = *(int *)((int)this + 0x30);
      local_40 = (uint3 *)((int)local_24 + (int)param_1);
      local_24 = (byte *)((int)param_1 + (int)param_2);
      local_3c = local_40;
      if ((int)puVar14[2] < 0) {
        local_c = iVar11;
        pbVar12 = extraout_EAX_00;
      }
      else {
        local_c = -iVar11;
        pbVar12 = extraout_EAX_00 + (local_30 - 1) * iVar11;
      }
      pbVar15 = extraout_EAX_00 + iVar11 * local_30;
      puVar9 = local_40;
      pbVar13 = pbVar12;
      if (puVar14[4] == 2) {
        while ((extraout_EAX_00 <= pbVar13 && (pbVar13 < pbVar15))) {
          if (puVar9 < local_40) {
            return -0x7fffbffb;
          }
          pbVar19 = (byte *)((int)puVar9 + 1);
          if (local_24 <= pbVar19) {
            return -0x7fffbffb;
          }
          bVar10 = (byte)*puVar9;
          if (bVar10 == 0) {
            bVar10 = *pbVar19;
            uVar18 = (uint)bVar10;
            if (bVar10 == 0) {
              pbVar12 = pbVar13 + local_c;
              param_2 = pbVar12;
            }
            else {
              param_2 = pbVar15;
              if (uVar18 != 1) {
                if (uVar18 == 2) {
                  pbVar19 = (byte *)((int)puVar9 + 3);
                  if (local_24 <= pbVar19) {
                    return -0x7fffbffb;
                  }
                  puVar9 = (uint3 *)((int)puVar9 + 2);
                  pbVar12 = pbVar12 + (uint)*pbVar19 * local_c + (uint)*(byte *)puVar9;
                  param_2 = pbVar13;
                }
                else {
                  if (pbVar12 < extraout_EAX_00) {
                    return -0x7fffbffb;
                  }
                  if (pbVar15 < pbVar12 + uVar18) {
                    return -0x7fffbffb;
                  }
                  if ((bVar10 != 0) &&
                     (local_24 <= (byte *)(((int)(uVar18 - 1) >> 1) + 2 + (int)puVar9))) {
                    return -0x7fffbffb;
                  }
                  uVar18 = 0;
                  if (bVar10 != 0) {
                    do {
                      bVar10 = *(byte *)(((int)uVar18 >> 1) + 2 + (int)puVar9);
                      if ((uVar18 & 1) == 0) {
                        bVar10 = bVar10 >> 4;
                      }
                      else {
                        bVar10 = bVar10 & 0xf;
                      }
                      pbVar12[uVar18] = bVar10;
                      uVar18 = uVar18 + 1;
                    } while ((int)uVar18 < (int)(uint)*pbVar19);
                  }
                  pbVar12 = pbVar12 + *pbVar19;
                  puVar9 = (uint3 *)((int)puVar9 + ((*pbVar19 >> 1) + 1 & 0xfffffffe));
                  param_2 = pbVar13;
                }
              }
            }
          }
          else {
            if (pbVar12 < extraout_EAX_00) {
              return -0x7fffbffb;
            }
            if (pbVar15 < pbVar12 + bVar10) {
              return -0x7fffbffb;
            }
            uVar18 = 0;
            if (bVar10 != 0) {
              do {
                if ((uVar18 & 1) == 0) {
                  bVar10 = *pbVar19 >> 4;
                }
                else {
                  bVar10 = *pbVar19 & 0xf;
                }
                pbVar12[uVar18] = bVar10;
                uVar18 = uVar18 + 1;
              } while ((int)uVar18 < (int)(uint)(byte)*puVar9);
            }
            pbVar12 = pbVar12 + (byte)*puVar9;
            param_2 = pbVar13;
          }
          puVar9 = (uint3 *)((int)puVar9 + 2);
          pbVar13 = param_2;
        }
      }
      else if (puVar14[4] == 1) {
        while ((extraout_EAX_00 <= pbVar13 && (pbVar13 < pbVar15))) {
          if (puVar9 < local_40) {
            return -0x7fffbffb;
          }
          pbVar19 = (byte *)((int)puVar9 + 1);
          if (local_24 <= pbVar19) {
            return -0x7fffbffb;
          }
          bVar10 = (byte)*puVar9;
          if (bVar10 == 0) {
            uVar18 = (uint)*pbVar19;
            if (uVar18 == 0) {
              pbVar12 = pbVar13 + local_c;
              param_2 = pbVar12;
            }
            else {
              param_2 = pbVar15;
              if (uVar18 != 1) {
                if (uVar18 != 2) {
                  if (pbVar12 < extraout_EAX_00) {
                    return -0x7fffbffb;
                  }
                  if (pbVar15 < pbVar12 + uVar18) {
                    return -0x7fffbffb;
                  }
                  if (local_24 < (byte *)(uVar18 + 2 + (int)puVar9)) {
                    return -0x7fffbffb;
                  }
                  uVar6 = (uint)(*pbVar19 >> 2);
                  puVar16 = (ushort *)((int)puVar9 + 2);
                  pbVar19 = pbVar12;
                  for (; uVar6 != 0; uVar6 = uVar6 - 1) {
                    *(undefined4 *)pbVar19 = *(undefined4 *)puVar16;
                    puVar16 = puVar16 + 2;
                    pbVar19 = pbVar19 + 4;
                  }
                  for (uVar18 = uVar18 & 3; uVar18 != 0; uVar18 = uVar18 - 1) {
                    *pbVar19 = (byte)*puVar16;
                    puVar16 = (ushort *)((int)puVar16 + 1);
                    pbVar19 = pbVar19 + 1;
                  }
                  uVar18 = (uint)*(byte *)((int)puVar9 + 1);
                  puVar9 = (uint3 *)((int)puVar9 + (uVar18 + 1 & 0xfffffffe));
                  goto LAB_0057a6e7;
                }
                pbVar19 = (byte *)((int)puVar9 + 3);
                if (local_24 <= pbVar19) {
                  return -0x7fffbffb;
                }
                puVar9 = (uint3 *)((int)puVar9 + 2);
                pbVar12 = pbVar12 + (uint)*pbVar19 * local_c + (uint)*(byte *)puVar9;
                param_2 = pbVar13;
              }
            }
          }
          else {
            if (pbVar12 < extraout_EAX_00) {
              return -0x7fffbffb;
            }
            if (pbVar15 < pbVar12 + bVar10) {
              return -0x7fffbffb;
            }
            bVar2 = *pbVar19;
            pbVar19 = pbVar12;
            for (uVar18 = (uint)(bVar10 >> 2); uVar18 != 0; uVar18 = uVar18 - 1) {
              *(uint *)pbVar19 = CONCAT22(CONCAT11(bVar2,bVar2),CONCAT11(bVar2,bVar2));
              pbVar19 = pbVar19 + 4;
            }
            for (uVar18 = bVar10 & 3; uVar18 != 0; uVar18 = uVar18 - 1) {
              *pbVar19 = bVar2;
              pbVar19 = pbVar19 + 1;
            }
            uVar18 = (uint)(byte)*puVar9;
LAB_0057a6e7:
            pbVar12 = pbVar12 + uVar18;
            param_2 = pbVar13;
          }
          puVar9 = (uint3 *)((int)puVar9 + 2);
          pbVar13 = param_2;
        }
      }
      else if (*(short *)((int)puVar14 + 0xe) == 1) {
        for (; (extraout_EAX_00 <= pbVar12 && (pbVar12 < pbVar15)); pbVar12 = pbVar12 + local_c) {
          param_2 = (void *)0x0;
          if (local_20 != (void *)0x0) {
            do {
              *(byte *)((int)param_2 + (int)pbVar12) =
                   *(byte *)(((uint)param_2 >> 3) + (int)local_40) >>
                   (7 - ((byte)param_2 & 7) & 0x1f) & 1;
              param_2 = (void *)((int)param_2 + 1);
            } while (param_2 < local_20);
          }
          local_40 = (uint3 *)((int)local_40 + local_2c);
        }
      }
      else if (*(short *)((int)puVar14 + 0xe) == 4) {
        for (; (extraout_EAX_00 <= pbVar12 && (pbVar12 < pbVar15)); pbVar12 = pbVar12 + local_c) {
          pvVar8 = (void *)0x0;
          if (local_20 != (void *)0x0) {
            do {
              bVar10 = *(byte *)(((uint)pvVar8 >> 1) + (int)local_40);
              if (((uint)pvVar8 & 1) == 0) {
                bVar10 = bVar10 >> 4;
              }
              else {
                bVar10 = bVar10 & 0xf;
              }
              *(byte *)((int)pvVar8 + (int)pbVar12) = bVar10;
              pvVar8 = (void *)((int)pvVar8 + 1);
            } while (pvVar8 < local_20);
          }
          local_40 = (uint3 *)((int)local_40 + local_2c);
        }
      }
      else if (local_8 == 0x74) {
        local_50[0] = local_10;
        local_50[1] = local_14;
        local_50[2] = (uint)local_34;
        local_50[3] = local_28;
        uVar18 = 0;
        param_2 = pbVar12;
        do {
          puVar14 = (uint *)((int)local_50 + uVar18);
          *(int *)((int)local_98 + uVar18) = 0;
          if (*puVar14 != 0) {
            if ((*puVar14 & 1) == 0) {
              param_2 = (void *)0x0;
              do {
                *puVar14 = *puVar14 >> 1;
                param_2 = (void *)((int)param_2 + 1);
              } while ((*puVar14 & 1) == 0);
              *(int *)((int)local_98 + uVar18) = (int)param_2;
            }
            fVar5 = (float)(int)*puVar14;
            if ((int)*puVar14 < 0) {
              fVar5 = fVar5 + _DAT_005e72d8;
            }
            *(float *)((int)local_60 + uVar18) = _DAT_005e6a34 / fVar5;
          }
          uVar18 = uVar18 + 4;
        } while (uVar18 < 0x10);
        if (((local_10 == 0) && (local_14 == 0)) && (local_34 == (void *)0x0)) {
          local_60[2] = 0.0;
          local_50[2] = 1;
          local_50[1] = 1;
          local_60[1] = 0.0;
          local_50[0] = 1;
          local_60[0] = 0.0;
        }
        for (; (extraout_EAX_00 <= pbVar12 && (pbVar12 < pbVar15)); pbVar12 = pbVar12 + local_c) {
          local_18 = pbVar12;
          if (local_20 != (void *)0x0) {
            local_34 = local_20;
            puVar9 = local_40;
            do {
              sVar4 = *(short *)((int)local_38 + 0xe);
              if (sVar4 == 0x10) {
                param_2 = (void *)(uint)(ushort)*puVar9;
                puVar9 = (uint3 *)((int)puVar9 + 2);
              }
              else if (sVar4 == 0x18) {
                param_2 = (void *)(uint)*puVar9;
                puVar9 = (uint3 *)((int)puVar9 + 3);
              }
              else if (sVar4 == 0x20) {
                param_2 = *(void **)puVar9;
                puVar9 = puVar9 + 1;
              }
              uVar18 = 0;
              do {
                if (*(int *)((int)local_50 + uVar18) == 0) {
                  fVar5 = 1.0;
                }
                else {
                  local_3c = (uint3 *)((uint)param_2 >>
                                       ((byte)*(undefined4 *)((int)local_98 + uVar18) & 0x1f) &
                                      *(uint *)((int)local_50 + uVar18));
                  fVar5 = (float)(int)local_3c;
                  if ((int)local_3c < 0) {
                    fVar5 = fVar5 + _DAT_005e72d8;
                  }
                  fVar5 = fVar5 * *(float *)((int)local_60 + uVar18);
                }
                *(float *)(local_18 + uVar18) = fVar5;
                uVar18 = uVar18 + 4;
              } while (uVar18 < 0x10);
              local_18 = local_18 + 0x10;
              local_34 = (void *)((int)local_34 + -1);
            } while (local_34 != (void *)0x0);
          }
          local_40 = (uint3 *)((int)local_40 + local_2c);
        }
      }
      else {
        while ((extraout_EAX_00 <= pbVar12 && (pbVar12 < pbVar15))) {
          puVar9 = (uint3 *)((int)local_40 + local_2c);
          pbVar13 = pbVar12 + local_c;
          for (uVar18 = (uint)local_18 >> 2; uVar18 != 0; uVar18 = uVar18 - 1) {
            *(undefined4 *)pbVar12 = *(undefined4 *)local_40;
            local_40 = local_40 + 1;
            pbVar12 = pbVar12 + 4;
          }
          puVar17 = local_40;
          pbVar19 = pbVar12;
          for (uVar18 = (uint)local_18 & 3; local_40 = puVar9, pbVar12 = pbVar13, uVar18 != 0;
              uVar18 = uVar18 - 1) {
            *pbVar19 = (byte)*puVar17;
            puVar17 = (uint3 *)((int)puVar17 + 1);
            pbVar19 = pbVar19 + 1;
          }
        }
      }
    }
  }
  return 0;
}
