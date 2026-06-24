/* address: 0x005bcfd3 */
/* name: CDXTexture__Helper_005bcfd3 */
/* signature: void __stdcall CDXTexture__Helper_005bcfd3(uint param_1, void * param_2, int param_3) */


void CDXTexture__Helper_005bcfd3(uint param_1,void *param_2,int param_3)

{
  byte bVar1;
  int *piVar2;
  undefined1 *puVar3;
  int iVar4;
  uint uVar5;
  void *pvVar6;
  byte *pbVar7;
  uint uVar8;
  undefined1 *puVar9;
  undefined1 *puVar10;
  undefined1 *local_14;
  undefined1 *local_10;
  uint local_c;
  byte *local_8;

  pvVar6 = param_2;
  uVar5 = param_1;
  local_8 = *(byte **)param_2;
  local_c = *(uint *)((int)param_2 + 4);
  puVar10 = *(undefined1 **)(param_1 + 0x34);
  piVar2 = *(int **)(param_1 + 4);
  param_2 = *(void **)(param_1 + 0x20);
  if (puVar10 < *(undefined1 **)(param_1 + 0x30)) {
    local_10 = *(undefined1 **)(param_1 + 0x30) + (-1 - (int)puVar10);
    param_1 = *(uint *)(param_1 + 0x1c);
  }
  else {
    local_10 = (undefined1 *)(*(int *)(param_1 + 0x2c) - (int)puVar10);
    param_1 = *(uint *)(param_1 + 0x1c);
  }
  do {
    puVar9 = puVar10;
    switch(*piVar2) {
    case 0:
      if (((undefined1 *)0x101 < local_10) && (9 < local_c)) {
        *(void **)(uVar5 + 0x20) = param_2;
        *(uint *)(uVar5 + 0x1c) = param_1;
        *(uint *)((int)pvVar6 + 4) = local_c;
        *(int *)((int)pvVar6 + 8) = (int)(local_8 + (*(int *)((int)pvVar6 + 8) - *(int *)pvVar6));
        *(byte **)pvVar6 = local_8;
        *(undefined1 **)(uVar5 + 0x34) = puVar10;
        param_3 = CDXTexture__InflateFast_DecodeBlockStream
                            ((uint)*(byte *)(piVar2 + 4),(uint)*(byte *)((int)piVar2 + 0x11),
                             piVar2[5],piVar2[6],uVar5,pvVar6);
        puVar10 = *(undefined1 **)(uVar5 + 0x34);
        local_8 = *(byte **)pvVar6;
        local_c = *(uint *)((int)pvVar6 + 4);
        param_2 = *(void **)(uVar5 + 0x20);
        param_1 = *(uint *)(uVar5 + 0x1c);
        if (puVar10 < *(undefined1 **)(uVar5 + 0x30)) {
          local_10 = *(undefined1 **)(uVar5 + 0x30) + (-1 - (int)puVar10);
        }
        else {
          local_10 = (undefined1 *)(*(int *)(uVar5 + 0x2c) - (int)puVar10);
        }
        if (param_3 != 0) {
          *piVar2 = (uint)(param_3 != 1) * 2 + 7;
          break;
        }
      }
      piVar2[3] = (uint)*(byte *)(piVar2 + 4);
      piVar2[2] = piVar2[5];
      *piVar2 = 1;
    case 1:
      for (; param_1 < (uint)piVar2[3]; param_1 = param_1 + 8) {
        if (local_c == 0) goto LAB_005bd492;
        param_3 = 0;
        local_c = local_c - 1;
        param_2 = (void *)((uint)param_2 | (uint)*local_8 << ((byte)param_1 & 0x1f));
        local_8 = local_8 + 1;
      }
      pbVar7 = (byte *)(piVar2[2] + (*(uint *)(&DAT_0065ff60 + piVar2[3] * 4) & (uint)param_2) * 8);
      param_2 = (void *)((uint)param_2 >> (pbVar7[1] & 0x1f));
      param_1 = param_1 - pbVar7[1];
      bVar1 = *pbVar7;
      uVar8 = (uint)bVar1;
      if (uVar8 == 0) {
        pbVar7 = *(byte **)(pbVar7 + 4);
        *piVar2 = 6;
      }
      else {
        if ((bVar1 & 0x10) != 0) {
          piVar2[2] = uVar8 & 0xf;
          piVar2[1] = *(int *)(pbVar7 + 4);
          *piVar2 = 2;
          break;
        }
        if ((bVar1 & 0x40) != 0) {
          if ((bVar1 & 0x20) == 0) {
            *piVar2 = 9;
            *(char **)((int)pvVar6 + 0x18) = "invalid literal/length code";
switchD_005bd018_caseD_9:
            param_3 = -3;
            puVar9 = puVar10;
            goto LAB_005bd443;
          }
          *piVar2 = 7;
          break;
        }
        piVar2[3] = uVar8;
        pbVar7 = pbVar7 + *(int *)(pbVar7 + 4) * 8;
      }
LAB_005bd255:
      piVar2[2] = (int)pbVar7;
      break;
    case 2:
      for (; param_1 < (uint)piVar2[2]; param_1 = param_1 + 8) {
        if (local_c == 0) goto LAB_005bd492;
        param_3 = 0;
        local_c = local_c - 1;
        param_2 = (void *)((uint)param_2 | (uint)*local_8 << ((byte)param_1 & 0x1f));
        local_8 = local_8 + 1;
      }
      piVar2[1] = piVar2[1] + (*(uint *)(&DAT_0065ff60 + piVar2[2] * 4) & (uint)param_2);
      param_2 = (void *)((uint)param_2 >> ((byte)piVar2[2] & 0x1f));
      param_1 = param_1 - piVar2[2];
      piVar2[3] = (uint)*(byte *)((int)piVar2 + 0x11);
      piVar2[2] = piVar2[6];
      *piVar2 = 3;
    case 3:
      for (; param_1 < (uint)piVar2[3]; param_1 = param_1 + 8) {
        if (local_c == 0) goto LAB_005bd492;
        param_3 = 0;
        local_c = local_c - 1;
        param_2 = (void *)((uint)param_2 | (uint)*local_8 << ((byte)param_1 & 0x1f));
        local_8 = local_8 + 1;
      }
      pbVar7 = (byte *)(piVar2[2] + (*(uint *)(&DAT_0065ff60 + piVar2[3] * 4) & (uint)param_2) * 8);
      param_2 = (void *)((uint)param_2 >> (pbVar7[1] & 0x1f));
      param_1 = param_1 - pbVar7[1];
      bVar1 = *pbVar7;
      if ((bVar1 & 0x10) == 0) {
        if ((bVar1 & 0x40) != 0) {
          *piVar2 = 9;
          *(char **)((int)pvVar6 + 0x18) = "invalid distance code";
          goto switchD_005bd018_caseD_9;
        }
        piVar2[3] = (uint)bVar1;
        pbVar7 = pbVar7 + *(int *)(pbVar7 + 4) * 8;
        goto LAB_005bd255;
      }
      piVar2[2] = bVar1 & 0xf;
      piVar2[3] = *(int *)(pbVar7 + 4);
      *piVar2 = 4;
      break;
    case 4:
      for (; param_1 < (uint)piVar2[2]; param_1 = param_1 + 8) {
        if (local_c == 0) goto LAB_005bd492;
        param_3 = 0;
        local_c = local_c - 1;
        param_2 = (void *)((uint)param_2 | (uint)*local_8 << ((byte)param_1 & 0x1f));
        local_8 = local_8 + 1;
      }
      piVar2[3] = piVar2[3] + (*(uint *)(&DAT_0065ff60 + piVar2[2] * 4) & (uint)param_2);
      param_2 = (void *)((uint)param_2 >> ((byte)piVar2[2] & 0x1f));
      param_1 = param_1 - piVar2[2];
      *piVar2 = 5;
    case 5:
      local_14 = puVar10 + -piVar2[3];
      if (local_14 < *(undefined1 **)(uVar5 + 0x28)) {
        do {
          local_14 = local_14 + (*(int *)(uVar5 + 0x2c) - (int)*(undefined1 **)(uVar5 + 0x28));
        } while (local_14 < *(undefined1 **)(uVar5 + 0x28));
      }
      while (piVar2[1] != 0) {
        puVar9 = puVar10;
        if (local_10 == (undefined1 *)0x0) {
          if (puVar10 == *(undefined1 **)(uVar5 + 0x2c)) {
            local_10 = *(undefined1 **)(uVar5 + 0x30);
            puVar9 = *(undefined1 **)(uVar5 + 0x28);
            if (local_10 != puVar9) {
              if (puVar9 < local_10) {
                local_10 = local_10 + (-1 - (int)puVar9);
              }
              else {
                local_10 = *(undefined1 **)(uVar5 + 0x2c) + -(int)puVar9;
              }
              puVar10 = puVar9;
              if (local_10 != (undefined1 *)0x0) goto LAB_005bd369;
            }
          }
          *(undefined1 **)(uVar5 + 0x34) = puVar10;
          param_3 = CDXTexture__Helper_005bda5e((void *)uVar5,(int)pvVar6,param_3);
          puVar9 = *(undefined1 **)(uVar5 + 0x34);
          puVar10 = *(undefined1 **)(uVar5 + 0x30);
          if (puVar9 < puVar10) {
            local_10 = puVar10 + (-1 - (int)puVar9);
          }
          else {
            local_10 = (undefined1 *)(*(int *)(uVar5 + 0x2c) - (int)puVar9);
          }
          if ((puVar9 == *(undefined1 **)(uVar5 + 0x2c)) &&
             (puVar3 = *(undefined1 **)(uVar5 + 0x28), puVar10 != puVar3)) {
            puVar9 = puVar3;
            if (puVar3 < puVar10) {
              local_10 = puVar10 + (-1 - (int)puVar3);
            }
            else {
              local_10 = *(undefined1 **)(uVar5 + 0x2c) + -(int)puVar3;
            }
          }
          if (local_10 == (undefined1 *)0x0) goto LAB_005bd443;
        }
LAB_005bd369:
        param_3 = 0;
        *puVar9 = *local_14;
        puVar10 = puVar9 + 1;
        local_14 = local_14 + 1;
        local_10 = local_10 + -1;
        if (local_14 == *(undefined1 **)(uVar5 + 0x2c)) {
          local_14 = *(undefined1 **)(uVar5 + 0x28);
        }
        piVar2[1] = piVar2[1] + -1;
      }
      *piVar2 = 0;
      break;
    case 6:
      if (local_10 != (undefined1 *)0x0) goto LAB_005bd425;
      if (puVar10 == *(undefined1 **)(uVar5 + 0x2c)) {
        local_10 = *(undefined1 **)(uVar5 + 0x30);
        puVar9 = *(undefined1 **)(uVar5 + 0x28);
        if (local_10 != puVar9) {
          if (puVar9 < local_10) {
            local_10 = local_10 + (-1 - (int)puVar9);
          }
          else {
            local_10 = *(undefined1 **)(uVar5 + 0x2c) + -(int)puVar9;
          }
          puVar10 = puVar9;
          if (local_10 != (undefined1 *)0x0) goto LAB_005bd425;
        }
      }
      *(undefined1 **)(uVar5 + 0x34) = puVar10;
      param_3 = CDXTexture__Helper_005bda5e((void *)uVar5,(int)pvVar6,param_3);
      puVar9 = *(undefined1 **)(uVar5 + 0x34);
      puVar10 = *(undefined1 **)(uVar5 + 0x30);
      if (puVar9 < puVar10) {
        local_10 = puVar10 + (-1 - (int)puVar9);
      }
      else {
        local_10 = (undefined1 *)(*(int *)(uVar5 + 0x2c) - (int)puVar9);
      }
      if ((puVar9 == *(undefined1 **)(uVar5 + 0x2c)) &&
         (puVar3 = *(undefined1 **)(uVar5 + 0x28), puVar10 != puVar3)) {
        puVar9 = puVar3;
        if (puVar3 < puVar10) {
          local_10 = puVar10 + (-1 - (int)puVar3);
        }
        else {
          local_10 = *(undefined1 **)(uVar5 + 0x2c) + -(int)puVar3;
        }
      }
      if (local_10 == (undefined1 *)0x0) goto LAB_005bd443;
LAB_005bd425:
      param_3 = 0;
      *puVar9 = (char)piVar2[2];
      puVar10 = puVar9 + 1;
      local_10 = local_10 + -1;
      *piVar2 = 0;
      break;
    case 7:
      if (7 < param_1) {
        param_1 = param_1 - 8;
        local_c = local_c + 1;
        local_8 = local_8 + -1;
      }
      *(undefined1 **)(uVar5 + 0x34) = puVar10;
      param_3 = CDXTexture__Helper_005bda5e((void *)uVar5,(int)pvVar6,param_3);
      puVar10 = *(undefined1 **)(uVar5 + 0x34);
      if (*(undefined1 **)(uVar5 + 0x30) == puVar10) {
        *piVar2 = 8;
switchD_005bd018_caseD_8:
        param_3 = 1;
        puVar9 = puVar10;
LAB_005bd443:
        *(void **)(uVar5 + 0x20) = param_2;
        *(uint *)(uVar5 + 0x1c) = param_1;
        *(uint *)((int)pvVar6 + 4) = local_c;
        puVar10 = puVar9;
LAB_005bd455:
        iVar4 = *(int *)pvVar6;
        *(byte **)pvVar6 = local_8;
        *(int *)((int)pvVar6 + 8) = (int)(local_8 + (*(int *)((int)pvVar6 + 8) - iVar4));
      }
      else {
        *(void **)(uVar5 + 0x20) = param_2;
        *(uint *)(uVar5 + 0x1c) = param_1;
        *(uint *)((int)pvVar6 + 4) = local_c;
        iVar4 = *(int *)pvVar6;
        *(byte **)pvVar6 = local_8;
        *(int *)((int)pvVar6 + 8) = (int)(local_8 + (*(int *)((int)pvVar6 + 8) - iVar4));
      }
      *(undefined1 **)(uVar5 + 0x34) = puVar10;
      CDXTexture__Helper_005bda5e((void *)uVar5,(int)pvVar6,param_3);
      return;
    case 8:
      goto switchD_005bd018_caseD_8;
    case 9:
      goto switchD_005bd018_caseD_9;
    default:
      param_3 = -2;
      goto LAB_005bd443;
    }
  } while( true );
LAB_005bd492:
  *(void **)(uVar5 + 0x20) = param_2;
  *(uint *)(uVar5 + 0x1c) = param_1;
  *(undefined4 *)((int)pvVar6 + 4) = 0;
  goto LAB_005bd455;
}
