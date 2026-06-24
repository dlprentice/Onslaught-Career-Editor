/* address: 0x005be360 */
/* name: CDXTexture__Unk_005be360 */
/* signature: int __stdcall CDXTexture__Unk_005be360(int param_1, int param_2, int param_3, int param_4, int param_5, void * param_6) */


int CDXTexture__Unk_005be360
              (int param_1,int param_2,int param_3,int param_4,int param_5,void *param_6)

{
  byte bVar1;
  int iVar2;
  void *pvVar3;
  byte *pbVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  byte *pbVar12;
  byte *local_14;
  byte *local_10;
  byte *local_c;
  uint local_8;

  pvVar3 = param_6;
  local_10 = *(byte **)(param_5 + 0x34);
  uVar9 = *(uint *)(param_5 + 0x1c);
  local_c = *(byte **)param_6;
  local_8 = *(uint *)((int)param_6 + 4);
  param_6 = *(void **)(param_5 + 0x20);
  if (local_10 < *(byte **)(param_5 + 0x30)) {
    local_14 = *(byte **)(param_5 + 0x30) + (-1 - (int)local_10);
  }
  else {
    local_14 = (byte *)(*(int *)(param_5 + 0x2c) - (int)local_10);
  }
  uVar8 = *(uint *)(&DAT_0065ff60 + param_1 * 4);
  uVar6 = *(uint *)(&DAT_0065ff60 + param_2 * 4);
  do {
    for (; uVar9 < 0x14; uVar9 = uVar9 + 8) {
      local_8 = local_8 - 1;
      param_6 = (void *)((uint)param_6 | (uint)*local_c << ((byte)uVar9 & 0x1f));
      local_c = local_c + 1;
    }
    pbVar12 = (byte *)(param_3 + (uVar8 & (uint)param_6) * 8);
    bVar1 = *pbVar12;
LAB_005be40b:
    uVar7 = (uint)bVar1;
    if (uVar7 != 0) {
      param_6 = (void *)((uint)param_6 >> (pbVar12[1] & 0x1f));
      uVar9 = uVar9 - pbVar12[1];
      if ((bVar1 & 0x10) != 0) {
        uVar7 = uVar7 & 0xf;
        uVar10 = *(uint *)(&DAT_0065ff60 + uVar7 * 4) & (uint)param_6;
        param_6 = (void *)((uint)param_6 >> (sbyte)uVar7);
        uVar10 = uVar10 + *(int *)(pbVar12 + 4);
        for (uVar9 = uVar9 - uVar7; uVar9 < 0xf; uVar9 = uVar9 + 8) {
          local_8 = local_8 - 1;
          param_6 = (void *)((uint)param_6 | (uint)*local_c << ((byte)uVar9 & 0x1f));
          local_c = local_c + 1;
        }
        pbVar12 = (byte *)(param_4 + (uVar6 & (uint)param_6) * 8);
        param_6 = (void *)((uint)param_6 >> (pbVar12[1] & 0x1f));
        uVar9 = uVar9 - pbVar12[1];
        while( true ) {
          bVar1 = *pbVar12;
          if ((bVar1 & 0x10) != 0) {
            uVar7 = bVar1 & 0xf;
            for (; uVar9 < uVar7; uVar9 = uVar9 + 8) {
              local_8 = local_8 - 1;
              param_6 = (void *)((uint)param_6 | (uint)*local_c << ((byte)uVar9 & 0x1f));
              local_c = local_c + 1;
            }
            uVar11 = *(uint *)(&DAT_0065ff60 + uVar7 * 4) & (uint)param_6;
            param_6 = (void *)((uint)param_6 >> (sbyte)uVar7);
            local_14 = local_14 + -uVar10;
            uVar9 = uVar9 - uVar7;
            pbVar4 = local_10 + -(uVar11 + *(int *)(pbVar12 + 4));
            pbVar12 = *(byte **)(param_5 + 0x28);
            if (pbVar4 < pbVar12) {
              do {
                pbVar4 = pbVar4 + (*(int *)(param_5 + 0x2c) - (int)pbVar12);
              } while (pbVar4 < pbVar12);
              uVar7 = *(int *)(param_5 + 0x2c) - (int)pbVar4;
              if (uVar7 < uVar10) {
                param_1 = uVar10 - uVar7;
                do {
                  *local_10 = *pbVar4;
                  local_10 = local_10 + 1;
                  pbVar4 = pbVar4 + 1;
                  uVar7 = uVar7 - 1;
                } while (uVar7 != 0);
                pbVar12 = *(byte **)(param_5 + 0x28);
                do {
                  *local_10 = *pbVar12;
                  local_10 = local_10 + 1;
                  pbVar12 = pbVar12 + 1;
                  param_1 = param_1 + -1;
                } while (param_1 != 0);
              }
              else {
                *local_10 = *pbVar4;
                local_10[1] = pbVar4[1];
                local_10 = local_10 + 2;
                pbVar4 = pbVar4 + 2;
                param_1 = uVar10 - 2;
                do {
                  *local_10 = *pbVar4;
                  local_10 = local_10 + 1;
                  pbVar4 = pbVar4 + 1;
                  param_1 = param_1 + -1;
                } while (param_1 != 0);
              }
            }
            else {
              *local_10 = *pbVar4;
              local_10[1] = pbVar4[1];
              local_10 = local_10 + 2;
              pbVar4 = pbVar4 + 2;
              param_1 = uVar10 - 2;
              do {
                *local_10 = *pbVar4;
                local_10 = local_10 + 1;
                pbVar4 = pbVar4 + 1;
                param_1 = param_1 + -1;
              } while (param_1 != 0);
            }
            goto LAB_005be57b;
          }
          if ((bVar1 & 0x40) != 0) break;
          pbVar12 = pbVar12 + ((*(uint *)(&DAT_0065ff60 + (uint)bVar1 * 4) & (uint)param_6) +
                              *(int *)(pbVar12 + 4)) * 8;
          param_6 = (void *)((uint)param_6 >> (pbVar12[1] & 0x1f));
          uVar9 = uVar9 - pbVar12[1];
        }
        uVar8 = *(int *)((int)pvVar3 + 4) - local_8;
        *(char **)((int)pvVar3 + 0x18) = "invalid distance code";
        if (uVar9 >> 3 < uVar8) {
          uVar8 = uVar9 >> 3;
        }
LAB_005be5eb:
        iVar5 = -3;
        goto LAB_005be5ee;
      }
      if ((bVar1 & 0x40) == 0) break;
      uVar6 = uVar9 >> 3;
      if ((bVar1 & 0x20) == 0) {
        uVar8 = *(int *)((int)pvVar3 + 4) - local_8;
        *(char **)((int)pvVar3 + 0x18) = "invalid literal/length code";
        if (uVar6 < uVar8) {
          uVar8 = uVar6;
        }
        goto LAB_005be5eb;
      }
      uVar8 = *(int *)((int)pvVar3 + 4) - local_8;
      if (uVar6 < uVar8) {
        uVar8 = uVar6;
      }
      iVar5 = 1;
      goto LAB_005be5ee;
    }
    param_6 = (void *)((uint)param_6 >> (pbVar12[1] & 0x1f));
    uVar9 = uVar9 - pbVar12[1];
    local_14 = local_14 + -1;
    *local_10 = pbVar12[4];
    local_10 = local_10 + 1;
LAB_005be57b:
    if ((local_14 < (byte *)0x102) || (local_8 < 10)) {
      uVar8 = *(int *)((int)pvVar3 + 4) - local_8;
      if (uVar9 >> 3 < uVar8) {
        uVar8 = uVar9 >> 3;
      }
      iVar5 = 0;
LAB_005be5ee:
      *(void **)(param_5 + 0x20) = param_6;
      *(uint *)(param_5 + 0x1c) = uVar9 + uVar8 * -8;
      *(uint *)((int)pvVar3 + 4) = uVar8 + local_8;
      iVar2 = *(int *)pvVar3;
      *(uint *)pvVar3 = (int)local_c - uVar8;
      *(int *)((int)pvVar3 + 8) = *(int *)((int)pvVar3 + 8) + (((int)local_c - uVar8) - iVar2);
      *(byte **)(param_5 + 0x34) = local_10;
      return iVar5;
    }
  } while( true );
  pbVar12 = pbVar12 + ((*(uint *)(&DAT_0065ff60 + uVar7 * 4) & (uint)param_6) +
                      *(int *)(pbVar12 + 4)) * 8;
  bVar1 = *pbVar12;
  goto LAB_005be40b;
}
