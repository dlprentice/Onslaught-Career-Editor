/* address: 0x005b1e94 */
/* name: CTexture__Helper_005b1e94 */
/* signature: void __stdcall CTexture__Helper_005b1e94(void * param_1, void * param_2, void * param_3) */


void CTexture__Helper_005b1e94(void *param_1,void *param_2,void *param_3)

{
  int *piVar1;
  byte bVar2;
  byte *pbVar3;
  byte *pbVar4;
  void *pvVar5;
  uint uVar6;
  undefined4 uVar7;
  int iVar8;
  byte *extraout_EAX;
  byte *pbVar9;
  byte *local_1c;
  byte *local_18;
  byte *local_14;
  byte *local_10;
  byte *local_c;
  uint local_8;

  pvVar5 = param_1;
  local_c = *(byte **)((int)param_2 + 4);
  local_8 = *(uint *)((int)param_1 + 0x20);
  local_10 = *(byte **)((int)param_1 + 0x34);
  if (local_10 < *(byte **)((int)param_1 + 0x30)) {
    local_14 = *(byte **)((int)param_1 + 0x30) + (-1 - (int)local_10);
  }
  else {
    local_14 = (byte *)(*(int *)((int)param_1 + 0x2c) - (int)local_10);
  }
  uVar6 = *(uint *)param_1;
  param_1 = *(void **)((int)param_1 + 0x1c);
  pbVar9 = *(byte **)param_2;
  while (local_18 = pbVar9, uVar6 < 10) {
    switch((&switchD_005b1f0f::switchdataD_005b25b8)[uVar6]) {
    case (undefined *)0x5b1f3a:
      for (; pbVar9 = local_18, param_1 < (void *)0x3; param_1 = (void *)((int)param_1 + 8)) {
        if (local_c == (byte *)0x0) goto LAB_005b250f;
        param_3 = (void *)0x0;
        local_c = local_c + -1;
        local_8 = local_8 | (uint)*local_18 << ((byte)param_1 & 0x1f);
        local_18 = local_18 + 1;
      }
      uVar6 = (local_8 & 7) >> 1;
      *(uint *)((int)pvVar5 + 0x18) = local_8 & 1;
      if (uVar6 == 0) {
        uVar6 = (int)param_1 - 3U & 7;
        local_8 = (local_8 >> 3) >> (sbyte)uVar6;
        param_1 = (void *)(((int)param_1 - 3U) - uVar6);
        *(undefined4 *)pvVar5 = 1;
      }
      else if (uVar6 == 1) {
        CDXTexture__InflateFixedTrees_InitDescriptors();
        iVar8 = CDXTexture__InflateCodesState_Create();
        *(int *)((int)pvVar5 + 4) = iVar8;
        if (iVar8 == 0) goto LAB_005b255c;
        local_8 = local_8 >> 3;
        param_1 = (void *)((int)param_1 + -3);
        *(undefined4 *)pvVar5 = 6;
      }
      else {
        if (uVar6 == 2) {
          local_8 = local_8 >> 3;
          uVar6 = 3;
          param_1 = (void *)((int)param_1 + -3);
          goto LAB_005b1f95;
        }
        if (uVar6 == 3) {
          *(undefined4 *)pvVar5 = 9;
          *(char **)((int)param_2 + 0x18) = "invalid block type";
          *(uint *)((int)pvVar5 + 0x20) = local_8 >> 3;
          param_1 = (void *)((int)param_1 + -3);
          param_3 = (byte *)0xfffffffd;
          goto LAB_005b1ee6;
        }
      }
      break;
    case (undefined *)0x5b2001:
      for (; pbVar9 = local_18, param_1 < (void *)0x20; param_1 = (void *)((int)param_1 + 8)) {
        if (local_c == (byte *)0x0) goto LAB_005b250f;
        param_3 = (void *)0x0;
        local_c = local_c + -1;
        local_8 = local_8 | (uint)*local_18 << ((byte)param_1 & 0x1f);
        local_18 = local_18 + 1;
      }
      if (~local_8 >> 0x10 != (local_8 & 0xffff)) {
        *(undefined4 *)pvVar5 = 9;
        *(char **)((int)param_2 + 0x18) = "invalid stored block lengths";
        goto switchD_005b1f0f_caseD_5b24d2;
      }
      *(uint *)((int)pvVar5 + 4) = local_8 & 0xffff;
      param_1 = (void *)0x0;
      local_8 = 0;
      if (*(int *)((int)pvVar5 + 4) == 0) goto LAB_005b2140;
      uVar6 = 2;
LAB_005b1f95:
      *(uint *)pvVar5 = uVar6;
      break;
    case (undefined *)0x5b2062:
      if (local_c == (byte *)0x0) {
LAB_005b250f:
        *(uint *)((int)pvVar5 + 0x20) = local_8;
        *(void **)((int)pvVar5 + 0x1c) = param_1;
        *(undefined4 *)((int)param_2 + 4) = 0;
        goto LAB_005b1eef;
      }
      if (local_14 == (byte *)0x0) {
        local_14 = (byte *)0x0;
        if (local_10 == *(byte **)((int)pvVar5 + 0x2c)) {
          pbVar3 = *(byte **)((int)pvVar5 + 0x30);
          pbVar4 = *(byte **)((int)pvVar5 + 0x28);
          if (pbVar4 != pbVar3) {
            if (pbVar4 < pbVar3) {
              local_14 = pbVar3 + (-1 - (int)pbVar4);
            }
            else {
              local_14 = *(byte **)((int)pvVar5 + 0x2c) + -(int)pbVar4;
            }
            local_10 = pbVar4;
            if (local_14 != (byte *)0x0) goto LAB_005b2100;
          }
        }
        *(byte **)((int)pvVar5 + 0x34) = local_10;
        param_3 = (void *)CDXTexture__InflateOutputWindowFlush(pvVar5,(int)param_2,(int)param_3);
        local_1c = *(byte **)((int)pvVar5 + 0x30);
        local_10 = *(byte **)((int)pvVar5 + 0x34);
        if (local_10 < local_1c) {
          local_14 = local_1c + (-1 - (int)local_10);
        }
        else {
          local_14 = (byte *)(*(int *)((int)pvVar5 + 0x2c) - (int)local_10);
        }
        if (local_10 == *(byte **)((int)pvVar5 + 0x2c)) {
          pbVar3 = *(byte **)((int)pvVar5 + 0x28);
          if (pbVar3 != local_1c) {
            local_10 = pbVar3;
            if (pbVar3 < local_1c) {
              local_14 = local_1c + (-1 - (int)pbVar3);
            }
            else {
              local_14 = *(byte **)((int)pvVar5 + 0x2c) + -(int)pbVar3;
            }
          }
        }
        if (local_14 == (byte *)0x0) {
          *(uint *)((int)pvVar5 + 0x20) = local_8;
          *(void **)((int)pvVar5 + 0x1c) = param_1;
          *(byte **)((int)param_2 + 4) = local_c;
          *(int *)((int)param_2 + 8) =
               (int)(pbVar9 + (*(int *)((int)param_2 + 8) - *(int *)param_2));
          goto LAB_005b1ef9;
        }
      }
LAB_005b2100:
      param_3 = (void *)0x0;
      pbVar9 = *(byte **)((int)pvVar5 + 4);
      if (local_c < *(byte **)((int)pvVar5 + 4)) {
        pbVar9 = local_c;
      }
      if (local_14 < pbVar9) {
        pbVar9 = local_14;
      }
      pbVar3 = local_18 + (int)pbVar9;
      local_c = local_c + -(int)pbVar9;
      pbVar4 = local_10 + (int)pbVar9;
      local_14 = local_14 + -(int)pbVar9;
      for (uVar6 = (uint)pbVar9 >> 2; uVar6 != 0; uVar6 = uVar6 - 1) {
        *(undefined4 *)local_10 = *(undefined4 *)local_18;
        local_18 = local_18 + 4;
        local_10 = local_10 + 4;
      }
      for (uVar6 = (uint)pbVar9 & 3; uVar6 != 0; uVar6 = uVar6 - 1) {
        *local_10 = *local_18;
        local_18 = local_18 + 1;
        local_10 = local_10 + 1;
      }
      piVar1 = (int *)((int)pvVar5 + 4);
      *piVar1 = *piVar1 - (int)pbVar9;
      local_18 = pbVar3;
      local_10 = pbVar4;
      if (*piVar1 == 0) {
LAB_005b2140:
        uVar6 = -(uint)(*(int *)((int)pvVar5 + 0x18) != 0) & 7;
        goto LAB_005b1f95;
      }
      break;
    case (undefined *)0x5b214f:
      for (; param_1 < (void *)0xe; param_1 = (void *)((int)param_1 + 8)) {
        if (local_c == (byte *)0x0) goto LAB_005b250f;
        param_3 = (void *)0x0;
        local_c = local_c + -1;
        local_8 = local_8 | (uint)*pbVar9 << ((byte)param_1 & 0x1f);
        pbVar9 = pbVar9 + 1;
      }
      *(uint *)((int)pvVar5 + 4) = local_8 & 0x3fff;
      if ((0x1d < (local_8 & 0x1f)) || (uVar6 = (local_8 & 0x3fff) >> 5 & 0x1f, 0x1d < uVar6)) {
        *(undefined4 *)pvVar5 = 9;
        *(char **)((int)param_2 + 0x18) = "too many length or distance symbols";
        goto switchD_005b1f0f_caseD_5b24d2;
      }
      iVar8 = (**(code **)((int)param_2 + 0x20))
                        (*(undefined4 *)((int)param_2 + 0x28),uVar6 + 0x102 + (local_8 & 0x1f),4);
      *(int *)((int)pvVar5 + 0xc) = iVar8;
      if (iVar8 != 0) {
        local_8 = local_8 >> 0xe;
        param_1 = (void *)((int)param_1 + -0xe);
        *(undefined4 *)((int)pvVar5 + 8) = 0;
        *(undefined4 *)pvVar5 = 4;
        goto switchD_005b1f0f_caseD_5b221b;
      }
LAB_005b255c:
      param_3 = (byte *)0xfffffffc;
      goto LAB_005b1edd;
    case (undefined *)0x5b221b:
switchD_005b1f0f_caseD_5b221b:
      while (*(uint *)((int)pvVar5 + 8) < (*(uint *)((int)pvVar5 + 4) >> 10) + 4) {
        for (; param_1 < (void *)0x3; param_1 = (void *)((int)param_1 + 8)) {
          if (local_c == (byte *)0x0) goto LAB_005b250f;
          param_3 = (void *)0x0;
          local_c = local_c + -1;
          local_8 = local_8 | (uint)*pbVar9 << ((byte)param_1 & 0x1f);
          pbVar9 = pbVar9 + 1;
        }
        *(uint *)(*(int *)((int)pvVar5 + 0xc) +
                 *(int *)(&DAT_005f4a68 + *(int *)((int)pvVar5 + 8) * 4) * 4) = local_8 & 7;
        *(int *)((int)pvVar5 + 8) = *(int *)((int)pvVar5 + 8) + 1;
        param_1 = (void *)((int)param_1 + -3);
        local_8 = local_8 >> 3;
      }
      while (*(uint *)((int)pvVar5 + 8) < 0x13) {
        *(undefined4 *)
         (*(int *)((int)pvVar5 + 0xc) + *(int *)(&DAT_005f4a68 + *(int *)((int)pvVar5 + 8) * 4) * 4)
             = 0;
        *(int *)((int)pvVar5 + 8) = *(int *)((int)pvVar5 + 8) + 1;
      }
      *(undefined4 *)((int)pvVar5 + 0x10) = 7;
      local_14 = (byte *)CDXTexture__InflateDynamicTree_BuildBitLengthTree
                                   (*(int *)((int)pvVar5 + 0xc),(undefined4 *)((int)pvVar5 + 0x10),
                                    (int)pvVar5 + 0x14,*(int *)((int)pvVar5 + 0x24),(int)param_2);
      if (local_14 == (byte *)0x0) {
        *(undefined4 *)((int)pvVar5 + 8) = 0;
        *(undefined4 *)pvVar5 = 5;
        goto switchD_005b1f0f_caseD_5b2396;
      }
      goto LAB_005b2543;
    case (undefined *)0x5b2396:
switchD_005b1f0f_caseD_5b2396:
      while (*(uint *)((int)pvVar5 + 8) <
             (*(uint *)((int)pvVar5 + 4) >> 5 & 0x1f) + 0x102 + (*(uint *)((int)pvVar5 + 4) & 0x1f))
      {
        for (; param_1 < *(void **)((int)pvVar5 + 0x10); param_1 = (void *)((int)param_1 + 8)) {
          if (local_c == (byte *)0x0) goto LAB_005b250f;
          param_3 = (void *)0x0;
          local_c = local_c + -1;
          local_8 = local_8 | (uint)*pbVar9 << ((byte)param_1 & 0x1f);
          pbVar9 = pbVar9 + 1;
        }
        iVar8 = *(int *)((int)pvVar5 + 0x14) +
                (*(uint *)(&DAT_0065ff60 + (int)*(void **)((int)pvVar5 + 0x10) * 4) & local_8) * 8;
        bVar2 = *(byte *)(iVar8 + 1);
        local_14 = (byte *)(uint)bVar2;
        uVar6 = *(uint *)(iVar8 + 4);
        if (uVar6 < 0x10) {
          local_8 = local_8 >> (bVar2 & 0x1f);
          param_1 = (void *)((int)param_1 - (int)local_14);
          *(uint *)(*(int *)((int)pvVar5 + 0xc) + *(int *)((int)pvVar5 + 8) * 4) = uVar6;
          *(int *)((int)pvVar5 + 8) = *(int *)((int)pvVar5 + 8) + 1;
        }
        else {
          if (uVar6 == 0x12) {
            iVar8 = 7;
          }
          else {
            iVar8 = uVar6 - 0xe;
          }
          local_18 = (byte *)((uint)(uVar6 == 0x12) * 8 + 3);
          for (; param_1 < local_14 + iVar8; param_1 = (void *)((int)param_1 + 8)) {
            if (local_c == (byte *)0x0) goto LAB_005b250f;
            param_3 = (void *)0x0;
            local_c = local_c + -1;
            local_8 = local_8 | (uint)*pbVar9 << ((byte)param_1 & 0x1f);
            pbVar9 = pbVar9 + 1;
          }
          local_8 = local_8 >> (bVar2 & 0x1f);
          local_18 = local_18 + (*(uint *)(&DAT_0065ff60 + iVar8 * 4) & local_8);
          local_8 = local_8 >> ((byte)iVar8 & 0x1f);
          param_1 = (void *)((int)param_1 - (int)(local_14 + iVar8));
          iVar8 = *(int *)((int)pvVar5 + 8);
          if ((byte *)((*(uint *)((int)pvVar5 + 4) >> 5 & 0x1f) + 0x102 +
                      (*(uint *)((int)pvVar5 + 4) & 0x1f)) < local_18 + iVar8) {
LAB_005b2527:
            (**(code **)((int)param_2 + 0x24))
                      (*(undefined4 *)((int)param_2 + 0x28),*(undefined4 *)((int)pvVar5 + 0xc));
            *(undefined4 *)pvVar5 = 9;
            *(char **)((int)param_2 + 0x18) = "invalid bit length repeat";
            goto switchD_005b1f0f_caseD_5b24d2;
          }
          if (uVar6 == 0x10) {
            if (iVar8 == 0) goto LAB_005b2527;
            uVar7 = *(undefined4 *)(*(int *)((int)pvVar5 + 0xc) + -4 + iVar8 * 4);
          }
          else {
            uVar7 = 0;
          }
          do {
            *(undefined4 *)(*(int *)((int)pvVar5 + 0xc) + iVar8 * 4) = uVar7;
            iVar8 = iVar8 + 1;
            local_18 = local_18 + -1;
          } while (local_18 != (byte *)0x0);
          *(int *)((int)pvVar5 + 8) = iVar8;
          local_18 = (byte *)0x0;
        }
      }
      *(undefined4 *)((int)pvVar5 + 0x14) = 0;
      local_1c = (byte *)0x9;
      local_18 = (byte *)0x6;
      local_14 = (byte *)CDXTexture__InflateDynamicTree_BuildLitDistTrees
                                   ((void *)((*(uint *)((int)pvVar5 + 4) & 0x1f) + 0x101),
                                    (void *)((*(uint *)((int)pvVar5 + 4) >> 5 & 0x1f) + 1),
                                    *(void **)((int)pvVar5 + 0xc),&local_1c,&local_18);
      if (local_14 == (byte *)0x0) {
        iVar8 = CDXTexture__InflateCodesState_Create();
        if (iVar8 == 0) goto LAB_005b255c;
        *(int *)((int)pvVar5 + 4) = iVar8;
        (**(code **)((int)param_2 + 0x24))
                  (*(undefined4 *)((int)param_2 + 0x28),*(undefined4 *)((int)pvVar5 + 0xc));
        *(undefined4 *)pvVar5 = 6;
        goto switchD_005b1f0f_caseD_5b242f;
      }
LAB_005b2543:
      param_3 = local_14;
      if (local_14 == (byte *)0xfffffffd) {
        (**(code **)((int)param_2 + 0x24))
                  (*(undefined4 *)((int)param_2 + 0x28),*(undefined4 *)((int)pvVar5 + 0xc));
        *(undefined4 *)pvVar5 = 9;
        param_3 = local_14;
      }
      goto LAB_005b1edd;
    case (undefined *)0x5b242f:
switchD_005b1f0f_caseD_5b242f:
      *(uint *)((int)pvVar5 + 0x20) = local_8;
      *(void **)((int)pvVar5 + 0x1c) = param_1;
      *(byte **)((int)param_2 + 4) = local_c;
      *(int *)((int)param_2 + 8) = (int)(pbVar9 + (*(int *)((int)param_2 + 8) - *(int *)param_2));
      *(byte **)param_2 = pbVar9;
      *(byte **)((int)pvVar5 + 0x34) = local_10;
      CDXTexture__InflateCodesState_Process((uint)pvVar5,param_2,(int)param_3);
      param_3 = extraout_EAX;
      if (extraout_EAX != (byte *)0x1) goto LAB_005b1efe;
      param_3 = (void *)0x0;
      CDXTexture__InvokeReleaseCallback(*(int *)((int)pvVar5 + 4),(int)param_2);
      local_c = *(byte **)((int)param_2 + 4);
      local_10 = *(byte **)((int)pvVar5 + 0x34);
      local_18 = *(byte **)param_2;
      local_8 = *(uint *)((int)pvVar5 + 0x20);
      param_1 = *(void **)((int)pvVar5 + 0x1c);
      if (local_10 < *(byte **)((int)pvVar5 + 0x30)) {
        local_14 = *(byte **)((int)pvVar5 + 0x30) + (-1 - (int)local_10);
      }
      else {
        local_14 = (byte *)(*(int *)((int)pvVar5 + 0x2c) - (int)local_10);
      }
      if (*(int *)((int)pvVar5 + 0x18) != 0) {
        *(undefined4 *)pvVar5 = 7;
        goto switchD_005b1f0f_caseD_5b2569;
      }
      *(undefined4 *)pvVar5 = 0;
      break;
    case (undefined *)0x5b24d2:
switchD_005b1f0f_caseD_5b24d2:
      param_3 = (byte *)0xfffffffd;
      goto LAB_005b1edd;
    case (undefined *)0x5b2569:
switchD_005b1f0f_caseD_5b2569:
      pbVar9 = local_18;
      *(byte **)((int)pvVar5 + 0x34) = local_10;
      param_3 = (void *)CDXTexture__InflateOutputWindowFlush(pvVar5,(int)param_2,(int)param_3);
      local_10 = *(byte **)((int)pvVar5 + 0x34);
      if (*(byte **)((int)pvVar5 + 0x30) == local_10) {
        *(undefined4 *)pvVar5 = 8;
        goto switchD_005b1f0f_caseD_5b25b1;
      }
      *(uint *)((int)pvVar5 + 0x20) = local_8;
      *(void **)((int)pvVar5 + 0x1c) = param_1;
      *(byte **)((int)param_2 + 4) = local_c;
      iVar8 = *(int *)param_2;
      *(byte **)param_2 = pbVar9;
      *(int *)((int)param_2 + 8) = (int)(pbVar9 + (*(int *)((int)param_2 + 8) - iVar8));
      *(byte **)((int)pvVar5 + 0x34) = local_10;
      goto LAB_005b1efe;
    case (undefined *)0x5b25b1:
switchD_005b1f0f_caseD_5b25b1:
      param_3 = (byte *)0x1;
      goto LAB_005b1edd;
    }
    pbVar9 = local_18;
    uVar6 = *(uint *)pvVar5;
  }
  param_3 = (byte *)0xfffffffe;
LAB_005b1edd:
  *(uint *)((int)pvVar5 + 0x20) = local_8;
LAB_005b1ee6:
  *(void **)((int)pvVar5 + 0x1c) = param_1;
  *(byte **)((int)param_2 + 4) = local_c;
LAB_005b1eef:
  *(int *)((int)param_2 + 8) = (int)(pbVar9 + (*(int *)((int)param_2 + 8) - *(int *)param_2));
LAB_005b1ef9:
  *(byte **)param_2 = pbVar9;
  *(byte **)((int)pvVar5 + 0x34) = local_10;
LAB_005b1efe:
  CDXTexture__InflateOutputWindowFlush(pvVar5,(int)param_2,(int)param_3);
  return;
}
