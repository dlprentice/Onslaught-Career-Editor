/* address: 0x0058f66f */
/* name: CTexture__Unk_0058f66f */
/* signature: int __thiscall CTexture__Unk_0058f66f(void * this, void * param_1, int param_2, int param_3) */


int __thiscall CTexture__Unk_0058f66f(void *this,void *param_1,int param_2,int param_3)

{
  byte bVar1;
  int extraout_EAX;
  int iVar2;
  uint uVar3;
  uint extraout_EAX_00;
  int iVar4;
  int extraout_EAX_01;
  uint uVar5;
  byte *pbVar6;
  byte *pbVar7;
  byte *pbVar8;
  int unaff_EDI;
  bool bVar9;
  char *pcVar10;
  byte local_40 [16];
  int local_30;
  undefined4 local_2c;
  int local_28;
  int local_24;
  byte *local_20;
  byte *local_1c;
  byte *local_18;
  undefined4 local_14;
  undefined4 *local_10;
  int local_c;
  uint local_8;

  pbVar7 = *(byte **)((int)param_1 + 8);
  bVar1 = *pbVar7;
  local_10 = this;
  local_c = 0;
  local_8 = 0;
  local_14 = 0;
  local_2c = 0;
  local_30 = 1;
  local_24 = 0;
  local_28 = 0;
  local_1c = pbVar7;
  local_18 = pbVar7;
  local_20 = pbVar7;
  do {
    local_10 = this;
    if (bVar1 == 0) {
      if (((((((*(int *)((int)this + 0x78) == 0) || (local_c == 3)) || (local_c == 5)) ||
            ((local_c == 6 || (local_c == 8)))) ||
           ((local_c == 9 || ((local_c == 4 || (local_c == 0xf)))))) || (local_c == 0x12)) ||
         (local_c == 0x13)) {
LAB_0058facd:
        CFastVB__Helper_00426fd0(0x2c);
        if (extraout_EAX_01 == 0) {
          iVar2 = 0;
        }
        else {
          iVar2 = CTexture__Helper_0059996f();
        }
        if (iVar2 != 0) {
          if (param_2 == 0) {
            return iVar2;
          }
          *(undefined4 *)(iVar2 + 0x28) = *(undefined4 *)(param_2 + 0x28);
          *(undefined4 *)(param_2 + 0x28) = 0;
          return iVar2;
        }
      }
      else {
        CTexture__Helper_0058c893(*(void **)this,(int)param_1,0x7d5,0x5ed078);
LAB_0058f725:
        *(undefined4 *)((int)this + 0x4c) = 1;
        CFastVB__Helper_00426fd0(0x2c);
        if (extraout_EAX != 0) {
          iVar2 = CTexture__Helper_0059996f();
          return iVar2;
        }
      }
      return 0;
    }
    while ((*pbVar7 != 0 && (*pbVar7 != 0x5f))) {
      pbVar7 = pbVar7 + 1;
      local_18 = pbVar7;
    }
    uVar3 = (int)pbVar7 - (int)local_20;
    if (0xf < uVar3) goto LAB_0058fa9e;
    pbVar8 = local_20;
    pbVar6 = local_40;
    for (uVar5 = uVar3 >> 2; uVar5 != 0; uVar5 = uVar5 - 1) {
      *(undefined4 *)pbVar6 = *(undefined4 *)pbVar8;
      pbVar8 = pbVar8 + 4;
      pbVar6 = pbVar6 + 4;
    }
    bVar1 = *pbVar7;
    for (uVar5 = uVar3 & 3; uVar5 != 0; uVar5 = uVar5 - 1) {
      *pbVar6 = *pbVar8;
      pbVar8 = pbVar8 + 1;
      pbVar6 = pbVar6 + 1;
    }
    local_40[uVar3] = 0;
    if (bVar1 != 0) {
      pbVar7 = pbVar7 + 1;
      local_18 = pbVar7;
    }
    local_20 = pbVar7;
    if (local_30 != 0) {
      pbVar7 = local_40;
      pbVar8 = (byte *)0x0;
      pbVar6 = (byte *)0x0;
      if (local_40[0] == 0) {
LAB_0058f7c5:
        local_8 = 0xffffffff;
      }
      else {
        do {
          pbVar6 = (byte *)(int)(char)*pbVar7;
          uVar3 = CTexture__Helper_0056a05b(pbVar8,(byte *)(int)(char)*pbVar7,unaff_EDI);
          pbVar8 = pbVar6;
          if (uVar3 == 0) break;
          pbVar7 = pbVar7 + 1;
        } while (*pbVar7 != 0);
        pbVar6 = pbVar8;
        if (*pbVar7 == 0) goto LAB_0058f7c5;
        pbVar6 = pbVar7;
        CSoundManager__Helper_0055e2a6(pbVar7);
        local_8 = extraout_EAX_00;
      }
      if (*pbVar7 != 0) {
        *pbVar7 = 0;
        pbVar7 = pbVar7 + 1;
      }
      bVar1 = *pbVar7;
      if (bVar1 != 0) {
        do {
          pbVar8 = (byte *)(int)(char)bVar1;
          uVar3 = CTexture__Helper_0056a089(pbVar6,(byte *)(int)(char)bVar1,unaff_EDI);
          pbVar6 = pbVar8;
          if (uVar3 == 0) break;
          pbVar7 = pbVar7 + 1;
          bVar1 = *pbVar7;
        } while (bVar1 != 0);
        if (*pbVar7 != 0) goto LAB_0058fa9e;
      }
      iVar2 = 0;
      uVar3 = 0;
      do {
        pbVar8 = *(byte **)((int)&PTR_DAT_005ec010 + uVar3);
        pbVar7 = local_40;
        do {
          bVar1 = *pbVar7;
          bVar9 = bVar1 < *pbVar8;
          if (bVar1 != *pbVar8) {
LAB_0058f826:
            iVar4 = (1 - (uint)bVar9) - (uint)(bVar9 != 0);
            goto LAB_0058f82d;
          }
          if (bVar1 == 0) break;
          bVar1 = pbVar7[1];
          bVar9 = bVar1 < pbVar8[1];
          if (bVar1 != pbVar8[1]) goto LAB_0058f826;
          pbVar7 = pbVar7 + 2;
          pbVar8 = pbVar8 + 2;
        } while (bVar1 != 0);
        iVar4 = 0;
LAB_0058f82d:
        if (iVar4 == 0) break;
        uVar3 = uVar3 + 0x48;
        iVar2 = iVar2 + 1;
      } while (uVar3 < 0x5e8);
      if (iVar2 != 0x15) {
        iVar4 = local_10[0xe];
        uVar3 = *(uint *)(&DAT_005ec018 + (iVar4 + iVar2 * 0x12) * 4);
        if (uVar3 != 0xffffffff) {
          if ((int)uVar3 < 0) {
            if (local_8 == 0xffffffff) {
              if (param_2 == 0) goto LAB_0058fa9e;
              local_8 = *(uint *)(param_2 + 0x18);
            }
            else if (param_2 != 0) {
              local_8 = local_8 + *(int *)(param_2 + 0x18);
            }
            uVar3 = -uVar3;
          }
          else if (param_2 != 0) goto LAB_0058fa9e;
          if (local_8 == 0xffffffff) {
            if (uVar3 == 0) {
              local_8 = 0;
LAB_0058f8c0:
              local_c = (&DAT_005ec014)[iVar2 * 0x12];
              local_2c = (&DAT_005ec054)[iVar2 * 0x12];
              if (local_c == 2) {
                uVar3 = local_8 & 0x1fff;
                if (uVar3 < 0x800) {
                  local_c = 2;
                }
                else if (uVar3 < 0x1000) {
                  local_c = 0xb;
                }
                else if (uVar3 < 0x1800) {
                  local_c = 0xc;
                }
                else if (uVar3 < 0x2000) {
                  local_c = 0xd;
                }
                local_8 = local_8 & 0x7ff;
              }
              else if (local_c == -3) {
                local_c = 4;
LAB_0058f93d:
                local_8 = 0;
              }
              else if (local_c == -4) {
                local_c = 4;
                local_8 = 2;
              }
              else {
                if (local_c == -5) {
                  local_c = 4;
                }
                else {
                  if (local_c == -6) {
                    local_c = 0x11;
                    goto LAB_0058f93d;
                  }
                  if (local_c != -7) goto LAB_0058f982;
                  local_c = 0x11;
                }
                local_8 = 1;
              }
LAB_0058f982:
              local_30 = 0;
              if ((5 < iVar4) && (iVar4 < 10)) {
                local_24 = 1;
              }
              pbVar7 = local_18;
              if (((3 < iVar4) && (iVar4 < 6)) || ((0xc < iVar4 && (iVar4 < 0xf)))) {
                local_28 = 1;
              }
              goto LAB_0058f9b4;
            }
          }
          else if (((param_2 != 0) && (*(int *)(param_2 + 0x28) != 0)) || (local_8 < uVar3))
          goto LAB_0058f8c0;
        }
      }
LAB_0058fa9e:
      this = local_10;
      if (local_10[0x1e] != 0) {
        iVar2 = CTexture__Helper_0058f34c();
        if (iVar2 < 0) goto LAB_0058f725;
        goto LAB_0058facd;
      }
      if (param_2 == 0) {
        pcVar10 = "invalid register \'%s\'";
      }
      else {
        if (*(int *)(param_2 + 0x28) == 0) {
          CTexture__Helper_0058c893((void *)*local_10,(int)param_1,0x7d5,0x5ed040);
          goto LAB_0058f725;
        }
        if (*(int *)(*(int *)(param_2 + 0x28) + 0x10) == -1) goto LAB_0058f725;
        pcVar10 = "invalid register \'%s[...]\'";
      }
      CTexture__Helper_0058c893((void *)*local_10,(int)param_1,0x7d5,(int)pcVar10);
      goto LAB_0058f725;
    }
    if (local_24 == 0) {
LAB_0058fa73:
      if (local_28 != 0) {
        iVar2 = 4;
        bVar9 = true;
        pbVar8 = local_40;
        pbVar6 = &DAT_005ec7f4;
        do {
          if (iVar2 == 0) break;
          iVar2 = iVar2 + -1;
          bVar9 = *pbVar8 == *pbVar6;
          pbVar8 = pbVar8 + 1;
          pbVar6 = pbVar6 + 1;
        } while (bVar9);
        if (bVar9) {
          local_14 = 0xb000000;
          local_28 = 0;
          goto LAB_0058f9b4;
        }
      }
      goto LAB_0058fa9e;
    }
    iVar2 = 5;
    bVar9 = true;
    pbVar8 = local_40;
    pbVar6 = &DAT_005ed070;
    do {
      if (iVar2 == 0) break;
      iVar2 = iVar2 + -1;
      bVar9 = *pbVar8 == *pbVar6;
      pbVar8 = pbVar8 + 1;
      pbVar6 = pbVar6 + 1;
    } while (bVar9);
    if (bVar9) {
      local_14 = 0x2000000;
    }
    else {
      iVar2 = 4;
      bVar9 = true;
      pbVar8 = local_40;
      pbVar6 = &DAT_005ed06c;
      do {
        if (iVar2 == 0) break;
        iVar2 = iVar2 + -1;
        bVar9 = *pbVar8 == *pbVar6;
        pbVar8 = pbVar8 + 1;
        pbVar6 = pbVar6 + 1;
      } while (bVar9);
      if (bVar9) {
        local_14 = 0x4000000;
      }
      else {
        iVar2 = 3;
        bVar9 = true;
        pbVar8 = local_40;
        pbVar6 = &DAT_005eca78;
        do {
          if (iVar2 == 0) break;
          iVar2 = iVar2 + -1;
          bVar9 = *pbVar8 == *pbVar6;
          pbVar8 = pbVar8 + 1;
          pbVar6 = pbVar6 + 1;
        } while (bVar9);
        if (bVar9) {
          local_14 = 0x7000000;
        }
        else {
          iVar2 = 3;
          bVar9 = true;
          pbVar8 = local_40;
          pbVar6 = &DAT_005ed068;
          do {
            if (iVar2 == 0) break;
            iVar2 = iVar2 + -1;
            bVar9 = *pbVar8 == *pbVar6;
            pbVar8 = pbVar8 + 1;
            pbVar6 = pbVar6 + 1;
          } while (bVar9);
          if (!bVar9) {
            iVar2 = 3;
            bVar9 = true;
            pbVar8 = local_40;
            pbVar6 = &DAT_005ed064;
            do {
              if (iVar2 == 0) break;
              iVar2 = iVar2 + -1;
              bVar9 = *pbVar8 == *pbVar6;
              pbVar8 = pbVar8 + 1;
              pbVar6 = pbVar6 + 1;
            } while (bVar9);
            if (!bVar9) {
              iVar2 = 3;
              bVar9 = true;
              pbVar8 = local_40;
              pbVar6 = &DAT_005ed060;
              do {
                if (iVar2 == 0) break;
                iVar2 = iVar2 + -1;
                bVar9 = *pbVar8 == *pbVar6;
                pbVar8 = pbVar8 + 1;
                pbVar6 = pbVar6 + 1;
              } while (bVar9);
              if (!bVar9) {
                iVar2 = 3;
                bVar9 = true;
                pbVar8 = local_40;
                pbVar6 = &DAT_005ed05c;
                do {
                  if (iVar2 == 0) break;
                  iVar2 = iVar2 + -1;
                  bVar9 = *pbVar8 == *pbVar6;
                  pbVar8 = pbVar8 + 1;
                  pbVar6 = pbVar6 + 1;
                } while (bVar9);
                if (!bVar9) goto LAB_0058fa73;
              }
              local_14 = 0xa000000;
              goto LAB_0058fa6b;
            }
          }
          local_14 = 0x9000000;
        }
      }
    }
LAB_0058fa6b:
    local_24 = 0;
LAB_0058f9b4:
    bVar1 = *pbVar7;
    this = local_10;
  } while( true );
}
