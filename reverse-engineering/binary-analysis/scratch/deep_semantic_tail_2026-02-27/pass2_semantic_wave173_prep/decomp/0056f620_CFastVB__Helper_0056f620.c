/* address: 0x0056f620 */
/* name: CFastVB__Helper_0056f620 */
/* signature: void __thiscall CFastVB__Helper_0056f620(void * this, int param_1, uint param_2, int param_3, uint param_4) */


/* WARNING: Removing unreachable block (ram,0x0056fbac) */
/* WARNING: Removing unreachable block (ram,0x0056fbc1) */
/* WARNING: Removing unreachable block (ram,0x0056fbd0) */
/* WARNING: Removing unreachable block (ram,0x0056fbdd) */
/* WARNING: Removing unreachable block (ram,0x0056fbea) */
/* WARNING: Removing unreachable block (ram,0x0056fc84) */
/* WARNING: Removing unreachable block (ram,0x0056fc99) */
/* WARNING: Removing unreachable block (ram,0x0056fca8) */
/* WARNING: Removing unreachable block (ram,0x0056fcb1) */

void __thiscall
CFastVB__Helper_0056f620(void *this,int param_1,uint param_2,int param_3,uint param_4)

{
  int *piVar1;
  int iVar2;
  uint *ptr;
  bool bVar3;
  uint uVar4;
  void *extraout_EAX;
  uint uVar5;
  int iVar6;
  uint *extraout_EAX_00;
  undefined4 *extraout_EAX_01;
  undefined4 *extraout_EAX_02;
  undefined4 *extraout_EAX_03;
  undefined4 *puVar7;
  uint uVar8;
  void *extraout_EAX_04;
  void *extraout_EAX_05;
  void *extraout_EAX_06;
  void *extraout_EAX_07;
  int iVar9;
  void *unaff_EDI;
  int *piVar10;
  uint *local_1c;
  uint local_18;
  uint *local_14;
  undefined4 *local_10;
  void *local_c;
  uint local_8;
  int local_4;

  iVar2 = param_1;
  if (*(int *)((int)this + 4) == 0) {
    iVar9 = 0;
  }
  else {
    iVar9 = *(int *)((int)this + 8) - *(int *)((int)this + 4) >> 1;
  }
  uVar8 = iVar9 / 3;
  if (*(int *)(param_1 + 4) == 0) {
    uVar4 = 0;
  }
  else {
    uVar4 = *(int *)(param_1 + 0xc) - *(int *)(param_1 + 4) >> 2;
  }
  local_c = this;
  local_8 = uVar8;
  if (uVar4 < uVar8) {
    uVar4 = uVar8;
    if ((int)uVar8 < 0) {
      uVar4 = 0;
    }
    CFastVB__Helper_00426fd0(uVar4 * 4);
    CFastVB__Helper_00572f50(*(void **)(iVar2 + 4),*(void **)(iVar2 + 8),extraout_EAX);
    VFuncSlot_12_00405db0();
    OID__FreeObject_Callback(*(void **)(iVar2 + 4));
    *(void **)(iVar2 + 0xc) = (void *)((int)extraout_EAX + uVar8 * 4);
    iVar9 = CFastVB__CountDwordsFromPointerSpan(iVar2);
    *(void **)(iVar2 + 4) = extraout_EAX;
    *(void **)(iVar2 + 8) = (void *)((int)extraout_EAX + iVar9 * 4);
  }
  uVar4 = param_2;
  uVar5 = 0;
  param_1 = 0;
  uVar8 = (param_3 & 0xffffU) + 1;
  if (*(int *)(param_2 + 4) != 0) {
    uVar5 = *(int *)(param_2 + 8) - *(int *)(param_2 + 4) >> 2;
  }
  if (uVar5 < uVar8) {
    param_3 = *(int *)(param_2 + 8);
    piVar10 = &param_1;
    iVar9 = CFastVB__CountDwordsFromPointerSpan(param_2);
    CFastVB__Helper_005736d0((void *)uVar4,param_3,(void *)(uVar8 - iVar9),(uint)piVar10,unaff_EDI);
  }
  else {
    uVar5 = CFastVB__CountDwordsFromPointerSpan(param_2);
    if (uVar8 < uVar5) {
      CTexture__Helper_00572f20
                ((void *)uVar4,*(int *)(uVar4 + 4) + uVar8 * 4,*(void **)(uVar4 + 8),unaff_EDI);
    }
  }
  iVar9 = 0;
  if (uVar8 != 0) {
    do {
      iVar9 = iVar9 + 1;
      *(undefined4 *)(*(int *)(uVar4 + 4) + -4 + iVar9 * 4) = 0;
    } while (iVar9 < (int)uVar8);
  }
  if (0 < (int)local_8) {
    local_4 = 0;
    do {
      iVar9 = *(int *)((int)this + 4);
      uVar8 = (uint)*(ushort *)(iVar9 + local_4);
      iVar6 = local_4 + 4;
      uVar4 = (uint)*(ushort *)(iVar9 + local_4 + 2);
      local_4 = local_4 + 6;
      param_1 = CONCAT31(param_1._1_3_,1);
      local_18 = (uint)*(ushort *)(iVar9 + iVar6);
      param_3 = param_3 & 0xff000000;
      bVar3 = CFastVB__Helper_00571890(uVar8,uVar4,local_18);
      if (bVar3) goto LAB_0056fcc7;
      CFastVB__Helper_00426fd0(0x18);
      uVar5 = param_2;
      if (extraout_EAX_00 == (uint *)0x0) {
        local_14 = (uint *)0x0;
      }
      else {
        *extraout_EAX_00 = uVar8;
        extraout_EAX_00[1] = uVar4;
        extraout_EAX_00[2] = local_18;
        extraout_EAX_00[3] = 0xffffffff;
        extraout_EAX_00[4] = 0xffffffff;
        extraout_EAX_00[5] = 0xffffffff;
        local_14 = extraout_EAX_00;
      }
      local_1c = local_14;
      local_10 = (undefined4 *)CFastVB__Helper_0056f540(param_2,uVar8,uVar4);
      if (local_10 == (undefined4 *)0x0) {
        param_1 = param_1 & 0xffffff00;
        CFastVB__Helper_00426fd0(0x1c);
        if (extraout_EAX_01 == (undefined4 *)0x0) {
          local_10 = (undefined4 *)0x0;
        }
        else {
          extraout_EAX_01[3] = uVar8;
          extraout_EAX_01[4] = uVar4;
          extraout_EAX_01[1] = 0;
          extraout_EAX_01[2] = 0;
          extraout_EAX_01[5] = 0;
          extraout_EAX_01[6] = 0;
          *extraout_EAX_01 = 2;
          local_10 = extraout_EAX_01;
        }
        local_10[5] = *(undefined4 *)(*(int *)(uVar5 + 4) + uVar8 * 4);
        local_10[6] = *(undefined4 *)(*(int *)(uVar5 + 4) + uVar4 * 4);
        *(undefined4 **)(*(int *)(uVar5 + 4) + uVar8 * 4) = local_10;
        *(undefined4 **)(*(int *)(uVar5 + 4) + uVar4 * 4) = local_10;
        local_10[1] = local_1c;
      }
      else if (local_10[2] == 0) {
        param_3 = CONCAT31(param_3._1_3_,1);
        local_10[2] = local_14;
      }
      else {
        CFastVB__DispatchLockedRoute_6533e0(0x656e68);
      }
      local_14 = (uint *)CFastVB__Helper_0056f540(uVar5,uVar4,local_18);
      if (local_14 == (undefined4 *)0x0) {
        param_1 = param_1 & 0xffffff00;
        CFastVB__Helper_00426fd0(0x1c);
        if (extraout_EAX_02 == (undefined4 *)0x0) {
          local_14 = (undefined4 *)0x0;
        }
        else {
          extraout_EAX_02[3] = uVar4;
          extraout_EAX_02[4] = local_18;
          extraout_EAX_02[1] = 0;
          extraout_EAX_02[2] = 0;
          extraout_EAX_02[5] = 0;
          extraout_EAX_02[6] = 0;
          *extraout_EAX_02 = 2;
          local_14 = extraout_EAX_02;
        }
        local_14[5] = *(undefined4 *)(*(int *)(uVar5 + 4) + uVar4 * 4);
        local_14[6] = *(undefined4 *)(*(int *)(uVar5 + 4) + local_18 * 4);
        *(uint **)(*(int *)(uVar5 + 4) + uVar4 * 4) = local_14;
        *(uint **)(*(int *)(uVar5 + 4) + local_18 * 4) = local_14;
        local_14[1] = (uint)local_1c;
      }
      else if (local_14[2] == 0) {
        param_3._0_2_ = CONCAT11(1,(char)param_3);
        local_14[2] = (uint)local_1c;
      }
      else {
        CFastVB__DispatchLockedRoute_6533e0(0x656e68);
      }
      uVar4 = local_18;
      iVar9 = CFastVB__Helper_0056f540(uVar5,local_18,uVar8);
      local_18 = iVar9;
      if (iVar9 == 0) {
        CFastVB__Helper_00426fd0(0x1c);
        if (extraout_EAX_03 == (undefined4 *)0x0) {
          puVar7 = (undefined4 *)0x0;
        }
        else {
          extraout_EAX_03[3] = uVar4;
          extraout_EAX_03[4] = uVar8;
          extraout_EAX_03[1] = 0;
          extraout_EAX_03[2] = 0;
          extraout_EAX_03[5] = 0;
          extraout_EAX_03[6] = 0;
          *extraout_EAX_03 = 2;
          puVar7 = extraout_EAX_03;
        }
        puVar7[5] = *(undefined4 *)(*(int *)(uVar5 + 4) + uVar4 * 4);
        puVar7[6] = *(undefined4 *)(*(int *)(uVar5 + 4) + uVar8 * 4);
        *(undefined4 **)(*(int *)(uVar5 + 4) + uVar4 * 4) = puVar7;
        *(undefined4 **)(*(int *)(uVar5 + 4) + uVar8 * 4) = puVar7;
        puVar7[1] = local_1c;
LAB_0056f994:
        piVar10 = *(int **)(iVar2 + 8);
        if (*(int *)(iVar2 + 0xc) - (int)piVar10 >> 2 == 0) {
          if ((*(int *)(iVar2 + 4) == 0) ||
             (uVar8 = (int)piVar10 - *(int *)(iVar2 + 4) >> 2, uVar8 < 2)) {
            uVar8 = 1;
          }
          iVar6 = CFastVB__CountDwordsFromPointerSpan(iVar2);
          iVar6 = iVar6 + uVar8;
          iVar9 = iVar6;
          if (iVar6 < 0) {
            iVar9 = 0;
          }
          CFastVB__Helper_00426fd0(iVar9 << 2);
          CFastVB__Helper_00572f50(*(void **)(iVar2 + 4),piVar10,extraout_EAX_04);
          param_1 = (int)extraout_EAX_05;
          CTexture__Helper_00573ff0(extraout_EAX_05,1,&local_1c);
          CFastVB__Helper_00572f50(piVar10,*(void **)(iVar2 + 8),(void *)(param_1 + 4));
          VFuncSlot_12_00405db0();
          OID__FreeObject_Callback(*(void **)(iVar2 + 4));
          *(void **)(iVar2 + 0xc) = (void *)((int)extraout_EAX_04 + iVar6 * 4);
          iVar9 = CFastVB__CountDwordsFromPointerSpan(iVar2);
          iVar9 = (int)extraout_EAX_04 + iVar9 * 4 + 4;
          *(void **)(iVar2 + 4) = extraout_EAX_04;
        }
        else {
          CFastVB__Helper_00572f50(piVar10,piVar10,piVar10 + 1);
          CTexture__Helper_00573ff0
                    (*(void **)(iVar2 + 8),1 - ((int)*(void **)(iVar2 + 8) - (int)piVar10 >> 2),
                     &local_1c);
          piVar1 = *(int **)(iVar2 + 8);
          for (; piVar10 != piVar1; piVar10 = piVar10 + 1) {
            *piVar10 = (int)local_1c;
          }
LAB_0056fcbe:
          iVar9 = *(int *)(iVar2 + 8) + 4;
        }
        *(int *)(iVar2 + 8) = iVar9;
      }
      else {
        if (*(int *)(iVar9 + 8) == 0) {
          param_3._0_3_ = CONCAT12(1,(undefined2)param_3);
          *(uint **)(iVar9 + 8) = local_1c;
        }
        else {
          CFastVB__DispatchLockedRoute_6533e0(0x656e68);
        }
        ptr = local_1c;
        if ((char)param_1 == '\0') goto LAB_0056f994;
        uVar8 = CFastVB__Helper_0056f5c0(local_1c,iVar2);
        if ((char)uVar8 == '\0') {
          piVar10 = *(int **)(iVar2 + 8);
          if (*(int *)(iVar2 + 0xc) - (int)piVar10 >> 2 == 0) {
            if ((*(int *)(iVar2 + 4) == 0) || ((uint)((int)piVar10 - *(int *)(iVar2 + 4) >> 2) < 2))
            {
              iVar9 = 1;
            }
            else {
              iVar9 = CFastVB__CountDwordsFromPointerSpan(iVar2);
            }
            iVar6 = CFastVB__CountDwordsFromPointerSpan(iVar2);
            iVar6 = iVar6 + iVar9;
            iVar9 = iVar6;
            if (iVar6 < 0) {
              iVar9 = 0;
            }
            CFastVB__Helper_00426fd0(iVar9 * 4);
            CFastVB__Helper_00572f50(*(void **)(iVar2 + 4),piVar10,extraout_EAX_06);
            param_1 = (int)extraout_EAX_07;
            CTexture__Helper_00573ff0(extraout_EAX_07,1,&local_1c);
            CFastVB__Helper_00572f50(piVar10,*(void **)(iVar2 + 8),(void *)(param_1 + 4));
            VFuncSlot_12_00405db0();
            OID__FreeObject_Callback(*(void **)(iVar2 + 4));
            *(void **)(iVar2 + 0xc) = (void *)((int)extraout_EAX_06 + iVar6 * 4);
            iVar9 = CFastVB__CountDwordsFromPointerSpan(iVar2);
            *(void **)(iVar2 + 4) = extraout_EAX_06;
            *(int *)(iVar2 + 8) = (int)extraout_EAX_06 + iVar9 * 4 + 4;
            goto LAB_0056fcc7;
          }
          CFastVB__Helper_00572f50(piVar10,piVar10,piVar10 + 1);
          CTexture__Helper_00573ff0
                    (*(void **)(iVar2 + 8),1 - ((int)*(void **)(iVar2 + 8) - (int)piVar10 >> 2),
                     &local_1c);
          piVar1 = *(int **)(iVar2 + 8);
          for (; piVar10 != piVar1; piVar10 = piVar10 + 1) {
            *piVar10 = (int)local_1c;
          }
          goto LAB_0056fcbe;
        }
        OID__FreeObject_Callback(ptr);
        if ((char)param_3 != '\0') {
          local_10[2] = 0;
        }
        if (param_3._1_1_ != '\0') {
          local_14[2] = 0;
        }
        if (param_3._2_1_ != '\0') {
          *(undefined4 *)(iVar9 + 8) = 0;
        }
      }
LAB_0056fcc7:
      local_8 = local_8 - 1;
      this = local_c;
    } while (local_8 != 0);
  }
  return;
}
