/* address: 0x0059d036 */
/* name: CDXTexture__Helper_0059d036 */
/* signature: void __stdcall CDXTexture__Helper_0059d036(void * param_1, void * param_2, int param_3) */


void CDXTexture__Helper_0059d036(void *param_1,void *param_2,int param_3)

{
  void *pvVar1;
  byte bVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  int *piVar6;
  uint uVar7;
  int *piVar8;
  byte *pbVar9;
  int *piVar10;
  byte *pbVar11;
  int local_18 [4];
  uint local_8;

  if ((param_2 != (void *)0x0) && (param_1 != (void *)0x0)) {
    local_18[3] = *(int *)(&DAT_005f39d8 + param_3 * 4);
    iVar3 = *(int *)param_1;
    iVar5 = iVar3 * local_18[3];
    bVar2 = *(byte *)((int)param_1 + 0xb);
    if (bVar2 == 1) {
      local_18[2] = 0;
      pbVar11 = (byte *)((iVar3 - 1U >> 3) + (int)param_2);
      pbVar9 = (byte *)((iVar5 - 1U >> 3) + (int)param_2);
      local_8 = 7 - (iVar3 - 1U & 7);
      param_3 = 7 - (iVar5 - 1U & 7);
      if (iVar3 != 0) {
        do {
          bVar2 = *pbVar11;
          local_18[1] = local_18[3];
          if (0 < local_18[3]) {
            do {
              *pbVar9 = (byte)(0x7f7f >> (7 - (byte)param_3 & 0x1f)) & *pbVar9 |
                        (bVar2 >> ((byte)local_8 & 0x1f) & 1) << ((byte)param_3 & 0x1f);
              if (param_3 == 7) {
                param_3 = 0;
                pbVar9 = pbVar9 + -1;
              }
              else {
                param_3 = param_3 + 1;
              }
              local_18[1] = local_18[1] + -1;
            } while (local_18[1] != 0);
          }
          if (local_8 == 7) {
            local_8 = 0;
            pbVar11 = pbVar11 + -1;
          }
          else {
            local_8 = local_8 + 1;
          }
          local_18[2] = local_18[2] + 1;
        } while ((uint)local_18[2] < *(uint *)param_1);
      }
    }
    else if (bVar2 == 2) {
      local_18[2] = 0;
      pbVar11 = (byte *)((iVar3 - 1U >> 2) + (int)param_2);
      pbVar9 = (byte *)((iVar5 - 1U >> 2) + (int)param_2);
      local_8 = (3 - (iVar3 - 1U & 3)) * 2;
      param_3 = (3 - (iVar5 - 1U & 3)) * 2;
      if (iVar3 != 0) {
        do {
          bVar2 = *pbVar11;
          local_18[1] = local_18[3];
          if (0 < local_18[3]) {
            do {
              *pbVar9 = (byte)(0x3f3f >> (6 - (byte)param_3 & 0x1f)) & *pbVar9 |
                        (bVar2 >> ((byte)local_8 & 0x1f) & 3) << ((byte)param_3 & 0x1f);
              if (param_3 == 6) {
                param_3 = 0;
                pbVar9 = pbVar9 + -1;
              }
              else {
                param_3 = param_3 + 2;
              }
              local_18[1] = local_18[1] + -1;
            } while (local_18[1] != 0);
          }
          if (local_8 == 6) {
            local_8 = 0;
            pbVar11 = pbVar11 + -1;
          }
          else {
            local_8 = local_8 + 2;
          }
          local_18[2] = local_18[2] + 1;
        } while ((uint)local_18[2] < *(uint *)param_1);
      }
    }
    else if (bVar2 == 4) {
      local_18[2] = 0;
      pbVar11 = (byte *)((iVar3 - 1U >> 1) + (int)param_2);
      pbVar9 = (byte *)((iVar5 - 1U >> 1) + (int)param_2);
      local_8 = (iVar3 - 1U & 1) * -4 + 4;
      param_3 = (iVar5 - 1U & 1) * -4 + 4;
      if (iVar3 != 0) {
        do {
          bVar2 = *pbVar11;
          local_18[1] = local_18[3];
          if (0 < local_18[3]) {
            do {
              *pbVar9 = (byte)(0xf0f >> (4 - (byte)param_3 & 0x1f)) & *pbVar9 |
                        (bVar2 >> ((byte)local_8 & 0x1f) & 0xf) << ((byte)param_3 & 0x1f);
              if (param_3 == 4) {
                param_3 = 0;
                pbVar9 = pbVar9 + -1;
              }
              else {
                param_3 = param_3 + 4;
              }
              local_18[1] = local_18[1] + -1;
            } while (local_18[1] != 0);
          }
          if (local_8 == 4) {
            local_8 = 0;
            pbVar11 = pbVar11 + -1;
          }
          else {
            local_8 = local_8 + 4;
          }
          local_18[2] = local_18[2] + 1;
        } while ((uint)local_18[2] < *(uint *)param_1);
      }
    }
    else {
      local_8 = 0;
      uVar7 = (uint)(bVar2 >> 3);
      piVar6 = (int *)((iVar3 + -1) * uVar7 + (int)param_2);
      param_2 = (void *)((iVar5 + -1) * uVar7 + (int)param_2);
      if (iVar3 != 0) {
        do {
          piVar8 = piVar6;
          piVar10 = local_18;
          for (uVar4 = (uint)(bVar2 >> 5); iVar3 = local_18[3], uVar4 != 0; uVar4 = uVar4 - 1) {
            *piVar10 = *piVar8;
            piVar8 = piVar8 + 1;
            piVar10 = piVar10 + 1;
          }
          for (uVar4 = uVar7 & 3; uVar4 != 0; uVar4 = uVar4 - 1) {
            *(char *)piVar10 = (char)*piVar8;
            piVar8 = (int *)((int)piVar8 + 1);
            piVar10 = (int *)((int)piVar10 + 1);
          }
          if (0 < iVar3) {
            local_18[2] = iVar3;
            do {
              pvVar1 = (void *)((int)param_2 - uVar7);
              piVar8 = local_18;
              for (uVar4 = (uint)(bVar2 >> 5); uVar4 != 0; uVar4 = uVar4 - 1) {
                *(int *)param_2 = *piVar8;
                piVar8 = piVar8 + 1;
                param_2 = (int *)((int)param_2 + 4);
              }
              local_18[2] = local_18[2] + -1;
              for (uVar4 = uVar7 & 3; uVar4 != 0; uVar4 = uVar4 - 1) {
                *(char *)param_2 = (char)*piVar8;
                piVar8 = (int *)((int)piVar8 + 1);
                param_2 = (int *)((int)param_2 + 1);
              }
              param_2 = pvVar1;
            } while (local_18[2] != 0);
          }
          piVar6 = (int *)((int)piVar6 - uVar7);
          local_8 = local_8 + 1;
        } while (local_8 < *(uint *)param_1);
      }
    }
    *(int *)param_1 = iVar5;
    *(uint *)((int)param_1 + 4) = (uint)*(byte *)((int)param_1 + 0xb) * iVar5 + 7 >> 3;
  }
  return;
}
