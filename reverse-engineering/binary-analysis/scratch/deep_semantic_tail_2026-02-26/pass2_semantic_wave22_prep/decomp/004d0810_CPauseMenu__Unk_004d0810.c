/* address: 0x004d0810 */
/* name: CPauseMenu__Unk_004d0810 */
/* signature: void __thiscall CPauseMenu__Unk_004d0810(void * this, void * param_1, int param_2) */


void __thiscall CPauseMenu__Unk_004d0810(void *this,void *param_1,int param_2)

{
  undefined1 *puVar1;
  undefined4 *puVar2;
  short *psVar3;
  void *pvVar4;
  void *pvVar5;
  void *pvVar6;
  void *unaff_EDI;
  float fVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  int iVar11;
  undefined4 uVar12;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  pvVar4 = ExceptionList;
  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d4632;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  *(undefined4 *)((int)this + 0x38) = *(undefined4 *)((int)param_1 + 8);
  puVar1 = *(undefined1 **)((int)param_1 + 8);
  if ((int)puVar1 < 0x3fc4fa) {
    if (puVar1 == (undefined1 *)0x3fc4f9) {
      *(undefined4 *)((int)this + 0x10) = 0;
      fVar7 = PLATFORM__GetSysTimeFloat();
      *(float *)((int)this + 0x30) = fVar7;
      if (*(int **)((int)this + 8) != (int *)0x0) {
        (**(code **)(**(int **)((int)this + 8) + 4))(1);
        *(undefined4 *)((int)this + 8) = 0;
      }
      if (*(int **)((int)this + 0x3c) != (int *)0x0) {
        (**(code **)(**(int **)((int)this + 0x3c) + 4))(1);
        *(undefined4 *)((int)this + 0x3c) = 0;
      }
      *(undefined4 *)((int)this + 0x48) = 1;
      pvVar4 = DAT_008a9d94;
      iVar11 = 0;
      do {
        pvVar5 = CGame__GetController(&DAT_008a9a98,iVar11);
        if (pvVar5 != (void *)0x0) {
          pvVar5 = CGame__GetController(&DAT_008a9a98,iVar11);
          pvVar5 = CController__GetToControl(pvVar5);
          if (pvVar5 == this) {
            pvVar5 = pvVar4;
            pvVar6 = CGame__GetController(&DAT_008a9a98,iVar11);
            CController__SetToControl(pvVar6,pvVar5);
          }
        }
        iVar11 = iVar11 + 1;
      } while (iVar11 < 2);
      CExplosionInitThing__Unk_0048ff90((int)DAT_008a9d94);
      iVar11 = 1;
    }
    else if ((int)puVar1 < 0xcadaa) {
      if (puVar1 != (undefined1 *)0xcada9) {
        if (puVar1 == (undefined1 *)0x0) {
          switch(*(undefined4 *)((int)param_1 + 0x18)) {
          case 1:
            pvVar4 = (void *)(*(int *)((int)this + 0x24) + 3);
            break;
          case 2:
            pvVar4 = (void *)(*(int *)((int)this + 0x24) + 2);
            break;
          case 3:
            goto switchD_004d08cf_caseD_3;
          default:
            goto switchD_004d08cf_caseD_4;
          case 0x4e:
          case 0x4f:
            goto switchD_004d08cf_caseD_4e;
          }
LAB_004d0c22:
          *(void **)((int)this + 0x24) = pvVar4;
          CUnit__Unk_004e5c90((void *)((int)this + 0x14),pvVar4,(int)unaff_EDI);
          CMenuItemRange__ResetIterator();
          iVar11 = 1;
          goto LAB_004d089b;
        }
        if (puVar1 == (undefined1 *)0x6f9da) {
          if ((*(int *)((int)this + 0x24) == 1) &&
             (iVar11 = CPauseMenu__Unk_004d0de0(), iVar11 != 0)) {
            ExceptionList = local_c;
            return;
          }
          *(undefined4 *)((int)this + 0x24) = 0;
          CUnit__Unk_004e5c90((void *)((int)this + 0x14),(void *)0x0,(int)unaff_EDI);
          CMenuItemRange__ResetIterator();
          goto LAB_004d0899;
        }
        if (puVar1 != (undefined1 *)0x7a211) {
          iVar11 = 1;
          goto LAB_004d089b;
        }
      }
      puVar2 = (undefined4 *)
               OID__AllocObject(0x4c,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x661);
      local_4 = 0;
      if (puVar2 == (undefined4 *)0x0) {
        puVar2 = (undefined4 *)0x0;
      }
      else {
        CGameMenu__ctor_like_004d0e40(puVar2);
        uVar12 = 0xb000c000;
        uVar10 = 1;
        uVar9 = 0x43a00000;
        uVar8 = 0x43a00000;
        local_4._0_1_ = 1;
        psVar3 = CText__GetStringById(&g_Text,0x77780);
        CMenuItemRangeVariant__Init(psVar3,uVar8,uVar9,uVar10,uVar12);
        local_4._0_1_ = 2;
        CSPtrSet__ctor(puVar2 + 0xf);
        local_4 = CONCAT31(local_4._1_3_,3);
        *puVar2 = &PTR_CFrontEndPage__ActiveNotification_NoOp_005de71c;
        CMenuItemRange__LoadTexture();
      }
      local_4 = 0xffffffff;
      *(undefined4 **)((int)this + 8) = puVar2;
      puVar2 = (undefined4 *)
               OID__AllocObject(0x1c,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x662);
      if (puVar2 == (undefined4 *)0x0) {
        puVar2 = (undefined4 *)0x0;
      }
      else {
        puVar2[1] = 3;
        puVar2[2] = 0x378d6;
        puVar2[3] = 0;
        puVar2[4] = 1;
        puVar2[5] = 0xffd6d6d6;
        puVar2[6] = 0;
        *puVar2 = &PTR_CMenuItem__scalar_deleting_dtor_005db440;
      }
      iVar11 = *(int *)((int)this + 8);
      pvVar4 = (void *)OID__AllocObject(0xc,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x8f2);
      local_4 = 4;
      if (pvVar4 == (void *)0x0) {
        pvVar4 = (void *)0x0;
      }
      else {
        pvVar4 = CPauseMenu__Unk_004d0db0(pvVar4,puVar2,(int)this,0x7d1,unaff_EDI);
      }
      local_4 = 0xffffffff;
      CSPtrSet__AddToHead((void *)(iVar11 + 0x3c),pvVar4);
      CMenuItemRange__AddItem(puVar2);
      puVar2 = (undefined4 *)
               OID__AllocObject(0x1c,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x663);
      if (puVar2 == (undefined4 *)0x0) {
        puVar2 = (undefined4 *)0x0;
      }
      else {
        puVar2[1] = 3;
        puVar2[2] = 0x50cf2;
        puVar2[3] = 0;
        puVar2[4] = 1;
        puVar2[5] = 0xffd6d6d6;
        puVar2[6] = 0;
        *puVar2 = &PTR_CMenuItem__scalar_deleting_dtor_005db440;
      }
      iVar11 = *(int *)((int)this + 8);
      pvVar4 = (void *)OID__AllocObject(0xc,0x80,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x8f2);
      local_4 = 5;
      if (pvVar4 == (void *)0x0) {
        pvVar4 = (void *)0x0;
      }
      else {
        pvVar4 = CPauseMenu__Unk_004d0db0(pvVar4,puVar2,(int)this,2000,unaff_EDI);
      }
      local_4 = 0xffffffff;
      CSPtrSet__AddToHead((void *)(iVar11 + 0x3c),pvVar4);
      CMenuItemRange__AddItem(puVar2);
      pvVar4 = *(void **)((int)this + 8);
      iVar11 = 0;
      do {
        pvVar5 = CGame__GetController(&DAT_008a9a98,iVar11);
        if (pvVar5 != (void *)0x0) {
          pvVar5 = CGame__GetController(&DAT_008a9a98,iVar11);
          pvVar5 = CController__GetToControl(pvVar5);
          if (pvVar5 == this) {
            pvVar5 = pvVar4;
            pvVar6 = CGame__GetController(&DAT_008a9a98,iVar11);
            CController__SetToControl(pvVar6,pvVar5);
          }
        }
        iVar11 = iVar11 + 1;
      } while (iVar11 < 2);
      iVar11 = 1;
      *(undefined1 *)(*(int *)((int)this + 8) + 8) = 1;
    }
    else if (puVar1 == (undefined1 *)0x148fe9) {
      *(undefined4 *)((int)param_1 + 8) = 0x226f16;
      CEngine__Unk_004d3020(DAT_008a9d3c,0,(float)unaff_EDI);
      iVar11 = 1;
    }
    else {
      if (puVar1 != (undefined1 *)0x226f16) goto switchD_004d08cf_caseD_4;
      *(undefined4 *)((int)param_1 + 8) = 0x148fe9;
      CEngine__Unk_004d3020(DAT_008a9d3c,1,(float)unaff_EDI);
      iVar11 = 1;
    }
  }
  else if ((int)puVar1 < 0x939ef5) {
    if (puVar1 == &DAT_00939ef4) {
      ExceptionList = pvVar4;
      return;
    }
    if (puVar1 == (undefined1 *)0x41d6e9) {
      CPauseMenu__Unk_004d06e0(this);
LAB_004d0899:
      iVar11 = 2;
    }
    else {
      if (puVar1 != &LAB_00437a3e) {
        if (puVar1 == &DAT_008251dc) {
switchD_004d08cf_caseD_3:
          pvVar4 = (void *)(*(int *)((int)this + 0x24) + 1);
          goto LAB_004d0c22;
        }
        goto switchD_004d08cf_caseD_4;
      }
      *(undefined4 *)((int)this + 0x10) = 0;
      fVar7 = PLATFORM__GetSysTimeFloat();
      *(float *)((int)this + 0x30) = fVar7;
      if (*(int **)((int)this + 8) != (int *)0x0) {
        (**(code **)(**(int **)((int)this + 8) + 4))(1);
        *(undefined4 *)((int)this + 8) = 0;
      }
      if (*(int **)((int)this + 0x3c) != (int *)0x0) {
        (**(code **)(**(int **)((int)this + 0x3c) + 4))(1);
        *(undefined4 *)((int)this + 0x3c) = 0;
      }
      *(undefined4 *)((int)this + 0x48) = 1;
      *(undefined4 *)((int)this + 0xc) = 1;
      iVar11 = 1;
    }
  }
  else {
    if (puVar1 == (undefined1 *)0x9d5a3f) {
      ExceptionList = pvVar4;
      return;
    }
    if (puVar1 == (undefined1 *)0x1f08cea) {
      *(undefined4 *)((int)this + 0x10) = 0;
      fVar7 = PLATFORM__GetSysTimeFloat();
      *(float *)((int)this + 0x30) = fVar7;
      if (*(int **)((int)this + 8) != (int *)0x0) {
        (**(code **)(**(int **)((int)this + 8) + 4))(1);
        *(undefined4 *)((int)this + 8) = 0;
      }
      if (*(int **)((int)this + 0x3c) != (int *)0x0) {
        (**(code **)(**(int **)((int)this + 0x3c) + 4))(1);
        *(undefined4 *)((int)this + 0x3c) = 0;
      }
      *(undefined4 *)((int)this + 0x48) = 1;
      pvVar4 = DAT_008a9d88;
      iVar11 = 0;
      do {
        pvVar5 = CGame__GetController(&DAT_008a9a98,iVar11);
        if (pvVar5 != (void *)0x0) {
          pvVar5 = CGame__GetController(&DAT_008a9a98,iVar11);
          pvVar5 = CController__GetToControl(pvVar5);
          if (pvVar5 == this) {
            pvVar5 = pvVar4;
            pvVar6 = CGame__GetController(&DAT_008a9a98,iVar11);
            CController__SetToControl(pvVar6,pvVar5);
          }
        }
        iVar11 = iVar11 + 1;
      } while (iVar11 < 2);
      CMessageLog__Unk_004b9ea0((int)DAT_008a9d88);
    }
switchD_004d08cf_caseD_4:
    iVar11 = 1;
  }
LAB_004d089b:
  CFrontEnd__PlaySound(iVar11);
switchD_004d08cf_caseD_4e:
  ExceptionList = local_c;
  return;
}
